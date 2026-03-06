from fastapi import APIRouter, Request, Depends
from app.feature_flags.deps import require_feature
from app.services.montagem_service import comparar_objetos
from app.services.gabaritos import OBJETOS_ESPERADOS
from app.services.posto_fsm import processar_estado_posto, processar_estado_posto_0
from app.services.mensagens_postos import (
    mensagem_posto_0_inicio,
    mensagem_posto_0_montagem,
    mensagem_posto_0_finalizado,
    obter_mensagem_etapa,
)
from app import state
from app.mqtt_instance import mqtt


router = APIRouter(prefix="/camera", tags=["Camera"])


def mensagem_projetor(posto_id: int, mensagem: str):
    state.set_mensagem(
        posto_id,
        {
            "mensagem": {
                "texto": mensagem,
                "position": "bottom-right",
                "anchor": "center",
                "bg": "rgba(0,0,0,1)",
                "color": "#ffffff",
                "fontSize": 28
            }
        }
    )


@router.get("/{posto_id}")
async def get_estado_posto(posto_id: int):
    return {
        "status": "ok",
        "posto": posto_id,
        "estado": state.get_estado(posto_id),
    }


@router.post("/{posto_id}", dependencies=[Depends(require_feature("camera"))])
async def atualizar_borda(posto_id: int, request: Request):
    dados = await request.json()

    # Atualiza retângulos/frame
    state.set_frame(posto_id, dados)

    if posto_id == 0:
        retangulos = dados.get("retangulos", [])
        unsigned = dados.get("unassigned", [])
        objetos_detectados = set(dados.get("objetos", []))

        for item in retangulos:
            objetos_detectados.add(item.get("id"))

        objetos_esperados = OBJETOS_ESPERADOS.get(0, set())

        extras = set()
        for item in unsigned:
            extras.add(item.get("id"))

        resultado = comparar_objetos(
            objetos_detectados,
            objetos_esperados
        )

        if len(resultado["faltantes"]) == 0 and len(extras) == 0:
            mensagem = mensagem_posto_0_finalizado(
                posto_id,
                objetos_esperados,
                objetos_detectados
            )
            await processar_estado_posto_0("FINALIZADO")

        elif len(objetos_detectados) == 0:
            mensagem = mensagem_posto_0_inicio(
                posto_id,
                objetos_esperados,
                objetos_detectados
            )
            await processar_estado_posto_0("INICIO")

        else:
            mensagem = mensagem_posto_0_montagem(
                posto_id,
                objetos_esperados,
                objetos_detectados,
                extras
            )
            await processar_estado_posto_0("MONTAGEM")

    elif posto_id in (1, 2):
        etapa = int(dados.get("etapa", 1))
        await processar_estado_posto(posto_id, dados)
        mensagem = obter_mensagem_etapa(posto_id, etapa)

    else:
        mensagem = f"POSTO {posto_id}\n\nNenhuma lógica específica implementada."

    mensagem_projetor(posto_id, mensagem)

    return {"status": "ok"}