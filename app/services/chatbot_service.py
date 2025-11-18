import os
import google.generativeai as genai


class ChatbotService:

    def __init__(self, model_name="gemini-2.5-pro"):
        """
        Serviço responsável por conversar com o modelo Gemini.
        """
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise EnvironmentError("API Key do Gemini não encontrada. Configure GEMINI_API_KEY no .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def responder(self, pergunta: str) -> str:
        """
        Gera uma resposta do modelo Gemini baseado na pergunta do usuário.
        """
        if not pergunta or not pergunta.strip():
            raise ValueError("A pergunta não pode estar vazia.")

        try:
            resposta = self.model.generate_content(pergunta)
            return resposta.text.strip() if resposta and resposta.text else ""
        except Exception as e:
            # O controller decide como exibir
            raise RuntimeError(f"Erro ao processar a pergunta no Gemini: {str(e)}")
