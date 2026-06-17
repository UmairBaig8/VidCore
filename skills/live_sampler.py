import cv2
import time
from skills.video_loader import open_video


def sample_live(video_path, interval=0.5):
    cap = open_video(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(int(fps * interval), 1)

    start_wall = time.time()
    last_slot = -1

    while True:
        elapsed = time.time() - start_wall
        target_frame = int(elapsed * fps)

        if target_frame >= total_frames:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if not ret:
            break

        current_slot = int(elapsed // interval)
        if current_slot > last_slot:
            last_slot = current_slot
            yield elapsed, frame

    cap.release()


def count_live_frames(video_path, interval=0.5):
    import cv2
    cap = open_video(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    cap.release()
    return max(int(duration / interval), 1)
