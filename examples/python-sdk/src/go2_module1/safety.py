from __future__ import annotations

from time import monotonic
from typing import Any

from .models import MotionCommand, RobotState


class ImuSafetyController:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def command_for(self, state: RobotState | None, desired_vx: float) -> tuple[MotionCommand, str]:
        if state is None or monotonic() - state.timestamp > float(self.config["state_timeout_s"]):
            return MotionCommand.stop(), "state_timeout"

        pitch = abs(state.pitch_deg)
        roll = abs(state.roll_deg)
        if pitch >= float(self.config["stop_pitch_deg"]) or roll >= float(
            self.config["stop_roll_deg"]
        ):
            return MotionCommand.stop(), "tilt_stop"
        if pitch >= float(self.config["slow_pitch_deg"]) or roll >= float(
            self.config["slow_roll_deg"]
        ):
            return MotionCommand(vx=min(desired_vx, float(self.config["slow_speed_mps"]))), "tilt_slow"
        return MotionCommand(vx=desired_vx), "normal"

