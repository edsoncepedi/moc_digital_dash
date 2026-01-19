const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");

// --- CONFIGURAÇÃO MANUAL (PARA DEBUG NO UBUNTU) ---
// Se estiver rodando localmente no Ubuntu, pode deixar automático.
// Se estiver acessando de outro PC, coloque o IP do Ubuntu aqui.
// Ex: const SERVER_IP = "192.168.1.15:8000";
const SERVER_IP = null; 
// --------------------------------------------------

function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

let estadoAtual = [];
let socket = null;

function conectarWebSocket() {
    // Se já tiver conexão aberta ou conectando, não faz nada
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
        return;
    }

    // Lógica inteligente de URL
    let wsUrl;
    if (SERVER_IP) {
        // Se você definiu o IP manualmente lá em cima
        wsUrl = `ws://${SERVER_IP}/ws/front`;
    } else {
        // Automático: Pega o IP que está na barra de endereço do navegador
        const protocol = location.protocol === "https:" ? "wss" : "ws";
        const host = location.host; // Ex: 192.168.0.X:8000
        wsUrl = `${protocol}://${host}/ws/front`;
    }

    console.log(`🔌 Tentando conectar em: ${wsUrl}`);

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("✅ WebSocket conectado com sucesso!");
    };

    socket.onmessage = (event) => {
        try {
            // Ignora mensagens de controle (como "ping") se não for JSON válido ou se for apenas texto
            if (event.data === "ping") return;

            const dados = JSON.parse(event.data);

            if (dados.acao === "overlay_update") {
                estadoAtual = dados.retangulos || [];
            }
        } catch (e) {
            // Se não for JSON, apenas ignora (pode ser heartbeat)
            // console.warn("Mensagem não-JSON recebida", event.data);
        }
    };

    socket.onerror = (error) => {
        console.error("❌ Erro no WebSocket. Verifique:", error);
        console.error("1. O Backend está rodando com --host 0.0.0.0?");
        console.error("2. O Firewall do Ubuntu liberou a porta 8000? (sudo ufw allow 8000)");
        console.error("3. O IP está correto?");
    };

    socket.onclose = (event) => {
        if (event.wasClean) {
            console.warn(`⚠️ Desconectado limpo (Código: ${event.code})`);
        } else {
            console.error("⚠️ Queda de conexão abrupta (Servidor caiu ou IP inalcançável).");
        }
        
        // Tenta reconectar em 2 segundos
        socket = null;
        setTimeout(conectarWebSocket, 2000);
    };
}

// Inicia a conexão
conectarWebSocket();

// --- RENDER LOOP ---
function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const r of estadoAtual) {
        if (!r.mostra) continue;

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