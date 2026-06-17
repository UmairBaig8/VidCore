import csv
from pathlib import Path
from core.paths import output_dir


def save_csv(events, video_name):
    out = output_dir() / "csv"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{video_name}.csv"

    fieldnames = ["timestamp", "scene", "event", "reasoning", "commentary"]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for ev in events:
            row = {k: ev.get(k, "") for k in fieldnames}
            writer.writerow(row)

    return path
