import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from app import state  # Importa o estado compartilhado

conexoes = {}

async def ws_front(ws: WebSocket, posto_id: int):
    await ws.accept()

    if posto_id not in conexoes:
        conexoes[posto_id] = []
    
    conexoes[posto_id].append(ws)
    print(f"🟢 Cliente conectado no CANAL DO POSTO {posto_id}")

    try:
        while True:
            await ws.receive_text() # Mantém vivo (Heartbeat)
    except:
        pass
    finally:
        # Remove da lista ao desconectar
        if posto_id in conexoes and ws in conexoes[posto_id]:
            conexoes[posto_id].remove(ws)
            print(f"🔴 Cliente desconectado do POSTO {posto_id}")

# Loop de Broadcast para o Projetor
async def overlay_sender():
    print("🚀 Sistema Multi-Posto Iniciado")
    while True:
        await asyncio.sleep(0.033) # 30 FPS

        for posto_id, lista_sockets in conexoes.items():
            if not lista_sockets:
                continue

            # Pega o dado do arquivo state.py (que foi atualizado pelo POST)
            payload = state.get_frame(posto_id)
            if not payload:
                continue
            
            # 2. Envia APENAS para os projetores daquele posto
            texto = json.dumps(payload)
            tarefas = [ws.send_text(texto) for ws in lista_sockets]
            if tarefas:
                # Dispara em paralelo e ignora erros de envio
                await asyncio.gather(*tarefas, return_exceptions=True)
"""
            resultados = await asyncio.gather(*tarefas, return_exceptions=True)

            for ws, res in zip(fronts.copy(), resultados):
                if isinstance(res, Exception):
                    if ws in fronts: fronts.remove(ws)"""