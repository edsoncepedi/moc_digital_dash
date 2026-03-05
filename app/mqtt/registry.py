from app.mqtt.handlers import handle_feature_calibracao, handle_dispositivo_posto
from app.mqtt.topics import Topics

ROUTES = {
    Topics.FEATURE_CALIBRACAO: handle_feature_calibracao,
    Topics.RESET_POSTO: handle_dispositivo_posto
}

async def dispatch(topic: str, payload):

    # 1) reset de posto
    if topic == Topics.RESET_POSTO:
        posto_nome = payload.get("posto")  # ou como vier no payload
        await handle_dispositivo_posto(posto_nome, payload)
        return

    # 2) calibracao
    if topic == Topics.FEATURE_CALIBRACAO:
        await handle_feature_calibracao(payload)
        return

    # 3) tópico dinâmico
    prefix = "rastreio_nfc/esp32/"
    suffix = "/dispositivo"

    if topic.startswith(prefix) and topic.endswith(suffix):
        posto_nome = topic[len(prefix):-len(suffix)]
        await handle_dispositivo_posto(posto_nome, payload)
        return

    # 4) fallback
    print(f"⚠️ No handler for topic: {topic}, payload: {payload}")