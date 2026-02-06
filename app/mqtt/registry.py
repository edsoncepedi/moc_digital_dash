from app.mqtt.handlers import handle_feature_calibracao, handle_dispositivo_posto
from app.mqtt.topics import Topics

ROUTES = {
    Topics.FEATURE_CALIBRACAO: handle_feature_calibracao,
    Topics.RESET_POSTO: handle_dispositivo_posto
}

async def dispatch(topic: str, payload):
    # 1) rotas fixas
    handler = ROUTES.get(topic)
    if handler:
        await handler(payload)
        return

    # 2) tópico dinâmico: rastreio_nfc/esp32/{posto}/dispositivo
    prefix = "rastreio_nfc/esp32/"
    suffix = "/dispositivo"

    if topic.startswith(prefix) and topic.endswith(suffix):
        posto_nome = topic[len(prefix):-len(suffix)]  # ex: "posto_0"
        await handle_dispositivo_posto(posto_nome, payload)
        return

    # 3) fallback
    print(f"⚠️ No handler for topic: {topic}, payload: {payload}")