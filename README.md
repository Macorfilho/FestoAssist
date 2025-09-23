# FestoTech Assistant ("NewSon")

## Visão Geral

O **FestoTech Assistant**, apelidado de **"NewSon"**, é um assistente de IA especialista na Estação de Manipulação Pneumática da Festo, projetado para atuar como o cérebro de um sistema de **Digital Twin**. Ele fornece respostas técnicas rápidas e precisas, baseadas em documentos, para operadores e técnicos de manutenção.

Utilizando uma arquitetura de **Geração Aumentada por Recuperação (RAG)**, o assistente garante que cada resposta seja extraída diretamente de uma base de conhecimento confiável (documentos PDF da Festo), eliminando o risco de informações incorretas ou "alucinações" da IA.

## Arquitetura de Software (SOLID)

A aplicação foi refatorada para seguir os princípios **SOLID**, resultando em um design desacoplado, modular e de fácil manutenção. A inicialização ocorre no `app.py` através do padrão **Application Factory**, que compõe a aplicação injetando as dependências necessárias.

-   **`app.py` (Camada de Composição e API)**
    -   Utiliza **Flask** para expor uma API RESTful (`/chat`, `/health`).
    -   Atua como o "contêiner de injeção de dependência": instancia todos os componentes (provedores, serviços) e os conecta na inicialização.

-   **`config.py` (Camada de Configuração)**
    -   `ConfigManager`: Centraliza o carregamento e o acesso a todas as configurações e variáveis de ambiente (`GOOGLE_API_KEY`, `REDIS_URL`), garantindo que a gestão de configurações seja isolada.

-   **`providers.py` (Camada de Provedores de Recursos)**
    -   `ModelProvider`: Responsável por inicializar e fornecer instâncias dos modelos de linguagem (LLM e Embeddings) do Google Gemini.
    -   `VectorStoreProvider`: Gerencia o carregamento do banco de dados vetorial **FAISS** e fornece o `retriever` para busca de documentos.
    -   `ChatHistoryProvider`: Gerencia a conexão com o **Redis** e fornece o mecanismo de histórico de conversas.

-   **`agent_manager.py` (Camada de Serviço/Lógica de Negócio)**
    -   `AgentService`: Orquestra a lógica de negócio principal. Recebe suas dependências (LLM, retriever, provedor de histórico) via injeção de dependência. Sua única responsabilidade é construir e executar a cadeia RAG conversacional usando **LangChain**.

## Fluxo de Execução

1.  **Inicialização (`app.py`)**: A aplicação é iniciada, e a função `create_app` instancia o `ConfigManager`, os `Providers` e, finalmente, o `AgentService`, injetando todas as dependências.
2.  **Requisição de Chat**: Um usuário envia uma pergunta para o endpoint `/chat`.
3.  **Execução da Cadeia (`AgentService`)**: O `AgentService` utiliza as dependências injetadas para executar a cadeia RAG:
    a.  O `ChatHistoryProvider` recupera o histórico da conversa do Redis.
    b.  O `VectorStoreProvider` (via `retriever`) busca os documentos relevantes no FAISS.
    c.  O `ModelProvider` (via `llm`) gera uma resposta com base na pergunta, no histórico e nos documentos recuperados.
4.  **Resposta da API**: A resposta gerada é retornada ao usuário.

## Configuração do Ambiente

Siga os passos abaixo para configurar e executar o projeto localmente.

### 1. Pré-requisitos

-   Python 3.9 ou superior
-   Docker (para executar o Redis)

### 2. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd FestoAssist
```

### 3. Criar Ambiente Virtual e Instalar Dependências

```bash
# Criar um ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt
```

### 4. Iniciar o Redis com Docker

```bash
docker run -d -p 6379:6379 --name redis-festo redis
```

### 5. Configurar Variáveis de Ambiente

Crie um arquivo `.env` a partir do exemplo.

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas credenciais:

-   `GOOGLE_API_KEY`: Sua chave de API do Google.
-   `REDIS_URL`: Se você usou o comando Docker acima, o valor padrão `redis://localhost:6379` já está correto.

## Como Usar

### 1. Construir o Banco de Dados Vetorial

Antes de iniciar o servidor, processe os PDFs da pasta `pdfs/`:

```bash
python build_vectorstore.py
```

### 2. Iniciar o Servidor Flask

Com o índice criado e o Redis rodando, inicie a API:

```bash
python app.py
```

O servidor estará disponível em `http://localhost:8000`.

## Uso da API

Envie uma requisição `POST` para o endpoint `/chat`.

### Exemplo com `curl`

```bash
curl -X POST http://localhost:8000/chat \
-H "Content-Type: application/json" \
-d 
'{    "question": "Qual é o diâmetro do êmbolo do atuador DSNU?",    "session_id": "user123_session456"
}'
```

### Exemplo de Resposta

```json
{
  "answer": "O diâmetro do êmbolo do atuador DSNU pode variar. De acordo com a documentação, existem modelos com diâmetros de 8, 10, 12, 16, 20 e 25 mm."
}
```

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.