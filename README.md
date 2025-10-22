# 🧩 Sistema Digital Dash — FastAPI + WebSocket + Jinja2

Este projeto implementa um sistema interativo de monitoramento e controle visual chamado **Digital Dash**, construído em **FastAPI** com suporte a **WebSockets**, **Jinja2** e **Uvicorn**.  
Ele exibe e atualiza elementos gráficos (retângulos, mensagens, imagens) em tempo real conforme o estado do processo de montagem avança.

---

## 🚀 Funcionalidades principais

- Interface Web com **duas telas**:
  - `/projetor` → Exibe instruções visuais (etapas e imagens).
  - `/monitor` → Interface de controle e feedback.
- Comunicação **em tempo real via WebSocket**.
- Controle de fluxo de montagem dividido em **etapas**.
- Envio dinâmico de:
  - Retângulos, setas e mensagens via API HTTP.
  - Estados e comandos em broadcast para todos os clientes conectados.
- Sistema de **ativação/desativação** do processo (`/pronto`, `/reset`).
- Suporte a **Jinja2 Templates** e **arquivos estáticos** (imagens, CSS, JS).

---

## 🧱 Estrutura do projeto

```
meu_projeto/
├── app/
│   ├── main.py                # Código principal (FastAPI + WebSocket)
│   ├── templates/             # HTMLs (projetor.html, monitor.html)
│   └── static/                # Arquivos estáticos (imagens, CSS, JS)
│
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Configuração do container Docker
├── .dockerignore              # Arquivos a ignorar no build
└── README.md
```

---

## ⚙️ Tecnologias utilizadas

- **Python 3.12**
- **FastAPI** — Framework web moderno e rápido
- **Uvicorn** — Servidor ASGI de alto desempenho
- **Jinja2** — Templates HTML
- **WebSockets** — Comunicação em tempo real

---

## 🧰 Instalação local (sem Docker)

### 1️⃣ Crie e ative um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

### 2️⃣ Instale as dependências
```bash
pip install -r requirements.txt
```

### 3️⃣ Execute o servidor
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse em: [http://localhost:8000/projetor](http://localhost:8000/projetor)  
ou: [http://localhost:8000/monitor](http://localhost:8000/monitor)

---

## 🐋 Execução com Docker

### 1️⃣ Construa a imagem
```bash
docker build -t digital_dash .
```

### 2️⃣ Rode o container
```bash
docker run -d -p 8000:8000 digital_dash
```

Acesse em:  
👉 [http://localhost:8000/projetor](http://localhost:8000/projetor)  
👉 [http://localhost:8000/monitor](http://localhost:8000/monitor)

---

## 🧠 Principais endpoints

| Método | Endpoint | Descrição |
|--------|-----------|-----------|
| `GET` | `/projetor` | Retorna a interface principal (visualização) |
| `GET` | `/monitor` | Retorna o painel de controle |
| `POST` | `/pronto` | Ativa o sistema |
| `POST` | `/reset` | Reinicia o processo |
| `POST` | `/mensagem` | Envia mensagens para a interface |
| `POST` | `/visao` | Recebe dados de visão e atualiza estado |
| `POST` | `/retangulo` | Cria ou atualiza um retângulo |
| `POST` | `/apagar_retangulo` | Remove um retângulo |
| `POST` | `/seta` | Desenha setas na interface |
| `POST` | `/apagar_seta` | Remove setas |
| `POST` | `/etapas` | Avança etapas do processo |

---

## 💡 Observações importantes

- O sistema só aceita requisições se estiver **ativo** (`/pronto`).
- A comunicação entre clientes e servidor ocorre via **WebSocket** (`/ws`).
- Ao encerrar uma montagem, o sistema é automaticamente desativado.

---

## 🧑‍💻 Autor

**Edson Alves da Silva**  
Desenvolvedor Python e integrador de sistemas FastAPI + MQTT + WebSocket.

---

## 📝 Licença

Este projeto é de uso interno e educacional.  
Sinta-se livre para adaptar ou expandir conforme suas necessidades.
