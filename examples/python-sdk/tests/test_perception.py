import unittest

import numpy as np

from go2_module1.perception import SectorPerception


class SectorPerceptionTest(unittest.TestCase):
    def test_detects_front_box_and_clear_left(self) -> None:
        config = {
            "forward_axis": "x",
            "left_axis": "y",
            "up_axis": "z",
            "forward_sign": 1.0,
            "left_sign": 1.0,
            "up_sign": 1.0,
            "min_height_m": -0.05,
            "max_height_m": 0.35,
            "min_range_m": 0.3,
            "max_range_m": 4.0,
            "front_half_width_m": 0.35,
            "side_inner_m": 0.2,
            "side_outer_m": 1.1,
            "distance_percentile": 10.0,
            "minimum_points": 3,
            "smoothing_frames": 1,
        }
        front = np.tile([0.8, 0.0, 0.1], (10, 1))
        right = np.tile([1.5, -0.7, 0.1], (10, 1))
        result = SectorPerception(config).analyze(np.vstack((front, right)), timestamp=1.0)
        self.assertAlmostEqual(result.front, 0.8)
        self.assertAlmostEqual(result.right, 1.5)
        self.assertAlmostEqual(result.left, 4.0)


if __name__ == "__main__":
    unittest.main()

