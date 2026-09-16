from __future__ import annotations

from collections import deque
from time import monotonic
from typing import Any

import numpy as np

from .models import SectorDistances


AXIS_INDEX = {"x": 0, "y": 1, "z": 2}


class SectorPerception:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._history: deque[SectorDistances] = deque(
            maxlen=int(config.get("smoothing_frames", 3))
        )

    def analyze(self, xyz: np.ndarray, timestamp: float | None = None) -> SectorDistances:
        cfg = self.config
        forward = xyz[:, AXIS_INDEX[cfg["forward_axis"]]] * float(cfg["forward_sign"])
        left = xyz[:, AXIS_INDEX[cfg["left_axis"]]] * float(cfg["left_sign"])
        up = xyz[:, AXIS_INDEX[cfg["up_axis"]]] * float(cfg["up_sign"])
        radial = np.hypot(forward, left)

        valid = (
            (up >= float(cfg["min_height_m"]))
            & (up <= float(cfg["max_height_m"]))
            & (radial >= float(cfg["min_range_m"]))
            & (radial <= float(cfg["max_range_m"]))
            & (forward > 0.0)
        )
        forward = forward[valid]
        left = left[valid]
        max_range = float(cfg["max_range_m"])
        front_half = float(cfg["front_half_width_m"])
        side_inner = float(cfg["side_inner_m"])
        side_outer = float(cfg["side_outer_m"])

        result = SectorDistances(
            timestamp=monotonic() if timestamp is None else timestamp,
            left=self._distance(forward[(left >= side_inner) & (left <= side_outer)], max_range),
            front=self._distance(forward[np.abs(left) < front_half], max_range),
            right=self._distance(forward[(left <= -side_inner) & (left >= -side_outer)], max_range),
            point_count=int(valid.sum()),
        )
        self._history.append(result)
        return self._smoothed()

    def _distance(self, forward_values: np.ndarray, default: float) -> float:
        if len(forward_values) < int(self.config["minimum_points"]):
            return default
        return float(np.percentile(forward_values, float(self.config["distance_percentile"])))

    def _smoothed(self) -> SectorDistances:
        latest = self._history[-1]
        return SectorDistances(
            timestamp=latest.timestamp,
            left=float(np.median([item.left for item in self._history])),
            front=float(np.median([item.front for item in self._history])),
            right=float(np.median([item.right for item in self._history])),
            point_count=latest.point_count,
        )

