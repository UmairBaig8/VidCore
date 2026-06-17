import cv2
from skills.video_loader import open_video


def sample_frames(video_path, interval=0.5):
    cap = open_video(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    step = int(fps * interval)
    if step < 1:
        step = 1

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % step == 0:
            yield frame_idx / fps, frame
        frame_idx += 1

    cap.release()


def count_frames(video_path, interval=0.5):
    cap = open_video(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    step = int(fps * interval)
    if step < 1:
        step = 1

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        duration_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        if duration_ms <= 0:
            cap.release()
            return 0
        total = int(fps * duration_ms / 1000)

    cap.release()
    count = total // step
    return count if count > 0 else 1
