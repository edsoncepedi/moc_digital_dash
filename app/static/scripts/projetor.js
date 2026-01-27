const canvas = document.getElementById("overlay");
const ctx = canvas.getContext("2d");

let mensagemAtual = null;

// --- CONFIGURAÇÃO DE IP ---
// Deixe null para detecção automática (recomendado se rodar no mesmo PC ou via DNS)
// Se precisar forçar o IP do Raspberry/Ubuntu, coloque ex: "192.168.1.15:8000"
const SERVER_IP = null; 

// --- DETECÇÃO AUTOMÁTICA DE POSTO ---
// Lê o parâmetro ?posto=X da URL. Se não tiver, assume 1.
const urlParams = new URLSearchParams(window.location.search);
const POSTO_ID = urlParams.get('posto') || 1;

console.log(`🖥️ Iniciando Projetor para o POSTO: ${POSTO_ID}`);

// --- ESTADO GLOBAL ---
let estadoAtual = []; // Guarda os retângulos recebidos do backend
let socket = null;    // Objeto WebSocket

// --- CONFIGURAÇÃO DE CALIBRAÇÃO (Valores Padrão) ---
// offX/Y: Deslocamento em pixels
// scX/Y: Multiplicador de escala (Zoom)
// key: Fator de correção trapezoidal (Perspectiva)
const savedConfig = {
    offX: 0, 
    offY: 0,
    scX: 1.0, 
    scY: 1.0,
    key: 0.0 
};

// --- MAPEAMENTO DOS INPUTS HTML ---
// Vincula os sliders (range) e as caixas de número (number) do HTML
const inputs = {
    offX: { range: document.getElementById("offsetX"), num: document.getElementById("numOffsetX") },
    offY: { range: document.getElementById("offsetY"), num: document.getElementById("numOffsetY") },
    scX:  { range: document.getElementById("scaleX"),  num: document.getElementById("numScaleX") },
    scY:  { range: document.getElementById("scaleY"),  num: document.getElementById("numScaleY") },
    key:  { range: document.getElementById("keystone"), num: document.getElementById("numKeystone") }
};

// =========================================================
// 1. LÓGICA DE INTERFACE E CALIBRAÇÃO
// =========================================================

/**
 * Atualiza o valor na memória, nos sliders e salva no LocalStorage (backup temporário)
 */
function updateVal(key, value) {
    const val = parseFloat(value);
    savedConfig[key] = val;
    
    // Atualiza elementos HTML se existirem
    if (inputs[key] && inputs[key].range) inputs[key].range.value = val;
    if (inputs[key] && inputs[key].num) inputs[key].num.value = val;

    // Salva backup local
    localStorage.setItem("proj_config_v3", JSON.stringify(savedConfig));
}

// Inicializa os listeners dos inputs
Object.keys(inputs).forEach(key => {
    // Se inputs existirem no HTML
    if (inputs[key].range) {
        inputs[key].range.oninput = (e) => updateVal(key, e.target.value);
        inputs[key].num.oninput = (e) => updateVal(key, e.target.value);
    }
});

/**
 * Reseta para os valores padrão (sem distorção)
 */
window.resetCalibration = () => {
    updateVal("offX", 0);
    updateVal("offY", 0);
    updateVal("scX", 1.0);
    updateVal("scY", 1.0);
    updateVal("key", 0.0);
};

/**
 * Tecla 'H' para esconder/mostrar o painel de calibração
 */
window.addEventListener("keydown", (e) => {
    if (e.key.toLowerCase() === 'h') {
        const panel = document.getElementById("calibration-panel");
        if (panel) {
            panel.style.display = panel.style.display === "none" ? "block" : "none";
        }
    }
});

// Ajusta o canvas ao redimensionar a janela
function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();


// =========================================================
// 2. COMUNICAÇÃO COM O SERVIDOR (API & WEBSOCKET)
// =========================================================

/**
 * Salva a calibração atual num arquivo JSON no Backend (Raspberry Pi/Ubuntu)
 */
window.salvarNoServidor = async () => {
    try {
        const response = await fetch(`/api/calibracao/${POSTO_ID}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(savedConfig)
        });
        
        const res = await response.json();
        if (res.status === 'ok') {
            alert("✅ Configuração salva no Servidor com sucesso!");
        } else {
            alert("❌ Erro ao salvar: " + res.msg);
        }
    } catch (e) {
        console.error(e);
        alert("Erro de conexão ao tentar salvar.");
    }
};

/**
 * Carrega a calibração do arquivo JSON do Backend
 */
window.carregarDoServidor = async () => {
    try {
        const response = await fetch(`/api/calibracao/${POSTO_ID}`);
        const dados = await response.json();

        // Verifica se vieram dados válidos
        if (dados && typeof dados.scX !== 'undefined') {
            console.log("📂 Configuração carregada do servidor:", dados);
            
            // Atualiza memória e interface
            Object.keys(inputs).forEach(key => {
                if (dados[key] !== undefined) {
                    updateVal(key, dados[key]);
                }
            });
        } else {
            console.log("⚠️ Nenhuma configuração salva no servidor, usando padrão ou LocalStorage.");
            // Tenta recuperar do LocalStorage se o servidor falhar
            const local = JSON.parse(localStorage.getItem("proj_config_v3"));
            if (local) {
                Object.keys(local).forEach(k => updateVal(k, local[k]));
            }
        }
    } catch (e) {
        console.warn("Erro ao buscar calibração no servidor (pode ser a primeira execução).");
    }
};

/**
 * Gerencia a conexão WebSocket para receber os retângulos em tempo real
 */
function conectarWebSocket() {
    // Evita múltiplas conexões
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
        return;
    }

    // Determina a URL
    let wsUrl;
    if (SERVER_IP) {
        wsUrl = `ws://${SERVER_IP}/ws/front/${POSTO_ID}`;
    } else {
        const protocol = location.protocol === "https:" ? "wss" : "ws";
        const host = location.host;
        wsUrl = `${protocol}://${location.host}/ws/front/${POSTO_ID}`;
    }

    console.log(`🔌 Conectando WebSocket em: ${wsUrl}`);
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("✅ WebSocket Conectado!");
    };

    socket.onmessage = (event) => {
        try {
            if (event.data === "ping") return;

            const dados = JSON.parse(event.data);

            if (dados.acao === "overlay_update") {
                estadoAtual = dados.retangulos || [];

                // Exibe mensagem se existir
                if ("mensagem" in dados) {
                    const m = dados.mensagem;
                    mensagemAtual = (m && typeof m === "object" && "mensagem" in m) ? m.mensagem : m;
                    console.log("📨 Mensagem atualizada:", mensagemAtual);
                }
            }
        } catch (e) {
            // ignora erros
        }
    };

    socket.onclose = (e) => {
        // Reconexão inteligente
        console.warn("⚠️ WebSocket desconectado. Tentando reconectar em 1s...");
        socket = null;
        setTimeout(conectarWebSocket, 1000);
    };
}


// =========================================================
// 3. RENDER LOOP (DESENHO E MATEMÁTICA)
// =========================================================

function render() {
    // Limpa a tela
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Centro da tela (usado como ponto de fuga para perspectiva)
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    for (const r of estadoAtual) {
        if (!r.mostra) continue;

        // --- PASSO 1: ESCALA BASE ---
        // Adapta a resolução da câmera (ex: 640x640) para a resolução do projetor (ex: 1920x1080)
        let baseScaleX = 1;
        let baseScaleY = 1;

        if (r.frame_w && r.frame_h) {
            baseScaleX = canvas.width / r.frame_w;
            baseScaleY = canvas.height / r.frame_h;
        }

        // Posição e tamanho "crus" ajustados apenas para a tela cheia
        let rawX = r.x * baseScaleX;
        let rawY = r.y * baseScaleY;
        let rawW = r.w * baseScaleX;
        let rawH = r.h * baseScaleY;

        // --- PASSO 2: CORREÇÃO DE PERSPECTIVA (KEYSTONE) ---
        // Calcula a distância vertical do objeto em relação ao centro
        let deltaY = (rawY - cy);
        
        // Fator de distorção:
        // Se 'key' < 0: Objetos abaixo do centro diminuem (Corrige projeção inclinada para baixo)
        // Se 'key' > 0: Objetos abaixo do centro aumentam
        let perspectiveFactor = 1 + (deltaY * savedConfig.key);

        // --- PASSO 3: APLICAÇÃO FINAL ---
        // Combina: Zoom Manual * Fator Perspectiva
        let finalScaleX = savedConfig.scX * perspectiveFactor;
        let finalScaleY = savedConfig.scY * perspectiveFactor;

        // Tamanho Final
        const finalW = rawW * finalScaleX;
        const finalH = rawH * finalScaleY;

        // Posição Final:
        // A posição se expande a partir do centro (cx, cy) baseado na escala
        // E soma o deslocamento manual (offX, offY)
        const finalX = cx + (rawX - cx) * finalScaleX + savedConfig.offX;
        const finalY = cy + (rawY - cy) * finalScaleY + savedConfig.offY;

        // --- DESENHO ---
        ctx.strokeStyle = r.cor || "#00FF00";
        ctx.lineWidth = 4;
        //ctx.strokeRect(finalX, finalY, finalW, finalH);
        // Substitua o ctx.strokeRect(finalX, finalY, finalW, finalH) por:

        const len = Math.min(finalW, finalH) * 0.2; // Tamanho do canto (20%)

        ctx.beginPath();
        ctx.lineWidth = 4;
        ctx.strokeStyle = r.cor || "#00FF00";

        // Canto Superior Esquerdo
        ctx.moveTo(finalX, finalY + len);
        ctx.lineTo(finalX, finalY);
        ctx.lineTo(finalX + len, finalY);

        // Canto Superior Direito
        ctx.moveTo(finalX + finalW - len, finalY);
        ctx.lineTo(finalX + finalW, finalY);
        ctx.lineTo(finalX + finalW, finalY + len);

        // Canto Inferior Direito
        ctx.moveTo(finalX + finalW, finalY + finalH - len);
        ctx.lineTo(finalX + finalW, finalY + finalH);
        ctx.lineTo(finalX + finalW - len, finalY + finalH);

        // Canto Inferior Esquerdo
        ctx.moveTo(finalX + len, finalY + finalH);
        ctx.lineTo(finalX, finalY + finalH);
        ctx.lineTo(finalX, finalY + finalH - len);

        ctx.stroke();

        // Desenha Texto (ID)
        if (r.texto) {
            ctx.font = "bold 24px Arial";
            ctx.fillStyle = r.cor || "#00FF00";
            // Ajusta posição do texto para acompanhar o retângulo
            ctx.fillText(r.texto, finalX, Math.max(30, finalY - 10));
        }
    }
    if (mensagemAtual) {
        desenharPopup(mensagemAtual);
    }
    // Loop de animação
    requestAnimationFrame(render);
}

function desenharPopup(msg) {
    const m = msg?.mensagem ?? msg;
    if (!m) return;

    const text = m.texto ?? "";
    if (!text) return;

    const pad = m.padding ?? 12;
    const fontSize = m.fontSize ?? 24;
    const radius = m.radius ?? 10;

    const bg = m.bg ?? "rgba(0,0,0,0.75)";
    const border = m.border ?? "rgb(255, 255, 255)";
    const textColor = m.color ?? "#ffffff";

    ctx.save();
    ctx.font = `bold ${fontSize}px Arial`;
    ctx.textBaseline = "top";

    const metrics = ctx.measureText(text);
    const boxW = metrics.width + pad * 2;
    const boxH = fontSize + pad * 2;

    // =============================
    // POSICIONAMENTO AUTOMÁTICO
    // =============================

    let boxX, boxY;

    if (typeof m.x === "number" && typeof m.y === "number") {
        // 📍 posição absoluta
        boxX = m.x;
        boxY = m.y;
    } else {
        const margin = m.margin ?? 50;
        const pos = m.position ?? "top-center";

        switch (pos) {
            case "top-left":
                boxX = margin;
                boxY = margin;
                break;

            case "top-center":
                boxX = (canvas.width - boxW) / 2;
                boxY = margin;
                break;

            case "top-right":
                boxX = canvas.width - boxW - margin;
                boxY = margin;
                break;

            case "center":
                boxX = (canvas.width - boxW) / 2;
                boxY = (canvas.height - boxH) / 2;
                break;

            case "bottom-left":
                boxX = margin;
                boxY = canvas.height - boxH - margin;
                break;

            case "bottom-center":
                boxX = (canvas.width - boxW) / 2;
                boxY = canvas.height - boxH - margin;
                break;

            case "bottom-right":
                boxX = canvas.width - boxW - margin;
                boxY = canvas.height - boxH - margin;
                break;

            default:
                boxX = canvas.width - boxW - margin;
                boxY = margin;
                break;
        }
    }

    // =============================
    // DESENHO
    // =============================

    // sombra
    ctx.shadowColor = "rgba(0,0,0,0.6)";
    ctx.shadowBlur = 10;
    ctx.shadowOffsetY = 4;

    // caixa
    roundRect(ctx, boxX, boxY, boxW, boxH, radius);
    ctx.fillStyle = bg;
    ctx.fill();

    // borda
    ctx.shadowColor = "transparent";
    ctx.lineWidth = m.borderWidth ?? 5;
    ctx.strokeStyle = border;
    ctx.stroke();

    // texto
    ctx.fillStyle = textColor;
    ctx.textAlign = "center";
    ctx.fillText(text, boxX + boxW / 2, boxY + pad);

    ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
    const radius = Math.min(r, w/2, h/2);
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.arcTo(x + w, y, x + w, y + h, radius);
    ctx.arcTo(x + w, y + h, x, y + h, radius);
    ctx.arcTo(x, y + h, x, y, radius);
    ctx.arcTo(x, y, x + w, y, radius);
    ctx.closePath();
}

// --- INICIALIZAÇÃO DO SISTEMA ---
// 1. Carrega configurações do servidor
carregarDoServidor();
// 2. Inicia conexão WebSocket
conectarWebSocket();
// 3. Inicia Loop de Renderização
render();