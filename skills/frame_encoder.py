import cv2
import base64


def encode_frame(frame, quality=60, max_dim=1024):
    """Encode frame to base64 JPEG. Lower quality + max_dim = smaller payload = faster vLLM."""
    try:
        h, w = frame.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
        success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not success:
            return None
        return base64.b64encode(buffer).decode()
    except cv2.error:
        return None