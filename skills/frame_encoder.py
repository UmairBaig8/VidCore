import cv2
import base64


def encode_frame(frame):
    try:
        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            return None
        return base64.b64encode(buffer).decode()
    except cv2.error:
        return None