# NewSon – Assistente Conversacional IA para Automação Industrial

## Sumário

- [Visão Geral](#-visão-geral)
- [Contexto & Integração](#-contexto--integração)
- [Funcionalidades Principais](#-funcionalidades-principais)
- [Arquitetura](#-arquitetura)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura de Diretórios](#-estrutura-de-diretórios)
- [Configuração do Ambiente](#-configuração-do-ambiente)
- [Como Executar](#-como-executar)
- [API e Endpoints](#-api-e-endpoints)
- [Eventos Socket.IO](#-eventos-socketio)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Pipeline RAG](#-pipeline-rag)
- [Melhorias Futuras](#-melhorias-futuras)
- [Contribuição](#-contribuição)
- [Autores](#-autores)
- [Licença](#-licença)

---

## Visão Geral

**NewSon** é o **Assistente Conversacional IA** oficial do projeto [festo-digital-twin](https://github.com/Macorfilho/festo-digital-twin). Desenvolvido como módulo especializado, o NewSon oferece **interação em linguagem natural** para usuários do sistema de gêmeo digital, permitindo:

- ✅ Consultas técnicas e explicações sobre equipamentos Festo
- ✅ Assistência em resolução de problemas e troubleshooting
- ✅ Interpretação de alertas e eventos do sistema
- ✅ Orientações sobre manutenção preventiva e corretiva
- ✅ Análise de históricos de sensores e equipamentos
- ✅ Suporte ao usuário 24/7 via chat integrado

O NewSon utiliza **Retrieval-Augmented Generation (RAG)** para fornecer respostas contextualizadas baseadas em documentação técnica da Festo, históricos do sistema e conhecimento de domínio industrial.

---

## Contexto & Integração

### Relação com Festo Digital Twin

Este repositório é um **módulo dedicado** do projeto [festo-digital-twin](https://github.com/Macorfilho/festo-digital-twin), responsável especificamente pela camada de **inteligência conversacional**.

```
festo-digital-twin (Projeto Principal)
├── Backend (Flask/Python) - API REST
├── Frontend (React/TypeScript) - Interface
├── Simulation - Simuladores de sensores
├── Database (MySQL) - Dados
└── NewSon (Este repositório) ← Assistente IA
    ├── Chat API
    ├── RAG Pipeline
    └── LLM Integration
```

### Integração com Sistema Principal

O NewSon se integra ao gêmeo digital através de:

1. **Autenticação JWT**: Usa os mesmos tokens do sistema principal
2. **WebSocket**: Comunicação em tempo real via Socket.IO
3. **API REST**: Endpoints RESTful para chat e contexto
4. **Acesso a Dados**: Lê dados do banco MySQL do projeto pai via APIs protegidas
5. **Notificações**: Integração com sistema de alertas para contexto

```
┌──────────────────────────┐
│   Interface Frontend      │
│   (Chat Component)       │
└────────────┬─────────────┘
             │
      [Socket.IO / HTTP]
             │
     ┌───────▼──────────┐
     │   NewSon API     │
     │   (Este repo)    │
     └───────┬──────────┘
             │
    ┌────────┴──────────┐
    │                   │
┌───▼─────┐      ┌──────▼─────┐
│ Backend  │      │ RAG        │
│ Principal│      │ Pipeline   │
└──────────┘      └──────┬─────┘
                         │
                  ┌──────▼──────┐
                  │ LLM/GenAI   │
                  │ (OCI, OpenAI)
                  └─────────────┘
```

---

## Funcionalidades Principais

### 1. Chat Interativo em Tempo Real

- Conversa fluida com contexto de sessão
- Suporte a múltiplas linguagens (PT-BR, EN)
- Histórico de conversas armazenado e recuperável
- Indicadores de typing e status

**Exemplo**:

```
Usuário: "O que significa o alerta 'Temperature High' no sensor 03?"
NewSon: "O sensor de temperatura 03, vinculado ao equipamento Compressor Principal,
        detectou leitura acima do threshold de 75°C. Recomenda-se verificar o sistema
        de refrigeração. Último registro: 78.5°C às 14:30 de hoje."
```

### 2. Busca Contextualizada com RAG

- Recupera documentação técnica relevante
- Integra informações do banco de dados do gêmeo digital
- Busca em manuais PDF, articles, e históricos
- Ranking de relevância automático

### 3. Assistência com Alertas

- Explica alertas ativos do sistema
- Sugere ações corretivas baseadas em regras
- Recupera histórico de alertas similares
- Propõe manutenção preventiva

### 4. Troubleshooting e Diagnostics

- Guias passo-a-passo para resolução de problemas
- Perguntas esclarecedoras para diagnóstico
- Recomendações de ações baseadas em padrões históricos
- Integração com dados de manutenção

### 5. Análise de Dados e Métricas

- Interpretação de gráficos e séries temporais
- Resumo de performance de equipamentos
- Previsões baseadas em tendências
- Relatórios de saúde do sistema

### 6. Base de Conhecimento Integrada

- Manuais técnicos Festo (PDFs)
- Documentação de configuração
- Casos de sucesso e best practices
- FAQ do sistema

---

## Arquitetura

### Componentes Principais

```
┌──────────────────────────────────────────────────┐
│          CAMADA DE APRESENTAÇÃO                  │
│  ┌────────────────────────────────────────────┐ │
│  │   Chat Interface (React Component)         │ │
│  │  • Message rendering                       │ │
│  │  • Input handling                          │ │
│  │  • Real-time notifications                 │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
                    ↕ WebSocket/HTTP
┌──────────────────────────────────────────────────┐
│       CAMADA DE SERVIÇO (NewSon API)             │
│  ┌────────────────────────────────────────────┐ │
│  │  FastAPI Application                       │ │
│  │  • Chat endpoints                          │ │
│  │  • Session management                      │ │
│  │  • Auth middleware (JWT)                   │ │
│  └────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │  Context Manager                           │ │
│  │  • User context                            │ │
│  │  • Conversation history                    │ │
│  │  • Equipment/sensor context                │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
                    ↕
┌──────────────────────────────────────────────────┐
│        CAMADA DE INTELIGÊNCIA (RAG)              │
│  ┌────────────────────────────────────────────┐ │
│  │  RAG Pipeline                              │ │
│  │  • Query embedding                         │ │
│  │  • Similarity search                       │ │
│  │  • Context assembly                        │ │
│  │  • Prompt engineering                      │ │
│  └────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │  Vector Database                           │ │
│  │  • Document embeddings                     │ │
│  │  • Knowledge base indexes                  │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
                    ↕
┌──────────────────────────────────────────────────┐
│    CAMADA DE MODELOS & INTEGRAÇÕES              │
│  ┌────────────────────────────────────────────┐ │
│  │  LLM Integration                           │ │
│  │  • OpenAI / Claude / Gemini               │ │
│  │  • OCI Generative AI                       │ │
│  │  • Ollama (modelos locais)                 │ │
│  └────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │  External APIs                             │ │
│  │  • Festo Digital Twin Backend              │ │
│  │  • Embedding services                      │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
```

---

## Tecnologias Utilizadas

### Backend

| Tecnologia          | Versão | Propósito                |
| ------------------- | ------ | ------------------------ |
| **Python**          | 3.10+  | Linguagem principal      |
| **FastAPI**         | 0.100+ | Framework web assíncrono |
| **Uvicorn**         | 0.23+  | Servidor ASGI            |
| **Pydantic**        | 2.0+   | Validação de dados       |
| **python-socketio** | 5.10+  | WebSocket em tempo real  |
| **httpx**           | 0.24+  | Cliente HTTP assíncrono  |
| **PyJWT**           | 2.8+   | Validação de tokens JWT  |

### IA & NLP

| Tecnologia         | Propósito                       |
| ------------------ | ------------------------------- |
| **LangChain**      | Orquestração de RAG e LLM       |
| **OpenAI API**     | Embeddings e GPT (opcional)     |
| **OCI GenAI**      | Geração de texto (Oracle Cloud) |
| **Ollama**         | Modelos LLM locais              |
| **FAISS / Qdrant** | Vector database para embeddings |
| **PyPDF**          | Processamento de PDFs técnicos  |

### Banco de Dados

| Tecnologia    | Propósito                        |
| ------------- | -------------------------------- |
| **Redis**     | Cache de sessões e embeddings    |
| **MySQL**     | Histórico de conversas (via API) |
| **Vector DB** | Armazenamento de embeddings      |

### DevOps & Cloud

| Tecnologia        | Propósito              |
| ----------------- | ---------------------- |
| **Docker**        | Containerização        |
| **Oracle Cloud**  | Infraestrutura e GenAI |
| **python-dotenv** | Variáveis de ambiente  |

---

## Estrutura de Diretórios

```
NewSon/
│
├── app/                              # Código principal da aplicação
│   ├── __init__.py
│   ├── main.py                       # Entry point FastAPI
│   │
│   ├── api/                          # Rotas e endpoints
│   │   ├── __init__.py
│   │   ├── chat.py                   # Endpoints de chat
│   │   ├── context.py                # Gerenciar contexto de usuário
│   │   └── health.py                 # Health check
│   │
│   ├── services/                     # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── chat_service.py           # Orquestração do chat
│   │   ├── rag_service.py            # Pipeline RAG
│   │   ├── llm_service.py            # Integração com LLM
│   │   ├── embedding_service.py      # Geração de embeddings
│   │   └── context_service.py        # Gerenciar contexto
│   │
│   ├── models/                       # Modelos de dados (Pydantic)
│   │   ├── __init__.py
│   │   ├── chat.py                   # Mensagem, conversa
│   │   ├── context.py                # Contexto de usuário
│   │   └── response.py               # Formato de resposta
│   │
│   ├── integrations/                 # Integrações externas
│   │   ├── __init__.py
│   │   ├── openai_client.py          # Integração OpenAI
│   │   ├── oci_client.py             # Integração OCI GenAI
│   │   ├── ollama_client.py          # Integração Ollama
│   │   ├── festo_api_client.py       # Cliente do projeto pai
│   │   └── vector_db_client.py       # Cliente Vector DB
│   │
│   ├── rag/                          # Pipeline RAG
│   │   ├── __init__.py
│   │   ├── retriever.py              # Componente de busca
│   │   ├── ranker.py                 # Ranking de relevância
│   │   ├── prompt_builder.py         # Construção de prompts
│   │   └── knowledge_base.py         # Gerenciador KB
│   │
│   ├── utils/                        # Utilitários
│   │   ├── __init__.py
│   │   ├── logger.py                 # Logging configurado
│   │   ├── validators.py             # Validações
│   │   ├── jwt_helper.py             # Funções JWT
│   │   └── cache.py                  # Cache utilities
│   │
│   ├── config.py                     # Configurações da app
│   ├── dependencies.py               # Dependências compartilhadas
│   └── exceptions.py                 # Exceções customizadas
│
├── knowledge_base/                   # Base de conhecimento
│   ├── documents/                    # Documentos PDF/texto
│   │   ├── festo_manuals/
│   │   ├── technical_guides/
│   │   └── best_practices/
│   │
│   ├── embeddings/                   # Embeddings pré-processados
│   └── index_metadata.json           # Metadados dos índices
│
├── tests/                            # Testes automatizados
│   ├── test_chat_service.py
│   ├── test_rag_service.py
│   ├── test_api_endpoints.py
│   └── conftest.py
│
├── migrations/                       # Migrações de banco (se aplicável)
│   └── versions/
│
├── scripts/                          # Scripts utilitários
│   ├── ingest_documents.py           # Ingrir PDFs na KB
│   ├── build_embeddings.py           # Gerar embeddings iniciais
│   └── test_llm_connection.py        # Testar conexão LLM
│
├── docker/                           # Arquivos Docker
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/                             # Documentação
│   ├── architecture.md               # Documentação arquitetura
│   ├── rag_pipeline.md               # Pipeline RAG detalhado
│   ├── api_reference.md              # Referência de API
│   └── deployment.md                 # Guia de deployment
│
├── .env.example                      # Exemplo de variáveis
├── requirements.txt                  # Dependências Python
├── pyproject.toml                    # Configuração projeto
├── .dockerignore                     # Ignorar no Docker
├── .gitignore
├── README.md                         # Este arquivo
└── LICENSE                           # Licença do projeto
```

---

## Configuração do Ambiente

### Pré-requisitos

- **Python 3.10 ou superior** ([Download](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes - vem com Python)
- **Git** ([Download](https://git-scm.com/))
- Acesso à **API do projeto festo-digital-twin** (rodando localmente ou em produção)
- Chaves de API para serviços de LLM (OpenAI, OCI, etc.)

### Opcional (Recomendado)

- **Docker** - Para containerização
- **Ollama** - Para rodar modelos LLM localmente
- **Redis** - Para cache distribuído
- **Postman/Insomnia** - Para testes de API

### 1. Clone o Repositório

```bash
git clone https://github.com/Macorfilho/NewSon.git
cd NewSon
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Aplicação
FASTAPI_ENV=development
FASTAPI_PORT=5050
DEBUG=true

# JWT (usar do projeto pai ou gerar novo)
JWT_SECRET=sua-chave-secreta-aqui
JWT_ALGORITHM=HS256

# Conexão com Festo Digital Twin
FESTO_BACKEND_URL=http://localhost:5000
FESTO_API_KEY=token-ou-chave-acesso

# LLM - Escolher um (primário)
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Ou OCI GenAI
OCI_CONFIG_PATH=/path/to/oci/config
OCI_COMPARTMENT_ID=ocid1.compartment...

# Ou Ollama (local)
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Vector Database
VECTOR_DB_TYPE=faiss  # ou: qdrant, pinecone
VECTOR_DB_URL=http://localhost:6333  # Se usar Qdrant
PINECONE_API_KEY=...  # Se usar Pinecone

# Redis (opcional, para cache)
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/newson.log

# Embedding Service
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32
```

### 5. Preparar Base de Conhecimento

Ingerir documentos técnicos:

```bash
python scripts/ingest_documents.py \
  --source knowledge_base/documents \
  --vector-db faiss \
  --model sentence-transformers/all-MiniLM-L6-v2
```

Isso irá:

- Ler todos os PDFs em `knowledge_base/documents/`
- Fazer chunking do texto
- Gerar embeddings
- Indexar no vector database

---

## Como Executar

### Modo Desenvolvimento

```bash
# Certificar-se de que o ambiente virtual está ativo
source venv/bin/activate  # Linux/Mac

# Certificar-se de que festo-digital-twin está rodando em http://localhost:5000
# (ou ajustar FESTO_BACKEND_URL no .env)

# Iniciar NewSon
python -m app.main
```

Você verá:

```
INFO:     Uvicorn running on http://127.0.0.1:5050
INFO:     Application startup complete
```

Acesse:

- **Swagger UI**: http://localhost:5050/docs
- **ReDoc**: http://localhost:5050/redoc

### Modo Produção com Gunicorn

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:5050
```

### Com Docker

```bash
docker build -f docker/Dockerfile -t newson:latest .
docker run -p 5050:5050 --env-file .env newson:latest
```

Ou com docker-compose:

```bash
docker-compose -f docker/docker-compose.yml up
```

---

## API e Endpoints

### Base URL

```
http://localhost:5050/api
```

### Autenticação

Todos os endpoints requerem JWT token no header:

```
Authorization: Bearer <JWT_TOKEN>
```

---

### Chat Endpoints

#### POST `/api/chat/message`

Enviar mensagem e receber resposta IA.

**Request Body**:

```json
{
  "message": "Como resolver erro de stuck no atuador DSBC?",
  "context": {
    "equipment_id": 5,
    "sensor_id": 3,
    "alert_id": 12
  },
  "session_id": "user-session-uuid"
}
```

**Response** (200 OK):

```json
{
  "response": "Para resolver erros de stuck no atuador DSBC, recomenda-se...",
  "sources": [
    {
      "document": "Festo_DSBC_Manual.pdf",
      "page": 42,
      "relevance": 0.92
    }
  ],
  "actions": [
    {
      "action": "CHECK_PRESSURE",
      "description": "Verificar pressão de ar comprimido"
    }
  ],
  "confidence": 0.87,
  "timestamp": "2025-11-03T18:15:00Z"
}
```

---

#### GET `/api/chat/history/{session_id}`

Obter histórico de conversa.

**Query Parameters**:

- `limit` (opcional, padrão: 50): Número de mensagens
- `offset` (opcional, padrão: 0): Paginação

**Response** (200 OK):

```json
{
  "session_id": "user-session-uuid",
  "messages": [
    {
      "id": "msg-001",
      "role": "user",
      "content": "Como resolver erro de stuck?",
      "timestamp": "2025-11-03T18:10:00Z"
    },
    {
      "id": "msg-002",
      "role": "assistant",
      "content": "Para resolver...",
      "timestamp": "2025-11-03T18:10:15Z"
    }
  ],
  "total": 2
}
```

---

#### DELETE `/api/chat/history/{session_id}`

Limpar histórico de conversa.

**Response** (204 No Content)

---

### Knowledge Base Endpoints

#### GET `/api/knowledge/search`

Buscar na base de conhecimento.

**Query Parameters**:

- `query` (obrigatório): Termo de busca
- `limit` (opcional, padrão: 10): Resultados

**Response** (200 OK):

```json
{
  "query": "DSBC",
  "results": [
    {
      "document": "Festo_DSBC_Manual.pdf",
      "page": 42,
      "excerpt": "DSBC é um atuador pneumático...",
      "relevance": 0.95
    }
  ],
  "count": 1
}
```

---

#### POST `/api/knowledge/ingest`

Ingerir novo documento (admin only).

**Request Body**:

```json
{
  "file_url": "https://example.com/manual.pdf",
  "document_type": "manual",
  "tags": ["DSBC", "atuador", "pneumático"]
}
```

---

### Health Check

#### GET `/api/health`

Verificar status do serviço.

**Response** (200 OK):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-03T18:15:00Z",
  "services": {
    "llm": "connected",
    "vector_db": "connected",
    "festo_backend": "connected"
  }
}
```

---

## Eventos Socket.IO

### Conexão

**Evento**: `connect`

```javascript
socket.on("connect", () => {
  console.log("Conectado ao NewSon");
  socket.emit("authenticate", { token: JWT_TOKEN });
});
```

---

### Autenticação

**Evento**: `authenticate`

```javascript
socket.emit("authenticate", {
  token: "eyJ0eXAiOiJKV1QiLCJhbGc...",
});
```

**Resposta**: `authenticated`

```javascript
socket.on("authenticated", (data) => {
  console.log("Autenticado:", data.user);
});
```

---

### Chat em Tempo Real

**Enviar mensagem**: `chat_message`

```javascript
socket.emit("chat_message", {
  message: "Como está o compressor?",
  context: { equipment_id: 5 },
});
```

**Receber resposta**: `chat_response`

```javascript
socket.on("chat_response", (data) => {
  console.log("Resposta:", data.response);
});
```

---

### Typing Indicator

**Evento**: `typing`

```javascript
socket.on("typing", (data) => {
  console.log("NewSon está digitando...");
});
```

---

## Exemplos de Uso

### Exemplo 1: Chat Simples via REST

```bash
curl -X POST "http://localhost:5050/api/chat/message" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Qual é a pressão normal do compressor?",
    "session_id": "user-123"
  }'
```

**Resposta**:

```json
{
  "response": "A pressão normal de operação do compressor principal é 6.5 bar. Valores acima de 7 bar podem disparar alertas de alta pressão.",
  "sources": [
    {
      "document": "Festo_Compressor_Manual.pdf",
      "page": 15
    }
  ],
  "confidence": 0.94
}
```

---

### Exemplo 2: Chat com Contexto de Equipment

```python
import requests

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "message": "O que fazer com esse alerta?",
    "context": {
        "equipment_id": 5,
        "alert_id": 42,
        "alert_type": "TEMPERATURE_HIGH"
    }
}

response = requests.post(
    "http://localhost:5050/api/chat/message",
    headers=headers,
    json=payload
)

print(response.json()['response'])
```

**Saída esperada**:

```
Detecto que você tem um alerta de temperatura alta no equipamento ID 5.
Recomendações:
1. Verificar ventilação do equipamento
2. Limpar filtros de ar se necessário
3. Consultar histórico de manutenção para padrões
4. Se persistir, contatar técnico de manutenção
```

---

### Exemplo 3: Chat via Socket.IO (JavaScript)

```javascript
import io from "socket.io-client";

const socket = io("http://localhost:5050", {
  auth: {
    token: JWT_TOKEN,
  },
});

socket.on("connect", () => {
  console.log("Conectado!");
});

socket.on("authenticated", (data) => {
  console.log("Usuário autenticado:", data.user);

  // Enviar mensagem
  socket.emit("chat_message", {
    message: "Qual sensor está com problema?",
    context: { equipment_id: 7 },
  });
});

socket.on("typing", () => {
  console.log("NewSon está digitando...");
});

socket.on("chat_response", (data) => {
  console.log("Resposta:", data.response);
  console.log("Confiança:", data.confidence);
});
```

---

## Pipeline RAG

### Fluxo Completo

```
1. QUERY DO USUÁRIO
   "Como resolver stuck no DSBC?"
        ↓
2. EMBEDDING DA QUERY
   query_vector = embedding_model(query)
   # dimensão: 384D
        ↓
3. BUSCA NO VECTOR DB
   results = vector_db.similarity_search(
     query_vector,
     top_k=5
   )
   # Encontra 5 documentos mais similares
        ↓
4. RANKING
   ranked = ranker.rank(results)
   # Rearranja por relevância
        ↓
5. MONTAGEM DO CONTEXTO
   context = """
   Documento 1: "DSBC é um atuador..."
   Documento 2: "Para stuck, verificar..."
   Documento 3: "Pressão recomendada..."
   """
        ↓
6. CONSTRUÇÃO DO PROMPT
   prompt = f"""
   Você é um especialista em automação Festo.
   Contexto técnico: {context}
   Pergunta: {query}
   Responda com precisão e cite as fontes.
   """
        ↓
7. GERAÇÃO COM LLM
   response = llm(prompt)
   # OpenAI / OCI GenAI / Ollama
        ↓
8. RESPOSTA AO USUÁRIO
   {
     "response": "Para resolver stuck no DSBC...",
     "sources": [...],
     "confidence": 0.92
   }
```

### Configuração RAG

**Arquivo**: `app/rag/prompt_builder.py`

```python
SYSTEM_PROMPT = """
Você é NewSon, um assistente especialista em automação industrial Festo.
Suas características:
- Responda com precisão técnica
- Cite sempre as fontes de informação
- Seja conciso e prático
- Sugira ações quando apropriado
- Indique confiança da resposta (0-100%)
- Use português claro e profissional
"""

CHAT_TEMPLATE = """
Contexto técnico relevante:
{context}

Histórico da conversa:
{history}

Pergunta atual: {query}

Responda seguindo as instruções do sistema. Inclua confiança da resposta.
"""
```

---

## Melhorias Futuras

### Fase 1 - Aprimoramentos Imediatos

- [ ] Testes automatizados (pytest) para cobertura >80%
- [ ] Documentação interativa (Swagger detalhado)
- [ ] Logging estruturado com ELK
- [ ] Métricas e monitoramento (Prometheus)
- [ ] Rate limiting por usuário
- [ ] Cache inteligente de respostas

### Fase 2 - IA Avançada

- [ ] Fine-tuning de modelos com dados históricos
- [ ] Detecção de intenção customizada
- [ ] Multi-turn conversations com memory longo-termo
- [ ] Análise de sentimento do usuário
- [ ] Respostas multimodais (texto + imagem)
- [ ] Suporte a voice input/output

### Fase 3 - Recursos Industriais

- [ ] Integração com OPC UA
- [ ] Análise preditiva avançada
- [ ] Geração automática de relatórios
- [ ] Integração com sistemas ERP
- [ ] Suporte a múltiplos idiomas com qualidade
- [ ] Conformidade com regulações industriais

### Fase 4 - Edge & Performance

- [ ] Deployment em edge devices
- [ ] Quantização de modelos para latência <100ms
- [ ] Processamento offline-first
- [ ] Escalabilidade horizontal
- [ ] Multi-tenant support

---

## Contribuição

Este projeto faz parte do ecossistema [festo-digital-twin](https://github.com/Macorfilho/festo-digital-twin).

### Como Contribuir

1. **Fork** o repositório
2. **Crie uma branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra um Pull Request**

### Padrões de Código

- Use **type hints** em Python 3.10+
- Siga **PEP 8** para estilo
- Adicione **docstrings** em funções
- Escreva **testes** para novas features
- Mantenha **cobertura > 80%**

### Reportar Bugs

Abra uma [issue](https://github.com/Macorfilho/NewSon/issues) descrevendo:

- Comportamento esperado
- Comportamento observado
- Passos para reproduzir
- Ambiente (OS, Python version, etc.)

---

## Parceiros & Apoiadores

### FIAP

**Faculdade de Informática e Administração Paulista**

Instituição líder em educação tecnológica no Brasil, focada em formar profissionais para transformação digital e Indústria 4.0.

### Festo

**Festo Automação Ltda.**

Líder mundial em tecnologia de automação pneumática e elétrica, pioneira em soluções de Indústria 4.0.

- Website: [festo.com/br](https://www.festo.com/br)

---

**Desenvolvido com pelo grupo NewByte para FIAP × Festo**

</div>
