"""
Pro video template builder — intro cards, score overlays, transitions, outro cards.
All powered by ffmpeg filtergraphs.
"""

import subprocess
import tempfile
from pathlib import Path


def _safe(text):
    return text.replace("'", "'\\\\''").replace(":", "\\:")


def build_intro(video_path, title, subtitle="", duration=3.0):
    """Prepend an intro card to an existing video."""
    import tempfile
    tmp = Path(tempfile.mktemp(suffix=".mp4"))

    vf = (
        f"drawtext=fontsize=48:fontcolor=white:"
        f"text='{_safe(title)}':x=(w-text_w)/2:y=(h-text_h)/2-30:"
        f"enable='between(t,0,{duration})',"
        f"drawtext=fontsize=28:fontcolor=#cccccc:"
        f"text='{_safe(subtitle)}':x=(w-text_w)/2:y=(h-text_h)/2+30:"
        f"enable='between(t,0,{duration})'"
    )

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(video_path),
        "-vf", vf,
        "-c:a", "copy",
        str(tmp),
    ], check=False)
    return tmp if tmp.exists() else video_path


def add_score_overlay(video_path, score_text, position="top-right"):
    """Add score text overlay on a clip."""
    tmp = Path(tempfile.mktemp(suffix=".mp4"))

    if position == "top-right":
        x_expr = "w-text_w-20"
        y_expr = "20"
    elif position == "top-left":
        x_expr = "20"
        y_expr = "20"
    else:
        x_expr = "(w-text_w)/2"
        y_expr = "20"

    vf = (
        f"drawtext=fontsize=36:fontcolor=white:box=1:"
        f"boxcolor=black@0.6:boxborderw=10:"
        f"text='{_safe(score_text)}':x={x_expr}:y={y_expr}:"
        f"enable='between(t,0,5)'"
    )

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(video_path),
        "-vf", vf,
        "-c:a", "copy",
        str(tmp),
    ], check=False)
    return tmp if tmp.exists() else video_path


def add_transition(clip_a, clip_b, transition="fade", duration=0.5):
    """Crossfade between two clips."""
    if transition != "fade":
        return [clip_a, clip_b]

    tmp = Path(tempfile.mktemp(suffix=".mp4"))
    # xfade requires both clips to be same resolution/fps
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(clip_a),
        "-i", str(clip_b),
        "-filter_complex",
        f"xfade=transition=fade:duration={duration}:offset=0",
        "-c:a", "copy",
        str(tmp),
    ], check=False)
    return tmp if tmp.exists() else clip_b


def build_pro_reel(clip_paths, output_path, intro_title="Highlights",
                   intro_subtitle="VidCore AI", score="0-0"):
    """Build a pro-level reel with intro, overlays, and stitching."""
    if not clip_paths:
        return None

    processed = []
    for i, cp in enumerate(clip_paths):
        p = Path(cp)
        if p.exists():
            p = add_score_overlay(p, f"⚽ {score}")
            processed.append(str(p))

    if not processed:
        return None

    if len(processed) == 1:
        final = build_intro(Path(processed[0]), intro_title, intro_subtitle)
        subprocess.run(["cp", str(final), str(output_path)])
        return output_path

    # concat with concat filter (supports transitions)
    concat_file = output_path.with_suffix(".txt")
    lines = [f"file '{p}'" for p in processed]
    concat_file.write_text("\n".join(lines))

    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path),
    ], check=True)

    concat_file.unlink(missing_ok=True)

    final = build_intro(output_path, intro_title, intro_subtitle)
    if final != output_path:
        subprocess.run(["mv", str(final), str(output_path)])

    return output_path
