from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from fastapi import HTTPException
from functools import wraps
import json
import os

sistema_ativo = {"ativo": False}
estado_global = {}

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

connections: list[WebSocket] = []

def requer_sistema_ativo(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not sistema_ativo["ativo"]:
            raise HTTPException(status_code=403, detail="Sistema não está ativo.")
        return await func(*args, **kwargs)
    return wrapper

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
            data = await websocket.receive_text()
            msg = json.loads(data)
            estado_global.update(msg["dados"])
            print("📨 Estado atualizado:", estado_global)
    except WebSocketDisconnect:
        connections.remove(websocket)

@app.post("/mensagem")
@requer_sistema_ativo
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
@requer_sistema_ativo
async def desenhar_retangulo(dados: dict):
    pacote = {
        "acao": "desenhar_retangulo",
        "id": dados.get("id"),
        "x": dados.get("x"),
        "y": dados.get("y"),
        "largura": dados.get("largura"),
        "altura": dados.get("altura"),
        "cor": dados.get("cor"),
        "texto": dados.get("texto"),
        "mostra": dados.get("mostra"),
    }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))
    return {"status": "retangulo desenhado"}

@app.post("/apagar_retangulo")
@requer_sistema_ativo
async def apagar_retangulo(dados: dict):
    pacote = {
        "acao": "apagar_retangulo",
        "id": dados.get("id", 100)
    }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))
    return {"status": "retangulo apagado"}

@app.post("/seta")
@requer_sistema_ativo
async def desenhar_seta(dados: dict):
    x = dados.get("x")
    y = dados.get("y")
    if y <100:
        y = 100
    pacote = {
        "acao": "desenhar_seta",
        "id": dados.get("id"),
        "x1": x,
        "y1": y-100,
        "x2": x+100,
        "y2": y-100,
        "cor": dados.get("cor")
    }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))
    return {"status": "seta desenhada"}

@app.post("/apagar_seta")
@requer_sistema_ativo
async def apagar_seta(dados: dict):
    pacote = {
        "acao": "apagar_seta",
        "id": dados.get("id", 100)
    }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))
    return {"status": "seta apagado"}

@app.post("/reset")
@requer_sistema_ativo
async def reset_dash():
    sistema_ativo["ativo"] = False
    mensagem = {
        "acao": "reinicia_Digital_Dash",
    }

    # Enviar JSON para todos os clientes conectados
    for conn in connections:
        try:
            await conn.send_text(json.dumps(mensagem))
        except Exception as e:
            print("Erro ao enviar mensagem:", e)
    print("Sistema Resetado.")
    return {"status": "Sistema Resetado."}

@app.post("/overlay")
@requer_sistema_ativo
async def overlay_update(dados: dict):

    pacote = {
        "acao": "overlay_update",
        "retangulos": dados.get("retangulos", [])
    }

    for ws in connections:
        await ws.send_text(json.dumps(pacote))

    return {"status": "ok", "total": len(pacote["retangulos"])}

@app.post("/pronto")
async def sistema_pronto():
    sistema_ativo["ativo"] = True
    mensagem = {
        "acao": "inicia_Digital_Dash",
    }

    # Enviar JSON para todos os clientes conectados
    for conn in connections:
        try:
            await conn.send_text(json.dumps(mensagem))
        except Exception as e:
            print("Erro ao enviar mensagem:", e)
    print("🚀 Sistema habilitado para atender requisições.")
    return {"status": "ok"}

async def muda_cor_retan(id, cor):
    pacote = {
        "acao": "desenhar_retangulo",
        "id": id,
        "cor": cor
        }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))

async def habilita_retan(id, texto,cor):
    pacote = {
        "acao": "desenhar_retangulo",
        "id": id,
        "cor": cor,
        "texto": texto,
        "mostra": True
        }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))

async def desabilita_retan(id):
    pacote = {
        "acao": "desenhar_retangulo",
        "id": id,
        "mostra": False
        }
    for ws in connections:
        await ws.send_text(json.dumps(pacote))