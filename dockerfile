# Dockerfile
# Use uma imagem base Python com ferramentas de desenvolvimento
FROM python:3.11-slim

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT 8080

WORKDIR /app

# Instala pacotes do sistema necessários para:
# 1. build-essential (para compilação)
# 2. libpq-dev (para psycopg2-binary/PostgreSQL)
# 3. libjpeg-dev/zlib1g-dev (para Pillow/imagens)
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements.txt e instala as dependências Python
# Esta etapa AGORA deve funcionar, desde que você tenha removido 'mysqlclient'
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto (inclui o entrypoint.sh)
COPY . .

# Dá permissão de execução para o entrypoint.sh
RUN chmod +x entrypoint.sh

# A porta que o Gunicorn vai ouvir. O Cloud Run precisa da porta 8080.
EXPOSE 8080

# Define o ponto de entrada para o nosso script
ENTRYPOINT ["sh", "./entrypoint.sh"]
