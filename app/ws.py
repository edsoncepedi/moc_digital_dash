import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from app import state  # Importa o estado compartilhado

fronts: list[WebSocket] = []

async def ws_front(ws: WebSocket):
    await ws.accept()
    fronts.append(ws)
    print(f"🟢 FRONT conectado. Total: {len(fronts)}")
    try:
        while True:
            await ws.receive_text() # Mantém vivo
    except:
        pass
    finally:
        if ws in fronts: fronts.remove(ws)

# Loop de Broadcast para o Projetor
async def overlay_sender():
    print("🚀 Loop de Broadcast Iniciado")
    while True:
        await asyncio.sleep(0.033) # 30 FPS

        # Pega o dado do arquivo state.py (que foi atualizado pelo POST)
        payload = state.get_frame()
        
        if not fronts or not payload:
            continue

        texto = json.dumps(payload)
        
        # Envia para todos os projetores
        tarefas = [ws.send_text(texto) for ws in fronts]
        resultados = await asyncio.gather(*tarefas, return_exceptions=True)

        for ws, res in zip(fronts.copy(), resultados):
            if isinstance(res, Exception):
                if ws in fronts: fronts.remove(ws)