import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._completion_list = []
        self._hits = []
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = []

    def set_completion_list(self, completion_list):
        self._completion_list = completion_list
        self._hits = []
        self.position = 0
        self['values'] = []

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())
        
        _hits = []
        for item in self._completion_list:
            # Modificado para buscar em qualquer parte do nome (case insensitive)
            if self.get().lower() in item.lower():
                _hits.append(item)
        
        if _hits != self._hits:
            self._hits = _hits
            self['values'] = _hits
        
        if self._hits:
            self['values'] = self._hits
            self.icursor(self.position)

    def handle_keyrelease(self, event):
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        
        if event.keysym == "Left":
            if self.position < self.index(tk.END):
                self.delete(self.position, tk.END)
            else:
                self.position = self.position-1
                self.delete(self.position, tk.END)
        
        if event.keysym == "Right":
            self.position = self.index(tk.END)
        
        if len(event.keysym) == 1 or event.keysym == "BackSpace":
            self.autocomplete()

class SistemaEstoque:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de Estoque")
        self.root.geometry("1000x700")
        
        # Configuração do banco de dados
        self.db_config = {
            'host': 'localhost',
            'database': 'projeto_final',
            'user': 'postgres',
            'password': 'Edu1Sal2',
            'port': '5432'
        }
        
        # Criar widgets
        self.criar_widgets()
        self.carregar_produtos_combobox()
        
    def conectar_banco(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{str(e)}")
            return None
    
    def criar_widgets(self):
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba de Produtos
        self.aba_produtos = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_produtos, text="Produtos")
        self.criar_aba_produtos()
        
        # Aba de Lotes
        self.aba_lotes = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_lotes, text="Lotes")
        self.criar_aba_lotes()
        
        # Aba de Movimentações
        self.aba_movimentacoes = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_movimentacoes, text="Movimentações")
        self.criar_aba_movimentacoes()
        
        # Aba de Consultas
        self.aba_consultas = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_consultas, text="Consultas")
        self.criar_aba_consultas()
    
    def criar_aba_produtos(self):
        # Frame de cadastro
        frame_cadastro = ttk.LabelFrame(self.aba_produtos, text="Cadastro de Produto")
        frame_cadastro.pack(fill=tk.X, padx=10, pady=5)
        
        # Campos do formulário - REMOVIDO O CAMPO DESCRIÇÃO
        ttk.Label(frame_cadastro, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.prod_nome = ttk.Entry(frame_cadastro, width=60)  # Aumentado para width=60
        self.prod_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        
        ttk.Label(frame_cadastro, text="Unidade de Medida:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.prod_unidade = ttk.Entry(frame_cadastro, width=10)
        self.prod_unidade.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Botões
        btn_frame = ttk.Frame(frame_cadastro)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)  # Ajustado columnspan
        
        ttk.Button(btn_frame, text="Cadastrar", command=self.cadastrar_produto).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpar", command=self.limpar_campos_produto).pack(side=tk.LEFT, padx=5)

        # Frame principal para lista e edição
        frame_principal = ttk.Frame(self.aba_produtos)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Lista de produtos
        frame_lista = ttk.LabelFrame(frame_principal, text="Lista de Produtos")
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        self.tree_produtos = ttk.Treeview(frame_lista, columns=('ID', 'Nome', 'Unidade'), show='headings')
        self.tree_produtos.heading('ID', text='', anchor=tk.W)
        self.tree_produtos.heading('Nome', text='Nome')
        self.tree_produtos.heading('Unidade', text='Unidade')
        self.tree_produtos.column('ID', width=0, stretch=tk.NO)
        self.tree_produtos.column('Nome', width=375, anchor=tk.CENTER)
        self.tree_produtos.column('Unidade', width=100, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_produtos.yview)
        hsb = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree_produtos.xview)
        self.tree_produtos.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_produtos.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Frame de edição
        frame_edicao = ttk.LabelFrame(frame_principal, text="Editar Produto")
        frame_edicao.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Campos de edição 
        ttk.Label(frame_edicao, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.editar_prod_nome = ttk.Entry(frame_edicao, width=40)  # Pode aumentar se necessário
        self.editar_prod_nome.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_edicao, text="Unidade de Medida:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.editar_prod_unidade = ttk.Entry(frame_edicao, width=10)
        self.editar_prod_unidade.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Botão de salvar edição
        btn_salvar_edicao = ttk.Button(frame_edicao, text="Salvar Alterações", command=self.salvar_edicao_produto)
        btn_salvar_edicao.grid(row=2, column=0, columnspan=2, pady=10)

        # Variável para armazenar o ID do produto sendo editado
        self.produto_editando_id = None
        
        # Carregar produtos
        self.carregar_produtos()
        
        # Bind para seleção
        self.tree_produtos.bind('<<TreeviewSelect>>', self.selecionar_produto)

    def selecionar_produto(self, event):
        selected = self.tree_produtos.focus()
        if not selected:
            return
            
        values = self.tree_produtos.item(selected, 'values')
        self.produto_editando_id = values[0]
        
        # Preencher campos de edição
        self.editar_prod_nome.delete(0, tk.END)
        self.editar_prod_nome.insert(0, values[1])
        self.editar_prod_unidade.delete(0, tk.END)
        self.editar_prod_unidade.insert(0, values[2])
        
        # Carregar descrição
        conn = self.conectar_banco()
        if not conn:
            return
        
        conn.close()

    def salvar_edicao_produto(self):
        if not self.produto_editando_id:
            messagebox.showwarning("Aviso", "Nenhum produto selecionado para edição!")
            return
            
        novo_nome = self.editar_prod_nome.get().strip()
        nova_unidade = self.editar_prod_unidade.get().strip()
        
        if not novo_nome or not nova_unidade:
            messagebox.showwarning("Aviso", "Nome e unidade de medida são obrigatórios!")
            return
            
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE produto SET nome = %s, unidade_medida = %s WHERE id_produto = %s",  # REMOVIDO DESCRICAO
                (novo_nome, nova_unidade, self.produto_editando_id)
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
            
            # Atualizar as listas
            self.carregar_produtos()
            self.carregar_produtos_combobox()
            self.carregar_produtos_combobox_peps()
            self.carregar_estoque_consolidado()
            self.carregar_lotes_disponiveis()
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar produto:\n{str(e)}")
        finally:
            conn.close()
    
    def criar_aba_lotes(self):
        # Frame principal para cadastro/edição e lista
        frame_principal = ttk.Frame(self.aba_lotes)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame superior para cadastro e edição
        frame_superior = ttk.Frame(frame_principal)
        frame_superior.pack(fill=tk.X, pady=5)
        
        # Frame de cadastro (esquerda)
        frame_cadastro = ttk.LabelFrame(frame_superior, text="Entrada de Lote")
        frame_cadastro.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Campos do formulário de cadastro
        ttk.Label(frame_cadastro, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_produto = AutocompleteCombobox(frame_cadastro)
        self.combo_produto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_produto['state'] = 'normal'
        self.combo_produto['width'] = 60
        
        ttk.Label(frame_cadastro, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.lote_quantidade = ttk.Entry(frame_cadastro)
        self.lote_quantidade.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_cadastro, text="Valor Unitário:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.lote_valor = ttk.Entry(frame_cadastro)
        self.lote_valor.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_cadastro, text="Fornecedor:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.lote_fornecedor = ttk.Entry(frame_cadastro, width=40)
        self.lote_fornecedor.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame_cadastro, text="Nº Nota Fiscal:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.lote_nota = ttk.Entry(frame_cadastro)
        self.lote_nota.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Botões de cadastro
        btn_frame_cadastro = ttk.Frame(frame_cadastro)
        btn_frame_cadastro.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame_cadastro, text="Registrar Entrada", command=self.registrar_entrada).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_cadastro, text="Limpar", command=self.limpar_campos_lote).pack(side=tk.LEFT, padx=5)
        
        # Frame de edição (direita)
        frame_edicao = ttk.LabelFrame(frame_superior, text="Editar Lote")
        frame_edicao.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Campos do formulário de edição
        ttk.Label(frame_edicao, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.editar_combo_produto = AutocompleteCombobox(frame_edicao, state='readonly')
        self.editar_combo_produto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.editar_combo_produto['width'] = 50
        
        ttk.Label(frame_edicao, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.editar_lote_quantidade = ttk.Entry(frame_edicao)
        self.editar_lote_quantidade.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_edicao, text="Valor Unitário:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.editar_lote_valor = ttk.Entry(frame_edicao)
        self.editar_lote_valor.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(frame_edicao, text="Fornecedor:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.editar_lote_fornecedor = ttk.Entry(frame_edicao, width=40)
        self.editar_lote_fornecedor.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(frame_edicao, text="Nº Nota Fiscal:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.editar_lote_nota = ttk.Entry(frame_edicao)
        self.editar_lote_nota.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Botão de salvar edição
        btn_salvar_edicao = ttk.Button(frame_edicao, text="Salvar Alterações", command=self.salvar_edicao_lote)
        btn_salvar_edicao.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Variável para armazenar o ID do lote sendo editado
        self.lote_editando_id = None
        
        # Frame inferior para lista de lotes
        frame_lista = ttk.LabelFrame(frame_principal, text="Lotes Cadastrados")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        self.tree_lotes = ttk.Treeview(frame_lista, columns=('ID', 'Produto', 'Quantidade', 'Valor', 'Fornecedor', 'Entrada'), show='headings')
        self.tree_lotes.heading('ID', text='ID')
        self.tree_lotes.heading('Produto', text='Produto')
        self.tree_lotes.heading('Quantidade', text='Quantidade')
        self.tree_lotes.heading('Valor', text='Valor Unitário')
        self.tree_lotes.heading('Fornecedor', text='Fornecedor')
        self.tree_lotes.heading('Entrada', text='Data Entrada')
        
        for col in ('ID', 'Quantidade', 'Valor'):
            self.tree_lotes.column(col, width=80, anchor='e')
        self.tree_lotes.column('Produto', width=200, anchor=tk.CENTER)
        self.tree_lotes.column('Fornecedor', width=150, anchor=tk.CENTER)
        self.tree_lotes.column('Entrada', width=120, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_lotes.yview)
        hsb = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree_lotes.xview)
        self.tree_lotes.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_lotes.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Carregar produtos no combobox
        self.carregar_produtos_combobox()
        # Carregar lotes
        self.carregar_lotes()
        
        # Bind para seleção
        self.tree_lotes.bind('<<TreeviewSelect>>', self.selecionar_lote)

    def selecionar_lote(self, event):
        selected = self.tree_lotes.focus()
        if not selected:
            return
            
        values = self.tree_lotes.item(selected, 'values')
        self.lote_editando_id = values[0]
        
        # Preencher campos de edição
        # Primeiro carrega todos os produtos no combobox de edição
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_produto, nome FROM produto ORDER BY nome")
            produtos = cursor.fetchall()
            produtos_formatados = [f"{p[0]} - {p[1]}" for p in produtos]
            self.editar_combo_produto.set_completion_list(produtos_formatados)
            
            # Buscar detalhes completos do lote
            cursor.execute("""
                SELECT l.id_produto, l.quantidade, l.valor_unitario, l.fornecedor, l.numero_nota
                FROM lote l
                WHERE l.id_lote = %s
            """, (self.lote_editando_id,))
            lote = cursor.fetchone()
            
            # Encontrar o produto correspondente no combobox
            produto_str = None
            for p in produtos_formatados:
                if p.startswith(f"{lote[0]} - "):
                    produto_str = p
                    break
                    
            if produto_str:
                self.editar_combo_produto.set(produto_str)
            
            self.editar_lote_quantidade.delete(0, tk.END)
            self.editar_lote_quantidade.insert(0, lote[1])
            
            self.editar_lote_valor.delete(0, tk.END)
            self.editar_lote_valor.insert(0, lote[2])
            
            self.editar_lote_fornecedor.delete(0, tk.END)
            self.editar_lote_fornecedor.insert(0, lote[3])
            
            self.editar_lote_nota.delete(0, tk.END)
            self.editar_lote_nota.insert(0, lote[4] if lote[4] else "")
            
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar detalhes do lote:\n{str(e)}")
        finally:
            conn.close()

    def salvar_edicao_lote(self):
        if not self.lote_editando_id:
            messagebox.showwarning("Aviso", "Nenhum lote selecionado para edição!")
            return
            
        produto_str = self.editar_combo_produto.get()
        if not produto_str:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
            
        try:
            produto_id = int(produto_str.split(' - ')[0])
        except:
            messagebox.showwarning("Aviso", "Selecione um produto válido!")
            return
            
        try:
            quantidade = float(self.editar_lote_quantidade.get())
            valor_unitario = float(self.editar_lote_valor.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade e valor unitário devem ser números válidos!")
            return
            
        fornecedor = self.editar_lote_fornecedor.get().strip()
        nota_fiscal = self.editar_lote_nota.get().strip()
        
        if not fornecedor:
            messagebox.showwarning("Aviso", "Fornecedor é obrigatório!")
            return
            
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lote 
                SET id_produto = %s, 
                    quantidade = %s, 
                    valor_unitario = %s, 
                    fornecedor = %s, 
                    numero_nota = %s
                WHERE id_lote = %s
            """, (produto_id, quantidade, valor_unitario, fornecedor, nota_fiscal if nota_fiscal else None, self.lote_editando_id))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Lote atualizado com sucesso!")
            
            # Atualizar as listas
            self.carregar_lotes()
            self.carregar_lotes_combobox()
            self.carregar_lotes_disponiveis()
            self.carregar_estoque_consolidado()
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar lote:\n{str(e)}")
        finally:
            conn.close()
    
    def criar_aba_movimentacoes(self):
        # Frame de saída
        frame_saida = ttk.LabelFrame(self.aba_movimentacoes, text="Saída de Estoque")
        frame_saida.pack(fill=tk.X, padx=10, pady=5)
        
        # Abas para métodos de saída
        notebook_saida = ttk.Notebook(frame_saida)
        notebook_saida.pack(fill=tk.X, padx=5, pady=5)
        
        # Aba PEPS
        aba_peps = ttk.Frame(notebook_saida)
        notebook_saida.add(aba_peps, text="PEPS")
        
        ttk.Label(aba_peps, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_produto_peps = AutocompleteCombobox(aba_peps)
        self.combo_produto_peps.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(aba_peps, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.saida_quantidade_peps = ttk.Entry(aba_peps)
        self.saida_quantidade_peps.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(aba_peps, text="OS:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.saida_os_peps = ttk.Entry(aba_peps)
        self.saida_os_peps.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(aba_peps, text="Responsável:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.saida_responsavel_peps = ttk.Entry(aba_peps)
        self.saida_responsavel_peps.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(aba_peps, text="Registrar Saída (PEPS)", command=self.registrar_saida_peps).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Aba Manual
        aba_manual = ttk.Frame(notebook_saida)
        notebook_saida.add(aba_manual, text="Manual")
        
        ttk.Label(aba_manual, text="Lote:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_lote_manual = ttk.Combobox(aba_manual, state="readonly", width=40)
        self.combo_lote_manual.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(aba_manual, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.saida_quantidade_manual = ttk.Entry(aba_manual)
        self.saida_quantidade_manual.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(aba_manual, text="OS:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.saida_os_manual = ttk.Entry(aba_manual)
        self.saida_os_manual.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(aba_manual, text="Responsável:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.saida_responsavel_manual = ttk.Entry(aba_manual)
        self.saida_responsavel_manual.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(aba_manual, text="Registrar Saída (Manual)", command=self.registrar_saida_manual).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Carregar comboboxes
        self.carregar_produtos_combobox_peps()
        self.carregar_lotes_combobox()
        
        # Lista de movimentações
        frame_lista = ttk.LabelFrame(self.aba_movimentacoes, text="Histórico de Movimentações")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Treeview
        self.tree_movimentacoes = ttk.Treeview(frame_lista, columns=('ID', 'Data', 'Tipo', 'Produto', 'Quantidade', 'OS', 'Responsável', 'Método'), show='headings')
        self.tree_movimentacoes.heading('ID', text='ID')
        self.tree_movimentacoes.heading('Data', text='Data')
        self.tree_movimentacoes.heading('Tipo', text='Tipo')
        self.tree_movimentacoes.heading('Produto', text='Produto')
        self.tree_movimentacoes.heading('Quantidade', text='Quantidade')
        self.tree_movimentacoes.heading('OS', text='OS')
        self.tree_movimentacoes.heading('Responsável', text='Responsável')
        self.tree_movimentacoes.heading('Método', text='Método')
        
        for col in ('ID', 'Quantidade'):
            self.tree_movimentacoes.column(col, width=60, anchor='e')
        self.tree_movimentacoes.column('Data', width=120, anchor=tk.CENTER)
        self.tree_movimentacoes.column('Tipo', width=80, anchor=tk.CENTER)
        self.tree_movimentacoes.column('Produto', width=150, anchor=tk.CENTER)
        self.tree_movimentacoes.column('OS', width=100, anchor=tk.CENTER)
        self.tree_movimentacoes.column('Responsável', width=120, anchor=tk.CENTER)
        self.tree_movimentacoes.column('Método', width=80, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_movimentacoes.yview)
        hsb = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree_movimentacoes.xview)
        self.tree_movimentacoes.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_movimentacoes.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Carregar movimentações
        self.carregar_movimentacoes()

    def criar_aba_consultas(self):
        # Frame de consultas
        frame_consultas = ttk.LabelFrame(self.aba_consultas, text="Consultas")
        frame_consultas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Abas para diferentes consultas
        notebook_consultas = ttk.Notebook(frame_consultas)
        notebook_consultas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba Estoque Consolidado
        aba_estoque = ttk.Frame(notebook_consultas)
        notebook_consultas.add(aba_estoque, text="Estoque Consolidado")
        
        # Frame de busca e botão de exclusão
        frame_busca_estoque = ttk.Frame(aba_estoque)
        frame_busca_estoque.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_busca_estoque, text="Buscar Produto:").pack(side=tk.LEFT, padx=5)
        self.entry_busca_estoque = ttk.Entry(frame_busca_estoque)
        self.entry_busca_estoque.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_busca_estoque.bind('<KeyRelease>', self.filtrar_estoque_consolidado)
        
        # Botão para excluir produto selecionado
        btn_excluir = ttk.Button(frame_busca_estoque, text="Excluir Produto", 
                                command=self.excluir_produto_selecionado)
        btn_excluir.pack(side=tk.RIGHT, padx=5)
        
        # Treeview para estoque consolidado
        self.tree_estoque = ttk.Treeview(aba_estoque, columns=('ID', 'Produto', 'Unidade', 'Saldo'), show='headings')
        self.tree_estoque.heading('ID', text='', anchor=tk.W)
        self.tree_estoque.heading('Produto', text='Produto')
        self.tree_estoque.heading('Unidade', text='Unidade')
        self.tree_estoque.heading('Saldo', text='Saldo Disponível')
        
        self.tree_estoque.column('ID', width=0, stretch=tk.NO)
        self.tree_estoque.column('Produto', width=200, anchor=tk.CENTER)
        self.tree_estoque.column('Unidade', width=50, anchor=tk.CENTER)
        self.tree_estoque.column('Saldo', width=80, anchor=tk.CENTER)
      
        self.tree_estoque.pack(fill=tk.BOTH, expand=True)
        
        # Aba Lotes Disponíveis
        aba_lotes = ttk.Frame(notebook_consultas)
        notebook_consultas.add(aba_lotes, text="Lotes Disponíveis")
        
        # Adicionando campo de busca para lotes
        frame_busca_lotes = ttk.Frame(aba_lotes)
        frame_busca_lotes.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_busca_lotes, text="Buscar Produto:").pack(side=tk.LEFT, padx=5)
        self.entry_busca_lotes = ttk.Entry(frame_busca_lotes)
        self.entry_busca_lotes.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_busca_lotes.bind('<KeyRelease>', self.filtrar_lotes_disponiveis)
        
        # Treeview para lotes disponíveis
        self.tree_lotes_disponiveis = ttk.Treeview(aba_lotes, columns=('ID', 'Produto', 'Unidade', 'Saldo', 'Entrada', 'Fornecedor'), show='headings')
        self.tree_lotes_disponiveis.heading('ID', text='ID')
        self.tree_lotes_disponiveis.heading('Produto', text='Produto')
        self.tree_lotes_disponiveis.heading('Unidade', text='Unidade')
        self.tree_lotes_disponiveis.heading('Saldo', text='Saldo')
        self.tree_lotes_disponiveis.heading('Entrada', text='Data Entrada')
        self.tree_lotes_disponiveis.heading('Fornecedor', text='Fornecedor')
        
        self.tree_lotes_disponiveis.column('ID', width=50, anchor='e')
        self.tree_lotes_disponiveis.column('Produto', width=200, anchor=tk.CENTER)
        self.tree_lotes_disponiveis.column('Unidade', width=80, anchor=tk.CENTER)
        self.tree_lotes_disponiveis.column('Saldo', width=80, anchor=tk.CENTER)
        self.tree_lotes_disponiveis.column('Entrada', width=100, anchor=tk.CENTER)
        self.tree_lotes_disponiveis.column('Fornecedor', width=150, anchor=tk.CENTER)
        
        vsb2 = ttk.Scrollbar(aba_lotes, orient="vertical", command=self.tree_lotes_disponiveis.yview)
        hsb2 = ttk.Scrollbar(aba_lotes, orient="horizontal", command=self.tree_lotes_disponiveis.xview)
        self.tree_lotes_disponiveis.configure(yscrollcommand=vsb2.set, xscrollcommand=hsb2.set)
        
        self.tree_lotes_disponiveis.pack(fill=tk.BOTH, expand=True)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)
        hsb2.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Carregar consultas
        self.carregar_estoque_consolidado()
        self.carregar_lotes_disponiveis()
        
        # Bind para seleção na treeview
        self.tree_estoque.bind('<<TreeviewSelect>>', self.selecionar_produto_consulta)

    def selecionar_produto_consulta(self, event):
        """Armazena o ID do produto selecionado na treeview de estoque consolidado"""
        selected = self.tree_estoque.focus()
        if selected:
            self.produto_selecionado_id = self.tree_estoque.item(selected, 'values')[0]

    def excluir_produto_selecionado(self):
        """Exclui o produto selecionado na treeview de estoque consolidado"""
        if not hasattr(self, 'produto_selecionado_id') or not self.produto_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir!")
            return
        
        # Confirmar com o usuário
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este produto?\nEsta ação não pode ser desfeita."):
            return
        
        conn = self.conectar_banco()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Verificar se existem lotes associados ao produto
            cursor.execute("SELECT COUNT(*) FROM lote WHERE id_produto = %s", (self.produto_selecionado_id,))
            lotes_count = cursor.fetchone()[0]
            
            if lotes_count > 0:
                messagebox.showwarning("Aviso", 
                    "Não é possível excluir este produto pois existem lotes associados a ele.\n"
                    "Exclua os lotes primeiro.")
                return
            
            # Excluir o produto
            cursor.execute("DELETE FROM produto WHERE id_produto = %s", (self.produto_selecionado_id,))
            conn.commit()
            
            messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            
            # Atualizar as listas
            self.carregar_estoque_consolidado()
            self.carregar_produtos()
            self.carregar_produtos_combobox()
            self.carregar_produtos_combobox_peps()
            
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao excluir produto:\n{str(e)}")
        finally:
            conn.close()
            # Limpar a seleção
            if hasattr(self, 'produto_selecionado_id'):
                del self.produto_selecionado_id

    def carregar_lotes_disponiveis(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    l.id_lote,
                    p.nome,
                    p.unidade_medida,
                    l.quantidade - COALESCE((
                        SELECT SUM(m.quantidade)
                        FROM movimentacao m
                        WHERE m.id_lote = l.id_lote AND m.tipo = 'SAIDA'
                    ), 0) as saldo,
                    to_char(l.data_entrada, 'DD/MM/YYYY'),
                    l.fornecedor
                FROM lote l
                JOIN produto p ON l.id_produto = p.id_produto
                WHERE l.quantidade - COALESCE((
                    SELECT SUM(m.quantidade)
                    FROM movimentacao m
                    WHERE m.id_lote = l.id_lote AND m.tipo = 'SAIDA'
                ), 0) > 0
                ORDER BY l.data_entrada
            """)
            rows = cursor.fetchall()
            
            # Limpar treeview
            self.tree_lotes_disponiveis.delete(*self.tree_lotes_disponiveis.get_children())
            
            # Armazenar os dados para filtro
            self._dados_lotes_disponiveis = rows
            
            # Inserir novos dados
            for row in rows:
                self.tree_lotes_disponiveis.insert('', tk.END, values=row)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar lotes disponíveis:\n{str(e)}")
        finally:
            conn.close()

    def filtrar_estoque_consolidado(self, event=None):
        termo = self.entry_busca_estoque.get().lower()
        
        # Limpar a treeview
        self.tree_estoque.delete(*self.tree_estoque.get_children())
        
        # Reinserir apenas os itens que correspondem ao filtro
        for row in getattr(self, '_dados_estoque', []):
            if termo in row[1].lower():  # row[1] é o nome do produto
                self.tree_estoque.insert('', tk.END, values=row)

    def filtrar_lotes_disponiveis(self, event=None):
        termo = self.entry_busca_lotes.get().lower()
        
        # Limpar a treeview
        self.tree_lotes_disponiveis.delete(*self.tree_lotes_disponiveis.get_children())
        
        # Reinserir apenas os itens que correspondem ao filtro
        for row in getattr(self, '_dados_lotes_disponiveis', []):
            if termo in row[1].lower():  # row[1] é o nome do produto
                self.tree_lotes_disponiveis.insert('', tk.END, values=row)
        
    # Métodos para Produtos
    def carregar_produtos(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_produto, nome, unidade_medida FROM produto ORDER BY nome")
            rows = cursor.fetchall()
            
            # Limpar treeview
            for item in self.tree_produtos.get_children():
                self.tree_produtos.delete(item)
                
            # Inserir novos dados
            for row in rows:
                self.tree_produtos.insert('', tk.END, values=row)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
        finally:
            conn.close()
    
    def cadastrar_produto(self):
        nome = self.prod_nome.get().strip()
        unidade = self.prod_unidade.get().strip()  
        
        if not nome or not unidade:
            messagebox.showwarning("Aviso", "Nome e unidade de medida são obrigatórios!")
            return
            
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO produto (nome, unidade_medida) VALUES (%s, %s)",  
                (nome, unidade)
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            self.limpar_campos_produto()
            self.carregar_produtos()
            self.carregar_produtos_combobox()
            self.carregar_produtos_combobox_peps()
            self.carregar_estoque_consolidado()
            self.carregar_lotes_disponiveis()
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao cadastrar produto:\n{str(e)}")
        finally:
            conn.close()
    
    def limpar_campos_produto(self):
        self.prod_nome.delete(0, tk.END)
        self.prod_unidade.delete(0, tk.END)
    
    def carregar_produtos_combobox(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_produto, nome FROM produto ORDER BY nome")
            produtos = cursor.fetchall()
            
            produtos_formatados = [f"{p[0]} - {p[1]}" for p in produtos]
            
            self.combo_produto.set_completion_list(produtos_formatados)
            
            if produtos_formatados:
                self.combo_produto.set(produtos_formatados[0])
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
        finally:
            conn.close()
    
    def carregar_produtos_combobox_peps(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_produto, nome FROM produto ORDER BY nome")
            produtos = cursor.fetchall()
            
            # Formatar como "ID - Nome" igual às outras combobox
            produtos_formatados = [f"{p[0]} - {p[1]}" for p in produtos]
            
            self.combo_produto_peps.set_completion_list(produtos_formatados)
            
            if produtos_formatados:
                self.combo_produto_peps.set(produtos_formatados[0])
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
        finally:
            conn.close()
    
    # Métodos para Lotes
    def carregar_lotes(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id_lote, p.nome, l.quantidade, l.valor_unitario, l.fornecedor, 
                       to_char(l.data_entrada, 'DD/MM/YYYY HH24:MI')
                FROM lote l
                JOIN produto p ON l.id_produto = p.id_produto
                ORDER BY l.data_entrada DESC
            """)
            rows = cursor.fetchall()
            
            # Limpar treeview
            for item in self.tree_lotes.get_children():
                self.tree_lotes.delete(item)
                
            # Inserir novos dados
            for row in rows:
                self.tree_lotes.insert('', tk.END, values=row)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar lotes:\n{str(e)}")
        finally:
            conn.close()
    
    def registrar_entrada(self):
        produto_str = self.combo_produto.get()
        if not produto_str:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
            
        try:
            produto_id = int(produto_str.split(' - ')[0])
        except:
            messagebox.showwarning("Aviso", "Selecione um produto válido!")
            return
            
        try:
            quantidade = float(self.lote_quantidade.get())
            valor_unitario = float(self.lote_valor.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade e valor unitário devem ser números válidos!")
            return
            
        fornecedor = self.lote_fornecedor.get().strip()
        nota_fiscal = self.lote_nota.get().strip()
        
        if not fornecedor:
            messagebox.showwarning("Aviso", "Fornecedor é obrigatório!")
            return
            
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT entrada_lote(%s, %s, %s, %s, %s)
            """, (produto_id, quantidade, valor_unitario, fornecedor, nota_fiscal))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            messagebox.showinfo("Sucesso", resultado)
            self.limpar_campos_lote()
            self.carregar_lotes()
            self.carregar_lotes_combobox()
            self.carregar_lotes_disponiveis()
            self.carregar_estoque_consolidado()
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao registrar entrada de lote:\n{str(e)}")
        finally:
            conn.close()
    
    def limpar_campos_lote(self):
        self.lote_quantidade.delete(0, tk.END)
        self.lote_valor.delete(0, tk.END)
        self.lote_fornecedor.delete(0, tk.END)
        self.lote_nota.delete(0, tk.END)
    
    def carregar_lotes_combobox(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.id_lote, p.nome, l.quantidade - COALESCE((
                    SELECT SUM(m.quantidade)
                    FROM movimentacao m
                    WHERE m.id_lote = l.id_lote AND m.tipo = 'SAIDA'
                ), 0) as saldo
                FROM lote l
                JOIN produto p ON l.id_produto = p.id_produto
                WHERE l.quantidade - COALESCE((
                    SELECT SUM(m.quantidade)
                    FROM movimentacao m
                    WHERE m.id_lote = l.id_lote AND m.tipo = 'SAIDA'
                ), 0) > 0
                ORDER BY l.data_entrada
            """)
            lotes = cursor.fetchall()
            
            # Formatar para exibição no combobox (ID - Produto - Saldo)
            lotes_formatados = [f"{l[0]} - {l[1]} (Saldo: {l[2]})" for l in lotes]
            self.combo_lote_manual['values'] = lotes_formatados
            if lotes_formatados:
                self.combo_lote_manual.current(0)
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar lotes disponíveis:\n{str(e)}")
        finally:
            conn.close()
    
    # Métodos para Movimentações
    def carregar_movimentacoes(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id_movimentacao, 
                       to_char(m.data_movimentacao, 'DD/MM/YYYY HH24:MI'),
                       m.tipo,
                       p.nome,
                       m.quantidade,
                       m.os,
                       m.responsavel,
                       m.metodo
                FROM movimentacao m
                JOIN lote l ON m.id_lote = l.id_lote
                JOIN produto p ON l.id_produto = p.id_produto
                ORDER BY m.data_movimentacao DESC
            """)
            rows = cursor.fetchall()
            
            # Limpar treeview
            for item in self.tree_movimentacoes.get_children():
                self.tree_movimentacoes.delete(item)
                
            # Inserir novos dados
            for row in rows:
                self.tree_movimentacoes.insert('', tk.END, values=row)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar movimentações:\n{str(e)}")
        finally:
            conn.close()
    
    def registrar_saida_peps(self):
        produto_str = self.combo_produto_peps.get()
        if not produto_str:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
            
        try:
            # Extrai o ID do formato "ID - Nome"
            produto_id = int(produto_str.split(' - ')[0])
        except:
            messagebox.showwarning("Aviso", "Selecione um produto válido!")
            return
            
        try:
            quantidade = float(self.saida_quantidade_peps.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade deve ser um número válido!")
            return
            
        os_numero = self.saida_os_peps.get().strip()
        responsavel = self.saida_responsavel_peps.get().strip()
        
        if not os_numero or not responsavel:
            messagebox.showwarning("Aviso", "Número da OS e responsável são obrigatórios!")
            return
            
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT retirada_peps(%s, %s, %s, %s)", 
                        (produto_id, quantidade, responsavel, os_numero))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            messagebox.showinfo("Sucesso", resultado)
            self.saida_quantidade_peps.delete(0, tk.END)
            self.saida_os_peps.delete(0, tk.END)
            self.saida_responsavel_peps.delete(0, tk.END)
            
            # Atualizar as listas
            self.carregar_lotes()
            self.carregar_movimentacoes()
            self.carregar_lotes_combobox()
            self.carregar_lotes_disponiveis()
            self.carregar_estoque_consolidado()
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao registrar saída de estoque (PEPS):\n{str(e)}")
        finally:
            conn.close()
    
    def registrar_saida_manual(self):
        # Obter ID do lote do combobox (formato: "ID - Produto - Saldo: X")
        lote_str = self.combo_lote_manual.get()
        if not lote_str:
            messagebox.showwarning("Aviso", "Selecione um lote!")
            return
            
        try:
            lote_id = int(lote_str.split(' - ')[0])
        except:
            messagebox.showwarning("Aviso", "Selecione um lote válido!")
            return
            
        try:
            quantidade = float(self.saida_quantidade_manual.get())
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade deve ser um número válido!")
            return
            
        os_numero = self.saida_os_manual.get().strip()
        responsavel = self.saida_responsavel_manual.get().strip()
        
        if not os_numero or not responsavel:
            messagebox.showwarning("Aviso", "Número da OS e responsável são obrigatórios!")
            return
            
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Chamar a função saida_lote_manual
            cursor.execute("SELECT retirada_manual(%s, %s, %s, %s)", 
            (lote_id, quantidade, responsavel, os_numero))
            
            resultado = cursor.fetchone()[0]
            conn.commit()
            
            messagebox.showinfo("Sucesso", resultado)
            self.saida_quantidade_manual.delete(0, tk.END)
            self.saida_os_manual.delete(0, tk.END)
            self.saida_responsavel_manual.delete(0, tk.END)
            
            # Atualizar as listas
            self.carregar_lotes()
            self.carregar_movimentacoes()
            self.carregar_lotes_combobox()
            self.carregar_lotes_disponiveis()
            self.carregar_estoque_consolidado()
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao registrar saída de estoque (Manual):\n{str(e)}")
        finally:
            conn.close()
    
    # Métodos para Consultas
    def carregar_estoque_consolidado(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.id_produto,
                    p.nome,
                    p.unidade_medida,
                    COALESCE((
                        SELECT SUM(l.quantidade)
                        FROM lote l
                        WHERE l.id_produto = p.id_produto
                    ), 0) - COALESCE((
                        SELECT SUM(m.quantidade)
                        FROM movimentacao m
                        JOIN lote l ON m.id_lote = l.id_lote
                        WHERE l.id_produto = p.id_produto AND m.tipo = 'SAIDA'
                    ), 0) as saldo
                FROM produto p
                ORDER BY p.nome
            """)
            rows = cursor.fetchall()
            
            # Limpar treeview
            self.tree_estoque.delete(*self.tree_estoque.get_children())
            
            # Armazenar os dados para filtro
            self._dados_estoque = rows
            
            # Inserir novos dados
            for row in rows:
                self.tree_estoque.insert('', tk.END, values=row)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar estoque consolidado:\n{str(e)}")
        finally:
            conn.close()

# Função principal para executar a aplicação
def main():
    root = tk.Tk()
    app = SistemaEstoque(root)
    root.mainloop()

if __name__ == "__main__":
    main()