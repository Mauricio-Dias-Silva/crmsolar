# ==============================================================================
# DOCKERFILE PADRÃO (PYTHONJET)
# ==============================================================================
FROM python:3.11-slim

# Otimizações
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT 8080

WORKDIR /app

# Instalação de dependências de sistema (A "Vacina" para erros)
# Suporte para: PostgreSQL, Imagens (Pillow), Criptografia e Compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libssl-dev \
    openssl \
    libffi-dev \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalação de pacotes Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o código e prepara a inicialização
COPY . .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["sh", "./entrypoint.sh"]