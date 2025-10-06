from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
import json


class Etapa(BaseModel):
    name: str
    etapa: int | None

app = FastAPI()

# Servir arquivos estáticos (css/js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Usar templates HTML
templates = Jinja2Templates(directory="templates")


# Lista de conexões WebSocket ativas
connections: list[WebSocket] = []


# Serve an HTML page
@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)   # <- adiciona a conexão ativa
    try:
        while True: 
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        connections.remove(websocket)  # <- remove quando desconecta
        print("Client disconnected")

# Rota POST que envia dados para os WebSockets
@app.post("/etapas")
async def etapas(etapa: Etapa):
    proximaEtapa = (etapa.etapa or 0) + 1
    mensagem = f"Vá para etapa {proximaEtapa}"
    # Enviar para todos os WebSockets conectados
    for conn in connections:
        await conn.send_text(mensagem)
    
    return {"messagem": f"Notificação enviada para todos os clientes! Etapa: {etapa}"}