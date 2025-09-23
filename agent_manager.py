import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from config import ConfigManager
from providers import ModelProvider, VectorStoreProvider, ChatHistoryProvider

class PromptFactory:
    """
    Cria e fornece os templates de prompt para a cadeia conversacional.
    """
    @staticmethod
    def create_contextualize_prompt() -> ChatPromptTemplate:
        contextualize_q_system_prompt = (
            "Dada uma conversa e uma última pergunta que pode se referir ao contexto da conversa, "
            "formule uma pergunta independente que possa ser entendida sem a conversa. "
            "NÃO responda à pergunta, apenas reformule-a se necessário e, caso contrário, retorne-a como está."
        )
        return ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

    @staticmethod
    def create_qa_prompt() -> ChatPromptTemplate:
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
        return ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

class AgentService:
    """
    Constrói a cadeia RAG conversacional a partir de dependências injetadas.
    """
    def __init__(self, llm, retriever, history_provider: ChatHistoryProvider):
        self.llm = llm
        self.retriever = retriever
        self.history_provider = history_provider
        self.prompt_factory = PromptFactory()

    def create_chain(self) -> RunnableWithMessageHistory:
        """
        Cria e retorna a cadeia RAG completa com gerenciamento de histórico.
        """
        contextualize_q_prompt = self.prompt_factory.create_contextualize_prompt()
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )

        qa_prompt = self.prompt_factory.create_qa_prompt()
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        return RunnableWithMessageHistory(
            rag_chain,
            self.history_provider.get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )