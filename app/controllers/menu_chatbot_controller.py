# app/controllers/menu_chatbot_controller.py

from app.services.chatbot_service import ChatbotService

def menu_chatbot(usuario):
    chatbot = ChatbotService()

    print("\n=== 🤖 Chatbot com Gemini ===")
    print("Digite sua pergunta ou 'sair' para voltar ao menu.")

    while True:
        pergunta = input("\n🗨️ Você: ").strip()
        if pergunta.lower() in ["sair", "0"]:
            break

        resposta = chatbot.responder(pergunta)
        print(f"\n🤖 Chatbot:\n{resposta}")
