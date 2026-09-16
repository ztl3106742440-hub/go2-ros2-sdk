from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class RobotState:
    timestamp: float
    roll_rad: float
    pitch_rad: float
    yaw_rad: float
    velocity_xyz: tuple[float, float, float]
    battery_percent: Optional[int] = None
    position_xyz: Optional[tuple[float, float, float]] = None

    @property
    def roll_deg(self) -> float:
        return float(np.degrees(self.roll_rad))

    @property
    def pitch_deg(self) -> float:
        return float(np.degrees(self.pitch_rad))

    @property
    def yaw_deg(self) -> float:
        return float(np.degrees(self.yaw_rad))


@dataclass(frozen=True)
class MotionCommand:
    vx: float = 0.0
    vy: float = 0.0
    vyaw: float = 0.0

    @classmethod
    def stop(cls) -> "MotionCommand":
        return cls()


@dataclass(frozen=True)
class SectorDistances:
    timestamp: float
    left: float
    front: float
    right: float
    point_count: int = 0


class AvoidanceMode(str, Enum):
    FORWARD = "forward"
    SLOW_DOWN = "slow_down"
    ASSESS = "assess"
    TURN = "turn"
    SIDESTEP = "sidestep"
    PASS = "pass"
    RECOVER = "recover"
    SAFETY_STOP = "safety_stop"
    FINISHED = "finished"


@dataclass(frozen=True)
class AvoidanceDecision:
    mode: AvoidanceMode
    command: MotionCommand
    reason: str
    chosen_side: Optional[str] = None
    events: tuple[str, ...] = field(default_factory=tuple)

