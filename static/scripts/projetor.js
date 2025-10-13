const box = document.getElementById('message-box');
const mensagem = document.getElementById('mensagem');
const overlay = document.getElementById('overlay');

// Mapa para rastrear os retângulos ativos pela sua ID
const retangulosAtivos = new Map();

let timerInterval = null;
let segundos = 0;

// --- Funções do Timer e Mensagem (permanecem as mesmas) ---

function atualizarTimer() {
    const minutos = Math.floor(segundos / 60);
    const segs = segundos % 60;
    const timerEl = document.getElementById('timer');
    if (timerEl) {
        timerEl.textContent = `${String(minutos).padStart(2, '0')}:${String(segs).padStart(2, '0')}`;
    }
}

function iniciarTimer() {
    segundos = 0;
    atualizarTimer();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        segundos++;
        atualizarTimer();
    }, 1000);
}

function pararTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

function mostrarMensagem(posto, texto, posicao = "top-right", mostrarTimer = true) {
    const timerExistente = document.getElementById('timer');
    if (timerExistente) {
        timerExistente.remove();
    }

    if (mostrarTimer) {
        mensagem.innerHTML = `${posto} <br> ${texto}<span id="timer" style="margin-left:10px;font-size:0.9em;color:white;"></span>`;
        iniciarTimer();
    } else {
        mensagem.innerHTML = `${posto} <br> ${texto}`;
        pararTimer();
    }

    box.classList.remove("bottom-right", "bottom-left", "top-right", "top-left", "centered");
    box.classList.add(posicao);
    box.style.display = "block";
    setTimeout(() => box.style.opacity = 1, 50);
}

function limparMensagem() {
    box.style.opacity = 0;
    pararTimer();
    setTimeout(() => {
        box.style.display = "none";
        mensagem.textContent = "";
    }, 300);
}

// --- Funções de Retângulo (ATUALIZADAS E NOVAS) ---

/**
 * Remove todos os retângulos da tela e do rastreamento.
 */
function limparRetangulos() {
    overlay.innerHTML = "";
    retangulosAtivos.clear();
}

/**
 * Desenha um novo retângulo ou atualiza um existente de forma inteligente.
 * @param {string} id - Identificador único para o retângulo.
 * @param {number} [x] - Posição X (opcional).
 * @param {number} [y] - Posição Y (opcional).
 * @param {number} [largura] - Largura do retângulo (opcional).
 * @param {number} [altura] - Altura do retângulo (opcional).
 * @param {string} [cor] - Cor da borda (opcional).
 * @param {string} [texto] - Texto a ser exibido acima do retângulo (opcional).
 */
/**
 * Versão final e robusta da função para desenhar/modificar retângulos e seus textos.
 */
function desenharRetangulo(id, x, y, largura, altura, cor, texto) {
    if (!id) {
        console.error("⚠️ É necessário um ID para desenhar ou modificar um retângulo.");
        return;
    }

    let rect = retangulosAtivos.get(id);
    const corFinal = cor ?? 'white';

    // --- CENÁRIO 1: O RETÂNGULO NÃO EXISTE (CRIAR) ---
    if (!rect) {
        rect = document.createElement('div');
        rect.classList.add('rect');
        overlay.appendChild(rect);
        retangulosAtivos.set(id, rect);
    }

    // --- ATUALIZA AS PROPRIEDADES DO RETÂNGULO (PARA NOVOS E EXISTENTES) ---
    rect.style.left = `${x ?? 0}px`;
    rect.style.top = `${y ?? 0}px`;
    rect.style.width = `${largura ?? 100}px`;
    rect.style.height = `${altura ?? 50}px`;
    rect.style.borderColor = corFinal;

    // --- GERENCIA O TEXTO (LABEL) ---
    let label = rect.querySelector('.rect-label');

    // Condição para MOSTRAR o texto: o campo 'texto' deve existir e não ser vazio.
    if (texto) {
        if (!label) { // Se o label não existe, cria.
            label = document.createElement('span');
            label.className = 'rect-label';
            rect.appendChild(label);
        }
        label.textContent = texto;
        label.style.color = corFinal; // Garante que a cor esteja sempre sincronizada.
    }
    // Condição para REMOVER o texto: se o campo 'texto' não for enviado ou for vazio.
    else if (label) {
        label.remove();
    }
}

/**
 * Apaga um retângulo específico da tela.
 * @param {string} id - O ID do retângulo a ser apagado.
 */
function apagarRetangulo(id) {
    if (retangulosAtivos.has(id)) {
        const rect = retangulosAtivos.get(id);
        rect.remove(); // Remove o elemento do DOM
        retangulosAtivos.delete(id); // Remove do nosso mapa de rastreamento
    } else {
        console.warn(`⚠️ Tentativa de apagar retângulo com ID "${id}", mas ele não foi encontrado.`);
    }
}


// --- WebSocket Principal (ATUALIZADO) ---

function conectarWebSocket() {
    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const host = location.host;
    const ws = new WebSocket(`${protocol}://${host}/ws`);

    ws.onopen = () => console.log("✅ Conectado ao WebSocket");

    ws.onmessage = (event) => {
        console.log("Mensagem recebida:", event.data);
        try {
            const dados = JSON.parse(event.data);

            switch (dados.acao) {
                case "mensagem":
                    mostrarMensagem(dados.posto, dados.texto, dados.posicao, dados.mostrar_timer ?? true);
                    break;
                
                // Ação renomeada para maior clareza
                case "desenhar_retangulo":
                    // Passe o novo parâmetro 'dados.texto' para a função
                    desenharRetangulo(dados.id, dados.x, dados.y, dados.largura, dados.altura, dados.cor, dados.texto);
                    break;

                // Nova ação para apagar um retângulo específico
                case "apagar_retangulo":
                    apagarRetangulo(dados.id);
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
        } catch (e) {
            console.error("Erro ao processar mensagem:", e);
        }
    };

    ws.onclose = () => {
        console.warn("⚠️ Conexão perdida. Tentando reconectar...");
        setTimeout(conectarWebSocket, 3000);
    };
}

conectarWebSocket();