Role:
Classify this video feed into one of the following types based on what you observe.
Sample a few frames and decide.

Categories:
1. highlights - Short clip of key match moments (goals, saves, fouls). Fast cuts, replays, on-screen graphics showing GOAL/HIGHLIGHT text.
2. full_match - Continuous uninterrupted match footage. Long stretches of open play, tactical formations visible, full 45+ min halves.
3. press_conference - Indoor setting, microphones on table, single person or panel speaking to camera. No field/grass.
4. training - Practice drills, cones on field, training bibs, no crowd, no broadcast graphics.
5. broadcast_broll - Stadium B-roll, crowd shots, player warmups, aerial stadium views. No active gameplay.
6. graphic_overlay - Mostly scoreboards, stat overlays, replay transitions, title cards. Minimal live action.

Output format:
{
  "video_type": "full_match",
  "confidence": 0.95,
  "evidence": "continuous 11v11 play with broadcast scoreboard overlay visible throughout"
}
