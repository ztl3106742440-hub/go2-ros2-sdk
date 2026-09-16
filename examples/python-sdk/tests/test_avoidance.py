import unittest

from go2_module1.avoidance import AvoidanceController
from go2_module1.models import AvoidanceMode, SectorDistances


class AvoidanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "cruise_speed_mps": 0.25,
            "slow_speed_mps": 0.12,
            "sidestep_speed_mps": 0.22,
            "turn_speed_radps": 0.45,
            "slow_distance_m": 1.5,
            "stop_distance_m": 0.9,
            "clear_distance_m": 1.4,
            "side_clearance_m": 0.8,
            "decision_margin_m": 0.15,
            "confirm_frames": 2,
            "assess_duration_s": 0.2,
            "turn_duration_s": 0.2,
            "sidestep_duration_s": 0.2,
            "pass_duration_s": 0.2,
            "recover_duration_s": 0.2,
            "max_state_duration_s": 2.0,
            "cloud_timeout_s": 1.0,
        }

    def sectors(self, timestamp: float, front: float, left: float = 3.0, right: float = 1.0):
        return SectorDistances(timestamp, left, front, right, 100)

    def test_selects_clearer_left_side(self) -> None:
        controller = AvoidanceController(self.config)
        controller.update(self.sectors(0.0, 0.8), now=0.0)
        decision = controller.update(self.sectors(0.1, 0.8), now=0.1)
        self.assertEqual(decision.mode, AvoidanceMode.ASSESS)
        decision = controller.update(self.sectors(0.4, 0.8), now=0.4)
        self.assertEqual(decision.mode, AvoidanceMode.TURN)
        self.assertEqual(decision.chosen_side, "left")

    def test_cloud_timeout_stops(self) -> None:
        controller = AvoidanceController(self.config)
        decision = controller.update(self.sectors(0.0, 4.0), now=2.0)
        self.assertEqual(decision.mode, AvoidanceMode.SAFETY_STOP)


if __name__ == "__main__":
    unittest.main()

