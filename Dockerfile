# Usar uma imagem base com Python
FROM python:3.11-slim-bookworm

# Instalar Java 17 (Necessário para o Lavalink v4) e dependências do sistema
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos de dependências
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Expor a porta do Web App (55555 ou a que você configurou)
EXPOSE 55555

# Comando para rodar o bot
CMD ["python", "-u", "main.py"]
