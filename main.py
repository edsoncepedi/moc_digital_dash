from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import json

class Etapa(BaseModel):
    posto: str
    etapa: int 
    posicao: str = Field(default="bottom-right")
    instrucao: list[str] = Field(default_factory=lambda: [
        "Execute etapa 1",
        "Execute etapa 2",
        "Execute etapa 3",
        "Execute etapa 4",
        "Execute etapa 5",
        "Execute etapa 6",
        "Execute etapa 7",
        "Produto finalizado. Inicie uma nova montagem."
    ])

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
connections: list[WebSocket] = []


@app.get("/projetor")
async def get(request: Request):
    return templates.TemplateResponse("projetor.html", {"request": request})

@app.get("/monitor")
async def get(request: Request):
    return templates.TemplateResponse("monitor.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)


@app.post("/mensagem")
async def enviar_mensagem(dados: dict):
    pacote = {
        "acao": "mensagem",
        "texto": dados.get("texto", "Mensagem vazia"),
        "posicao": dados.get("posicao", "bottom-right")
    }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))
    return {"status": "mensagem enviada"}


@app.post("/retangulo")
async def enviar_retangulo(dados: dict):
    pacote = {
        "acao": "retangulo",
        "x": dados.get("x", 100),
        "y": dados.get("y", 100),
        "largura": dados.get("largura", 120),
        "altura": dados.get("altura", 60)
    }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))
    return {"status": "retangulo desenhado"}

@app.post("/etapas")
async def etapas(etapa: Etapa):
    """Recebe instruções e envia via WebSocket"""
    if etapa.etapa < 0 or etapa.etapa >= len(etapa.instrucao):
        return {"erro": "Índice de etapa inválido"}
    
    timer = False
    if etapa.etapa < 7:
        timer = True

    erro = False
    if etapa.etapa == 4:
        erro = True

    mensagem = {
        "acao": "mensagem",
        "etapa": etapa.etapa,
        "posto": f"{etapa.posto}",
        "texto": f"{etapa.instrucao[etapa.etapa]}",
        "posicao": etapa.posicao,
        "mostrar_timer": timer,
        "erro": erro
    }

    # Enviar JSON para todos os clientes conectados
    for conn in connections:
        try:
            await conn.send_text(json.dumps(mensagem))
        except Exception as e:
            print("Erro ao enviar mensagem:", e)

    return {"status": "enviado", "mensagem": mensagem}