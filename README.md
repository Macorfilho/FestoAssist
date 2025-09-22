# FestoTech Assistant

## Visão Geral

O **FestoTech Assistant** é um assistente de IA especialista na Estação de Manipulação Pneumática da Festo. Seu propósito é fornecer suporte técnico rápido e preciso para operadores e técnicos de manutenção, respondendo a perguntas sobre hardware, operação e manutenção do sistema.

O assistente utiliza uma arquitetura de Geração Aumentada por Recuperação (RAG) para garantir que suas respostas sejam baseadas estritamente em uma base de conhecimento de documentos técnicos (PDFs), evitando especulações e garantindo precisão.

## Arquitetura

A aplicação é construída como uma API RESTful e utiliza um conjunto de tecnologias modernas para processamento de linguagem natural e gerenciamento de conversas:

-   **API Backend:** **Flask** é usado para criar o servidor web e expor os endpoints da API, como `/chat`.
-   **Orquestração de IA:** **LangChain** é o framework central que conecta todos os componentes. Ele gerencia a lógica de recuperação de informações, o histórico da conversa e a interação com o modelo de linguagem.
-   **Modelo de Linguagem (LLM):** **Google Gemini** (especificamente o modelo `gemini-1.5-flash`) é usado para entender as perguntas e gerar as respostas em linguagem natural. O `embedding-001` é usado para criar as representações vetoriais dos documentos.
-   **Banco de Dados Vetorial:** **FAISS (Facebook AI Similarity Search)** é utilizado para armazenar os embeddings dos documentos técnicos. Ele permite uma busca de similaridade semântica extremamente rápida para encontrar os trechos de texto mais relevantes para a pergunta do usuário.
-   **Memória da Conversa:** **Redis** é usado para armazenar o histórico de cada sessão de chat. Isso permite que o assistente mantenha o contexto da conversa, respondendo a perguntas de acompanhamento de forma coerente.

## Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto localmente.

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd FestoAssist
```

### 2. Criar Ambiente Virtual e Instalar Dependências

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar um ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto, copiando o arquivo de exemplo.

```bash
cp .env.example .env
```

Agora, edite o arquivo `.env` e adicione suas credenciais:

-   `GOOGLE_API_KEY`: Sua chave de API do Google para usar os modelos Gemini.
-   `REDIS_URL`: A URL de conexão para sua instância Redis. O valor padrão `redis://localhost:6379` funciona para uma instalação local padrão.

## Como Usar

A execução da aplicação é feita em duas etapas principais.

### 1. Construir o Banco de Dados Vetorial

Antes de iniciar o servidor, você precisa processar os PDFs da pasta `pdfs/` e construir o índice FAISS. Execute o seguinte script:

```bash
python build_vectorstore.py
```

Este comando irá ler os documentos, dividi-los em trechos, gerar os embeddings e salvar o índice na pasta `faiss_index/`. Você só precisa executar este script uma vez ou sempre que os documentos PDF forem atualizados.

### 2. Iniciar o Servidor Flask

Com o índice criado, inicie a API:

```bash
python app.py
```

O servidor estará rodando em `http://localhost:8000`.

## Uso da API

Para interagir com o assistente, envie uma requisição `POST` para o endpoint `/chat`.

### Exemplo com `curl`

```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d 
'{
    "question": "Qual é o diâmetro do êmbolo do atuador DSNU-12-70-P-A?",
    "session_id": "user123_session456"
}'
```

-   `question`: A pergunta que você deseja fazer ao assistente.
-   `session_id`: Um identificador único para a sessão da conversa. O histórico será associado a este ID.

### Exemplo de Resposta

A API retornará uma resposta em formato JSON:

```json
{
  "answer": "O diâmetro do êmbolo do atuador DSNU-12-70-P-A é de 12 mm."
}
```
