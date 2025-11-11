import tkinter as tk
from tkinter import ttk, messagebox
from app.services.estoque_service import EstoqueService

class ConsultaEstoqueViewer:
    def __init__(self, root, usuario_logado):
        self.usuario = usuario_logado
        self.grupo = usuario_logado.grupo

        if self.grupo not in ["vendedor", "engenheiro", "gerencia", "ti"]:
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            return

        self.root = tk.Toplevel(root)
        self.root.title("🔍 Consulta de Estoque")
        self.root.geometry("1000x500")

        self.service = EstoqueService()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_produtos()

    def criar_widgets(self):
        ttk.Label(self.frame, text="🔍 Consulta de Estoque", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("ID", "Nome", "Descrição", "Quantidade", "Unidade", "Preço Unitário", "Estoque Mínimo")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=140)

        self.tree.pack(fill="both", expand=True, pady=10)

        filtro_frame = ttk.Frame(self.frame)
        filtro_frame.pack(fill="x", pady=5)

        ttk.Label(filtro_frame, text="🔍 Consultar por nome:").pack(side="left", padx=5)
        self.entrada_nome = ttk.Entry(filtro_frame, width=30)
        self.entrada_nome.pack(side="left")
        ttk.Button(filtro_frame, text="Buscar", command=self.filtrar_por_nome).pack(side="left", padx=5)

        botoes = ttk.Frame(self.frame)
        botoes.pack(pady=5)
        ttk.Button(botoes, text="🔄 Atualizar", command=self.carregar_produtos).pack(side="left", padx=5)
        ttk.Button(botoes, text="📋 Detalhes do Produto", command=self.exibir_detalhes).pack(side="left", padx=5)

    def carregar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        produtos = self.service.listar_produtos()
        for p in produtos:
            self.tree.insert("", "end", values=(
                p.id, p.nome, p.descricao, p.quantidade, p.unidade,
                f"R${p.preco_unitario:.2f}", p.estoque_minimo
            ))

    def filtrar_por_nome(self):
        nome = self.entrada_nome.get().strip().lower()
        if not nome:
            self.carregar_produtos()
            return

        encontrados = [p for p in self.service.listar_produtos() if nome in p.nome.lower()]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in encontrados:
            self.tree.insert("", "end", values=(
                p.id, p.nome, p.descricao, p.quantidade, p.unidade,
                f"R${p.preco_unitario:.2f}", p.estoque_minimo
            ))

    def exibir_detalhes(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um produto para ver os detalhes.")
            return

        valores = self.tree.item(item, "values")
        produto_id = valores[0]

        produto = self.service.repo.buscar_por_id(produto_id)
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Detalhes do Produto #{produto.id}")
        win.geometry("400x350")

        ttk.Label(win, text=f"🆔 ID: {produto.id}", font=("Helvetica", 12, "bold")).pack(pady=5)
        ttk.Label(win, text=f"📦 Nome: {produto.nome}").pack(pady=5)
        ttk.Label(win, text=f"📏 Unidade: {produto.unidade}").pack(pady=5)
        ttk.Label(win, text=f"📊 Quantidade: {produto.quantidade}").pack(pady=5)
        ttk.Label(win, text=f"🔻 Estoque Mínimo: {produto.estoque_minimo}").pack(pady=5)
        ttk.Label(win, text=f"💲 Preço Unitário: R${produto.preco_unitario:.2f}").pack(pady=5)

        ttk.Label(win, text="📝 Descrição:", font=("Helvetica", 10, "bold")).pack(pady=(10, 0))
        txt = tk.Text(win, wrap="word", height=5)
        txt.insert("end", produto.descricao)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=5)
