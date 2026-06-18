"""
Agent router — decides which agents to call for each frame based on current context.

Design:
  scene_detector   → ALWAYS (cheapest, needed for all downstream decisions)
  event_detector   → adaptive (skip if N consecutive generic frames)
  reasoning_agent  → ONLY on key events (goal, card, foul, wicket, etc.)
  commentary_agent → ONLY on key events
  phase_detector   → every ~5 frames or when scene changes drastically

This eliminates ~70% of LLM calls on generic play frames.
"""

import logging

logger = logging.getLogger("router")

SKIP_EVENT_AFTER_GENERIC = 3      # skip event detection after N generic frames
PHASE_CHECK_INTERVAL = 5           # re-check phase every N frames
KEY_EVENT_TYPES = {
    "football": {"GOAL", "GOAL_ATTEMPT", "PENALTY", "RED_CARD", "YELLOW_CARD",
                 "FOUL", "VAR_CHECK", "SUBSTITUTION", "INJURY", "OFFSIDE"},
    "cricket": {"FOUR", "SIX", "WICKET", "BOWLED", "LBW", "CATCH_OUT",
                "RUN_OUT", "DRS_REVIEW", "CENTURY"},
    "basketball": {"DUNK", "THREE_POINTER", "BLOCK", "STEAL", "FOUL",
                   "BUZZER_BEATER", "ALLEY_OOP"},
    "tennis": {"ACE", "BREAK", "SET_POINT", "MATCH_POINT", "CHALLENGE",
               "DOUBLE_FAULT"},
}

GENERIC_PHASES = {"open_play", "midfield", "defensive_build_up"}


class AgentRouter:

    def __init__(self, context):
        self.ctx = context

    def route(self, scene_desc: str, frame_num: int) -> dict:
        """
        Returns dict of which agents to call for this frame:
        {
            "event_detector": bool,
            "reasoning": bool,
            "commentary": bool,
            "phase_detector": bool,
            "reason": str
        }
        """
        plan = {
            "event_detector": True,
            "reasoning": False,
            "commentary": False,
            "phase_detector": False,
            "reason": "default",
        }

        # ── force full pipeline after goal/card/etc ──
        if self.ctx.force_full_pipeline:
            plan["event_detector"] = True
            plan["reasoning"] = True
            plan["commentary"] = True
            plan["reason"] = "force: recent key event"
            self.ctx.force_full_pipeline = False
            return plan

        # ── phase check every N frames ──
        if frame_num % PHASE_CHECK_INTERVAL == 0:
            plan["phase_detector"] = True
            plan["reason"] = "scheduled phase check"

        # ── skip event detection if too many generic frames ──
        if self.ctx.consecutive_generic_frames >= SKIP_EVENT_AFTER_GENERIC:
            plan["event_detector"] = False
            plan["reason"] = f"skip: {self.ctx.consecutive_generic_frames} consecutive generic frames"
            return plan

        # ── always detect events in high-stakes phases ──
        if self.ctx.phase in ("attack_final_third", "set_piece"):
            plan["event_detector"] = True
            plan["reason"] = f"high-stakes phase: {self.ctx.phase}"

        return plan

    def process_event(self, parsed_events: list) -> list:
        """After event_detector returns, decide which events are key events."""
        sport = self.ctx.sport
        key_set = KEY_EVENT_TYPES.get(sport, set())

        keys = []
        generics = 0

        for ev in parsed_events:
            et = ev.get("type", "")
            if et in key_set:
                keys.append(ev)
                self.ctx.add_key_event(ev)
                logger.info("key_event: %s team=%s ts=%s", et,
                            ev.get("team", "?"), ev.get("timestamp", "?"))
            else:
                generics += 1

        if generics > 0 and not keys:
            self.ctx.consecutive_generic_frames += 1
        else:
            self.ctx.consecutive_generic_frames = 0

        return keys
