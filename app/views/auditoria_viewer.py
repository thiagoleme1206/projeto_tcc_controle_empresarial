import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.services.auditoria_service import AuditoriaService

class AuditoriaViewer:
    def __init__(self, master, usuario):
        self.master = master
        self.usuario = usuario
        self.service = AuditoriaService()

        if self.usuario.grupo != "ti":
            messagebox.showerror("Acesso Negado", "❌ Este módulo é restrito ao grupo TI.")
            self.master.destroy()
            return

        self.master.title("📄 Módulo de Auditoria")
        self.master.geometry("1000x650")
        self.centralizar_janela(1000, 650)
        self.master.configure(bg="#f0f2f5")

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
        titulo = ttk.Label(self.master, text="📄 Logs de Auditoria", font=("Helvetica", 16, "bold"))
        titulo.pack(pady=15)

        # Filtros
        filtros_frame = ttk.Frame(self.master)
        filtros_frame.pack(pady=10)

        # Filtro por usuário
        ttk.Label(filtros_frame, text="Usuário:").grid(row=0, column=0, padx=5, sticky="e")
        self.usuario_entry = ttk.Entry(filtros_frame, width=25)
        self.usuario_entry.grid(row=0, column=1, padx=5)
        ttk.Button(filtros_frame, text="Buscar", command=self.buscar_por_usuario).grid(row=0, column=2, padx=10)

        # Filtro por data
        ttk.Label(filtros_frame, text="Data (DD/MM/AAAA):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.data_entry = ttk.Entry(filtros_frame, width=25)
        self.data_entry.grid(row=1, column=1, padx=5)
        ttk.Button(filtros_frame, text="Buscar", command=self.buscar_por_data).grid(row=1, column=2, padx=10)

        # Grade com logs
        colunas = ("Usuário", "Ação", "Módulo", "Descrição", "Data")
        self.tree_logs = ttk.Treeview(self.master, columns=colunas, show="headings", height=20)

        for col in colunas:
            self.tree_logs.heading(col, text=col)
            self.tree_logs.column(col, anchor="center", width=150 if col != "Descrição" else 300)

        self.tree_logs.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Botão voltar
        ttk.Button(self.master, text="Voltar", command=self.master.destroy).pack(pady=10)

    def buscar_por_usuario(self):
        nome = self.usuario_entry.get().strip()
        if not nome:
            messagebox.showwarning("Campo obrigatório", "Digite o nome de usuário.")
            return
        try:
            logs = self.service.consultar_por_usuario(nome)
            self.exibir_logs(logs)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def buscar_por_data(self):
        data_str = self.data_entry.get().strip()
        try:
            data_formatada = datetime.strptime(data_str, "%d/%m/%Y").date()
            logs = self.service.consultar_por_data(data_formatada)
            self.exibir_logs(logs)
        except ValueError:
            messagebox.showerror("Data inválida", "Insira uma data no formato DD/MM/AAAA.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def exibir_logs(self, logs):
        # Limpa os logs existentes
        for row in self.tree_logs.get_children():
            self.tree_logs.delete(row)

        if not logs:
            messagebox.showinfo("Resultado", "Nenhum log encontrado.")
            return

        for log in logs:
            usuario, acao, modulo, descricao, data = log
            data_formatada = data.strftime("%d/%m/%Y %H:%M:%S")
            self.tree_logs.insert("", "end", values=(usuario, acao, modulo, descricao, data_formatada))
