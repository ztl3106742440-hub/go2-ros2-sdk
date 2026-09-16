from __future__ import annotations

import math
import threading
from abc import ABC, abstractmethod
from time import monotonic
from typing import Any, Callable

import numpy as np

from .models import MotionCommand, RobotState
from .pointcloud import pointcloud2_xyz

StateCallback = Callable[[RobotState], None]
CloudCallback = Callable[[np.ndarray, float], None]


class RobotBackend(ABC):
    @abstractmethod
    def start(self, state_callback: StateCallback, cloud_callback: CloudCallback | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def move(self, command: MotionCommand) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class MockBackend(RobotBackend):
    """Deterministic-enough synthetic backend for development and class demos."""

    def __init__(self, scenario: str = "boxes"):
        self.scenario = scenario
        self.last_command = MotionCommand.stop()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._state_callback: StateCallback | None = None
        self._cloud_callback: CloudCallback | None = None
        self._started_at = 0.0

    def start(self, state_callback: StateCallback, cloud_callback: CloudCallback | None = None) -> None:
        self._state_callback = state_callback
        self._cloud_callback = cloud_callback
        self._started_at = monotonic()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def move(self, command: MotionCommand) -> None:
        self.last_command = command

    def stop(self) -> None:
        self.last_command = MotionCommand.stop()

    def close(self) -> None:
        self.stop()
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)

    def _run(self) -> None:
        while not self._stop_event.wait(0.05):
            elapsed = monotonic() - self._started_at
            pitch = math.radians(7.0) if self.scenario == "tilt" and 3.0 < elapsed < 5.0 else 0.0
            if self.scenario == "tilt" and 5.0 <= elapsed < 6.5:
                pitch = math.radians(18.0)
            state = RobotState(
                timestamp=monotonic(),
                roll_rad=0.0,
                pitch_rad=pitch,
                yaw_rad=0.0,
                velocity_xyz=(self.last_command.vx, self.last_command.vy, 0.0),
                battery_percent=82,
                position_xyz=(elapsed * self.last_command.vx, 0.0, 0.0),
            )
            if self._state_callback:
                self._state_callback(state)
            if self._cloud_callback:
                self._cloud_callback(self._mock_cloud(elapsed), monotonic())

    def _mock_cloud(self, elapsed: float) -> np.ndarray:
        rng = np.random.default_rng(int(elapsed * 10))
        # Keep background points far away so the teaching demo has clear transitions.
        points = rng.uniform([2.5, -1.2, 0.0], [4.0, 1.2, 0.3], size=(160, 3))
        # A box appears ahead, then clears after the mock robot has had time to bypass it.
        if self.scenario == "boxes" and 3.0 < elapsed < 11.0:
            box = rng.uniform([0.75, -0.18, 0.0], [0.95, 0.18, 0.45], size=(180, 3))
            points = np.vstack((points, box))
        return points.astype(np.float32)


class UnitreeSdkBackend(RobotBackend):
    """Thin adapter around unitree_sdk2_python.

    SDK imports are intentionally lazy so offline tests do not require the SDK.
    Point-cloud topic candidates still require read-only validation on the real Go2.
    """

    def __init__(self, interface: str, topics: dict[str, Any], armed: bool = False):
        self.interface = interface
        self.topics = topics
        self.armed = armed
        self._sport_client: Any = None
        self._subscribers: list[Any] = []
        self._latest_low_state: Any = None
        self._state_callback: StateCallback | None = None

    def start(self, state_callback: StateCallback, cloud_callback: CloudCallback | None = None) -> None:
        try:
            from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
            from unitree_sdk2py.go2.sport.sport_client import SportClient
            from unitree_sdk2py.idl.sensor_msgs.msg.dds_ import PointCloud2_
            from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_, SportModeState_
        except ImportError as exc:
            raise RuntimeError(
                "unitree_sdk2py is not installed. Run: "
                "python3 -m pip install -e /home/ztl/unitree_sdk2_python"
            ) from exc

        ChannelFactoryInitialize(0, self.interface)
        self._state_callback = state_callback

        low_sub = ChannelSubscriber(self.topics["low_state"], LowState_)
        low_sub.Init(self._on_low_state, 10)
        sport_sub = ChannelSubscriber(self.topics["sport_state"], SportModeState_)
        sport_sub.Init(self._on_sport_state, 10)
        self._subscribers.extend((low_sub, sport_sub))

        if cloud_callback:
            # First candidate only for now. Use the probe command before changing this.
            cloud_topic = self.topics["point_cloud_candidates"][0]

            def on_cloud(message: Any) -> None:
                cloud_callback(pointcloud2_xyz(message), monotonic())

            cloud_sub = ChannelSubscriber(cloud_topic, PointCloud2_)
            cloud_sub.Init(on_cloud, 2)
            self._subscribers.append(cloud_sub)

        self._sport_client = SportClient()
        self._sport_client.SetTimeout(3.0)
        self._sport_client.Init()

    def move(self, command: MotionCommand) -> None:
        if not self.armed:
            return
        self._sport_client.Move(command.vx, command.vy, command.vyaw)

    def stop(self) -> None:
        if self._sport_client is not None and self.armed:
            self._sport_client.StopMove()

    def close(self) -> None:
        self.stop()
        for subscriber in self._subscribers:
            try:
                subscriber.Close()
            except Exception:
                pass

    def _on_low_state(self, message: Any) -> None:
        self._latest_low_state = message

    def _on_sport_state(self, message: Any) -> None:
        battery = None
        if self._latest_low_state is not None:
            battery = int(self._latest_low_state.bms_state.soc)
        state = RobotState(
            timestamp=monotonic(),
            roll_rad=float(message.imu_state.rpy[0]),
            pitch_rad=float(message.imu_state.rpy[1]),
            yaw_rad=float(message.imu_state.rpy[2]),
            velocity_xyz=tuple(float(value) for value in message.velocity),
            battery_percent=battery,
            position_xyz=tuple(float(value) for value in message.position),
        )
        if self._state_callback:
            self._state_callback(state)
