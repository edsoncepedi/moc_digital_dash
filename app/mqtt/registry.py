from app.mqtt.handlers import handle_feature_calibracao
from app.mqtt.topics import Topics

ROUTES = {
    Topics.FEATURE_CALIBRACAO: handle_feature_calibracao
}

async def dispatch(topic: str, payload: dict):
    handler = ROUTES.get(topic)
    if handler:
        await handler(payload)
    print(f"⚠️ No handler for topic: {topic}, payload: {payload}")