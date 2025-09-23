import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import ConfigManager
from providers import ModelProvider, VectorStoreProvider, ChatHistoryProvider
from agent_manager import AgentService

def create_app():
    """
    Cria e configura a instância da aplicação Flask.
    """
    app = Flask(__name__)
    CORS(app)

    conversational_chain = None
    try:
        # 1. Instanciar ConfigManager
        config = ConfigManager()
        genai.configure(api_key=config.get_google_api_key())

        # 2. Instanciar Provedores
        model_provider = ModelProvider(config)
        vectorstore_provider = VectorStoreProvider(model_provider)
        history_provider = ChatHistoryProvider(config)

        # 3. Obter dependências para o AgentService
        llm = model_provider.get_llm()
        retriever = vectorstore_provider.get_retriever()

        # 4. Instanciar AgentService com injeção de dependência
        agent_service = AgentService(llm, retriever, history_provider)
        
        # 5. Criar a cadeia conversacional
        conversational_chain = agent_service.create_chain()
        
        print("✅ Agente pronto para receber perguntas.")

    except Exception as e:
        print(f"❌ Erro fatal durante a inicialização: {e}")
        # A variável conversational_chain permanecerá None

    # --- Definição das Rotas da API ---
    @app.route('/chat', methods=['POST'])
    def chat():
        """
        Endpoint para receber perguntas e retornar respostas do agente.
        """
        if not conversational_chain:
            return jsonify({"error": "O agente não foi inicializado corretamente. Verifique os logs do servidor."}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "A requisição deve conter um corpo JSON."}), 400

        required_fields = ['question', 'session_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_message = f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"
            return jsonify({"error": error_message}), 400

        question = data.get('question')
        session_id = data.get('session_id')

        try:
            response = conversational_chain.invoke(
                {"input": question},
                config={"configurable": {"session_id": session_id}}
            )
            return jsonify({"answer": response['answer']})

        except Exception as e:
            print(f"Erro ao invocar a cadeia RAG: {e}")
            return jsonify({"error": "Ocorreu um erro ao processar sua pergunta."}), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Endpoint de verificação de saúde.
        """
        if conversational_chain:
            return jsonify({"status": "ok", "message": "FestoTech Assistant está operacional."}), 200
        else:
            return jsonify({"status": "error", "message": "FestoTech Assistant não está operacional."}), 500
            
    return app

# --- Execução do Servidor ---
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)