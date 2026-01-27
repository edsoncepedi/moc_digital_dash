from fastapi import APIRouter, Request
from app import state

router = APIRouter(prefix="/camera", tags=["Camera"])

@router.post("/{posto_id}")
async def processar_etapas(posto_id: int, request: Request):
    dados = await request.json()

    match posto_id:
        case 0:
            resposta = "Zero"
        case 1:
            resposta = "Um"
        case 2:
            resposta = "Dois"
        case _:
            resposta = "Outro valor"

    state.set_mensagem(posto_id, dados)

    return {
        "status": "ok",
        "posto": posto_id,
        "resposta": resposta
    }