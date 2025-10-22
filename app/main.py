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

instrucoes = [
        "Organize painel esquerdo de acordo com Etapa 0",
        "Mova a forma correspondente à peça da Etapa 1 para a Base",
        "Mova a forma correspondente à peça da Etapa 2 para a Base",
        "Mova a forma correspondente à peça da Etapa 3 para a Base",
        "Mova a forma correspondente à peça da Etapa 4 para a Base",
        "Produto finalizado. Retire todas as peças para reiniciar o sistema!"
    ]

class Etapa(BaseModel):
    posto: str
    etapa: int 
    posicao: str = Field(default="bottom-right")
    erro: bool
    instrucao: list[str] = Field(default_factory=lambda: [
        "Organize painel esquerdo de acordo com Etapa 0",
        "Mova a forma correspondente à peça da Etapa 1 para a Base",
        "Mova a forma correspondente à peça da Etapa 2 para a Base",
        "Mova a forma correspondente à peça da Etapa 3 para a Base",
        "Mova a forma correspondente à peça da Etapa 4 para a Base",
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

maquina_estado = {'posto_1': 0}
peca = ["quadrado", "pentagono", "triangulo", "hexagono"]

@app.post("/visao")
@requer_sistema_ativo
async def receber_visao(dados: dict):
    pacote = {'left1': dados.get("left1"), 
              'left2': dados.get("left2"), 
              'left3': dados.get("left3"), 
              'left4': dados.get("left4"), 
              'right1': dados.get("right1"), 
              'right2': dados.get("right2"), 
              'right3': dados.get("right3"), 
              'right4': dados.get("right4")
    }

    if maquina_estado["posto_1"] == 0:
        #Atualiza cor dos retangulos
        for i in range(4):
            if pacote[f"left{i+1}"] == None:
                await muda_cor_retan(f"left{i+1}", "white")

            elif pacote[f"left{i+1}"] == peca[i]:
                await muda_cor_retan(f"left{i+1}", "green")

            elif pacote[f"left{i+1}"] != peca[i]:
                await muda_cor_retan(f"left{i+1}", "red")

        #Condição para proxima etapa
        if pacote["left1"] == peca[0] and pacote["left2"] == peca[1] and pacote["left3"] == peca[2] and pacote["left4"] == peca[3]:
            await muda_etapa(1)
            for i in range(4):
                await desabilita_retan(f"left{i+1}")
            await habilita_retan("right1", peca[0].capitalize(), "white")
            await habilita_retan("left1", peca[0].capitalize(), "green")

            maquina_estado["posto_1"] = 1

    elif maquina_estado["posto_1"] == 1:
        i = 1
        if pacote[f"left{i}"] == None:
            await muda_cor_retan(f"left{i}", "white")
        elif pacote[f"left{i}"] == peca[i-1]:
            await muda_cor_retan(f"left{i}", "green")
        elif pacote[f"left{i}"] != peca[i-1]:
            await muda_cor_retan(f"left{i}", "red")
        
        if pacote[f"right{i}"] == None:
            await muda_cor_retan(f"right{i}", "white")
        elif pacote[f"right{i}"] == peca[i-1]:
            await muda_cor_retan(f"right{i}", "green")
        elif pacote[f"right{i}"] != peca[i-1]:
            await muda_cor_retan(f"right{i}", "red")

        if pacote["right1"] == peca[0] and pacote["left2"] == peca[1] and pacote["left3"] == peca[2] and pacote["left4"] == peca[3]:
            await muda_etapa(i+1)
            await desabilita_retan(f"left{i}")
            await desabilita_retan(f"right{i}")

            await habilita_retan(f"right{i+1}", "Estrela", "white")
            await habilita_retan(f"left{i+1}", "Estrela", "green")

            maquina_estado["posto_1"] = i+1
    
    elif maquina_estado["posto_1"] == 2:
        i = 2
        if pacote[f"left{i}"] == None:
            await muda_cor_retan(f"left{i}", "white")
        elif pacote[f"left{i}"] == peca[i-1]:
            await muda_cor_retan(f"left{i}", "green")
        elif pacote[f"left{i}"] != peca[i-1]:
            await muda_cor_retan(f"left{i}", "red")
        
        if pacote[f"right{i}"] == None:
            await muda_cor_retan(f"right{i}", "white")
        elif pacote[f"right{i}"] == peca[i-1]:
            await muda_cor_retan(f"right{i}", "green")
        elif pacote[f"right{i}"] != peca[i-1]:
            await muda_cor_retan(f"right{i}", "red")

        if pacote["right1"] == peca[0] and pacote["right2"] == peca[1] and pacote["left3"] == peca[2] and pacote["left4"] == peca[3]:
            await muda_etapa(i+1)
            await desabilita_retan(f"left{i}")
            await desabilita_retan(f"right{i}")

            await habilita_retan(f"right{i+1}", peca[i].capitalize(), "white")
            await habilita_retan(f"left{i+1}", peca[i].capitalize(), "green")

            maquina_estado["posto_1"] = i+1

    elif maquina_estado["posto_1"] == 3:
        i = 3
        if pacote[f"left{i}"] == None:
            await muda_cor_retan(f"left{i}", "white")
        elif pacote[f"left{i}"] == peca[i-1]:
            await muda_cor_retan(f"left{i}", "green")
        elif pacote[f"left{i}"] != peca[i-1]:
            await muda_cor_retan(f"left{i}", "red")
        
        if pacote[f"right{i}"] == None:
            await muda_cor_retan(f"right{i}", "white")
        elif pacote[f"right{i}"] == peca[i-1]:
            await muda_cor_retan(f"right{i}", "green")
        elif pacote[f"right{i}"] != peca[i-1]:
            await muda_cor_retan(f"right{i}", "red")

        if pacote["right1"] == peca[0] and pacote["right2"] == peca[1] and pacote["right3"] == peca[2] and pacote["left4"] == peca[3]:
            await muda_etapa(i+1)
            await desabilita_retan(f"left{i}")
            await desabilita_retan(f"right{i}")

            await habilita_retan(f"right{i+1}", peca[i].capitalize(), "white")
            await habilita_retan(f"left{i+1}", peca[i].capitalize(), "green")

            maquina_estado["posto_1"] = i+1

    elif maquina_estado["posto_1"] == 4:
        i = 4
        if pacote[f"left{i}"] == None:
            await muda_cor_retan(f"left{i}", "white")
        elif pacote[f"left{i}"] == peca[i-1]:
            await muda_cor_retan(f"left{i}", "green")
        elif pacote[f"left{i}"] != peca[i-1]:
            await muda_cor_retan(f"left{i}", "red")
        
        if pacote[f"right{i}"] == None:
            await muda_cor_retan(f"right{i}", "white")
        elif pacote[f"right{i}"] == peca[i-1]:
            await muda_cor_retan(f"right{i}", "green")
        elif pacote[f"right{i}"] != peca[i-1]:
            await muda_cor_retan(f"right{i}", "red")

        if pacote["right1"] == peca[0] and pacote["right2"] == peca[1] and pacote["right3"] == peca[2] and pacote["right4"] == peca[3]:
            await muda_etapa(i+1, timer=False)
            await desabilita_retan(f"left{i}")
            for i in range(4):
                await habilita_retan(f"right{i+1}", peca[i].capitalize(), "white")

            maquina_estado["posto_1"] = 5

    elif maquina_estado["posto_1"] == 5:
        for i in range(4):
            if pacote[f"right{i+1}"] == None:
                await muda_cor_retan(f"right{i+1}", "green")
            elif pacote[f"right{i+1}"] == peca[i]:
                await muda_cor_retan(f"right{i+1}", "white")
            elif pacote[f"right{i+1}"] != peca[i]:
                await muda_cor_retan(f"right{i+1}", "red")

        if pacote["right1"] == None and pacote["right2"] == None and pacote["right3"] == None and pacote["right4"] == None:
            sistema_ativo["ativo"] = False
            maquina_estado["posto_1"] = 0

            imagem = {"acao": "mostrar_imagem", "titulo": ""}

            for ws in connections:
                await ws.send_text(json.dumps(imagem))

            mensagem = {
                "acao": "reinicia_Digital_Dash",
            }

            # Enviar JSON para todos os clientes conectados
            for conn in connections:
                try:
                    await conn.send_text(json.dumps(mensagem))
                except Exception as e:
                    print("Erro ao enviar mensagem:", e)

            
    return {"status": "visao processada"}

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
    ref_x_montagem = 700
    ref_y_montagem = 200

    ref_x_organiza = 100
    ref_y_organiza = 200

    largura_peca = 225
    distancia_x = 250
    distancia_y = 300

    x = [400, 100, 1500, ref_x_organiza, ref_x_organiza+distancia_x, ref_x_organiza, ref_x_organiza+distancia_x, ref_x_montagem, ref_x_montagem+distancia_x, ref_x_montagem, ref_x_montagem+distancia_x, ref_x_montagem-60]
    y = [700, 700, 700, ref_y_organiza, ref_y_organiza, ref_y_organiza+distancia_y, ref_y_organiza+distancia_y, ref_y_montagem, ref_y_montagem, ref_y_montagem+distancia_y, ref_y_montagem+distancia_y, ref_y_montagem-50]
    largura = [1100, 300, 300, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, 590]
    altura = [200, 200, 200, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, largura_peca, 590]
    texto = ['Console', 'Left', 'Rigth', 'Quadrado', 'Estrela', 'Triângulo', 'Hexágono', 'Quadrado', 'Decágono', 'Triângulo', 'Hexágono', 'Base']
    id = ['Console', 'Left', 'Rigth', 'left1', 'left2', 'left3', 'left4', 'right1', 'right2', 'right3', 'right4', 'proxy']
    mostra = [False, False, False, True, True, True, True, False, False, False, False, True]

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

    await muda_etapa(0)

async def muda_etapa(etapa, erro=False, timer=True):
    mensagem = {
            "acao": "mensagem",
            "etapa": etapa,
            "posto": f"Posto 1",
            "texto": f"{instrucoes[etapa]}",
            "posicao": "top-right",
            "mostrar_timer": timer,
            "erro": erro}

    for conn in connections:
        try:
            await conn.send_text(json.dumps(mensagem))
        except Exception as e:
            print("Erro ao enviar mensagem:", e)
    
    imagem = {"acao": "mostrar_imagem", "src": f"/static/img/etapa{etapa}.png", "titulo": f"Etapa {etapa}"}
    for ws in connections:
            await ws.send_text(json.dumps(imagem))

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