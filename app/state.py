# Variável global compartilhada
# Armazena o último frame processado pelo YOLO
ultimo_frame = {
    "acao": "overlay_update",
    "retangulos": []
}

def set_frame(dados):
    global ultimo_frame
    ultimo_frame = dados

def get_frame():
    return ultimo_frame