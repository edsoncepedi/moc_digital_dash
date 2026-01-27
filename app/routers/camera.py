from fastapi import APIRouter, Request, Depends
from app.feature_flags.deps import require_feature
from app.services.montagem_service import comparar_objetos
from app.services.gabaritos import OBJETOS_ESPERADOS
from app import state

router = APIRouter(prefix="/camera", tags=["Camera"])

def mensagem_projetor(posto_id: int, mensagem: str):
    state.set_mensagem(
        posto_id,
        {
            "mensagem": {
                "texto": mensagem,
                "position": "top-rigth",
                "anchor": "center",
                "bg": "rgba(0,0,0,1)",
                "color": "#ffffff",
                "fontSize": 28
            }
        }
    )

@router.post("/{posto_id}", dependencies=[Depends(require_feature("camera"))])
async def processar_etapas(posto_id: int, request: Request):
    dados = await request.json()

    resposta = {"status": "ok", "posto": posto_id}

    # 🔹 Lógica específica do posto 0
    if posto_id == 0:
        objetos_detectados = set(dados.get("objetos", []))
        objetos_esperados = OBJETOS_ESPERADOS.get(0, set())

        resultado = comparar_objetos(
            objetos_detectados,
            objetos_esperados
        )
        print(f"[POSTO {posto_id}] Resultado da montagem: {resultado}")
        resposta.update(resultado)
        mensagem_projetor(posto_id, "Verificando montagem...")
        # Envia pro frontend

    return resposta