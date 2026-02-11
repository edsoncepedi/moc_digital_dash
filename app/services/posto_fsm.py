from app import state
from app.mqtt_instance import mqtt

ESTADOS = ("INICIO", "MONTAGEM", "FINALIZADO")

async def on_transicao_estado(posto_id: int, anterior: str, atual: str):
    # Exemplo: publica quando entra em montagem
    if anterior == "INICIO" and atual == "MONTAGEM":
        await mqtt.publish(f"rastreio_nfc/esp32/{posto_id}/dispositivo", "BT1")

    await mqtt.publish(
        f"visao/posto_{posto_id}/estado",
        {"estado": atual},
        qos=1,
        retain=True
    )


def calcular_estado(posto_id: int, dados: dict) -> str:
    # Exemplo: posto 1 e 2 usam etapa
    if posto_id in [1, 2]:
        etapa = int(dados.get("etapa", 1))
        if etapa == 1:
            return "INICIO"
        elif etapa in [2, 3, 4]:
            return "MONTAGEM"
        else:
            return "FINALIZADO"

    # posto 0 usa lógica de faltantes/extras
    if posto_id == 0:
        pronto = bool(dados.get("pronto", False))  # exemplo
        if pronto:
            return "FINALIZADO"

        tem_objetos = len(dados.get("objetos", [])) > 0
        return "MONTAGEM" if tem_objetos else "INICIO"

    return "INICIO"


async def processar_estado_posto(posto_id: int, dados: dict):
    """
    Função chamada em alta frequência pela rota /camera/{posto_id}.
    Só faz algo quando detecta mudança de estado.
    """

    # 1) calcula o novo estado com base nos dados
    novo_estado = calcular_estado(posto_id, dados)

    # 2) pega o estado anterior
    estado_anterior = state.get_estado(posto_id)

    # 3) se não mudou, não faz nada
    if novo_estado == estado_anterior:
        return

    # 4) atualiza state
    state.set_estado(posto_id, novo_estado)

    # 5) dispara evento mqtt dependendo da transição
    await on_transicao_estado(posto_id, estado_anterior, novo_estado)
