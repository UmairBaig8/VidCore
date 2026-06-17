"""
Event-driven live reel generator — generates clips as key events are detected,
not waiting for full analysis to complete.
"""

import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

from core.paths import output_dir
from skills.highlight_reel import _check_ffmpeg


class LiveReelBuilder:
    """Accumulates clips as events are detected during live analysis."""

    def __init__(self, video_path, video_name, clip_before=8.0, clip_after=5.0):
        self.video_path = video_path
        self.video_name = video_name
        self.clip_before = clip_before
        self.clip_after = clip_after
        self.clips = []
        self.events_log = []
        self.use_ffmpeg = _check_ffmpeg()

        self.out_dir = output_dir() / "reels" / "live"
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def add_event(self, event):
        """Called when a key event is detected. Extracts clip immediately."""
        if not self.use_ffmpeg:
            return None

        ts = event.get("timestamp", "").replace("s", "")
        try:
            t = float(ts)
        except (ValueError, TypeError):
            return None

        event_type = event.get("type", "event")
        team = event.get("team", "")
        player = event.get("player", event.get("batsman", ""))

        start = max(0, t - self.clip_before)
        duration = self.clip_before + self.clip_after
        idx = len(self.clips)

        clip_path = self.out_dir / f"{self.video_name}_live_{idx:03d}.mp4"

        try:
            self._extract_clip(start, duration, clip_path)
        except Exception as e:
            print(f"\n    ⚠ clip extract failed: {e}", flush=True)
            return None

        overlay_path = self._add_event_overlay(clip_path, event_type, t, team, idx) or clip_path

        self.clips.append({
            "path": str(overlay_path),
            "timestamp": t,
            "event_type": event_type,
            "team": team,
            "player": player,
            "time": datetime.now().isoformat(),
        })
        self.events_log.append(event)

        self._write_manifest()

        try:
            self._update_growing_reel()
        except Exception as e:
            print(f"\n    ⚠ reel concat failed: {e}", flush=True)

        mm, ss = int(t // 60), int(t % 60)
        print(f"\n  📼 [{mm:02d}:{ss:02d}] {event_type}"
              f"{' (' + team + ')' if team else ''} "
              f"→ clip {idx} ({len(self.clips)} total)", flush=True)

        return self.clips[-1]

    def _update_growing_reel(self):
        """Re-concat all clips into the growing reel — call after each new event."""
        growing_path = self.out_dir / f"{self.video_name}_reel.mp4"
        if len(self.clips) == 1:
            subprocess.run(["cp", self.clips[0]["path"], str(growing_path)])
        else:
            concat_file = growing_path.with_suffix(".txt")
            lines = [f"file '{p['path']}'" for p in self.clips]
            concat_file.write_text("\n".join(lines))
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                str(growing_path),
            ], check=True)
            concat_file.unlink(missing_ok=True)

    def _extract_clip(self, start_sec, duration, out_path):
        try:
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "warning",
                "-ss", str(start_sec),
                "-i", str(self.video_path),
                "-t", str(duration),
                "-c", "copy",
                str(out_path),
            ], check=True, timeout=30)
        except subprocess.CalledProcessError as e:
            print(f"\n    ⚠ clip extraction failed (time={start_sec:.1f}s): {e}", flush=True)
            raise

    def _add_event_overlay(self, clip_path, event_type, timestamp, team, idx):
        """Add text overlay showing event type + time on the clip."""
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=".mp4"))
        label = f"{event_type}"
        if team:
            label += f" ({team})"
        time_label = f"{int(timestamp // 60)}:{int(timestamp % 60):02d}"

        label_esc = label.replace("'", "'\\\\''").replace(":", "\\:")
        time_esc = time_label.replace("'", "'\\\\''").replace(":", "\\:")

        vf = (
            f"drawtext=fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5:"
            f"boxborderw=8:"
            f"text='{label_esc}':x=10:y=10:enable='between(t,0,3)',"
            f"drawtext=fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:"
            f"boxborderw=8:"
            f"text='{time_esc}':x=w-text_w-10:y=10:enable='between(t,0,3)'"
        )

        try:
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "warning",
                "-i", str(clip_path),
                "-vf", vf,
                "-c:a", "copy",
                str(tmp),
            ], check=True, timeout=30)
            tmp.replace(clip_path)
        except Exception:
            return clip_path
        return clip_path

    def _write_manifest(self):
        import json
        manifest = {
            "video_name": self.video_name,
            "clips": self.clips,
            "count": len(self.clips),
            "last_updated": datetime.now().isoformat(),
        }
        manifest_path = self.out_dir / f"{self.video_name}_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))

    def finalize(self, intro_text="", outro_text=""):
        """Return the path to the final reel (already up to date)."""
        final_path = self.out_dir / f"{self.video_name}_reel.mp4"
        return final_path if final_path.exists() else None
