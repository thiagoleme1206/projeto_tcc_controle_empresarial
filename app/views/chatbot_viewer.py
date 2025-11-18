import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from app.services.chatbot_service import ChatbotService
import threading

class ChatbotViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("🤖 Chatbot - Gemini")
        self.master.geometry("600x500")
        self.centralizar_janela(600, 500)

        self.chatbot = ChatbotService()
        self.create_widgets()

    def centralizar_janela(self, largura, altura):
        """Centraliza a janela na tela."""
        self.master.update_idletasks()
        largura_tela = self.master.winfo_screenwidth()
        altura_tela = self.master.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.master.geometry(f"{largura}x{altura}+{x}+{y}")

    def create_widgets(self):
        # Título
        titulo = ttk.Label(self.master, text="🤖 Chatbot com Gemini", font=("Helvetica", 16, "bold"))
        titulo.pack(pady=10)

        # Área de conversa (scrolled)
        self.text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=20, font=("Helvetica", 11))
        self.text_area.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.text_area.insert(tk.END, "Digite sua pergunta abaixo e pressione 'Enviar'.\n\n")
        self.text_area.config(state=tk.DISABLED)

        # Entrada de texto
        self.entry = ttk.Entry(self.master, width=80)
        self.entry.pack(padx=20, pady=(5, 10))
        self.entry.bind("<Return>", lambda event: self.enviar_pergunta())

        # Botões
        botoes_frame = ttk.Frame(self.master)
        botoes_frame.pack(pady=5)

        btn_enviar = ttk.Button(botoes_frame, text="Enviar", command=self.enviar_pergunta)
        btn_enviar.grid(row=0, column=0, padx=10)

        btn_voltar = ttk.Button(botoes_frame, text="Voltar", command=self.master.destroy)
        btn_voltar.grid(row=0, column=1, padx=10)

    def enviar_pergunta(self):
        pergunta = self.entry.get().strip()
        if not pergunta:
            return

        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, f"🗨️ Você: {pergunta}\n")
        self.text_area.insert(tk.END, f"🤖 Chatbot: Digitando...\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

        self.entry.delete(0, tk.END)
        self.entry.config(state=tk.DISABLED)

        # Desabilita botão de enviar
        for widget in self.master.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child["text"] == "Enviar":
                        child.config(state=tk.DISABLED)

        self.digitando_index = self.text_area.index("end-2l")
        threading.Thread(target=self.gerar_resposta_em_thread, args=(pergunta,), daemon=True).start()

    def gerar_resposta_em_thread(self, pergunta):
        try:
            resposta = self.chatbot.responder(pergunta)
        except Exception as e:
            resposta = f"❌ Erro: {e}"
        self.text_area.after(0, lambda: self.exibir_resposta(resposta))

    def exibir_resposta(self, resposta):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(self.digitando_index, f"{self.digitando_index} lineend + 1c")
        self.text_area.insert(self.digitando_index, f"🤖 Chatbot: {resposta}\n\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)
        self.entry.config(state=tk.NORMAL)

        # Reabilita botão de enviar
        for widget in self.master.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button) and child["text"] == "Enviar":
                        child.config(state=tk.NORMAL)
