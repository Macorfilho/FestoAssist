import os
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_redis import RedisChatMessageHistory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredMarkdownLoader
import nltk
from config import ConfigManager

class ModelProvider:
    """
    Fornece instâncias dos modelos de linguagem (LLM e Embeddings).
    """
    def __init__(self, config: ConfigManager):
        """
        Inicializa o provedor de modelos com uma instância de ConfigManager.

        Args:
            config: A instância do gerenciador de configurações.
        """
        self.config = config
        self._embeddings = None
        self._llm = None

    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """
        Retorna uma instância do modelo de embeddings, inicializando-a se necessário.
        """
        if self._embeddings is None:
            print("Inicializando modelo de Embeddings...")
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001", 
                api_key=self.config.get_google_api_key()
            )
        return self._embeddings

    def get_llm(self) -> ChatGoogleGenerativeAI:
        """
        Retorna uma instância do modelo de chat (LLM), inicializando-a se necessário.
        """
        if self._llm is None:
            print("Inicializando modelo de Chat (LLM)...")
            self._llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.2,
                api_key=self.config.get_google_api_key()
            )
        return self._llm

class VectorStoreProvider:
    """
    Carrega o VectorStore e fornece um retriever. Constrói o índice automaticamente se não existir.
    """
    def __init__(self, model_provider: ModelProvider, index_path: str = "faiss_index", documents_path: str = "pdfs"):
        """
        Inicializa o provedor de vector store.

        Args:
            model_provider: A instância do provedor de modelos.
            index_path: O caminho para o diretório do índice FAISS.
            documents_path: O caminho para o diretório dos documentos.
        """
        self.model_provider = model_provider
        self.index_path = index_path
        self.documents_path = documents_path
        self._retriever = None

    def _load_document(self, file_path):
        """Carrega um único documento com base na sua extensão."""
        try:
            if file_path.suffix == ".pdf":
                loader = PyMuPDFLoader(str(file_path))
            elif file_path.suffix == ".md":
                loader = UnstructuredMarkdownLoader(str(file_path))
            else:
                return None  # Ignora arquivos não suportados

            print(f"Carregando: {file_path.name}")
            return loader.load()
        except Exception as e:
            print(f"Erro ao carregar {file_path.name}: {e}")
            return None

    def _load_documents_from_folders(self, paths):
        """
        Carrega documentos PDF e Markdown de uma lista de diretórios.
        """
        all_docs = []
        for folder_path in paths:
            path = Path(folder_path)
            if not path.exists():
                print(f"Aviso: O diretório '{folder_path}' não foi encontrado.")
                continue

            for file_path in path.glob("**/*"):  # Usar **/* para buscar em subdiretórios
                if file_path.is_file():
                    docs = self._load_document(file_path)
                    if docs:
                        all_docs.extend(docs)

        return all_docs

    def _build_and_save_vectorstore(self):
        """
        Função principal para construir e salvar o índice FAISS.
        """
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            print(f"Aviso: Não foi possível baixar dados NLTK: {e}")

        # --- 1. Carregar todos os documentos ---
        print("\n--- Iniciando carregamento de documentos ---")
        document_folders = [self.documents_path]
        docs = self._load_documents_from_folders(document_folders)

        if not docs:
            raise ValueError("Nenhum documento encontrado. Verifique se os arquivos estão no diretório correto.")

        print(f"\nTotal de páginas/documentos carregados: {len(docs)}")

        # --- 2. Dividir os documentos em chunks ---
        print("\n--- Dividindo documentos em chunks ---")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)
        print(f"Total de chunks criados: {len(splits)}")

        # --- 3. Inicializar o modelo de Embeddings ---
        print("\n--- Inicializando modelo de embeddings da Google ---")
        embeddings = self.model_provider.get_embeddings()

        # --- 4. Criar e salvar o índice FAISS ---
        print("\n--- Construindo o índice vetorial FAISS (isso pode levar alguns minutos) ---")
        vectorstore = FAISS.from_documents(splits, embeddings)
        vectorstore.save_local(self.index_path)
        print(f"Índice FAISS salvo com sucesso no diretório '{self.index_path}'.")

    def get_retriever(self):
        """
        Carrega o índice FAISS e retorna um retriever.
        """
        if self._retriever is None:
            index_path = Path(self.index_path)
            if not index_path.exists() or not index_path.is_dir():
                raise FileNotFoundError(
                    f"O diretório do índice FAISS não foi encontrado em '{self.index_path}'. "
                    "Certifique-se de que o índice foi construído e está no local correto antes de iniciar a aplicação."
                )

            print(f"Carregando índice FAISS local de '{self.index_path}'...")
            try:
                embeddings = self.model_provider.get_embeddings()
                vectorstore = FAISS.load_local(
                    self.index_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                self._retriever = vectorstore.as_retriever()
                print("Índice carregado com sucesso.")
            except Exception as e:
                print(f"Erro ao carregar o índice FAISS: {e}")
                raise
        return self._retriever

class ChatHistoryProvider:
    """
    Fornece o mecanismo de histórico de chat.
    """
    def __init__(self, config: ConfigManager):
        """
        Inicializa o provedor de histórico de chat.

        Args:
            config: A instância do gerenciador de configurações.
        """
        self.config = config

    def get_history(self, session_id: str) -> RedisChatMessageHistory:
        """
        Cria e retorna uma instância de RedisChatMessageHistory para um ID de sessão.
        """
        return RedisChatMessageHistory(
            session_id=session_id,
            redis_url=self.config.get_redis_url()
        )
