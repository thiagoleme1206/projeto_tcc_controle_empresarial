# app/services/chatbot_service.py

import google.generativeai as genai
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        api_key = "AIzaSyAMeZSDlajssXRZVmH7FkTpDzbn3cSqzf8"

        if not api_key:
            raise Exception("❌ API KEY do Gemini não encontrada. Configure no .env como GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")

    def responder(self, pergunta):
        try:
            resposta = self.model.generate_content(pergunta)
            return resposta.text.strip()
        except Exception as e:
            return f"❌ Erro ao processar a pergunta: {e}"
