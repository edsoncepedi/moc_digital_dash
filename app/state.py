from app.services.utils import normalizar_componente, processar_objetos_visao
from threading import Lock

_lock = Lock()

_frames = {}
_mensagens = {}
_estados = {}

# -------- ESTADOS --------
def get_estado(posto_id: int):
    return _estados.get(posto_id, "INICIO")

def set_estado(posto_id: int, estado: str):
    with _lock:
        _estados[posto_id] = estado

def mudou_estado(posto_id: int, novo_estado: str) -> bool:
    with _lock:
        antigo = _estados.get(posto_id, "INICIO")
        if antigo != novo_estado:
            _estados[posto_id] = novo_estado
            return True
    return False

# -------- FRAMES --------

def set_frame(posto_id: int, dados: dict):
    with _lock:
        _frames[posto_id] = dados

def get_frame(posto_id: int):
    return _frames.get(posto_id)

# -------- MENSAGENS --------

def set_mensagem(posto_id: int, mensagem: dict):
    with _lock:
        _mensagens[posto_id] = mensagem

def get_mensagem(posto_id: int):
    return _mensagens.get(posto_id)

def clear_mensagem(posto_id: int):
    with _lock:
        _mensagens.pop(posto_id, None)

def get_overlay(posto_id: int):
    """
    Retorna o payload completo para o overlay, incluindo frame e mensagem.
    """
    objetos = []

    frame = get_frame(posto_id)

    if frame:
        objetos += processar_objetos_visao(
            frame.get("retangulos", []),
            "#ffffff",
            posto_id
        )

        objetos += processar_objetos_visao(
            frame.get("unassigned", []),
            "#ff0000",
            posto_id
        )
    
    mensagem = get_mensagem(posto_id)

    overlay = {
        "acao": "overlay_update",
        "retangulos": objetos,
        "mensagem": mensagem
    }
    return overlay

def reset_posto(posto_id: int):
    with _lock:
        _frames.pop(posto_id, None)
        _mensagens.pop(posto_id, None)
        _estados.pop(posto_id, None)
