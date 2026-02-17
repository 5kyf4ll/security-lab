# sentra/core/streamer.py
import cv2
from flask import Response


def generate_mjpeg(camera):
    """
    Generador de frames en formato MJPEG para streaming web.
    """
    while True:
        frame = camera.get_frame()

        if frame is None:
            continue

        # Codificar frame a JPEG
        ret, buffer = cv2.imencode(".jpg", frame)
        if not ret:
            continue

        jpg_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpg_bytes + b"\r\n"
        )


def video_feed(camera):
    return Response(
        generate_mjpeg(camera),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )