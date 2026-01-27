import asyncio
import json
import aiomqtt
from app.mqtt.registry import dispatch

BROKER = "172.16.10.175"
PORT = 1883

class MQTTClient:
    def __init__(self):
        self.client = aiomqtt.Client(BROKER, PORT)

    async def start(self):
        asyncio.create_task(self._listen())

    async def _listen(self):
        async with self.client as client:
            await client.subscribe("#")

            async for message in client.messages:
                payload = message.payload.decode()
                await dispatch(message.topic.value, json.loads(payload))

    async def publish(self, topic: str, payload: dict):
        async with self.client as client:
            await client.publish(topic, json.dumps(payload))