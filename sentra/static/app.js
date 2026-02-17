document.addEventListener("DOMContentLoaded", () => {

    /* ================= ROTACION PLAYER ================= */
    let rotation = 0;

    const player = document.getElementById("livePlayer");
    const rotator = document.getElementById("rotator");

    function applyRotation() {
        player.style.transform = `rotate(${rotation}deg)`;

        rotator.style.aspectRatio =
            Math.abs(rotation % 180) === 90 ? "9 / 16" : "16 / 9";
    }

    document.getElementById("rotateCW").onclick = () => {
        rotation += 90;
        applyRotation();
    };

    document.getElementById("rotateCCW").onclick = () => {
        rotation -= 90;
        applyRotation();
    };


    /* ================= VISOR DE ARCHIVOS ================= */

    const viewerGrid = document.getElementById("viewerGrid");
    const switchBtns = document.querySelectorAll(".switch-btn");

    let currentMode = "captures";

    async function loadFiles() {
        try {
            const res = await fetch("/files");
            const data = await res.json();

            viewerGrid.innerHTML = "";

            const files = currentMode === "captures"
                ? data.captures
                : data.videos;

            files.slice().reverse().forEach(file => {
                const item = document.createElement("div");
                item.className = "viewer-item";

                if (currentMode === "captures") {

                    item.innerHTML = `
                        <img src="/screenshots/${file}" class="thumb-img">
                        <span>${file}</span>
                    `;

                    /* abrir en nueva pestaña */
                    item.onclick = () => {
                        window.open(`/screenshots/${file}`, "_blank");
                    };

                } else {

                    item.innerHTML = `
                        <div class="thumb-video-placeholder">🎬</div>
                        <span>${file}</span>
                    `;

                    /* descargar video */
                    item.onclick = () => {
                        const a = document.createElement("a");
                        a.href = `/videos/${file}`;
                        a.download = file;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    };
                }

                viewerGrid.appendChild(item);
            });

        } catch (err) {
            console.warn("Error cargando archivos:", err);
        }
    }

    /* ===== SWITCH ===== */
    switchBtns.forEach(btn => {
        btn.addEventListener("click", () => {

            switchBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentMode = btn.dataset.mode;   // ← FIX REAL
            loadFiles();
        });
    });


    /* ================= CAPTURA ================= */
    document.getElementById("captureBtn").onclick = async () => {
        try {
            const res = await fetch("/capture", { method: "POST" });
            const data = await res.json();

            if (data.status === "ok") {
                loadFiles(); // refresca visor
            }
        } catch (err) {
            console.warn("Error en captura:", err);
        }
    };


    /* ================= GRABACION ================= */
    let recording = false;
    const recordBtn = document.querySelector(".tool-btn:nth-child(4)");

    recordBtn.onclick = async () => {

        try {
            if (!recording) {
                const res = await fetch("/record/start", { method: "POST" });
                const data = await res.json();

                if (data.ok) {
                    recording = true;
                    recordBtn.textContent = "⏹ Detener";
                }

            } else {
                const res = await fetch("/record/stop", { method: "POST" });
                const data = await res.json();

                if (data.ok) {
                    recording = false;
                    recordBtn.textContent = "⏺ Grabar";
                    loadFiles();
                }
            }
        } catch (err) {
            console.warn("Error en grabacion:", err);
        }
    };


    /* ================= SNAPSHOTS ================= */

    async function updateStatus() {
        const res = await fetch("/snapshots/status");
        const data = await res.json();

        document.getElementById("snapStatus").textContent =
            data.enabled
                ? `Estado: ON cada ${data.interval}s`
                : "Estado: OFF";
    }

    document.getElementById("snapEnable").onclick = async () => {
        const interval = document.getElementById("intervalInput").value;

        await fetch("/snapshots/enable", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ interval })
        });

        updateStatus();
    };

    document.getElementById("snapDisable").onclick = async () => {
        await fetch("/snapshots/disable", { method: "POST" });
        updateStatus();
    };

    updateStatus();


    /* ===== AUTO-REFRESH ===== */
    setInterval(loadFiles, 5000);

    /* ===== INIT ===== */
    loadFiles();

});