from app.services.utils import normalizar_componente
from threading import Lock
import json
import time

_lock = Lock()

_frames = {}
_mensagens = {}
_estados = {}

# controle de histerese
_mensagem_candidata = {}
_mensagem_ts = {}

# tempo necessário para aceitar troca de mensagem
TEMPO_HISTERESE_MENSAGEM = 0.25  # segundos


# -------------------------------------------------
# utilitário para comparar mensagens
# -------------------------------------------------

def _mensagem_key(mensagem):
    if mensagem is None:
        return None

    try:
        return json.dumps(mensagem, sort_keys=True, ensure_ascii=False)
    except Exception:
        return str(mensagem)


# -------------------------------------------------
# ESTADOS
# -------------------------------------------------

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


# -------------------------------------------------
# FRAMES
# -------------------------------------------------

def set_frame(posto_id: int, dados: dict):
    with _lock:
        _frames[posto_id] = dados


def get_frame(posto_id: int):
    return _frames.get(posto_id)


# -------------------------------------------------
# MENSAGEM COM HISTERESE
# -------------------------------------------------

def set_mensagem(posto_id: int, mensagem):

    agora = time.monotonic()

    with _lock:

        atual = _mensagens.get(posto_id)

        key_atual = _mensagem_key(atual)
        key_nova = _mensagem_key(mensagem)

        # mesma mensagem -> nada muda
        if key_atual == key_nova:
            _mensagem_candidata.pop(posto_id, None)
            _mensagem_ts.pop(posto_id, None)
            return

        candidata = _mensagem_candidata.get(posto_id)

        # nova candidata
        if candidata is None or _mensagem_key(candidata) != key_nova:

            _mensagem_candidata[posto_id] = mensagem
            _mensagem_ts[posto_id] = agora
            return

        # candidata já existe -> verificar tempo
        if agora - _mensagem_ts.get(posto_id, agora) >= TEMPO_HISTERESE_MENSAGEM:

            _mensagens[posto_id] = mensagem
            _mensagem_candidata.pop(posto_id, None)
            _mensagem_ts.pop(posto_id, None)


def get_mensagem(posto_id: int):
    return _mensagens.get(posto_id)


def clear_mensagem(posto_id: int):
    set_mensagem(posto_id, None)


# -------------------------------------------------
# PROCESSAMENTO DE OBJETOS
# -------------------------------------------------

def _processar_objetos(lista, cor, posto_id):

    objetos = []

    for obj in lista:

        texto = obj["texto"].lower()

        if "hand" in texto:
            obj["mostra"] = False
            continue

        if posto_id == 2 and ("cpu" in texto or "fan" in texto):
            obj["mostra"] = False
            continue

        obj["cor"] = cor
        obj["texto"] = normalizar_componente(obj["texto"])

        objetos.append(obj)

    return objetos


# -------------------------------------------------
# OVERLAY
# -------------------------------------------------

def get_overlay(posto_id: int):

    objetos = []

    frame = get_frame(posto_id)

    if frame:

        objetos += _processar_objetos(
            frame.get("retangulos", []),
            "#ffffff",
            posto_id
        )

        objetos += _processar_objetos(
            frame.get("unassigned", []),
            "#ff0000",
            posto_id
        )

    mensagem = get_mensagem(posto_id)

    return {
        "acao": "overlay_update",
        "retangulos": objetos,
        "mensagem": mensagem
    }


# -------------------------------------------------
# RESET
# -------------------------------------------------

def reset_posto(posto_id: int):

    with _lock:

        _frames.pop(posto_id, None)
        _mensagens.pop(posto_id, None)
        _estados.pop(posto_id, None)

        _mensagem_candidata.pop(posto_id, None)
        _mensagem_ts.pop(posto_id, None)