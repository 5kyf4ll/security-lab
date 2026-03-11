document.addEventListener("DOMContentLoaded", () => {
    
    /* --- ESTADO GLOBAL --- */
    let rotation = 0;
    let currentMode = "captures";
    let isRecording = false;

    const player = document.getElementById("livePlayer");
    const rotator = document.getElementById("rotator");
    const viewerGrid = document.getElementById("viewerGrid");
    const recordBtn = document.getElementById("recordBtn");
    const recIndicator = document.getElementById("recIndicator");
    const snapStatus = document.getElementById("snapStatus");

    /* --- ROTACIÓN --- */
    function applyRotation() {
        player.style.transform = `rotate(${rotation}deg)`;
        // Ajustar aspecto visual si es 90 o 270 grados
        if (Math.abs(rotation % 180) === 90) {
            rotator.style.aspectRatio = "9 / 16";
        } else {
            rotator.style.aspectRatio = "16 / 9";
        }
    }

    document.getElementById("rotateCW").onclick = () => { rotation += 90; applyRotation(); };
    document.getElementById("rotateCCW").onclick = () => { rotation -= 90; applyRotation(); };

    /* --- CARGA DE ARCHIVOS --- */
    async function loadFiles() {
        try {
            const res = await fetch("/files");
            if (!res.ok) throw new Error("Error en servidor");
            const data = await res.json();

            viewerGrid.innerHTML = "";
            const files = currentMode === "captures" ? data.captures : data.videos;

            if (!files || files.length === 0) {
                viewerGrid.innerHTML = "<p style='grid-column: 1/-1; text-align: center; opacity: 0.5; padding: 20px;'>No hay archivos disponibles</p>";
                return;
            }

            files.slice().reverse().forEach(file => {
                const item = document.createElement("div");
                item.className = "viewer-item";

                if (currentMode === "captures") {
                    item.innerHTML = `
                        <img src="/screenshots/${file}" class="thumb-img" loading="lazy">
                        <span>${file}</span>
                    `;
                    item.onclick = () => window.open(`/screenshots/${file}`, "_blank");
                } else {
                    item.innerHTML = `
                        <div class="thumb-placeholder">🎬</div>
                        <span>${file}</span>
                    `;
                    item.onclick = () => {
                        const a = document.createElement("a");
                        a.href = `/videos/${file}`;
                        a.download = file;
                        a.click();
                    };
                }
                viewerGrid.appendChild(item);
            });
        } catch (err) {
            console.error("Error cargando archivos:", err);
        }
    }

    /* --- SWITCH CAPTURAS/VIDEOS --- */
    document.querySelectorAll(".switch-btn").forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll(".switch-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentMode = btn.dataset.mode;
            loadFiles();
        };
    });

    /* --- CAPTURA MANUAL --- */
    document.getElementById("captureBtn").onclick = async () => {
        try {
            const res = await fetch("/capture", { method: "POST" });
            const data = await res.json();
            if (data.status === "ok") loadFiles();
        } catch (err) { console.error("Error en captura:", err); }
    };

    /* --- GRABACIÓN --- */
    recordBtn.onclick = async () => {
        const endpoint = isRecording ? "/record/stop" : "/record/start";
        try {
            const res = await fetch(endpoint, { method: "POST" });
            const data = await res.json();

            if (data.ok || data.status === "ok") {
                isRecording = !isRecording;
                recordBtn.classList.toggle("recording-active", isRecording);
                recIndicator.classList.toggle("hidden", !isRecording);
                recordBtn.innerHTML = isRecording ? "<span>⏹</span> Detener" : "<span>⏺</span> Grabar";
                if (!isRecording) loadFiles();
            }
        } catch (err) { console.error("Error en grabación:", err); }
    };

    /* --- SNAPSHOTS AUTOMÁTICOS --- */
    async function getSnapStatus() {
        try {
            const res = await fetch("/snapshots/status");
            const data = await res.json();
            snapStatus.textContent = data.enabled 
                ? `ON (${data.interval}s)` 
                : "Estado: OFF";
            snapStatus.style.color = data.enabled ? "#4ade80" : "#94a3b8";
        } catch (e) {}
    }

    document.getElementById("snapEnable").onclick = async () => {
        const interval = document.getElementById("intervalInput").value;
        await fetch("/snapshots/enable", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ interval })
        });
        getSnapStatus();
    };

    document.getElementById("snapDisable").onclick = async () => {
        await fetch("/snapshots/disable", { method: "POST" });
        getSnapStatus();
    };

    /* --- INICIALIZACIÓN --- */
    loadFiles();
    getSnapStatus();
    // Refrescar lista cada 10 segundos automáticamente
    setInterval(loadFiles, 10000);
});