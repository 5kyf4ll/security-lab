# sentra/core/camera.py
import cv2
import threading


class Camera:
    def __init__(self, max_devices: int = 5):
        self.cap = None
        self.index = None
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

        self._detect_camera(max_devices)
        self._start_reader()

    # --------------------------------------------------
    # Detecta automaticamente la primera camara disponible
    # --------------------------------------------------
    def _detect_camera(self, max_devices: int):
        for i in range(max_devices):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.cap = cap
                self.index = i
                print(f"[Sentra] Camara detectada en indice {i}")
                return

        raise RuntimeError("No se encontro ninguna capturadora disponible")

    # --------------------------------------------------
    # Hilo que mantiene el ultimo frame actualizado
    # --------------------------------------------------
    def _start_reader(self):
        self.running = True
        thread = threading.Thread(target=self._reader_loop, daemon=True)
        thread.start()

    def _reader_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            with self.lock:
                self.frame = frame

    # --------------------------------------------------
    # Devuelve el ultimo frame disponible
    # --------------------------------------------------
    def get_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    # --------------------------------------------------
    # Resolucion real de la capturadora
    # --------------------------------------------------
    def get_resolution(self):
        if not self.cap:
            return None

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height

    # --------------------------------------------------
    # Liberar recursos al cerrar
    # --------------------------------------------------
    def release(self):
        self.running = False
        if self.cap:
            self.cap.release()