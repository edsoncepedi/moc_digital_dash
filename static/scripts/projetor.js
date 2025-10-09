const box = document.getElementById('message-box');
const mensagem = document.getElementById('mensagem');
const overlay = document.getElementById('overlay');

let timerInterval = null;
let segundos = 0;

// Atualiza o contador visualmente
function atualizarTimer() {
    const minutos = Math.floor(segundos / 60);
    const segs = segundos % 60;
    const timerEl = document.getElementById('timer');
    if (timerEl) {
        timerEl.textContent = `${String(minutos).padStart(2, '0')}:${String(segs).padStart(2, '0')}`;
    }
}

// Inicia o timer
function iniciarTimer() {
    segundos = 0;
    atualizarTimer();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        segundos++;
        atualizarTimer();
    }, 1000);
}

// Para o timer
function pararTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

// Mostra mensagem e controla o timer
function mostrarMensagem(texto, posicao = "bottom-right", mostrarTimer = true) {
    // Se já existe um timer e o novo comando não deve exibir, removemos ele
    const timerExistente = document.getElementById('timer');
    if (timerExistente) {
        timerExistente.remove();
    }

    if (mostrarTimer) {
        mensagem.innerHTML = `${texto} <span id="timer" style="margin-left:10px;font-size:0.9em;color:white;;"></span>`;
        iniciarTimer();
    } else {
        mensagem.textContent = texto;
        pararTimer(); // garante que o timer pare se estava ativo
    }

    // Atualiza posição e exibe
    box.classList.remove("bottom-right", "bottom-left", "top-right", "top-left", "centered");
    box.classList.add(posicao);
    box.style.display = "block";
    setTimeout(() => box.style.opacity = 1, 50);
}

// Oculta a mensagem
function limparMensagem() {
    box.style.opacity = 0;
    pararTimer();
    setTimeout(() => {
        box.style.display = "none";
        mensagem.textContent = "";
    }, 300);
}

// Remove todos os retângulos
function limparRetangulos() {
    overlay.innerHTML = "";
}

// Desenha um retângulo com bordas
function desenharRetangulo(x, y, largura = 100, altura = 50) {
    const rect = document.createElement('div');
    rect.classList.add('rect');
    rect.style.left = `${x}px`;
    rect.style.top = `${y}px`;
    rect.style.width = `${largura}px`;
    rect.style.height = `${altura}px`;
    overlay.appendChild(rect);
}

// WebSocket principal
function conectarWebSocket() {
    const ws = new WebSocket("ws://localhost:5000/ws");

    ws.onopen = () => console.log("✅ Conectado ao WebSocket");

    ws.onmessage = (event) => {
        console.log("Mensagem recebida:", event.data);
        try {
            const dados = JSON.parse(event.data);

            switch (dados.acao) {
                case "mensagem":
                    mostrarMensagem(dados.texto, dados.posicao, dados.mostrar_timer ?? true);
                    break;
                case "retangulo":
                    desenharRetangulo(dados.x, dados.y, dados.largura, dados.altura);
                    break;
                case "limpar_mensagem":
                    limparMensagem();
                    break;
                case "limpar_retangulos":
                    limparRetangulos();
                    break;
                default:
                    console.warn("⚠️ Ação desconhecida:", dados.acao);
            }
        } catch {
            mostrarMensagem(event.data, "bottom-right");
        }
    };

    ws.onclose = () => {
        console.warn("⚠️ Conexão perdida. Tentando reconectar...");
        setTimeout(conectarWebSocket, 3000);
    };
}

conectarWebSocket();
