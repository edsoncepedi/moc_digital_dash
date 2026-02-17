from fastapi import APIRouter, Request, Depends
from app.feature_flags.deps import require_feature
from app.services.montagem_service import comparar_objetos
from app.services.gabaritos import OBJETOS_ESPERADOS
from app import state
import os, json

router = APIRouter(prefix="/api", tags=["Calibração"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

@router.get("/config/{posto_id}")
async def get_config_posto(posto_id: int):
    arquivo = os.path.join(BASE_DIR, f"config_{posto_id}.json")

    # Valores padrão caso o arquivo não exista
    default_config = {
        "ROI_X": 35,
        "ROI_Y": 211,
        "ROI_W": 535,
        "ROI_H": 300,
        "CONFIDENCE_THRESHOLD": 0.3
    }

    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Garante que as chaves existam, mesmo se o JSON vier incompleto
            for k, v in default_config.items():
                if k not in data:
                    data[k] = v

            return data

        except Exception as e:
            print(f"Erro ao ler config do posto {posto_id}: {e}")
            return default_config

    return default_config