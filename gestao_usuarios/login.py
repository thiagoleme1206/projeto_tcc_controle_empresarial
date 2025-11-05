import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import os
from run import abrir_gestao_usuarios  # Importa a função do run.py

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Gestão de Usuários")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.criar_interface()

    def criar_interface(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Gestão de Usuários", font=('Helvetica', 16, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=20
        )

        ttk.Label(main_frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_usuario = ttk.Entry(main_frame)
        self.entry_usuario.grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(main_frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_senha = ttk.Entry(main_frame, show="*")
        self.entry_senha.grid(row=2, column=1, sticky=tk.EW, pady=5)

        btn_login = ttk.Button(main_frame, text="Entrar", command=self.fazer_login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

        main_frame.columnconfigure(1, weight=1)

        # Enter → login
        self.entry_senha.bind("<Return>", lambda event: self.fazer_login())

    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),
                user=usuario,
                password=senha,
                port=os.getenv("DB_PORT")
            )
            cursor = conn.cursor()

            # Verifica se o usuário existe, está ativo e é admin
            cursor.execute("""
                SELECT nivel_acesso 
                FROM usuarios 
                WHERE login = %s AND ativo = TRUE
            """, (usuario,))
            resultado = cursor.fetchone()

            if resultado:
                nivel = resultado[0]
                if nivel.lower() == "admin":
                    messagebox.showinfo("Bem-vindo", "Login bem-sucedido! Abrindo painel de controle...")
                    self.root.destroy()
                    abrir_gestao_usuarios()
                else:
                    messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este sistema.")
            else:
                messagebox.showerror("Erro", "Usuário não encontrado ou inativo!")

            cursor.close()
            conn.close()

        except UnicodeDecodeError:
            messagebox.showerror("Erro", "Login/senha incorretos")

        except psycopg2.OperationalError as error:
            # Se o erro for de autenticação, trata como login inválido
            if "password authentication failed" in str(error).lower():
                messagebox.showerror("Erro", "Login/senha incorretos")
            else:
                messagebox.showerror("Erro de Conexão", f"Não foi possível conectar:\n{str(error)}")

        except Exception as e:
            # Se for erro de codificação, trata como erro de login
            if "codec can't decode" in str(e).lower():
                messagebox.showerror("Erro", "Login/senha incorretos")
            else:
                messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()