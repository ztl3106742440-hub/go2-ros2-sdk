import math
import unittest
from time import monotonic

from go2_module1.models import RobotState
from go2_module1.safety import ImuSafetyController


class SafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = ImuSafetyController(
            {
                "slow_pitch_deg": 5.0,
                "stop_pitch_deg": 15.0,
                "slow_roll_deg": 8.0,
                "stop_roll_deg": 18.0,
                "slow_speed_mps": 0.15,
                "state_timeout_s": 0.5,
            }
        )

    def state(self, pitch_deg: float) -> RobotState:
        return RobotState(monotonic(), 0.0, math.radians(pitch_deg), 0.0, (0, 0, 0))

    def test_slows_on_warning_tilt(self) -> None:
        command, reason = self.controller.command_for(self.state(8.0), 0.3)
        self.assertEqual(reason, "tilt_slow")
        self.assertEqual(command.vx, 0.15)

    def test_stops_on_excessive_tilt(self) -> None:
        command, reason = self.controller.command_for(self.state(16.0), 0.3)
        self.assertEqual(reason, "tilt_stop")
        self.assertEqual(command.vx, 0.0)


if __name__ == "__main__":
    unittest.main()

