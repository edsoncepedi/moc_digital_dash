#!/bin/bash

# =========================
# CONFIGURAÇÕES
# =========================
CONTAINER_NAME="servidor_fastapi_digi"
IMAGE_NAME="moc_digital_dash"
IMAGE_TAG="latest"
PORT_HOST=5000
PORT_CONTAINER=5000

# =========================
# PARAR CONTAINER (SE EXISTIR)
# =========================
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Parando container $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME
fi

# =========================
# REMOVER CONTAINER (SE EXISTIR)
# =========================
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🗑️ Removendo container $CONTAINER_NAME..."
    docker rm $CONTAINER_NAME
fi

# =========================
# REMOVER IMAGEM (SE EXISTIR)
# =========================
if [ "$(docker images -q $IMAGE_NAME:$IMAGE_TAG)" ]; then
    echo "🗑️ Removendo imagem $IMAGE_NAME:$IMAGE_TAG..."
    docker rmi $IMAGE_NAME:$IMAGE_TAG
fi

# =========================
# BUILD DA NOVA IMAGEM
# =========================
echo "🔨 Buildando nova imagem..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

if [ $? -ne 0 ]; then
    echo "❌ Erro no build da imagem. Abortando."
    exit 1
fi

# =========================
# SUBIR NOVO CONTAINER
# =========================
echo "🚀 Subindo novo container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT_HOST:$PORT_CONTAINER \
    -v $(pwd)/configs:/app/configs \
    -e CONFIG_DIR=/app/configs \
    --restart always \
    $IMAGE_NAME:$IMAGE_TAG

echo "✅ Deploy concluído com sucesso!"
