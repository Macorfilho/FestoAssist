# FestoTech Assistant ("NewSon")

## Visão Geral

O **FestoTech Assistant**, apelidado de **"NewSon"**, é um assistente de IA especialista na Estação de Manipulação Pneumática da Festo, projetado para atuar como o cérebro de um sistema de **Digital Twin**. Em ambientes industriais, tempo é dinheiro. Quando um operador precisa de uma informação crítica, ele não pode perder tempo folheando manuais. O NewSon resolve esse problema, fornecendo respostas rápidas e precisas, baseadas em documentos técnicos, para garantir a eficiência e a segurança da operação.

Utilizando uma arquitetura de **Geração Aumentada por Recuperação (RAG)**, o assistente garante que cada resposta seja extraída diretamente de uma base de conhecimento confiável (documentos PDF da Festo), eliminando o risco de informações incorretas ou "alucinações" da IA.

## Arquitetura

A aplicação é construída como uma API RESTful, combinando tecnologias de ponta para oferecer uma solução robusta e especializada.

-   **API Backend:** **Flask** serve como a espinha dorsal da aplicação, expondo endpoints como `/chat`.
-   **Orquestração de IA:** **LangChain** é o cérebro da operação. Ele gerencia o fluxo de dados e integra os componentes. Uma característica chave é o **prompt de sistema**, que define a persona "NewSon" e injeta um **contexto fixo** sobre a composição do hardware da estação (atuadores, válvulas, sensores), garantindo que o assistente sempre conheça o sistema que monitora.
-   **Modelo de Linguagem (LLM):** **Google Gemini (`gemini-2.5-pro`)** é o motor de geração de linguagem, responsável por compreender as perguntas e formular respostas coesas, seguindo as regras estritas de sua persona. O `embedding-001` é usado para a vetorização dos documentos.
-   **Banco de Dados Vetorial:** **FAISS** armazena os embeddings dos documentos técnicos, permitindo buscas de similaridade semântica em alta velocidade para encontrar o contexto relevante para a pergunta do usuário.
-   **Memória da Conversa:** **Redis** atua como uma memória de curto prazo, armazenando o histórico de cada sessão de chat para manter o contexto em conversas contínuas.

## Fluxo de Execução

1.  **Recebimento da Pergunta:** O usuário envia uma pergunta para o endpoint `/chat` via API.
2.  **Recuperação do Histórico:** O LangChain recupera o histórico da conversa associado à sessão do Redis.
3.  **Busca na Base Vetorial:** A pergunta é usada para consultar o índice FAISS, que retorna os trechos de documentos mais relevantes.
4.  **Geração Aumentada:** Os trechos recuperados, o histórico da conversa e a pergunta original são combinados em um *prompt* otimizado. Este prompt inclui a **persona "NewSon"** e o **contexto fixo do sistema**, garantindo que a resposta seja técnica e contextualizada.
5.  **Geração da Resposta:** O *prompt* é enviado ao Google Gemini, que gera uma resposta seguindo as regras definidas (foco técnico, sem especulação, etc.).
6.  **Atualização do Histórico:** A nova interação é salva no Redis.
7.  **Retorno ao Usuário:** A resposta final é enviada de volta ao usuário em formato JSON.

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
'{    "question": "Qual é o diâmetro do êmbolo do atuador DSNU-12-70-P-A?",    "session_id": "user123_session456"
}'
```

### Exemplo de Resposta

```json
{
  "answer": "O diâmetro do êmbolo do atuador DSNU-12-70-P-A é de 12 mm."
}
```

## Como Contribuir

Contribuições são bem-vindas! Siga os passos abaixo:

1.  **Fork o repositório.**
2.  **Crie uma branch:** `git checkout -b feature/sua-feature`.
3.  **Faça suas alterações.**
4.  **Faça o commit:** `git commit -m 'feat: Adiciona nova funcionalidade' `.
5.  **Envie para o seu fork:** `git push origin feature/sua-feature`.
6.  **Abra um Pull Request.**

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
