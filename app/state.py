# Variável global compartilhada
# Armazena o último frame processado pelo YOLO
frames = {}

def set_frame(posto_id: int, dados: dict):
    frames[posto_id] = dados

def get_frame(posto_id: int):
    # Retorna o frame do posto ou None se não existir
    return frames.get(posto_id)