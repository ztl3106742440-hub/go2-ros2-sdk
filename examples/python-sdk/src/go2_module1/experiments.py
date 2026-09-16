from __future__ import annotations

import math
import threading
from pathlib import Path
from time import monotonic, sleep
from typing import Any

from .avoidance import AvoidanceController
from .backend import RobotBackend
from .models import AvoidanceDecision, MotionCommand, RobotState, SectorDistances
from .perception import SectorPerception
from .recorder import CsvRecorder
from .safety import ImuSafetyController


class SharedData:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.state: RobotState | None = None
        self.sectors: SectorDistances | None = None

    def set_state(self, state: RobotState) -> None:
        with self.lock:
            self.state = state

    def set_sectors(self, sectors: SectorDistances) -> None:
        with self.lock:
            self.sectors = sectors

    def snapshot(self) -> tuple[RobotState | None, SectorDistances | None]:
        with self.lock:
            return self.state, self.sectors


def experiment1(backend: RobotBackend, duration: float, output: Path) -> None:
    shared = SharedData()
    backend.start(shared.set_state)
    try:
        with CsvRecorder(output) as recorder:
            end = monotonic() + duration
            while monotonic() < end:
                state, _ = shared.snapshot()
                if state:
                    recorder.write(state)
                    print(
                        f"RPY=({state.roll_deg:6.1f}, {state.pitch_deg:6.1f}, {state.yaw_deg:6.1f}) deg "
                        f"velocity={state.velocity_xyz} battery={state.battery_percent}%"
                    )
                sleep(0.1)
    finally:
        backend.close()


def experiment2(backend: RobotBackend) -> None:
    backend.start(lambda _: None)
    square = [
        (MotionCommand(vx=0.2), 1.5, "forward"),
        (MotionCommand(vyaw=-math.pi / 4), 2.0, "turn right"),
    ] * 4
    try:
        for command, duration, label in square:
            print(label, command)
            backend.move(command)
            sleep(duration)
            backend.stop()
            sleep(0.3)
    finally:
        backend.close()


def experiment3(
    backend: RobotBackend, safety_config: dict[str, Any], duration: float, output: Path
) -> None:
    shared = SharedData()
    controller = ImuSafetyController(safety_config)
    backend.start(shared.set_state)
    try:
        with CsvRecorder(output) as recorder:
            end = monotonic() + duration
            while monotonic() < end:
                state, _ = shared.snapshot()
                command, reason = controller.command_for(
                    state, float(safety_config["normal_speed_mps"])
                )
                backend.move(command)
                if state:
                    recorder.write(state)
                    print(f"{reason:14s} pitch={state.pitch_deg:5.1f} roll={state.roll_deg:5.1f}")
                sleep(0.05)
    finally:
        backend.close()


def experiment4(
    backend: RobotBackend,
    lidar_config: dict[str, Any],
    avoidance_config: dict[str, Any],
    safety_config: dict[str, Any],
    duration: float,
    output: Path,
) -> None:
    shared = SharedData()
    perception = SectorPerception(lidar_config)
    controller = AvoidanceController(avoidance_config)
    safety = ImuSafetyController(safety_config)

    def on_cloud(points: Any, timestamp: float) -> None:
        shared.set_sectors(perception.analyze(points, timestamp))

    backend.start(shared.set_state, on_cloud)
    try:
        with CsvRecorder(output) as recorder:
            end = monotonic() + duration
            while monotonic() < end:
                state, sectors = shared.snapshot()
                if state is None or sectors is None:
                    backend.stop()
                    print("waiting_for_state_and_cloud")
                    sleep(0.05)
                    continue
                decision = controller.update(sectors)
                safety_command, safety_reason = safety.command_for(state, decision.command.vx)
                if safety_reason == "tilt_slow":
                    decision = AvoidanceDecision(
                        decision.mode,
                        MotionCommand(vx=safety_command.vx),
                        safety_reason,
                        decision.chosen_side,
                        (*decision.events, "imu_slow"),
                    )
                elif safety_reason != "normal":
                    decision = AvoidanceDecision(
                        decision.mode,
                        MotionCommand.stop(),
                        safety_reason,
                        decision.chosen_side,
                        (*decision.events, "imu_stop"),
                    )
                backend.move(decision.command)
                if state:
                    recorder.write(state, sectors, decision)
                if sectors:
                    print(
                        f"{decision.mode.value:12s} L/F/R="
                        f"{sectors.left:.2f}/{sectors.front:.2f}/{sectors.right:.2f} "
                        f"{decision.reason}"
                    )
                sleep(0.05)
    finally:
        backend.close()
