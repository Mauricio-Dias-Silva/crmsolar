# ==============================================================================
# DOCKERFILE PADRÃO PARA PROJETOS DJANGO (PYTHONJET)
# ==============================================================================
FROM python:3.11-slim

# Otimizações do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT 8080

WORKDIR /app

# 1. Instalação de Dependências de Sistema (A "Vacina" para erros de build)
# Inclui suporte para Postgres (libpq), Imagens (libjpeg/zlib) e Criptografia (ssl/ffi)
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

# 2. Instalação de Dependências do Projeto
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 3. Cópia do Código
COPY . .

# 4. Preparação do Script de Inicialização
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# 5. Exposição da Porta
EXPOSE 8080

# 6. Comando de Entrada
ENTRYPOINT ["sh", "./entrypoint.sh"]
