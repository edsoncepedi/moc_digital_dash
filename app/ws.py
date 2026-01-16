import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from json import JSONDecodeError

# Lista de projetores conectados
fronts: list[WebSocket] = []

# Variável Global (Último estado válido)
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
            # Mantém conexão viva
            await ws.receive_text()
    except (WebSocketDisconnect, Exception):
        pass
    finally:
        print("❌ FRONT desconectou")
        if ws in fronts:
            fronts.remove(ws)

# ===============================
# BORDA (O YOLO) - VERSÃO BLINDADA
# ===============================
async def ws_borda(ws: WebSocket):
    global ultimo_estado
    await ws.accept()
    print("🟢 BORDA conectada")

    try:
        while True:
            try:
                # 1. Tenta receber o dado
                data = await ws.receive_json()

                # 2. Verifica se é um PING (ignora se for)
                if isinstance(data, dict) and data.get("acao") == "ping":
                    continue

                # 3. Validação básica (opcional, mas recomendada)
                if not isinstance(data, dict):
                    print(f"⚠️ Formato inválido recebido: {type(data)}")
                    continue

                # 4. Atualiza o estado global
                ultimo_estado = data

            except JSONDecodeError:
                print("⚠️ Erro: JSON inválido recebido (ignorado)")
                continue
            except KeyError as e:
                print(f"⚠️ Erro: Chave faltando no JSON: {e}")
                continue
            except Exception as e:
                # O PULO DO GATO: Captura erro genérico mas NÃO SAI DO LOOP
                print(f"⚠️ Erro no processamento do frame: {e}")
                continue

    except WebSocketDisconnect:
        print("⚠️ BORDA desconectou (Normal)")
    except Exception as e:
        # Erro fatal de conexão (cai aqui se a rede cair de vez)
        print(f"❌ Erro CRÍTICO na conexão da BORDA: {e}")

# ===============================
# LOOP DE ENVIO (Broadcast)
# ===============================
async def overlay_sender():
    print("🚀 Loop de Broadcast Iniciado")
    while True:
        await asyncio.sleep(0.033) # ~30 FPS para o projetor

        if not fronts or not ultimo_estado:
            continue

        try:
            texto = json.dumps(ultimo_estado)
            
            # Envia para todos
            tarefas = [ws.send_text(texto) for ws in fronts]
            resultados = await asyncio.gather(*tarefas, return_exceptions=True)

            # Limpa mortos
            for ws, res in zip(fronts.copy(), resultados):
                if isinstance(res, Exception):
                    if ws in fronts: fronts.remove(ws)

        except Exception as e:
            print(f"Erro no loop de envio: {e}")
            await asyncio.sleep(1)