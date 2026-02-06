from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.mqtt.client import MQTTClient
from app.mqtt_instance import mqtt

import asyncio, os

from app.ws import overlay_sender
from app.routers import (
    calibracao,
    camera,
    websocket,
    front
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.on_event("startup")
async def start_overlay_sender():
    asyncio.create_task(overlay_sender())

@app.on_event("startup")
async def startup():
    await mqtt.start()

@app.on_event("shutdown")
async def shutdown():
    await mqtt.stop()

# ⬇️ Registrando os routers
app.include_router(calibracao.router)
app.include_router(camera.router)
app.include_router(websocket.router)
app.include_router(front.router)