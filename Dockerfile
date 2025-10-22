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
# 📦 Dependências do sistema
# ==============================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ==============================================
# 📂 Diretório de trabalho
# ==============================================
WORKDIR /app

# ==============================================
# 📋 Instala dependências Python
# ==============================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==============================================
# 🧩 Copia o restante do projeto
# ==============================================
COPY . .

# ==============================================
# 🔥 Expõe a porta
# ==============================================
EXPOSE 5000

# ==============================================
# 🚀 Comando para iniciar o servidor
# OBS: main.py está dentro da pasta app
# ==============================================
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
