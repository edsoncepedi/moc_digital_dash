// ==========================
// LISTA DE ETAPAS
// ==========================
const etapas = [
    "Organize painel esquerdo de acordo com Etapa 0",
    "Mova a forma correspondente à peça da Etapa 1 para a Base",
    "Mova a forma correspondente à peça da Etapa 2 para a Base",
    "Mova a forma correspondente à peça da Etapa 3 para a Base",
    "Mova a forma correspondente à peça da Etapa 4 para a Base",
    "Produto finalizado. Retire todas as peças para reiniciar o sistema!"
];

const checklist = document.getElementById("checklist");
const status = document.getElementById("status");

// Cria os itens da lista
etapas.forEach((etapa, i) => {
  const li = document.createElement("li");
  li.className = `
    flex justify-between items-center p-3 border border-gray-200 rounded-xl
    hover:bg-blue-50 transition-all duration-200
  `;

  li.innerHTML = `
    <span class="text-gray-800 select-none">${etapa}</span>
    <div id="icon-${i}" class="etapa-icon estado-nenhum">•</div>
  `;
  checklist.appendChild(li);
});

// ==========================
// Funções auxiliares
// ==========================
function resetChecklist() {
  etapas.forEach((_, i) => {
    const icon = document.getElementById(`icon-${i}`);
    icon.className = "etapa-icon estado-nenhum";
    icon.textContent = "•";
  });
}

function marcarEtapa(index, erro = false) {
  const icon = document.getElementById(`icon-${index-1}`);
  if (!icon) return;

  if (erro) {
    icon.className = "etapa-icon estado-erro";
    icon.textContent = "✕";
  } else {
    icon.className = "etapa-icon estado-ok";
    icon.textContent = "✓";
  }
}

// ==========================
// CONEXÃO WEBSOCKET
// ==========================
function conectarWebSocket() {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const host = location.host;
  const ws = new WebSocket(`${protocol}://${host}/ws`);

  ws.onopen = () => {
    console.log("✅ Conectado ao WebSocket");
    status.textContent = "Conectado ao servidor WebSocket";
  };

  ws.onmessage = (event) => {
    try {
      const dados = JSON.parse(event.data);

      if (dados.acao === "mensagem" && typeof dados.etapa === "number") {
        if (dados.etapa === 0) {
          resetChecklist();
          marcarEtapa(0, dados.erro);
        } else {
          marcarEtapa(dados.etapa, dados.erro);
        }
      }

      if (dados.acao === "reinicia_Digital_Dash") {
          resetChecklist();
      }

    } catch (e) {
      console.error("Erro ao processar mensagem:", e);
    }
  };

  ws.onclose = () => {
    status.textContent = "Tentando reconectar...";
    setTimeout(conectarWebSocket, 3000);
  };
}

conectarWebSocket();

// ==========================
// BOTÃO "SISTEMA PRONTO"
// ==========================
document.getElementById("btnPronto").addEventListener("click", async () => {
  try {
    const resposta = await fetch("/pronto", { method: "POST" });
    if (resposta.ok) {
      status.textContent = "✅ Sistema habilitado para atender requisições.";
    } else {
      status.textContent = "⚠️ Falha ao enviar comando para o servidor.";
    }
  } catch (erro) {
    console.error("Erro ao enviar requisição:", erro);
    status.textContent = "❌ Erro de conexão com o servidor.";
  }
});
