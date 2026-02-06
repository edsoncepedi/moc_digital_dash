import asyncio
import json
import aiomqtt
from app.mqtt.registry import dispatch

BROKER = "172.16.10.175"
PORT = 1883

class MQTTClient:
    def __init__(self):
        self._client = None
        self._listen_task = None
        self._connected = asyncio.Event()

    async def start(self):
        # inicia o loop de conexão/escuta
        self._listen_task = asyncio.create_task(self._listen_forever())

        # opcional: espera conectar antes de seguir
        await asyncio.wait_for(self._connected.wait(), timeout=10)

    async def stop(self):
        if self._listen_task:
            self._listen_task.cancel()

        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except:
                pass

    async def _listen_forever(self):
        while True:
            try:
                print(f"📡 Conectando no MQTT {BROKER}:{PORT}...")

                client = aiomqtt.Client(BROKER, PORT)
                await client.__aenter__()

                self._client = client
                self._connected.set()

                print("✅ MQTT conectado!")
                await client.subscribe("#")  # depois a gente restringe isso

                async for message in client.messages:
                    try:
                        payload_txt = message.payload.decode(errors="ignore").strip()

                        try:
                            payload = json.loads(payload_txt)
                        except:
                            payload = payload_txt  # cai como string pura
                        await dispatch(message.topic.value, payload)

                    except Exception as e:
                        print(f"❌ Erro ao processar mensagem MQTT: {e}")

            except asyncio.CancelledError:
                print("🛑 MQTT listener cancelado.")
                break

            except Exception as e:
                print(f"⚠️ MQTT caiu: {e}")
                self._connected.clear()
                self._client = None
                await asyncio.sleep(2)  # retry

    async def publish(self, topic: str, payload: dict):
        if not self._client:
            print("⚠️ MQTT não conectado. Não foi possível publicar.")
            return

        try:
            await self._client.publish(topic, json.dumps(payload))
        except Exception as e:
            print(f"❌ Erro ao publicar MQTT: {e}")
