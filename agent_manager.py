import os
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_redis import RedisChatMessageHistory
import dotenv

dotenv.load_dotenv()

class AgentManager:
    """
    Gerencia a inicialização e a lógica do agente conversacional RAG.
    """
    def __init__(self):
        """
        Inicializa os modelos, embeddings e o vectorstore.
        """
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if not self.google_api_key:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
        
        genai.configure(api_key=self.google_api_key)

        print("Inicializando modelos...")
        # Modelo de Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            api_key=self.google_api_key
        )

        # Modelo de Chat (LLM)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.2,
        )

        print("Carregando índice FAISS local...")
        try:
            self.vectorstore = FAISS.load_local(
                "faiss_index", 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            self.retriever = self.vectorstore.as_retriever()
            print("Índice carregado com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar o índice FAISS: {e}")
            raise

    def get_chat_history(self, session_id: str) -> RedisChatMessageHistory:
        """
        Retorna uma instância de RedisChatMessageHistory para o ID da sessão.
        """
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("A variável de ambiente REDIS_URL não foi definida.")
        
        # Força uma mudança estrutural para o reloader do Flask
        history_kwargs = {
            "session_id": session_id,
            "redis_url": redis_url
        }
        return RedisChatMessageHistory(**history_kwargs)

    def get_conversational_chain(self) -> RunnableWithMessageHistory:
        """
        Constrói e retorna a cadeia RAG completa com gerenciamento de histórico.
        """
        # 1. Prompt para reescrever a pergunta do usuário com base no histórico
        contextualize_q_system_prompt = (
            "Dada uma conversa e uma última pergunta que pode se referir ao contexto da conversa, "
            "formule uma pergunta independente que possa ser entendida sem a conversa. "
            "NÃO responda à pergunta, apenas reformule-a se necessário e, caso contrário, retorne-a como está."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )

        # 2. Prompt principal para responder à pergunta com base no contexto recuperado
        qa_system_prompt = """
            ## Persona
            Você é o "NewSon", um assistente de IA especialista na Estação de Manipulação Pneumática Festo, que faz parte de um sistema de Digital Twin. Seu propósito é fornecer suporte técnico rápido e preciso para operadores e técnicos de manutenção.

            ## Contexto Fixo do Sistema
            A estação física que você monitora é uma Estação de Manipulação Pneumática da Festo. Lembre-se sempre de sua composição principal:
            - A estação possui dois atuadores pneumáticos principais que realizam as tarefas.
            - **1. Atuador de Avanço:** É identificado como `Atuador_Redondo`. Fisicamente, é um cilindro redondo do modelo **DSNU**.
            - **2. Atuador de Fixação:** É identificado como `Atuador_Quadrado`. Fisicamente, é um cilindro padrão do modelo **DSBC**.
            - **Controle:** Cada atuador é controlado por uma **Válvula Direcional 5/2 vias** (identificadas como V1 e V2).
            - **Monitoramento:** O estado de cada atuador (se está avançado ou recuado) é detectado por **sensores de fim de curso** magnéticos (1S1, 1S2, 2S1, 2S2).

            ## Regras de Resposta
            1.  **Use o Contexto Fixo:** Sempre leve em conta a composição da estação descrita acima para contextualizar suas respostas.
            2.  **Foco Técnico:** Responda exclusivamente a perguntas sobre o hardware, operação e manutenção do sistema pneumático. Suas respostas devem ser diretas, objetivas e baseadas estritamente no `Contexto Adicional` recuperado e no `Contexto Fixo do Sistema`.
            3.  **Precisão é Prioridade:** Se a informação não estiver disponível nos contextos fornecidos, declare que você não possui essa informação. Não especule.
            4.  **Cite as Fontes:** Ao usar uma informação, sempre que possível, referencie o documento de origem.
            5.  **Evite Tópicos de Software:** NUNCA discuta o desenvolvimento ou a arquitetura de software do Digital Twin. Se perguntado, diga que sua especialidade é o sistema pneumático físico.

            ## Tarefa
            Com base no `Contexto Fixo do Sistema` e no `Contexto Adicional` recuperado dos documentos técnicos, responda a `Pergunta` do usuário.

            **Contexto Adicional:**
            {context}

            **Pergunta:**
            {input}

            **Resposta Técnica:**
            """
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        # 3. Construir a cadeia que combina os documentos recuperados
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        # 4. Juntar tudo na cadeia RAG final
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        # 5. Envolver a cadeia com o gerenciador de histórico
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.get_chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        
        return conversational_rag_chain
