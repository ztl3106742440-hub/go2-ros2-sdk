from __future__ import annotations

import csv
from pathlib import Path

from .models import AvoidanceDecision, RobotState, SectorDistances


class CsvRecorder:
    FIELDNAMES = [
        "timestamp",
        "roll_deg",
        "pitch_deg",
        "yaw_deg",
        "vx",
        "vy",
        "vz",
        "battery_percent",
        "sector_left",
        "sector_front",
        "sector_right",
        "mode",
        "reason",
    ]

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", encoding="utf-8", newline="")
        self._writer = csv.DictWriter(self._handle, fieldnames=self.FIELDNAMES)
        self._writer.writeheader()

    def write(
        self,
        state: RobotState,
        sectors: SectorDistances | None = None,
        decision: AvoidanceDecision | None = None,
    ) -> None:
        self._writer.writerow(
            {
                "timestamp": f"{state.timestamp:.6f}",
                "roll_deg": f"{state.roll_deg:.3f}",
                "pitch_deg": f"{state.pitch_deg:.3f}",
                "yaw_deg": f"{state.yaw_deg:.3f}",
                "vx": f"{state.velocity_xyz[0]:.3f}",
                "vy": f"{state.velocity_xyz[1]:.3f}",
                "vz": f"{state.velocity_xyz[2]:.3f}",
                "battery_percent": state.battery_percent,
                "sector_left": "" if sectors is None else f"{sectors.left:.3f}",
                "sector_front": "" if sectors is None else f"{sectors.front:.3f}",
                "sector_right": "" if sectors is None else f"{sectors.right:.3f}",
                "mode": "" if decision is None else decision.mode.value,
                "reason": "" if decision is None else decision.reason,
            }
        )
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()

    def __enter__(self) -> "CsvRecorder":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

