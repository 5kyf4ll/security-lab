document.addEventListener("DOMContentLoaded", () => {

    let rotation = 0;

    const player = document.getElementById("livePlayer");
    const rotator = document.getElementById("rotator");

    function applyRotation() {
        player.style.transform = `rotate(${rotation}deg)`;

        // Cambiar relación de aspecto REAL del contenedor
        if (Math.abs(rotation % 180) === 90) {
            rotator.style.aspectRatio = "9 / 16";
        } else {
            rotator.style.aspectRatio = "16 / 9";
        }
    }

    document.getElementById("rotateCW").addEventListener("click", () => {
        rotation += 90;
        applyRotation();
    });

    document.getElementById("rotateCCW").addEventListener("click", () => {
        rotation -= 90;
        applyRotation();
    });
    // 📸 CAPTURA
    document.getElementById("captureBtn").addEventListener("click", async () => {
        try {
            const res = await fetch("/capture", { method: "POST" });
            const data = await res.json();

            if (data.status === "ok") {
                alert("Captura guardada: " + data.file);
            } else {
                alert("Error al capturar");
            }
        } catch (err) {
            alert("Error de conexion con el servidor");
        }
    });

    let recording = false;

    const recordBtn = document.querySelector(".tool-btn:nth-child(4)");

    recordBtn.addEventListener("click", async () => {

        if (!recording) {
            const res = await fetch("/record/start", { method: "POST" });
            const data = await res.json();

            if (data.ok) {
                recording = true;
                recordBtn.textContent = "⏹ Detener";
            } else {
                alert(data.msg);
            }

        } else {
            const res = await fetch("/record/stop", { method: "POST" });
            const data = await res.json();

            if (data.ok) {
                recording = false;
                recordBtn.textContent = "⏺ Grabar";
            } else {
                alert(data.msg);
            }
        }
    });

    async function updateStatus() {
        const res = await fetch("/snapshots/status");
        const data = await res.json();

        const status = document.getElementById("snapStatus");

        if (data.enabled) {
            status.textContent = `Estado: ON cada ${data.interval}s`;
        } else {
            status.textContent = "Estado: OFF";
        }
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

});