import os
import dotenv

dotenv.load_dotenv()

class ConfigManager:
    """
    Gerencia o carregamento e o acesso a configurações a partir de variáveis de ambiente.
    """
    def __init__(self):
        self._google_api_key = os.getenv("GOOGLE_API_KEY")
        self._redis_url = os.getenv("REDIS_URL")

    def get_google_api_key(self) -> str:
        """
        Retorna a GOOGLE_API_KEY. Lança um ValueError se não estiver definida.
        """
        if not self._google_api_key:
            raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
        return self._google_api_key

    def get_redis_url(self) -> str:
        """
        Retorna a REDIS_URL. Lança um ValueError se não estiver definida.
        """
        if not self._redis_url:
            raise ValueError("A variável de ambiente REDIS_URL não foi definida.")
        return self._redis_url
