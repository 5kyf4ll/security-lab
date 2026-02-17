# sentra/core/recorder.py
import os
import cv2
import threading
import time
from datetime import datetime


class VideoRecorder:
    def __init__(self, camera, fps=15):
        self.camera = camera

        self.recording = False
        self.writer = None
        self.thread = None

        self.fps = fps
        self.save_dir = "data/videos"
        os.makedirs(self.save_dir, exist_ok=True)

    # -----------------------------
    # LOOP DE GRABACION DIRECTA
    # -----------------------------
    def _record_loop(self):
        frame_interval = 1.0 / self.fps

        while self.recording:
            start = time.time()

            frame = self.camera.get_frame()
            if frame is not None and self.writer:
                self.writer.write(frame)

            # mantener FPS estable
            elapsed = time.time() - start
            sleep_time = max(0, frame_interval - elapsed)
            time.sleep(sleep_time)

    # -----------------------------
    # INICIAR
    # -----------------------------
    def start(self):
        if self.recording:
            return False, "Ya estaba grabando"

        frame = self.camera.get_frame()
        if frame is None:
            return False, "No hay frame disponible"

        h, w, _ = frame.shape

        filename = datetime.now().strftime("video_%Y%m%d_%H%M%S.mp4")
        path = os.path.join(self.save_dir, filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(path, fourcc, self.fps, (w, h))

        self.recording = True

        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

        return True, filename

    # -----------------------------
    # DETENER
    # -----------------------------
    def stop(self):
        if not self.recording:
            return False, "No estaba grabando"

        self.recording = False

        if self.thread:
            self.thread.join(timeout=2)

        if self.writer:
            self.writer.release()
            self.writer = None

        return True, "Grabacion detenida"


# instancia global
recorder = None