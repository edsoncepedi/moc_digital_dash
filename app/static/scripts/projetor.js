const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");

// Ajusta canvas ao tamanho da tela
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

let estadoAtual = [];

function conectarWebSocket() {
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocol}://${location.host}/ws/front`);

    ws.onopen = () => console.log("✅ WebSocket conectado");

    ws.onmessage = (event) => {
        try {
            const dados = JSON.parse(event.data);
            if (dados.acao === "overlay_update") {
                estadoAtual = dados.retangulos || [];
            }
        } catch (e) { console.error(e); }
    };

    ws.onclose = () => {
        console.warn("⚠️ Desconectado. Reconectando...");
        setTimeout(conectarWebSocket, 2000);
    };
}

conectarWebSocket();

function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const r of estadoAtual) {
        if (!r.mostra) continue;

        // --- CÁLCULO DE ESCALA ---
        let scaleX = 1;
        let scaleY = 1;

        // Se o backend enviar o tamanho original, calculamos a proporção
        if (r.frame_w && r.frame_h) {
            scaleX = canvas.width / r.frame_w;
            scaleY = canvas.height / r.frame_h;
        }

        const finalX = r.x * scaleX;
        const finalY = r.y * scaleY;
        const finalW = r.w * scaleX;
        const finalH = r.h * scaleY;

        // Retângulo
        ctx.strokeStyle = r.cor || "#00FF00";
        ctx.lineWidth = 4;
        ctx.strokeRect(finalX, finalY, finalW, finalH);

        // Texto
        if (r.texto) {
            ctx.font = "bold 24px Arial";
            ctx.fillStyle = r.cor || "#00FF00";
            ctx.fillText(r.texto, finalX, Math.max(30, finalY - 10));
        }
    }

    requestAnimationFrame(render);
}

render();