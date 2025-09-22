import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from agent_manager import AgentManager
import dotenv

dotenv.load_dotenv()

# --- 1. Inicialização do App Flask e do Agente ---
app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir requisições do frontend

try:
    # Instancia o gerenciador do agente uma vez na inicialização
    agent_manager = AgentManager()
    conversational_chain = agent_manager.get_conversational_chain()
    print("✅ Agente pronto para receber perguntas.")
except Exception as e:
    print(f"❌ Erro fatal durante a inicialização: {e}")
    # Se o agente não puder ser inicializado, as rotas retornarão erro.
    agent_manager = None
    conversational_chain = None

# --- 2. Definição das Rotas da API ---
@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint para receber perguntas e retornar respostas do agente.
    """
    if not conversational_chain:
        return jsonify({"error": "O agente não foi inicializado corretamente. Verifique os logs do servidor."}), 500

    data = request.get_json()
    if not data or 'question' not in data or 'session_id' not in data:
        return jsonify({"error": "A requisição deve conter 'question' e 'session_id'."}), 400

    question = data.get('question')
    session_id = data.get('session_id')

    try:
        # Invoca a cadeia com a pergunta e o ID da sessão para manter o histórico
        response = conversational_chain.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )
        
        # A resposta do RunnableWithMessageHistory está na chave 'answer'
        return jsonify({"answer": response['answer']})

    except Exception as e:
        print(f"Erro ao invocar a cadeia RAG: {e}")
        return jsonify({"error": "Ocorreu um erro ao processar sua pergunta."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de verificação de saúde.
    """
    if agent_manager and conversational_chain:
        return jsonify({"status": "ok", "message": "FestoTech Assistant está operacional."}), 200
    else:
        return jsonify({"status": "error", "message": "FestoTech Assistant não está operacional."}), 500

# --- 3. Execução do Servidor ---
if __name__ == "__main__":
    # Para desenvolvimento, use o servidor Flask.
    # Para produção, use um servidor WSGI como Gunicorn:
    # gunicorn --bind 0.0.0.0:8000 app:app
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
