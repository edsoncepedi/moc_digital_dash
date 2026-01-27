from fastapi import APIRouter, Request
from app import state
import os, json

router = APIRouter(prefix="/api", tags=["Calibração"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.post("/atualizar_borda/{posto_id}")
async def atualizar_borda(posto_id: int, request: Request):
    dados = await request.json()
    # Salva no estado global
    state.set_frame(posto_id, dados)
    return {"status": "ok"}

@router.get("/calibracao/{posto_id}")
async def get_calibracao(posto_id: int):
    arquivo = os.path.join(BASE_DIR, f"calibracao_{posto_id}.json")
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler calibração: {e}")
            return {}
    return {}

@router.post("/calibracao/{posto_id}")
async def save_calibracao(posto_id: int, request: Request):
    dados = await request.json()
    arquivo = os.path.join(BASE_DIR, f"calibracao_{posto_id}.json")
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=4)
    return {"status": "ok"}

@router.post("/mensagem/{posto_id}") 
async def enviar_mensagem(posto_id: int, request: Request): 
    """ Recebe mensagens de texto para exibição no overlay """ 
    dados = await request.json() 
    state.set_mensagem(posto_id, dados) 
    return { "status": "ok", "posto": posto_id, "mensagem": dados }