from flask import Flask, render_template, jsonify, request, send_from_directory
from core.camera import Camera
from core.streamer import video_feed
from core.capture_worker import CaptureWorker
from core.recorder import VideoRecorder

import os
from datetime import datetime
import cv2

app = Flask(__name__)

# --------------------------------------------------
# Inicializar componentes principales
# --------------------------------------------------
camera = Camera()

capture_worker = CaptureWorker(camera)
capture_worker.start()

recorder = VideoRecorder(camera, fps=15)

# Carpetas de almacenamiento
SCREENSHOTS_DIR = "data/screenshots"
VIDEOS_DIR = "data/videos"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)


# --------------------------------------------------
# Rutas web
# --------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def stream():
    return video_feed(camera)


# --------------------------------------------------
# 📸 CAPTURA MANUAL
# --------------------------------------------------
@app.route("/capture", methods=["POST"])
def capture():
    frame = camera.get_frame()

    if frame is None:
        return jsonify({"status": "error", "msg": "no frame"}), 500

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.jpg"
    path = os.path.join(SCREENSHOTS_DIR, filename)

    cv2.imwrite(path, frame)

    return jsonify({"status": "ok", "file": filename})


# --------------------------------------------------
# 🎥 GRABACION
# --------------------------------------------------
@app.route("/record/start", methods=["POST"])
def record_start():
    ok, msg = recorder.start()
    return jsonify({"ok": ok, "msg": msg})


@app.route("/record/stop", methods=["POST"])
def record_stop():
    ok, msg = recorder.stop()
    return jsonify({"ok": ok, "msg": msg})


# --------------------------------------------------
# 📂 LISTAR ARCHIVOS PARA EL VISOR
# --------------------------------------------------
@app.route("/files")
def list_files():
    screenshots = sorted(os.listdir(SCREENSHOTS_DIR))
    videos = sorted(os.listdir(VIDEOS_DIR))

    return jsonify({
        "captures": screenshots,
        "videos": videos
    })


# --------------------------------------------------
# 🖼 SERVIR SCREENSHOTS
# --------------------------------------------------
@app.route("/screenshots/<path:filename>")
def get_screenshot(filename):
    return send_from_directory(SCREENSHOTS_DIR, filename)


# --------------------------------------------------
# 🎬 SERVIR VIDEOS
# --------------------------------------------------
@app.route("/videos/<path:filename>")
def get_video(filename):
    return send_from_directory(VIDEOS_DIR, filename)


# --------------------------------------------------
# SNAPSHOTS CONTROL
# --------------------------------------------------
@app.route("/snapshots/enable", methods=["POST"])
def snapshots_enable():
    interval = request.json.get("interval", 5)
    capture_worker.enable(interval)

    return jsonify({
        "enabled": True,
        "interval": capture_worker.interval
    })


@app.route("/snapshots/disable", methods=["POST"])
def snapshots_disable():
    capture_worker.disable()

    return jsonify({
        "enabled": False
    })


@app.route("/snapshots/status")
def snapshots_status():
    return jsonify({
        "enabled": capture_worker.enabled,
        "interval": capture_worker.interval
    })


# --------------------------------------------------
# Cierre seguro
# --------------------------------------------------
def shutdown():
    print("\n[Sentra] Cerrando sistema...")
    capture_worker.stop()
    recorder.stop()
    camera.release()


# --------------------------------------------------
# Ejecucion principal
# --------------------------------------------------
if __name__ == "__main__":
    try:
        print("[Sentra] Iniciando servidor...")
        resolution = camera.get_resolution()
        if resolution:
            print(f"[Sentra] Resolucion detectada: {resolution[0]}x{resolution[1]}")

        app.run(host="0.0.0.0", port=5000, debug=False)

    except KeyboardInterrupt:
        pass
    finally:
        shutdown()