import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect

# Lista de projetores conectados
fronts: list[WebSocket] = []

# Variável Global (Substitui a Queue)
# Armazena apenas o último dado recebido.
ultimo_estado = None

# ===============================
# FRONT (O Projetor)
# ===============================
async def ws_front(ws: WebSocket):
    await ws.accept()
    fronts.append(ws)
    print(f"🟢 FRONT conectado. Total: {len(fronts)}")
    try:
        while True:
            # Mantém a conexão viva
            await ws.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        print("❌ FRONT desconectou")
        if ws in fronts:
            fronts.remove(ws)

# ===============================
# BORDA (O YOLO)
# ===============================
async def ws_borda(ws: WebSocket):
    global ultimo_estado
    await ws.accept()
    print("🟢 BORDA conectada")

    try:
        while True:
            # Recebe e sobrescreve imediatamente (Sem Fila = Sem Travamento)
            data = await ws.receive_json()
            ultimo_estado = data

    except WebSocketDisconnect:
        print("⚠️ BORDA desconectou (Normal)")
    except Exception as e:
        print(f"❌ Erro na conexão da BORDA: {e}")

# ===============================
# LOOP DE ENVIO (Broadcast)
# ===============================
async def overlay_sender():
    print("🚀 Loop de Broadcast Iniciado")
    while True:
        # Taxa de atualização do projetor (~30 FPS)
        await asyncio.sleep(0.033)

        if not fronts or not ultimo_estado:
            continue

        texto = json.dumps(ultimo_estado)

        # Envia para todos em paralelo
        tarefas = [ws.send_text(texto) for ws in fronts]
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)

        # Remove conexões mortas
        for ws, res in zip(fronts.copy(), resultados):
            if isinstance(res, Exception):
                if ws in fronts:
                    fronts.remove(ws)