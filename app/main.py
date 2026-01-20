from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import os
import json

# Importa o estado e os websockets
from app import state 
from app.ws import ws_front, overlay_sender

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

# Configuração de CORS (Essencial para Linux/Rede externa)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.on_event("startup")
async def start_overlay_sender():
    # Inicia o loop que envia dados para o projetor
    asyncio.create_task(overlay_sender())

# --- ROTA NOVA: Recebe dados do YOLO via HTTP ---
@app.post("/api/atualizar_borda/{posto_id}")
async def atualizar_borda(posto_id: int, request: Request):
    dados = await request.json()
    # Salva no estado global
    state.set_frame(posto_id, dados)
    return {"status": "ok"}
# ------------------------------------------------

# --- ROTA: Carregar Calibração (Ao iniciar o Front) ---
@app.get("/api/calibracao/{posto_id}")
async def get_calibracao(posto_id: int):
    arquivo = os.path.join(BASE_DIR, f"calibracao_{posto_id}.json")
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler calibração: {e}")
            return {}
    return {} # Retorna vazio se não tiver arquivo

# --- ROTA: Salvar Calibração (Quando clicar no botão) ---
@app.post("/api/calibracao/{posto_id}")
async def save_calibracao(posto_id: int, request: Request):
    try:
        dados = await request.json()
        arquivo = os.path.join(BASE_DIR, f"calibracao_{posto_id}.json")
        with open(arquivo, "w") as f:
            json.dump(dados, f, indent=4)
        print("✅ Calibração salva no disco!")
        return {"status": "ok", "msg": "Salvo com sucesso"}
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return {"status": "error", "msg": str(e)}

@app.get("/")
async def projetor(request: Request):
    return templates.TemplateResponse("projetor.html", {"request": request})

@app.websocket("/ws/front/{posto_id}")
async def websocket_front(websocket: WebSocket, posto_id: int):
    await ws_front(websocket, posto_id)