FROM python:3.11-slim

# Variáveis de ambiente para otimização
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala pacotes do sistema necessários
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    libssl-dev \
    libffi-dev \
    netcat-openbsd \
    && apt-get clean

# Copia o requirements.txt e instala as dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do projeto (inclui o entrypoint.sh)
COPY . .
COPY entrypoint.sh .
# Dá permissão de execução para o entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["sh", "./entrypoint.sh"]