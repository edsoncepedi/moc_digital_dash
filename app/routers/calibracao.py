from fastapi import APIRouter, Request, Depends
from app.feature_flags.deps import require_feature
from fastapi.templating import Jinja2Templates
from app.services.montagem_service import comparar_objetos
from app.services.gabaritos import OBJETOS_ESPERADOS
from app import state
import os, json
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["Calibração"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

POSTOS_VALIDOS = {0, 1, 2}

class ConfigPosto(BaseModel):
    ROI_X: int = Field(default=35)
    ROI_Y: int = Field(default=211)
    ROI_W: int = Field(default=535)
    ROI_H: int = Field(default=300)
    CONFIDENCE_THRESHOLD: float = Field(default=0.3, ge=0.0, le=1.0)

def _arquivo_config(posto_id: int) -> str:
    return os.path.join(BASE_DIR, f"config_{posto_id}.json")

def _validar_posto(posto_id: int):
    if posto_id not in POSTOS_VALIDOS:
        raise HTTPException(status_code=404, detail="Posto inválido")

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
    _validar_posto(posto_id)
    arquivo = _arquivo_config(posto_id)    

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

            cfg = ConfigPosto(**data)
            return cfg.model_dump()

        except Exception as e:
            print(f"Erro ao ler config do posto {posto_id}: {e}")
            return default_config

    return default_config

@router.post("/config/{posto_id}")
async def save_config_posto(posto_id: int, cfg: ConfigPosto):
    _validar_posto(posto_id)
    arquivo = _arquivo_config(posto_id)

    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(cfg.model_dump(), f, indent=4, ensure_ascii=False)
        return {"status": "ok", "posto": posto_id}
    except Exception as e:
        print(f"Erro ao salvar config do posto {posto_id}: {e}")
        raise HTTPException(status_code=500, detail="Falha ao salvar config")

@router.get("/config-ui")
async def config_ui(request: Request):
    return templates.TemplateResponse(
        "config_ui.html",
        {"request": request}
    )