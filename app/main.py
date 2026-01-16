from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import os

from app.ws import ws_front, ws_borda, overlay_sender

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.on_event("startup")
async def start_overlay_sender():
    asyncio.create_task(overlay_sender())

@app.get("/")
async def projetor(request: Request):
    return templates.TemplateResponse("projetor.html", {"request": request})

@app.websocket("/ws/front")
async def websocket_front(websocket: WebSocket):
    await ws_front(websocket)

@app.websocket("/ws/borda")
async def websocket_borda(websocket: WebSocket):
    await ws_borda(websocket)
