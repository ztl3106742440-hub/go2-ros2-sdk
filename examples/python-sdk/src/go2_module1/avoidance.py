from __future__ import annotations

from time import monotonic
from typing import Any

from .models import AvoidanceDecision, AvoidanceMode, MotionCommand, SectorDistances


class AvoidanceController:
    """Teaching-oriented local avoidance state machine.

    This is an initial framework. Durations and transitions must be tuned on the
    real Go2 before it is used for the filmed obstacle course.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.mode = AvoidanceMode.FORWARD
        self.chosen_side: str | None = None
        self._entered_at = monotonic()
        self._blocked_frames = 0
        self.avoidance_count = 0

    def reset(self) -> None:
        self.__init__(self.config)

    def update(
        self, sectors: SectorDistances | None, now: float | None = None
    ) -> AvoidanceDecision:
        now = monotonic() if now is None else now
        cfg = self.config
        events: list[str] = []

        if sectors is None:
            return self._enter(AvoidanceMode.SAFETY_STOP, now, "cloud_missing")
        if now - sectors.timestamp > float(cfg["cloud_timeout_s"]):
            return self._enter(AvoidanceMode.SAFETY_STOP, now, "cloud_timeout")
        if self.mode == AvoidanceMode.SAFETY_STOP:
            return self._decision(MotionCommand.stop(), "manual_reset_required")

        elapsed = now - self._entered_at
        if elapsed > float(cfg["max_state_duration_s"]) and self.mode not in {
            AvoidanceMode.FORWARD,
            AvoidanceMode.SLOW_DOWN,
        }:
            return self._enter(AvoidanceMode.SAFETY_STOP, now, "state_timeout")

        if self.mode == AvoidanceMode.FORWARD:
            if sectors.front <= float(cfg["stop_distance_m"]):
                self._blocked_frames += 1
                if self._blocked_frames >= int(cfg["confirm_frames"]):
                    return self._enter(AvoidanceMode.ASSESS, now, "front_blocked")
            else:
                self._blocked_frames = 0
            if sectors.front <= float(cfg["slow_distance_m"]):
                self.mode = AvoidanceMode.SLOW_DOWN
                self._entered_at = now
                events.append("slow_down")
                return self._decision(
                    MotionCommand(vx=float(cfg["slow_speed_mps"])),
                    "obstacle_near",
                    events,
                )
            return self._decision(MotionCommand(vx=float(cfg["cruise_speed_mps"])), "path_clear")

        if self.mode == AvoidanceMode.SLOW_DOWN:
            if sectors.front <= float(cfg["stop_distance_m"]):
                self._blocked_frames += 1
                if self._blocked_frames >= int(cfg["confirm_frames"]):
                    return self._enter(AvoidanceMode.ASSESS, now, "front_blocked")
            elif sectors.front > float(cfg["clear_distance_m"]):
                return self._enter(AvoidanceMode.FORWARD, now, "path_clear")
            return self._decision(MotionCommand(vx=float(cfg["slow_speed_mps"])), "obstacle_near")

        if self.mode == AvoidanceMode.ASSESS:
            if elapsed < float(cfg["assess_duration_s"]):
                return self._decision(MotionCommand.stop(), "assessing")
            self.chosen_side = "left" if sectors.left >= sectors.right else "right"
            if max(sectors.left, sectors.right) < float(cfg["side_clearance_m"]):
                return self._enter(AvoidanceMode.SAFETY_STOP, now, "no_side_clearance")
            return self._enter(AvoidanceMode.TURN, now, "side_selected", ("side_selected",))

        sign = 1.0 if self.chosen_side == "left" else -1.0
        if self.mode == AvoidanceMode.TURN:
            if elapsed >= float(cfg["turn_duration_s"]):
                return self._enter(AvoidanceMode.SIDESTEP, now, "turn_complete")
            return self._decision(
                MotionCommand(vyaw=sign * float(cfg["turn_speed_radps"])), "turning"
            )

        if self.mode == AvoidanceMode.SIDESTEP:
            if elapsed >= float(cfg["sidestep_duration_s"]):
                return self._enter(AvoidanceMode.PASS, now, "sidestep_complete")
            return self._decision(
                MotionCommand(vy=sign * float(cfg["sidestep_speed_mps"])), "sidestepping"
            )

        if self.mode == AvoidanceMode.PASS:
            if elapsed >= float(cfg["pass_duration_s"]):
                return self._enter(AvoidanceMode.RECOVER, now, "obstacle_passed")
            return self._decision(MotionCommand(vx=float(cfg["slow_speed_mps"])), "passing")

        if self.mode == AvoidanceMode.RECOVER:
            if elapsed >= float(cfg["recover_duration_s"]):
                self.avoidance_count += 1
                self.chosen_side = None
                return self._enter(AvoidanceMode.FORWARD, now, "recovered", ("avoidance_complete",))
            return self._decision(
                MotionCommand(vy=-sign * float(cfg["sidestep_speed_mps"])), "recovering"
            )

        return self._decision(MotionCommand.stop(), "finished")

    def _enter(
        self,
        mode: AvoidanceMode,
        now: float,
        reason: str,
        events: tuple[str, ...] = (),
    ) -> AvoidanceDecision:
        self.mode = mode
        self._entered_at = now
        self._blocked_frames = 0
        return self._decision(MotionCommand.stop(), reason, list(events))

    def _decision(
        self, command: MotionCommand, reason: str, events: list[str] | None = None
    ) -> AvoidanceDecision:
        return AvoidanceDecision(
            mode=self.mode,
            command=command,
            reason=reason,
            chosen_side=self.chosen_side,
            events=tuple(events or ()),
        )

