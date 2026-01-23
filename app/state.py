# Estado dos frames (já existe)
_frames = {}

# NOVO: estado das mensagens por posto
_mensagens = {}

def set_frame(posto_id: int, dados: dict):
    _frames[posto_id] = dados

def get_frame(posto_id: int):
    return _frames.get(posto_id)

# -------- MENSAGENS --------

def set_mensagem(posto_id: int, mensagem: dict):
    """
    Exemplo de mensagem:
    {
        "texto": "Objeto incorreto",
        "nivel": "erro",
        "timeout": 3000
    }
    """
    _mensagens[posto_id] = mensagem

def get_mensagem(posto_id: int):
    return _mensagens.get(posto_id)

def clear_mensagem(posto_id: int):
    _mensagens.pop(posto_id, None)

def get_overlay(posto_id: int):
    """
    Retorna o payload completo para o overlay, incluindo frame e mensagem.
    """
    overlay = {
        "acao": "overlay_update",
        "retangulos": get_frame(posto_id)["retangulos"] if get_frame(posto_id) else [],
        "mensagem": get_mensagem(posto_id)
    }
    return overlay