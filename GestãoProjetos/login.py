# login_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from main import SistemaPrincipal  # Importa a main depois do login

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Sistema Empresarial")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Variáveis para armazenar credenciais
        self.usuario_logado = None
        self.conn_config = {
            "host": "localhost",
            "database": "projeto_final",
            "user": None,
            "password": None,
            'port': '5432'
        }
        
        self.criar_interface()
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Title
        ttk.Label(main_frame, text="Sistema AVL", font=('Helvetica', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Campos de login
        ttk.Label(main_frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_usuario = ttk.Entry(main_frame)
        self.entry_usuario.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_senha = ttk.Entry(main_frame, show="*")
        self.entry_senha.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # Botão de login
        btn_login = ttk.Button(main_frame, text="Entrar", command=self.fazer_login)
        btn_login.grid(row=3, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)
        
        # Configura expansão
        main_frame.columnconfigure(1, weight=1)
        
        # Enter para login
        self.entry_senha.bind('<Return>', lambda event: self.fazer_login())
    
    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()
        
        if not usuario or not senha:
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
    
        try:
            # Tenta conexão com o banco
            conn = psycopg2.connect(
                host=self.conn_config['host'],
                database=self.conn_config['database'],
                user=usuario,
                password=senha
            )
            
            # Verifica se o usuário existe na tabela de usuários
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, nivel_acesso 
                FROM usuarios 
                WHERE login = %s AND ativo = TRUE
            """, (usuario,))
            
            resultado = cursor.fetchone()
            
            if resultado:
                # Armazena informações do usuário
                self.usuario_logado = {
                    'id': resultado[0],
                    'nome': resultado[1],
                    'nivel': resultado[2],
                    'login': usuario
                }
                
                # Armazena configurações de conexão
                self.conn_config['user'] = usuario
                self.conn_config['password'] = senha
                
                # Fecha a tela de login e abre o sistema principal
                self.root.destroy()
                
                # Cria nova janela para o sistema principal
                root_main = tk.Tk()
                SistemaPrincipal(root_main, self.conn_config, self.usuario_logado)
                root_main.mainloop()
                
            else:
                messagebox.showerror("Erro", "Usuário não encontrado ou inativo!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar:\n{str(e)}")
        
        except UnicodeDecodeError:
            messagebox.showerror("Erro de login", f"Usuário ou senha incorretos!")