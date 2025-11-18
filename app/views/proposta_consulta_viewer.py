import tkinter as tk
from tkinter import ttk, messagebox
from app.services.proposta_service import PropostaService

class PropostaConsultaViewer:
    def __init__(self, root, usuario_logado):
        self.usuario_logado = usuario_logado
        self.grupo = usuario_logado.grupo

        # 🔒 Controle de acesso
        if self.grupo not in ["vendedor", "ti", "engenheiro", "gerencia"]:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            return

        # Criação da janela principal do módulo
        self.root = tk.Toplevel(root)
        self.root.title("🔍 Consulta de Propostas")
        self.root.geometry("800x500")

        self.service = PropostaService()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()
        self.load_propostas()

    def create_widgets(self):
        ttk.Label(self.frame, text="🔍 Consulta de Propostas", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Grid de propostas
        colunas = ("ID", "Título", "Descrição", "Valor", "Status")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            self.tree.heading(col, text=col)
            if col == "Descrição":
                self.tree.column(col, width=250)
            elif col == "Título":
                self.tree.column(col, width=150)
            elif col == "Valor":
                self.tree.column(col, width=80)
            elif col == "Status":
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=40)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Barra inferior de ações
        frame_botoes = ttk.Frame(self.frame)
        frame_botoes.pack(fill="x", pady=10)

        ttk.Button(frame_botoes, text="🔄 Atualizar Lista", command=self.load_propostas).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="🔍 Detalhes da Proposta", command=self.exibir_detalhes).pack(side="left", padx=5)

    def load_propostas(self):
        """Carrega as propostas na Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            propostas = self.service.listar_propostas()
            for p in propostas:
                self.tree.insert("", "end", values=(p.id, p.titulo, p.descricao, f"R${p.valor:.2f}", p.status))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar propostas: {e}")

    def exibir_detalhes(self):
        """Abre uma janela com os detalhes completos da proposta selecionada"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma proposta para ver os detalhes.")
            return

        valores = self.tree.item(item)["values"]
        proposta_id = valores[0]

        proposta = self.service.repo.buscar_por_id(proposta_id)
        if not proposta:
            messagebox.showerror("Erro", "Proposta não encontrada.")
            return

        # Cria janela de detalhes
        win = tk.Toplevel(self.root)
        win.title(f"Detalhes da Proposta #{proposta.id}")
        win.geometry("400x350")

        ttk.Label(win, text=f"📋 ID: {proposta.id}", font=("Helvetica", 12, "bold")).pack(pady=5)
        ttk.Label(win, text=f"🧾 Título: {proposta.titulo}", wraplength=350).pack(pady=5)
        ttk.Label(win, text=f"💰 Valor: R${proposta.valor:.2f}").pack(pady=5)
        ttk.Label(win, text=f"📊 Status: {proposta.status}").pack(pady=5)

        ttk.Label(win, text="📝 Descrição:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
        text = tk.Text(win, wrap="word", height=10)
        text.insert("end", proposta.descricao)
        text.config(state="disabled")
        text.pack(fill="both", expand=True, padx=10, pady=5)
