from fastapi import APIRouter, Request, Depends
from app.feature_flags.deps import require_feature
from app.services.montagem_service import comparar_objetos
from app.services.gabaritos import OBJETOS_ESPERADOS
from app.services.utils import nome_amigavel, nomes_amigaveis_numerados
from app.services.posto_fsm import processar_estado_posto, processar_estado_posto_0
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

def formatar_checklist(esperados, detectados):

    nomes = nomes_amigaveis_numerados(esperados)

    linhas = []

    for item in sorted(esperados):
        nome = nomes[item]

        if item in detectados:
            linhas.append(f"☑ {nome}")
        else:
            linhas.append(f"☐ {nome}")

    return "\n".join(linhas)

def formatar_itens(itens, vazio="Nenhum"):
    """
    Recebe list, set ou tuple e retorna string legível
    """
    if not itens:
        return vazio

    itens_ordenados = sorted(map(str, itens))

    return "\n".join(
        f"• {nome_amigavel(item)}"
        for item in itens_ordenados
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
        
        if len(resultado["faltantes"]) == 0 and len(extras) == 0:
            checklist = formatar_checklist(objetos_esperados, objetos_detectados)

            mensagem = (
                f"POSTO {posto_id}\n\n"
                f"Organização concluída! Passe para o próximo posto.\n\n"
                f"{checklist}"
            )
            await processar_estado_posto_0("FINALIZADO")
        elif len(objetos_detectados) == 0:
            checklist = formatar_checklist(objetos_esperados, objetos_detectados)

            mensagem = (
                f"POSTO {posto_id}\n\n"
                f"A mesa está vazia. Inicie a montagem:\n\n"
                f"{checklist}"
            )

            await processar_estado_posto_0("INICIO")

        else:
            checklist = formatar_checklist(objetos_esperados, objetos_detectados)

            mensagem = (
                f"POSTO {posto_id}\n\n"
                f"Checklist da montagem:\n\n"
                f"{checklist}"
            )
            if extras:
                mensagem += (
                    "\n\n⚠ Itens fora da receita:\n"
                    f"{formatar_itens(extras)}"
                )
            
            await processar_estado_posto_0("MONTAGEM")
    elif posto_id == 1:
        etapa = int(dados.get("etapa", 1))
        await processar_estado_posto(posto_id, dados)
        
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
        await processar_estado_posto(posto_id, dados)

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

    #resposta.update(resultado)
    mensagem_projetor(posto_id, mensagem)

    return {"status": "ok"}