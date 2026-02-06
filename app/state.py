_frames = {}
_mensagens = {}
_estados = {}

# -------- ESTADOS --------
def get_estado(posto_id: int):
    return _estados.get(posto_id, "INICIO")

def set_estado(posto_id: int, estado: str):
    _estados[posto_id] = estado

def mudou_estado(posto_id: int, novo_estado: str) -> bool:
    antigo = get_estado(posto_id)
    if antigo != novo_estado:
        _estados[posto_id] = novo_estado
        return True
    return False

# -------- FRAMES --------

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
    if get_frame(posto_id):
        objetos_corretos = get_frame(posto_id).get("retangulos", [])
        objetos_incorretos = get_frame(posto_id).get("unassigned", [])

        objetos = list()

        for obj in objetos_corretos:
            obj["cor"] = "#ffffff"
            objetos.append(obj)
        for obj in objetos_incorretos:
            obj["cor"] = "#ff0000"
            objetos.append(obj)
    
    overlay = {
        "acao": "overlay_update",
        "retangulos": objetos if get_frame(posto_id) else [],
        "mensagem": get_mensagem(posto_id)
    }
    return overlay

def reset_posto(posto_id: int):
    _frames.pop(posto_id, None)
    _mensagens.pop(posto_id, None)

    # se você tiver estados
    if "_estados" in globals():
        _estados.pop(posto_id, None)
