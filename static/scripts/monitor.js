// ==========================
// LISTA DE ETAPAS
// ==========================
const etapas = [
    "Etapa 0",
    "Etapa 1",
    "Etapa 2",
    "Etapa 3",
    "Etapa 4",
    "Etapa 5",
    "Etapa 6",
    "Etapa 7"
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
  const icon = document.getElementById(`icon-${index}`);
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
