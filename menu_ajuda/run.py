import customtkinter
import tkinter as tk
from tkinter import ttk
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import google.generativeai as genai
import threading

# Configuração da API Gemini
genai.configure(api_key="AIzaSyAMeZSDlajssXRZVmH7FkTpDzbn3cSqzf8")
modelo_gemini = genai.GenerativeModel("gemini-2.5-pro")

# Baixa recursos do NLTK
nltk.download("punkt")

# ChatBot local
def chatbot_local(mensagem):
    respostas = {
        "lista": "No projeto lista materiais, podemos: "
        "\n"
        "\n ====Criar lista===="
        "\n » Montar a lista de materiais através de produtos já cadastrados no estoque."
        "\n » Logo após inserir a quantidade e o valor unitário que o produto está sendo vendido para o cliente e adicionamos a lista. Ao finalizar a lista de materiais, informe o responsável pela lista, número de OS/Proposta e observações."
        "\n » No sistema, caso deseje excluir um item da lista de materiais, basta clicar no item da lista e 'Excluir Selecionado'"
        "\n » Pode-se realizar a limpeza da lista através do botão 'Limpar lista'"
        "\n » Para salvar a lista, clique no botão 'Salvar lista'"
        "\n » Caso queira gerar relatório da lista, clique em 'Gerar PDF'"
        "\n"
        "\n ====Na aba Adicionar valores===="
        "\n » Busque pelo número número de OS/Proposta e clique em 'Buscar', automaticamente o sistema irá preencher os campos restantes."
        "\n » Para realizar a edição do valor unitário, selecione o índice da lista que deseja editar, insira o valor nocampo valor unitário e clique em 'Atualizar valor', ou caso queire excluir, selecione o item da lista e cliqueem 'Excluir selecionado'."
        "\n » Por final, clique em 'Atualizar Lista' para atualizar no sistema."
        "\n » Caso queira gerar o .PDF com o novo relatório, clique em 'Gerar PDF'"
        "\n",
        "teste": "Na aba matéria você consegue fazer as seguintes funções: "
        "\n » Cadastrar: Para cadastrar você irá colocar os dados da matéria sem o id"
        "\n » Consultar: Aqui você irá apenas colocar o id da matéria e clicar em consultar para trazer os dados da matéria"
        "\n » Alterar: Sugiro consultar a matéria antes de alterar os dados, o mais importante é não mudar o id da matéria"
        "\n » Deletar: Sugiro consultar a matéria antes de deletar os dados da matéria para que não seja excluido a matéria errada"
        "\n",
        "nota": "Na aba nota você consegue fazer as seguintes funções: "
        "\n » Cadastrar: Para cadastrar você irá colocar os dados da nota sem o id"
        "\n » Consultar: Aqui você irá apenas colocar o id da nota e clicar em consultar para trazer os dados da nota"
        "\n » Alterar: Sugiro consultar a nota antes de alterar os dados, o mais importante é não mudar o id da nota"
        "\n",  
    }

    palavras = word_tokenize(mensagem.lower())
    stemmer = PorterStemmer()
    palavra_raiz = [stemmer.stem(palavra) for palavra in palavras]

    for palavra in palavra_raiz:
        if palavra in respostas:
            return respostas[palavra]

    return "Desculpe, não entendi sua pergunta. Poderia reformular?"

def processar_mensagem_gemini(mensagem):
    resposta = chatbot_gemini(mensagem)
    caixa_gemini.configure(state="normal")
    caixa_gemini.insert("end", f"Você: {mensagem}\n", "usuario")
    caixa_gemini.insert("end", f"Gemini: {resposta}\n", "chatbot")
    caixa_gemini.configure(state="disabled")

# ChatBot Gemini
def chatbot_gemini(mensagem):
    try:
        resposta = modelo_gemini.generate_content(mensagem)
        return resposta.text
    except Exception as e:
        return f"Erro ao acessar Gemini: {e}"

# Função enviar mensagem para aba local
def enviar_mensagem_local():
    mensagem = entrada_local.get()
    if mensagem.strip() == "":
        return
    resposta = chatbot_local(mensagem)
    caixa_local.configure(state="normal")
    caixa_local.insert("end", f"Você: {mensagem}\n", "usuario")
    caixa_local.insert("end", f"Chatbot: {resposta}\n", "chatbot")
    caixa_local.configure(state="disabled")
    entrada_local.delete(0, tk.END)

# Função enviar mensagem para aba Gemini
def enviar_mensagem_gemini():
    mensagem = entrada_gemini.get()
    if mensagem.strip() == "":
        return
    entrada_gemini.delete(0, tk.END)
    threading.Thread(target=processar_mensagem_gemini, args=(mensagem,), daemon=True).start()

# Interface principal com abas
def frmMain():
    global entrada_local, caixa_local, entrada_gemini, caixa_gemini

    janelaMain = customtkinter.CTk()
    janelaMain.title("Suporte para o usuário")
    janelaMain.geometry("700x600")
    janelaMain.resizable(False, False)

    notebook = ttk.Notebook(janelaMain)
    notebook.pack(fill="both", expand=True)

    # Aba ChatBot Local
    aba_local = customtkinter.CTkFrame(notebook)
    notebook.add(aba_local, text="Chat Local")

    caixa_local = tk.Text(aba_local, height=20, wrap=tk.WORD, state="disabled", bg="#1a1a1a", fg="white", font=("Arial", 12))
    caixa_local.pack(padx=10, pady=10, fill="both", expand=True)
    caixa_local.tag_config("usuario", foreground="lightgreen")
    caixa_local.tag_config("chatbot", foreground="cyan")

    frame_local = customtkinter.CTkFrame(aba_local)
    frame_local.pack(pady=10)

    entrada_local = customtkinter.CTkEntry(frame_local, width=400, placeholder_text="Digite sua mensagem...")
    entrada_local.grid(row=0, column=0, padx=10)
    entrada_local.bind('<Return>', lambda event: enviar_mensagem_local())

    botao_local = customtkinter.CTkButton(frame_local, text="Enviar", command=enviar_mensagem_local)
    botao_local.grid(row=0, column=1, padx=5)

    # Aba Gemini
    aba_gemini = customtkinter.CTkFrame(notebook)
    notebook.add(aba_gemini, text="Gemini")

    caixa_gemini = tk.Text(aba_gemini, height=20, wrap=tk.WORD, state="disabled", bg="#1a1a1a", fg="white", font=("Arial", 12))
    caixa_gemini.pack(padx=10, pady=10, fill="both", expand=True)
    caixa_gemini.tag_config("usuario", foreground="lightgreen")
    caixa_gemini.tag_config("chatbot", foreground="cyan")

    frame_gemini = customtkinter.CTkFrame(aba_gemini)
    frame_gemini.pack(pady=10)

    entrada_gemini = customtkinter.CTkEntry(frame_gemini, width=400, placeholder_text="Digite sua mensagem...")
    entrada_gemini.grid(row=0, column=0, padx=10)
    entrada_gemini.bind('<Return>', lambda event: enviar_mensagem_gemini())

    botao_gemini = customtkinter.CTkButton(frame_gemini, text="Enviar", command=enviar_mensagem_gemini)
    botao_gemini.grid(row=0, column=1, padx=5)

    janelaMain.mainloop()

frmMain()