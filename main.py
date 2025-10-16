from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from fastapi import HTTPException
from functools import wraps
import json

sistema_ativo = {"ativo": False}
estado_global = {}

class Etapa(BaseModel):
    posto: str
    etapa: int 
    posicao: str = Field(default="bottom-right")
    erro: bool
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

@app.post("/pronto")
async def sistema_pronto():
    sistema_ativo["ativo"] = True
    await inicia_montagem_retangulos()
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

@app.post("/etapas")
@requer_sistema_ativo
async def etapas(etapa: Etapa):
    """Recebe instruções e envia via WebSocket"""
    if etapa.etapa < 0 or etapa.etapa >= len(etapa.instrucao):
        return {"erro": "Índice de etapa inválido"}

    timer = False
    if etapa.etapa < 7:
        timer = True

    if not etapa.erro:
        mensagem = {
            "acao": "mensagem",
            "etapa": etapa.etapa,
            "posto": f"{etapa.posto}",
            "texto": f"{etapa.instrucao[etapa.etapa]}",
            "posicao": etapa.posicao,
            "mostrar_timer": timer,
            "erro": etapa.erro
        }
    else:
        mensagem = {
            "acao": "mensagem",
            "etapa": etapa.etapa,
            "posto": f"{etapa.posto}",
            "texto": f"Erro: {etapa.instrucao[etapa.etapa]}",
            "posicao": etapa.posicao,
            "mostrar_timer": False,
            "erro": etapa.erro
        }

    # Enviar JSON para todos os clientes conectados
    for conn in connections:
        try:
            await conn.send_text(json.dumps(mensagem))
        except Exception as e:
            print("Erro ao enviar mensagem:", e)

    return {"status": "enviado", "mensagem": mensagem}

async def inicia_montagem_retangulos():
    ref_x_montagem = 900
    ref_y_montagem = 200

    ref_x_organiza = 250
    ref_y_organiza = 200

    largura_peca = 150
    distancia_x = 200

    x = [400, 100, 1500, ref_x_organiza, ref_x_organiza+distancia_x, ref_x_organiza, ref_x_organiza+distancia_x, ref_x_montagem, ref_x_montagem+distancia_x, ref_x_montagem, ref_x_montagem+distancia_x, ref_x_montagem-50]
    y = [700, 700, 700, ref_y_organiza, ref_y_organiza, ref_y_organiza+250, ref_y_organiza+250, ref_y_montagem, ref_y_montagem, ref_y_montagem+250, ref_y_montagem+250, ref_y_montagem-80]
    largura = [1100, 300, 300, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, 450]
    altura = [200, 200, 200, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, 530]
    texto = ['Console', 'Left', 'Rigth', 'Quadrado', 'Decágono', 'Triângulo', 'Hexágono', 'Quadrado', 'Decágono', 'Triângulo', 'Hexágono', 'Base']
    id = ['Console', 'Left', 'Rigth', 'left1', 'left2', 'left3', 'left4', 'right1', 'right2', 'right3', 'right4', 'proxy']
    mostra = [False, False, False, True, True, True, True, True, True, True, True, True]

    for i in range(len(x)):
        pacote = {
            "acao": "desenhar_retangulo",
            "id": id[i],
            "x": x[i],
            "y": y[i],
            "largura": largura[i],
            "altura": altura[i],
            "cor": "white",
            "texto": texto[i],
            "mostra": mostra[i]
        }

        for ws in connections:
            await ws.send_text(json.dumps(pacote))