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
                "position": "bottom-right",
                "anchor": "center",
                "bg": "rgba(0,0,0,1)",
                "color": "#ffffff",
                "fontSize": 28
            }
        }
    )

def formatar_itens(itens, vazio="Nenhum"):
    """
    Recebe list, set ou tuple e retorna string legível
    """
    if not itens:
        return vazio

    # ordena para manter estabilidade visual
    itens_ordenados = sorted(map(str, itens))
    return "\n".join(f"• {item}" for item in itens_ordenados)

@router.post("/{posto_id}", dependencies=[Depends(require_feature("camera"))])
async def atualizar_borda(posto_id: int, request: Request):
    dados = await request.json()

    #Atualiza retagunlos
    state.set_frame(posto_id, dados)
    resposta = {"status": "ok", "posto": posto_id}

    # 🔹 Lógica específica do posto 0
    if posto_id == 0:   
        retagunlos = dados.get("retangulos", [])
        unsigned = dados.get("unassigned", [])
        objetos_detectados = set(dados.get("objetos", []))
        for item in retagunlos:
            objetos_detectados.add(item.get("id"))
        objetos_esperados = OBJETOS_ESPERADOS.get(0, set())

        extras = set()
        for item in unsigned:
            extras.add(item.get("id"))

        inseridos = set()
        for item in objetos_detectados:
            if item in objetos_esperados:
                inseridos.add(item)
        resultado = comparar_objetos(
            objetos_detectados,
            objetos_esperados
        )

        mensagem = (
            f"POSTO {posto_id}\n\n"
            f"Insira na mesa os sceguintes objetos:\n"
            f"{formatar_itens(resultado['faltantes'])}\n\n"
            f"Itens inseridos com sucesso:\n"
            f"{formatar_itens(inseridos)}"
        )

        if len(extras) > 0:
            mensagem += (
                f"\n\n"
                f"Retire os seguintes itens (Fora da Receita):\n"
                f"{formatar_itens(extras)}"
            )
    elif posto_id == 1:
        etapa = int(dados.get("etapa", 1))

        if etapa == 1:
            mensagem = f"POSTO {posto_id}\n\nPegue a CPU"
        elif etapa == 2:
            mensagem = f"POSTO {posto_id}\n\nInsira a CPU na placa-mãe"
        elif etapa == 3:
            mensagem = f"POSTO {posto_id}\n\nPegue a Fan"
        elif etapa == 4:
            mensagem = f"POSTO {posto_id}\n\nInsira a Fan no processador"
        elif etapa == 5:
            mensagem = f"POSTO {posto_id}\n\nMontagem concluida! Pressione a pedaleira para enviar o produto para o próximo posto."

    elif posto_id == 2:
        etapa = int(dados.get("etapa", 1))

        if etapa == 1:
            mensagem = f"POSTO {posto_id}\n\nPegue a primeira memoria."
        elif etapa == 2:
            mensagem = f"POSTO {posto_id}\n\nInsira a memoria no primeiro slot."
        elif etapa == 3:
            mensagem = f"POSTO {posto_id}\n\nPegue a segunda memória."
        elif etapa == 4:
            mensagem = f"POSTO {posto_id}\n\nInsira a memoria no segundo slot."
        elif etapa == 5:
            mensagem = f"POSTO {posto_id}\n\nMontagem concluida! Pressione a pedaleira para enviar o produto para o próximo posto."

    else:
        mensagem = f"POSTO {posto_id}\n\nNenhuma lógica específica implementada."

    resposta.update(resultado)
    mensagem_projetor(posto_id, mensagem)

    return {"status": "ok"}