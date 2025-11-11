import tkinter as tk
from tkinter import ttk, messagebox
from app.views.main_viewer import MainViewer
from app.services.auth_service import AuthService
from app.services.auditoria_service import AuditoriaService

class LoginViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")

        self.centralizar_janela(400, 350)

        self.auth = AuthService()
        self.auditoria = AuditoriaService()
        self.create_widgets()

    def centralizar_janela(self, largura, altura):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        titulo = ttk.Label(frame, text="Login - Gestão Empresarial", font=("Helvetica", 18, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")

        # Login
        ttk.Label(
            frame, text="Login", font=("Helvetica", 12), justify="center", anchor="center"
        ).grid(row=1, column=0, columnspan=2, pady=(0, 2))
        self.login_entry = ttk.Entry(frame, width=30)
        self.login_entry.grid(row=2, column=0, columnspan=2, pady=(0, 15))

        # Senha
        ttk.Label(
            frame, text="Senha", font=("Helvetica", 12), justify="center", anchor="center"
        ).grid(row=3, column=0, columnspan=2, pady=(0, 2))
        self.senha_entry = ttk.Entry(frame, show="*", width=30)
        self.senha_entry.grid(row=4, column=0, columnspan=2, pady=(0, 20))

        # Botão login
        btn_login = ttk.Button(frame, text="Entrar", command=self.autenticar_usuario)
        btn_login.grid(row=5, column=0, columnspan=2, pady=10)

        # Atalho ENTER
        self.root.bind("<Return>", lambda event: self.autenticar_usuario())

    def autenticar_usuario(self):
        login = self.login_entry.get().strip()
        senha = self.senha_entry.get().strip()

        usuario = self.auth.autenticar(login, senha)

        if usuario:
            self.auditoria.registrar_acao(
                usuario.login,
                "LOGIN",
                "autenticacao",
                f"Usuário '{usuario.login}' autenticado com sucesso."
            )
            self.abrir_main(usuario)
        else:
            self.auditoria.registrar_acao(
                login,
                "LOGIN_FALHOU",
                "autenticacao",
                f"Tentativa de login falhou para o usuário '{login}'."
            )
            messagebox.showerror("Erro", "Login inválido ou usuário inativo.")

    def abrir_main(self, usuario):
        self.root.destroy()
        root_main = tk.Tk()
        MainViewer(root_main, usuario)
        root_main.mainloop()
