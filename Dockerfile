# --- ESTÁGIO 1: BUILDER ---
# Este estágio instala dependências e baixa modelos necessários.
FROM python:3.12-slim-bookworm AS builder

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema (se necessário)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências Python em um ambiente virtual dentro do builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Baixa os dados necessários do NLTK
RUN python -m nltk.downloader punkt

# Copia os scripts necessários (removendo a construção do índice neste estágio)
COPY providers.py .
COPY config.py .

# --- ESTÁGIO 2: FINAL ---
# Este estágio cria a imagem final, otimizada para produção.
FROM python:3.12-slim-bookworm

# Define variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Cria um usuário não-root para executar a aplicação
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Copia o ambiente virtual com as dependências do estágio builder
COPY --from=builder /opt/venv /opt/venv

# Copia o código da aplicação
COPY app.py .
COPY agent_manager.py .
COPY config.py .
COPY providers.py .

# Copia o índice FAISS pré-construído do diretório local
COPY ./faiss_index ./faiss_index

# Expõe a porta que o Gunicorn irá usar
EXPOSE 8000

# Comando para iniciar a aplicação em produção com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:create_app()"]
