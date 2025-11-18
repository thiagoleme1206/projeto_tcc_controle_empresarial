import tkinter as tk
from tkinter import ttk, messagebox
from app.services.lista_materiais_service import ListaMateriaisService
from app.repositories.produto_repository import ProdutoRepository
from app.repositories.projeto_repository import ProjetoRepository
from app.models.lista_materiais_model import ItemListaMateriais
from tkinter import filedialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

class ListaMateriaisViewer:
    def __init__(self, root, usuario_logado):
        self.root = tk.Toplevel(root)
        self.root.title("\ud83d\udce6 Lista de Materiais")
        self.root.geometry("800x500")
        self.root.transient(root)
        self.root.focus_force()
        self.root.grab_set()

        self.usuario_logado = usuario_logado
        self.service = ListaMateriaisService()
        self.produto_repo = ProdutoRepository()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()
        self.carregar_listas()

    def create_widgets(self):
        ttk.Label(self.frame, text="\ud83d\udce6 Lista de Materiais", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("ID", "OS", "Respons\u00e1vel", "Observa\u00e7\u00e3o", "Criado em")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "ID" else 50)

        self.tree.pack(fill="both", expand=True, pady=10)

        botoes = ttk.Frame(self.frame)
        botoes.pack(pady=10)

        ttk.Button(botoes, text="\u2795 Criar Nova Lista", command=self.criar_lista).pack(side="left", padx=5)
        ttk.Button(botoes, text="\u270f\ufe0f Editar Lista", command=self.editar_lista).pack(side="left", padx=5)
        ttk.Button(botoes, text="\u274c Excluir Lista", command=self.excluir_lista).pack(side="left", padx=5)
        ttk.Button(botoes, text="\ud83d\udd0d Detalhar Itens", command=self.detalhar_itens).pack(side="left", padx=5)
        ttk.Button(botoes, text="📄 Gerar Relatório Lista", command=self.gerar_relatorio_pdf).pack(side="left", padx=5)


    def carregar_listas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        listas = self.service.listar_listas()
        for l in listas:
            self.tree.insert("", "end", values=(l.id_lista, l.os_referencia, l.responsavel, l.observacao, l.data_criacao.strftime("%d/%m/%Y")))

    def criar_lista(self):
        win = tk.Toplevel(self.root)
        win.title("\u2795 Criar Nova Lista de Materiais")
        win.geometry("400x300")
        win.transient(self.root)
        win.focus_force()
        win.grab_set()

        ttk.Label(win, text="OS de Refer\u00eancia:").pack()
        os_entry = ttk.Entry(win, width=40)
        os_entry.pack(pady=5)

        ttk.Label(win, text="Observa\u00e7\u00e3o:").pack()
        obs_entry = ttk.Entry(win, width=40)
        obs_entry.pack(pady=5)

        def continuar():
            numero_os = os_entry.get().strip()
            observacao = obs_entry.get().strip()

            if not numero_os:
                messagebox.showwarning("Campo obrigat\u00f3rio", "Informe a OS de refer\u00eancia.")
                return

            projeto_repo = ProjetoRepository()
            projeto = projeto_repo.buscar_por_os(numero_os)
            if not projeto:
                messagebox.showerror("OS n\u00e3o encontrada", "\u274c OS informada n\u00e3o foi identificada na base de projetos.")
                return

            win.destroy()
            self.abrir_janela_itens(numero_os, observacao)

        ttk.Button(win, text="Avan\u00e7ar", command=continuar).pack(pady=15)

    def abrir_janela_itens(self, numero_os, observacao, id_lista_existente=None):
        itens = []

        def adicionar_item():
            try:
                produto_id = int(produto_entry.get())
                produto = self.produto_repo.buscar_por_id(produto_id)
                if not produto:
                    messagebox.showerror("Produto n\u00e3o encontrado", "\u274c Produto com esse ID n\u00e3o existe.")
                    return

                quantidade = float(qtd_entry.get())
                obs = obs_entry.get()

                item = ItemListaMateriais(
                    id=None,
                    id_lista=id_lista_existente,
                    produto_id=produto_id,
                    nome_produto=produto.nome,
                    quantidade=quantidade,
                    unidade=produto.unidade,
                    preco_unitario=produto.preco_unitario,
                    observacao=obs
                )

                if id_lista_existente:
                    self.service.repo.adicionar_item(item)
                    messagebox.showinfo("Item adicionado", f"\u2705 {produto.nome} adicionado \u00e0 lista existente.")
                    item_win.destroy()
                    self.carregar_listas()
                else:
                    itens.append(item)
                    messagebox.showinfo("Item adicionado", f"\u2705 {produto.nome} adicionado \u00e0 nova lista.")

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        def salvar_lista():
            try:
                id_criada = self.service.criar_lista(numero_os, self.usuario_logado.nome, observacao, itens)
                messagebox.showinfo("Sucesso", f"\u2705 Lista criada com ID {id_criada}")
                item_win.destroy()
                self.carregar_listas()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        item_win = tk.Toplevel(self.root)
        item_win.title("\u2795 Adicionar Itens")
        item_win.geometry("400x350")
        item_win.transient(self.root)
        item_win.focus_force()
        item_win.grab_set()

        ttk.Label(item_win, text="ID do Produto:").pack()
        produto_entry = ttk.Entry(item_win, width=30)
        produto_entry.pack()

        ttk.Label(item_win, text="Quantidade:").pack()
        qtd_entry = ttk.Entry(item_win, width=30)
        qtd_entry.pack()

        ttk.Label(item_win, text="Observa\u00e7\u00e3o:").pack()
        obs_entry = ttk.Entry(item_win, width=30)
        obs_entry.pack()

        ttk.Button(item_win, text="Adicionar Item", command=adicionar_item).pack(pady=10)
        if not id_lista_existente:
            ttk.Button(item_win, text="Salvar Lista", command=salvar_lista).pack(pady=10)

    def abrir_janela_edicao_item(self, item, id_lista, tree_itens, parent_win):
        edit_win = tk.Toplevel(parent_win)
        edit_win.title(f"Editar Item {item.nome_produto}")
        edit_win.geometry("400x400")
        edit_win.transient(parent_win)
        edit_win.focus_force()
        edit_win.grab_set()

        # Campos editáveis
        def criar_label_entry(label_text, valor_inicial):
            ttk.Label(edit_win, text=label_text).pack()
            entry = ttk.Entry(edit_win, width=40)
            entry.insert(0, str(valor_inicial))
            entry.pack(pady=5)
            return entry

        qtd_entry = criar_label_entry("Quantidade:", item.quantidade)
        preco_entry = criar_label_entry("Preço Unitário:", item.preco_unitario)
        obs_entry = criar_label_entry("Observação:", item.observacao)

        def salvar():
            nova_qtde = float(qtd_entry.get()) if qtd_entry.get() != str(item.quantidade) else item.quantidade
            novo_preco = float(preco_entry.get()) if preco_entry.get() != str(item.preco_unitario) else item.preco_unitario
            nova_obs = obs_entry.get() if obs_entry.get() != item.observacao else item.observacao

            # Atualiza apenas se mudar
            if nova_qtde != item.quantidade:
                self.service.atualizar_quantidade(item.id, nova_qtde)

            if novo_preco != item.preco_unitario:
                self.service.atualizar_preco(item.id, novo_preco)

            if nova_obs != item.observacao:
                item.observacao = nova_obs
                self.service.repo.atualizar_observacao(item.id, nova_obs)

            messagebox.showinfo("Atualizado", "Item atualizado com sucesso.")
            edit_win.destroy()

            # Atualiza grid
            for child in tree_itens.get_children():
                tree_itens.delete(child)
            itens = self.service.buscar_itens(id_lista)
            for i in itens:
                tree_itens.insert("", "end", values=(i.id, i.nome_produto, i.quantidade, i.unidade, i.preco_unitario, i.observacao))

        ttk.Button(edit_win, text="💾 Salvar Item", command=salvar).pack(pady=10)
        ttk.Button(edit_win, text="🔙 Voltar", command=edit_win.destroy).pack()


    def editar_lista(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma lista para editar.")
            return

        valores = self.tree.item(item)["values"]
        id_lista = valores[0]

        itens = self.service.buscar_itens(id_lista)

        win = tk.Toplevel(self.root)
        win.title(f"✏️ Editar Itens da Lista {id_lista}")
        win.geometry("700x400")
        win.transient(self.root)
        win.focus_force()
        win.grab_set()

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=f"Lista de Itens - ID {id_lista}", font=("Helvetica", 14, "bold")).pack(pady=5)

        colunas = ("ID", "Produto", "Quantidade", "Unidade", "Preço", "Observação")
        tree_itens = ttk.Treeview(frame, columns=colunas, show="headings", height=10)

        for col in colunas:
            tree_itens.heading(col, text=col)
            tree_itens.column(col, width=120 if col != "ID" else 50)

        for item in itens:
            tree_itens.insert("", "end", values=(
                item.id, item.nome_produto, item.quantidade, item.unidade, item.preco_unitario, item.observacao
            ))

        tree_itens.pack(fill="both", expand=True, pady=10)

        # Botões
        botoes = ttk.Frame(frame)
        botoes.pack(pady=10)

        def adicionar_novo_item():
            item_win = tk.Toplevel(win)
            item_win.title("➕ Adicionar Novo Item")
            item_win.geometry("400x350")
            item_win.transient(win)
            item_win.focus_force()
            item_win.grab_set()

            ttk.Label(item_win, text="ID do Produto:").pack()
            produto_entry = ttk.Entry(item_win, width=30)
            produto_entry.pack()

            ttk.Label(item_win, text="Quantidade:").pack()
            qtd_entry = ttk.Entry(item_win, width=30)
            qtd_entry.pack()

            ttk.Label(item_win, text="Observação:").pack()
            obs_entry = ttk.Entry(item_win, width=30)
            obs_entry.pack()

            def adicionar():
                try:
                    produto_id = int(produto_entry.get())
                    produto = self.produto_repo.buscar_por_id(produto_id)
                    if not produto:
                        messagebox.showerror("Erro", "❌ Produto não encontrado.")
                        return

                    quantidade = float(qtd_entry.get())
                    obs = obs_entry.get()

                    novo_item = ItemListaMateriais(
                        id=None,
                        id_lista=id_lista,
                        produto_id=produto_id,
                        nome_produto=produto.nome,
                        quantidade=quantidade,
                        unidade=produto.unidade,
                        preco_unitario=produto.preco_unitario,
                        observacao=obs
                    )

                    self.service.repo.adicionar_item(novo_item)
                    messagebox.showinfo("✅ Sucesso", f"{produto.nome} adicionado à lista.")

                    # Atualiza o grid
                    tree_itens.insert("", "end", values=(
                        "-", produto.nome, quantidade, produto.unidade, produto.preco_unitario, obs
                    ))

                    item_win.destroy()
                except Exception as e:
                    messagebox.showerror("Erro", str(e))

            ttk.Button(item_win, text="Adicionar", command=adicionar).pack(pady=10)
            ttk.Button(item_win, text="Cancelar", command=item_win.destroy).pack()


        def abrir_edicao_item():
            sel = tree_itens.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um item para editar.")
                return

            valores = tree_itens.item(sel)["values"]
            id_item = valores[0]

            # Recupera o item completo do serviço
            item = next((i for i in itens if i.id == id_item), None)
            if not item:
                messagebox.showerror("Erro", "Item não encontrado.")
                return

            self.abrir_janela_edicao_item(item, id_lista, tree_itens, win)

        def excluir_item_selecionado():
            sel = tree_itens.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um item para excluir.")
                return

            valores = tree_itens.item(sel)["values"]
            id_item = valores[0]

            confirm = messagebox.askyesno("Confirmação", f"Excluir item {id_item}?")
            if confirm:
                self.service.remover_item(id_item)
                tree_itens.delete(sel)
                messagebox.showinfo("Removido", f"Item {id_item} excluído com sucesso.")

        ttk.Button(botoes, text="✏️ Editar Item", command=abrir_edicao_item).pack(side="left", padx=5)
        ttk.Button(botoes, text="🗑️ Excluir Item", command=excluir_item_selecionado).pack(side="left", padx=5)
        def salvar_lista():
            self.carregar_listas()
            messagebox.showinfo("Sucesso", "✅ Lista atualizada com sucesso.")
            win.destroy()  # Fecha a janela de edição após salvar
        ttk.Button(botoes, text="➕ Adicionar Item", command=adicionar_novo_item).pack(side="left", padx=5)
        ttk.Button(botoes, text="💾 Salvar Lista", command=salvar_lista).pack(side="left", padx=5)
        ttk.Button(botoes, text="🔙 Voltar", command=win.destroy).pack(side="left", padx=5)

    def excluir_lista(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma lista para excluir.")
            return

        valores = self.tree.item(item)["values"]
        id_lista = valores[0]

        confirm = messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir a lista {id_lista}?")
        if confirm:
            self.service.excluir_lista(id_lista)
            self.carregar_listas()
            messagebox.showinfo("Exclu\u00eddo", "\ud83d\uddd1\ufe0f Lista exclu\u00edda com sucesso.")

    def detalhar_itens(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma lista para ver os itens.")
            return

        valores = self.tree.item(item)["values"]
        id_lista = valores[0]
        itens = self.service.buscar_itens(id_lista)

        win = tk.Toplevel(self.root)
        win.title(f"Itens da Lista {id_lista}")
        win.geometry("700x400")
        win.transient(self.root)
        win.focus_force()
        win.grab_set()

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill="both", expand=True)

        # Cabeçalho
        ttk.Label(frame, text=f"📦 Itens da Lista {id_lista}", font=("Helvetica", 14, "bold")).pack(pady=5)

        colunas = ("Produto", "Quantidade", "Unidade", "Preço", "Observação")
        tree = ttk.Treeview(frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        tree.pack(fill="both", expand=True)

        # Inserir itens
        for i in itens:
            tree.insert("", "end", values=(
                i.nome_produto,
                i.quantidade,
                i.unidade,
                f"R${i.preco_unitario:.2f}",
                i.observacao or ""
            ))

    def gerar_relatorio_pdf(self):

        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma lista para gerar o relatório.")
            return

        valores = self.tree.item(item)["values"]
        id_lista = valores[0]
        os_referencia = valores[1]

        itens = self.service.buscar_itens(id_lista)
        if not itens:
            messagebox.showinfo("Sem dados", "Esta lista não possui itens.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Salvar relatório como..."
        )

        if not caminho:
            return  # Usuário cancelou

        try:
            pdf = canvas.Canvas(caminho, pagesize=A4)
            largura, altura = A4

            pdf.setTitle(f"Relatório Lista {id_lista}")

            # Cabeçalho principal
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(2 * cm, altura - 2 * cm, f"📦 Relatório da Lista de Materiais - ID {id_lista} (OS {os_referencia})")

            # Configuração de tabela
            colunas = ["Produto", "Quantidade", "Unidade", "Preço Unitário", "Total"]
            x_inicial = 2 * cm
            y = altura - 3 * cm
            espacamento_y = 1.0 * cm

            # Cabeçalho da tabela
            pdf.setFont("Helvetica-Bold", 10)
            for i, col in enumerate(colunas):
                x = x_inicial + i * 3.5 * cm
                pdf.drawString(x + 2, y + 3, col)
                pdf.rect(x, y, 3.5 * cm, -espacamento_y)

            y -= espacamento_y

            # Dados dos itens
            pdf.setFont("Helvetica", 10)
            valor_total = 0

            for item in itens:
                subtotal = item.quantidade * item.preco_unitario
                valor_total += subtotal

                col_values = [
                    str(item.nome_produto),
                    f"{item.quantidade:.2f}",
                    item.unidade,
                    f"R$ {item.preco_unitario:.2f}",
                    f"R$ {subtotal:.2f}"
                ]

                for i, value in enumerate(col_values):
                    x = x_inicial + i * 3.5 * cm
                    pdf.drawString(x + 2, y + 3, value)
                    pdf.rect(x, y, 3.5 * cm, -espacamento_y)

                y -= espacamento_y

                # Quebra de página
                if y < 3 * cm:
                    pdf.showPage()
                    y = altura - 3 * cm
                    pdf.setFont("Helvetica-Bold", 10)
                    for i, col in enumerate(colunas):
                        x = x_inicial + i * 3.5 * cm
                        pdf.drawString(x + 2, y + 3, col)
                        pdf.rect(x, y, 3.5 * cm, -espacamento_y)
                    y -= espacamento_y
                    pdf.setFont("Helvetica", 10)

            # Espaço e valor total
            y -= 0.7 * cm
            if y < 3 * cm:
                pdf.showPage()
                y = altura - 3 * cm

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(x_inicial, y, f"💰 Valor total: R$ {valor_total:.2f}")

            pdf.save()
            messagebox.showinfo("Sucesso", f"📄 Relatório salvo com sucesso em:\n{caminho}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório:\n{str(e)}")
