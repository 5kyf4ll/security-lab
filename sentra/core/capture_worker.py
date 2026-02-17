# sentra/core/capture_worker.py
import os
import time
import threading
from datetime import datetime
import cv2


class CaptureWorker:
    def __init__(self, camera, output_dir="data/snapshots", interval=5):
        self.camera = camera
        self.output_dir = output_dir

        self.interval = interval      # segundos entre capturas
        self.enabled = False          # ← switch ON/OFF
        self.running = False
        self.thread = None

        os.makedirs(self.output_dir, exist_ok=True)

    # --------------------------------------------------
    # Inicia el hilo (solo una vez)
    # --------------------------------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[Sentra] CaptureWorker iniciado")

    # --------------------------------------------------
    # Bucle principal
    # --------------------------------------------------
    def _loop(self):
        while self.running:

            # 🔹 si no esta habilitado → dormir poco y seguir
            if not self.enabled:
                time.sleep(0.2)
                continue

            frame = self.camera.get_frame()

            if frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}.jpg"
                filepath = os.path.join(self.output_dir, filename)

                cv2.imwrite(filepath, frame)
                print(f"[Sentra] Snapshot: {filename}")

            # dormir segun intervalo configurado
            time.sleep(self.interval)

    # --------------------------------------------------
    # CONTROL DESDE FLASK
    # --------------------------------------------------
    def enable(self, interval=None):
        """
        Activa capturas automaticas.
        Permite cambiar intervalo en caliente.
        """
        if interval is not None:
            self.interval = max(1, int(interval))  # minimo 1s

        self.enabled = True
        print(f"[Sentra] Snapshots ACTIVADOS cada {self.interval}s")

    def disable(self):
        """Desactiva capturas automaticas."""
        self.enabled = False
        print("[Sentra] Snapshots DESACTIVADOS")

    # --------------------------------------------------
    # Detener completamente
    # --------------------------------------------------
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[Sentra] CaptureWorker detenido")