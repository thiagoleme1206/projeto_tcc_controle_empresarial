import tkinter as tk
from tkinter import ttk, messagebox
from app.services.estoque_service import EstoqueService

class EstoqueViewer:
    def __init__(self, root, usuario_logado):
        self.usuario = usuario_logado
        self.acesso_total = usuario_logado.grupo in ["estoquista", "ti"]

        self.root = tk.Toplevel(root)
        self.root.title("📦 Gestão de Estoque")
        self.root.update_idletasks()
        largura = 1250
        altura = 500
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

        self.service = EstoqueService()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()
        self.carregar_produtos()

    def create_widgets(self):   
        ttk.Label(self.frame, text="📦 Produtos em Estoque", font=("Helvetica", 14)).pack(pady=5)

        colunas = ("ID", "Nome", "Descrição", "Quantidade", "Unidade", "Preço Unitário", "Estoque Mínimo")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=150)

        self.tree.pack(fill="both", expand=True, pady=10)

        filtro_frame = ttk.Frame(self.frame)
        filtro_frame.pack(fill="x", pady=5)

        ttk.Label(filtro_frame, text="🔍 Consultar por nome:").pack(side="left", padx=5)
        self.entrada_nome = ttk.Entry(filtro_frame, width=30)
        self.entrada_nome.pack(side="left")
        ttk.Button(filtro_frame, text="Buscar", command=self.consultar_produto).pack(side="left", padx=5)

        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="🔄 Atualizar Lista", command=self.carregar_produtos).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="➕ Novo Produto", command=self.abrir_criar_produto).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="✏️ Editar", command=self.abrir_editar_produto).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="🗑️ Excluir", command=self.excluir_produto).grid(row=0, column=3, padx=5)

    def carregar_produtos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        produtos = self.service.listar_produtos()
        for p in produtos:
            self.tree.insert("", "end", values=(p.id, p.nome, p.descricao, p.quantidade, p.unidade, f"R${p.preco_unitario:.2f}", p.estoque_minimo))

    def abrir_criar_produto(self):
        self.abrir_formulario_produto("Cadastrar Novo Produto")

    def abrir_editar_produto(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um produto para editar.")
            return

        dados = self.tree.item(item)["values"]
        self.abrir_formulario_produto("Editar Produto", produto_id=dados[0])

    def abrir_formulario_produto(self, titulo, produto_id=None):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("400x450")

        # Campos
        campos = {}

        def add_campo(label_text, row, is_text=False):
            ttk.Label(win, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            widget = ttk.Entry(win, width=30) if not is_text else tk.Text(win, height=3, width=30)
            widget.grid(row=row, column=1, padx=10, pady=5)
            campos[label_text] = widget

        add_campo("Nome", 0)
        add_campo("Descrição", 1, is_text=True)
        add_campo("Quantidade", 2)
        add_campo("Unidade", 3)
        add_campo("Preço Unitário", 4)
        add_campo("Estoque Mínimo", 5)

        if produto_id:
            produto = self.service.repo.buscar_por_id(produto_id)
            if produto:
                campos["Nome"].insert(0, produto.nome)
                campos["Descrição"].insert("1.0", produto.descricao)
                campos["Quantidade"].insert(0, produto.quantidade)
                campos["Unidade"].insert(0, produto.unidade)
                campos["Preço Unitário"].insert(0, produto.preco_unitario)
                campos["Estoque Mínimo"].insert(0, produto.estoque_minimo)

        def salvar():
            try:
                nome_valor = campos["Nome"].get().strip()
                if not nome_valor:
                    raise ValueError("O nome do produto é obrigatório.")

                descricao_valor = campos["Descrição"].get("1.0", "end").strip() or "sem obs"

                qtde_str = campos["Quantidade"].get().strip()
                if not qtde_str.isdigit():
                    raise ValueError("Quantidade é um campo obrigatório e deve ser um número inteiro.")
                quantidade_valor = int(qtde_str)

                unidade_valor = campos["Unidade"].get().strip()
                if not unidade_valor:
                    raise ValueError("Unidade é obrigatória.")

                preco_str = campos["Preço Unitário"].get().strip()
                if not preco_str:
                    raise ValueError("Preço unitário é obrigatório.")
                preco_valor = float(preco_str)

                estoque_str = campos["Estoque Mínimo"].get().strip()
                if not estoque_str.isdigit():
                    raise ValueError("Estoque mínimo é obrigatório e deve ser um número inteiro.")
                estoque_min_valor = int(estoque_str)

                if produto_id:
                    self.service.atualizar_produto(
                        produto_id, nome_valor, descricao_valor, quantidade_valor,
                        unidade_valor, preco_valor, estoque_min_valor
                    )
                    messagebox.showinfo("Sucesso", "Produto atualizado com sucesso.")
                else:
                    self.service.cadastrar_produto(
                        nome_valor, descricao_valor, quantidade_valor,
                        unidade_valor, preco_valor, estoque_min_valor
                    )
                    messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso.")

                win.destroy()
                self.carregar_produtos()

            except ValueError as ve:
                messagebox.showerror("Erro", str(ve))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar produto: {e}")

        ttk.Button(win, text="Salvar", command=salvar).grid(row=6, column=0, columnspan=2, pady=15)

    def excluir_produto(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
            return

        dados = self.tree.item(item)["values"]
        produto_id = dados[0]

        if messagebox.askyesno("Confirmar", f"Deseja excluir o produto ID {produto_id}?"):
            try:
                self.service.deletar_produto(produto_id)
                messagebox.showinfo("Sucesso", "Produto excluído.")
                self.carregar_produtos()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def consultar_produto(self):
        nome = self.entrada_nome.get().strip().lower()
        if not nome:
            self.carregar_produtos()
            return

        encontrados = [p for p in self.service.listar_produtos() if nome in p.nome.lower()]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in encontrados:
            self.tree.insert("", "end", values=(p.id, p.nome, p.descricao, p.quantidade, p.unidade, f"R${p.preco_unitario:.2f}", p.estoque_minimo))
