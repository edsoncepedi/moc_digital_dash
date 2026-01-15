from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os

from app.state import estado

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static e Templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

connections: list[WebSocket] = []


# -----------------------------
# WEBSOCKET
# -----------------------------
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except:
        connections.remove(ws)


# -----------------------------
# ROTAS HTML
# -----------------------------
@app.get("/")
async def projetor(request: Request):
    return templates.TemplateResponse("projetor.html", {"request": request})


# -----------------------------
# YOLO → FASTAPI
# -----------------------------
@app.post("/deteccoes")
async def receber_deteccoes(payload: dict):

    estado["retangulos"] = payload.get("retangulos", [])

    mensagem = {
        "acao": "overlay_update",
        "retangulos": estado["retangulos"]
    }

    texto = json.dumps(mensagem)

    for ws in connections:
        await ws.send_text(texto)

    return {"status": "ok"}

