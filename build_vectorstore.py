#!/usr/bin/env python3
import os
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredMarkdownLoader
import dotenv


# Carrega as variáveis de ambiente (necessário para a GOOGLE_API_KEY)
dotenv.load_dotenv()

# Configura a API Key do Gemini
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise KeyError
    genai.configure(api_key=GOOGLE_API_KEY)
    print("API Key do Gemini configurada com sucesso.")
except KeyError:
    print("Erro: A variável de ambiente GOOGLE_API_KEY não foi definida.")
    exit()

def _load_document(file_path):
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

def load_documents_from_folders(paths):
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
                docs = _load_document(file_path)
                if docs:
                    all_docs.extend(docs)
                
    return all_docs

def build_and_save_vectorstore():
    """
    Função principal para construir e salvar o índice FAISS.
    """
    # --- 1. Carregar todos os documentos ---
    print("\n--- Iniciando carregamento de documentos ---")
    # Adicione aqui todas as pastas que contêm seus documentos de conhecimento
    document_folders = ["pdfs/"] 
    docs = load_documents_from_folders(document_folders)
    
    if not docs:
        print("Nenhum documento encontrado. Abortando a criação do índice.")
        return
        
    print(f"\nTotal de páginas/documentos carregados: {len(docs)}")

    # --- 2. Dividir os documentos em chunks ---
    print("\n--- Dividindo documentos em chunks ---")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)
    print(f"Total de chunks criados: {len(splits)}")

    # --- 3. Inicializar o modelo de Embeddings ---
    print("\n--- Inicializando modelo de embeddings da Google ---")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=GOOGLE_API_KEY)

    # --- 4. Criar e salvar o índice FAISS ---
    print("\n--- Construindo o índice vetorial FAISS (isso pode levar alguns minutos) ---")
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local("faiss_index")
    print("Índice FAISS salvo com sucesso no diretório 'faiss_index'.")

if __name__ == "__main__":
    build_and_save_vectorstore()