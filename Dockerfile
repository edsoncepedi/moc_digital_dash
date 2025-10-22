# ==============================================
# 🐍 Imagem base leve do Python
# ==============================================
FROM python:3.12-slim

# ==============================================
# 🌍 Configurações de ambiente
# ==============================================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ==============================================
# 📦 Instala dependências do sistema (se necessário)
# ==============================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ==============================================
# 📂 Diretório de trabalho dentro do container
# ==============================================
WORKDIR /app

# ==============================================
# 📋 Copia o arquivo de dependências e instala
# ==============================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================
# 🧩 Copia o restante do projeto
# ==============================================
COPY . .

# ==============================================
# 🔥 Expõe a porta padrão do FastAPI/Uvicorn
# ==============================================
EXPOSE 5000

# ==============================================
# 🚀 Comando padrão para iniciar o servidor
# ==============================================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
