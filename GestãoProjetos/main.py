import tkinter as tk
from tkinter import ttk
import clientes, despesa, receita, orcamento, projeto
import psycopg2
import messagebox

class SistemaPrincipal:
    def __init__(self, root, conn_config, usuario_logado):
        self.root = root
        self.conn_config = conn_config
        self.usuario_logado = usuario_logado
        self.modulos = {}
        
        # Configura a janela principal
        self.root.title(f"Sistema AVL - Usuário: {usuario_logado['nome']}")
        self.root.geometry("1200x700")
        self.root.state('zoomed')
        
        # Cria e gerencia a conexão centralmente
        self.criar_conexao()
        self.configurar_usuario_auditoria()
        
        self.criar_menu()
        self.criar_area_trabalho()

    def criar_conexao(self):
        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha na conexão com o banco:\n{str(e)}")
            self.root.destroy()

    def __del__(self):
        # Fecha a conexão apenas quando o sistema principal for destruído
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def configurar_usuario_auditoria(self):
        """Configura o usuário para as triggers de auditoria"""
        try:
            self.cursor.execute(f"SET app.usuario_id = {self.usuario_logado['id']}")
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao configurar usuário para auditoria: {str(e)}")
    
    def criar_menu(self):
        # Barra de menu superior
        menubar = tk.Menu(self.root)
        
        # Menu de módulos
        modulos_menu = tk.Menu(menubar, tearoff=0)
        modulos_menu.add_command(label="Projetos", command=lambda: self.carregar_modulo("projeto"))
        modulos_menu.add_command(label="Clientes", command=lambda: self.carregar_modulo("clientes"))
        modulos_menu.add_command(label="Orçamentos", command=lambda: self.carregar_modulo("orcamento"))
        modulos_menu.add_command(label="Despesas", command=lambda: self.carregar_modulo("despesa"))
        modulos_menu.add_command(label="Receitas", command=lambda: self.carregar_modulo("receita"))
        menubar.add_cascade(label="Módulos", menu=modulos_menu)
        
        # Menu de sistema
        sistema_menu = tk.Menu(menubar, tearoff=0)
        sistema_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Sistema", menu=sistema_menu)
        
        self.root.config(menu=menubar)

    def sair(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            self.root.destroy()
    
    def criar_area_trabalho(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de status
        self.status_bar = ttk.Label(self.root, text="Bem-vindo ao Sistema Integrado", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=5)
    
    def carregar_modulo(self, modulo_nome):
        # Remove o módulo atual
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Carrega o novo módulo
        if modulo_nome == "clientes":
            from clientes import ModuloClientes
            self.modulos["clientes"] = clientes.ModuloClientes(self.main_frame, self.conn_config, self.conn, usuario_logado=self.usuario_logado)
        elif modulo_nome == "despesa":
            from despesa import ModuloDespesa
            self.modulos["despesa"] = despesa.ModuloDespesa(self.main_frame, self.conn_config, self.conn, usuario_logado=self.usuario_logado)
        elif modulo_nome == "receita":
            from receita import ModuloReceita
            self.modulos["receita"] = receita.ModuloReceita(self.main_frame, self.conn_config, self.conn, usuario_logado=self.usuario_logado)
        elif modulo_nome == "orcamento":
            from orcamento import ModuloOrcamento
            self.modulos["orcamento"] = orcamento.ModuloOrcamento(self.main_frame, self.conn_config, self.conn, usuario_logado=self.usuario_logado)
        elif modulo_nome == "projeto":
            from projeto import ModuloProjeto
            self.modulos["projeto"] = projeto.ModuloProjeto(self.main_frame, self.conn_config, conn=self.conn, usuario_logado=self.usuario_logado)
        
        # Atualiza a barra de status
        self.status_bar.config(text=f"Módulo Ativo: {modulo_nome.capitalize()}")

    def __del__(self):
        # Fecha a conexão apenas quando o sistema principal for destruído
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaPrincipal(root)
    root.mainloop()