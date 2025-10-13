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

function iniciarDigitalDash() {
    const tit = document.getElementById('digital_dash');
    tit.style.display = "block";

}

function mostrarMensagem(posto, texto, posicao = "top-right", mostrarTimer = true) {
    const timerExistente = document.getElementById('timer');
    if (timerExistente) {
        timerExistente.remove();
    }

    if (mostrarTimer) {
        mensagem.innerHTML = `${posto}<span id="timer" style="font-size:0.9em;color:white;"></span>`;
        showFloatingMessage(texto, 950, 750);
        iniciarTimer();
    } else {
        mensagem.innerHTML = `${posto}`;
        showFloatingMessage(texto, 950, 750);
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


// --- MAPA DE SETAS ATIVAS ---
const setasAtivas = new Map();

/**
 * Desenha ou atualiza uma seta entre dois pontos.
 * @param {string} id - Identificador único da seta.
 * @param {number} x1 - Coordenada X inicial.
 * @param {number} y1 - Coordenada Y inicial.
 * @param {number} x2 - Coordenada X final.
 * @param {number} y2 - Coordenada Y final.
 * @param {string} [cor='white'] - Cor da seta.
 * @param {number} [espessura=4] - Espessura da linha da seta.
 * @param {number} [tamanhoPonta=18] - Tamanho da ponta da seta.
 */
function desenharSeta(id, x1, y1, x2, y2, cor = 'white', espessura = 4, tamanhoPonta = 18) {
    if (!id) {
        console.error("⚠️ É necessário um ID para desenhar ou modificar uma seta.");
        return;
    }

    let seta = setasAtivas.get(id);

    // Cria a seta se ainda não existir
    if (!seta) {
        const linha = document.createElement('div');
        linha.className = 'arrow';

        const ponta = document.createElement('div');
        ponta.className = 'arrow-head';

        linha.appendChild(ponta);
        overlay.appendChild(linha);

        setasAtivas.set(id, { linha, ponta });
        seta = { linha, ponta };
    }

    const dx = x2 - x1;
    const dy = y2 - y1;
    const comprimento = Math.sqrt(dx * dx + dy * dy);
    const angulo = Math.atan2(dy, dx) * (180 / Math.PI);

    // Linha
    seta.linha.style.position = 'absolute';
    seta.linha.style.left = `${x1}px`;
    seta.linha.style.top = `${y1}px`;
    seta.linha.style.height = `${comprimento}px`;
    seta.linha.style.width = `${espessura}px`;
    seta.linha.style.backgroundColor = cor;
    seta.linha.style.transform = `rotate(${angulo}deg)`;
    seta.linha.style.transformOrigin = 'top left';
    seta.linha.style.borderRadius = `${espessura / 2}px`; // linha mais suave

    // Ponta
    seta.ponta.style.position = 'absolute';
    seta.ponta.style.width = '0';
    seta.ponta.style.height = '0';
    seta.ponta.style.borderLeft = `${tamanhoPonta / 2}px solid transparent`;
    seta.ponta.style.borderRight = `${tamanhoPonta / 2}px solid transparent`;
    seta.ponta.style.borderTop = `${tamanhoPonta}px solid ${cor}`;
    seta.ponta.style.top = `${comprimento - tamanhoPonta + (espessura / 2)}px`; // ajuste fino
    seta.ponta.style.left = `${-tamanhoPonta / 2 + espessura / 2}px`;
    seta.ponta.style.transform = `rotate(0deg)`;
}

/**
 * Remove uma seta específica da tela.
 * @param {string} id - ID da seta a ser removida.
 */
function apagarSeta(id) {
    if (setasAtivas.has(id)) {
        const seta = setasAtivas.get(id);
        seta.linha.remove();
        setasAtivas.delete(id);
    } else {
        console.warn(`⚠️ Tentativa de apagar seta com ID "${id}", mas ela não foi encontrada.`);
    }
}

/**
 * Remove todas as setas da tela.
 */
function limparSetas() {
    for (const { linha } of setasAtivas.values()) {
        linha.remove();
    }
    setasAtivas.clear();
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

/**
 * Exibe a nova mensagem flutuante em coordenadas absolutas (x, y)
 * @param {string} text - texto da mensagem
 * @param {number} x - coordenada horizontal
 * @param {number} y - coordenada vertical
 */
function showFloatingMessage(text, x, y) {
    const box = document.getElementById('floating-message');
    box.textContent = text;
    box.style.left = `${x}px`;
    box.style.top = `${y}px`;
    box.style.display = 'block';
    requestAnimationFrame(() => {
        box.style.opacity = '1';
    });
}

/** Oculta a nova mensagem */
function hideFloatingMessage() {
    const box = document.getElementById('floating-message');
    box.style.opacity = '0';
    setTimeout(() => box.style.display = 'none', 400);
}

// 💡 Exemplo de uso:
// showFloatingMessage("Mensagem dinâmica", 600, 300);
// setTimeout(hideFloatingMessage, 3000);


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

                case "desenhar_seta":
                    desenharSeta(dados.id, dados.x1, dados.y1, dados.x2, dados.y2, dados.cor, 6, 24);
                    break;

                case "apagar_seta":
                    apagarSeta(dados.id);
                    break;
        
                case "inicia_Digital_Dash":
                    iniciarDigitalDash();
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