import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime
from decimal import Decimal, InvalidOperation

class ModuloOrcamento:
    def __init__(self, parent_frame, conn_config, conn=None, usuario_logado=None):
        self.parent = parent_frame
        self.conn_config = conn_config
        self.conn = conn   
        self.cursor = self.conn.cursor() if conn else None
        self.usuario_logado = usuario_logado
        
        # Não crie uma nova conexão se já foi fornecida
        if not self.conn:
            self.criar_conexao()
        
        self.criar_interface()

    def criar_conexao(self):
        try:
            self.conn = psycopg2.connect(**self.conn_config)
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha na conexão com o banco:\n{str(e)}")
            raise

    def criar_interface(self):
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Cria o notebook
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cria as abas
        self.aba_cadastro = ttk.Frame(self.notebook)
        self.aba_alteracao = ttk.Frame(self.notebook) 
        self.aba_exclusao = ttk.Frame(self.notebook)
        self.aba_visualizacao = ttk.Frame(self.notebook)

        # Adiciona as abas ao notebook
        self.notebook.add(self.aba_cadastro, text="Cadastrar")
        self.notebook.add(self.aba_alteracao, text="Alterar")
        self.notebook.add(self.aba_exclusao, text="Excluir")
        self.notebook.add(self.aba_visualizacao, text="Visualizar")

        # Configura o conteúdo de cada aba
        self.criar_aba_cadastro()
        self.criar_aba_alteracao()
        self.criar_aba_exclusao()
        self.criar_aba_visualizacao()

    def criar_aba_cadastro(self):
        form_frame = ttk.LabelFrame(self.aba_cadastro, text=" Cadastro de Orçamento", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Configuração do grid
        for i in range(10):  # 10 linhas
            form_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(4):  # 4 colunas
            form_frame.grid_columnconfigure(j, weight=1)

        # Linha 0 - N° OS e Data
        ttk.Label(form_frame, text="N° OS Projeto:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os = ttk.Entry(form_frame, width=20)
        self.entry_os.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Data Orçamento:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_data = ttk.Entry(form_frame, width=20)
        self.entry_data.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Linha 1 - Mão de Obra e Alimentação
        ttk.Label(form_frame, text="Mão de Obra(R$):", font=('Arial', 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_mao_de_obra = ttk.Entry(form_frame, width=20)
        self.entry_mao_de_obra.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.entry_mao_de_obra.insert(0, "0.00")

        ttk.Label(form_frame, text="Alimentação(R$):", font=('Arial', 10)).grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_alimentacao = ttk.Entry(form_frame, width=20)
        self.entry_alimentacao.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.entry_alimentacao.insert(0, "0.00")

        # Linha 2 - Hospedagem e Viagem
        ttk.Label(form_frame, text="Hospedagem(R$):", font=('Arial', 10)).grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_hospedagem = ttk.Entry(form_frame, width=20)
        self.entry_hospedagem.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_hospedagem.insert(0, "0.00")

        ttk.Label(form_frame, text="Viagem(R$):", font=('Arial', 10)).grid(
            row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_viagem = ttk.Entry(form_frame, width=20)
        self.entry_viagem.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.entry_viagem.insert(0, "0.00")

        # Linha 3 - Segurança e Material
        ttk.Label(form_frame, text="Segurança Trabalho(R$):", font=('Arial', 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_seguranca_trabalho = ttk.Entry(form_frame, width=20)
        self.entry_seguranca_trabalho.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.entry_seguranca_trabalho.insert(0, "0.00")

        ttk.Label(form_frame, text="Material(R$):", font=('Arial', 10)).grid(
            row=3, column=2, sticky="e", padx=5, pady=5)
        self.entry_material = ttk.Entry(form_frame, width=20)
        self.entry_material.grid(row=3, column=3, sticky="w", padx=5, pady=5)
        self.entry_material.insert(0, "0.00")

        # Linha 4 - Equipamento e Andaime
        ttk.Label(form_frame, text="Equipamento(R$):", font=('Arial', 10)).grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_equipamento = ttk.Entry(form_frame, width=20)
        self.entry_equipamento.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.entry_equipamento.insert(0, "0.00")

        ttk.Label(form_frame, text="Andaime(R$):", font=('Arial', 10)).grid(
            row=4, column=2, sticky="e", padx=5, pady=5)
        self.entry_andaime = ttk.Entry(form_frame, width=20)
        self.entry_andaime.grid(row=4, column=3, sticky="w", padx=5, pady=5)
        self.entry_andaime.insert(0, "0.00")

        # Linha 5 - Documentação e Outros
        ttk.Label(form_frame, text="Documentação(R$):", font=('Arial', 10)).grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_documentacao = ttk.Entry(form_frame, width=20)
        self.entry_documentacao.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.entry_documentacao.insert(0, "0.00")

        ttk.Label(form_frame, text="Outros(R$):", font=('Arial', 10)).grid(
            row=5, column=2, sticky="e", padx=5, pady=5)
        self.entry_outros = ttk.Entry(form_frame, width=20)
        self.entry_outros.grid(row=5, column=3, sticky="w", padx=5, pady=5)
        self.entry_outros.insert(0, "0.00")

        # Linha 6 - Total
        ttk.Label(form_frame, text="Total(R$):", font=('Arial', 10, 'bold')).grid(
            row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_total = ttk.Entry(form_frame, width=20, state='readonly', font=('Arial', 10, 'bold'))
        self.entry_total.grid(row=6, column=1, sticky="w", padx=5, pady=5)
        self.entry_total.insert(0, "R$ 0.00")

        # Frame para botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=4, pady=(15, 5))

        # Botão Salvar
        btn_salvar = ttk.Button(btn_frame, text="Salvar Orçamento", 
                            command=self.salvar_orcamento,
                            style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        # Botão Limpar
        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                            command=self.limpar_campos_cadastro)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Configura cálculo automático do total
        campos_valores = [
            self.entry_mao_de_obra, self.entry_alimentacao, self.entry_hospedagem,
            self.entry_viagem, self.entry_seguranca_trabalho, self.entry_material,
            self.entry_equipamento, self.entry_andaime, self.entry_documentacao,
            self.entry_outros
        ]
        
        for campo in campos_valores:
            campo.bind('<KeyRelease>', self.calcular_total)

    def criar_aba_alteracao(self):

        # Container principal
        main_frame = ttk.Frame(self.aba_alteracao)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Seção de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Orçamento ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os_alt = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os_alt.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_orcamento_para_alteracao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Visualização rápida do orçamento encontrado
        self.tree_orcamento = ttk.Treeview(busca_frame, 
                                    columns=("OS", "Data", "Total"),
                                    show="headings",
                                    height=1)
        self.tree_orcamento.heading("OS", text="N° OS")
        self.tree_orcamento.heading("Data", text="Data Orçamento")
        self.tree_orcamento.heading("Total", text="Total")
        self.tree_orcamento.column("OS", width=100)
        self.tree_orcamento.column("Data", width=150)
        self.tree_orcamento.column("Total", width=150)
        self.tree_orcamento.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Seção de edição
        edit_frame = ttk.LabelFrame(main_frame, text=" Editar Orçamento ", padding=15)
        edit_frame.pack(fill=tk.BOTH, expand=True)

        # Configuração do grid
        for i in range(10):  # 10 linhas
            edit_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(4):  # 4 colunas
            edit_frame.grid_columnconfigure(j, weight=1)

        # Linha 0 - N° OS e Data
        ttk.Label(edit_frame, text="N° OS Projeto:", font=('Arial', 10)).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os_edit = ttk.Entry(edit_frame, width=20, state='readonly')
        self.entry_os_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(edit_frame, text="Data Orçamento:", font=('Arial', 10)).grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_data_edit = ttk.Entry(edit_frame, width=20)
        self.entry_data_edit.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Linha 1 - Mão de Obra e Alimentação
        ttk.Label(edit_frame, text="Mão de Obra(R$):", font=('Arial', 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_mao_de_obra_edit = ttk.Entry(edit_frame, width=20)
        self.entry_mao_de_obra_edit.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(edit_frame, text="Alimentação(R$):", font=('Arial', 10)).grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_alimentacao_edit = ttk.Entry(edit_frame, width=20)
        self.entry_alimentacao_edit.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Linha 2 - Hospedagem e Viagem
        ttk.Label(edit_frame, text="Hospedagem(R$):", font=('Arial', 10)).grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_hospedagem_edit = ttk.Entry(edit_frame, width=20)
        self.entry_hospedagem_edit.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(edit_frame, text="Viagem(R$):", font=('Arial', 10)).grid(
            row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_viagem_edit = ttk.Entry(edit_frame, width=20)
        self.entry_viagem_edit.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Linha 3 - Segurança e Material
        ttk.Label(edit_frame, text="Segurança Trabalho(R$):", font=('Arial', 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_seguranca_trabalho_edit = ttk.Entry(edit_frame, width=20)
        self.entry_seguranca_trabalho_edit.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(edit_frame, text="Material(R$):", font=('Arial', 10)).grid(
            row=3, column=2, sticky="e", padx=5, pady=5)
        self.entry_material_edit = ttk.Entry(edit_frame, width=20)
        self.entry_material_edit.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # Linha 4 - Equipamento e Andaime
        ttk.Label(edit_frame, text="Equipamento(R$):", font=('Arial', 10)).grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_equipamento_edit = ttk.Entry(edit_frame, width=20)
        self.entry_equipamento_edit.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(edit_frame, text="Andaime(R$):", font=('Arial', 10)).grid(
            row=4, column=2, sticky="e", padx=5, pady=5)
        self.entry_andaime_edit = ttk.Entry(edit_frame, width=20)
        self.entry_andaime_edit.grid(row=4, column=3, sticky="w", padx=5, pady=5)

        # Linha 5 - Documentação e Outros
        ttk.Label(edit_frame, text="Documentação(R$):", font=('Arial', 10)).grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_documentacao_edit = ttk.Entry(edit_frame, width=20)
        self.entry_documentacao_edit.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(edit_frame, text="Outros(R$):", font=('Arial', 10)).grid(
            row=5, column=2, sticky="e", padx=5, pady=5)
        self.entry_outros_edit = ttk.Entry(edit_frame, width=20)
        self.entry_outros_edit.grid(row=5, column=3, sticky="w", padx=5, pady=5)

        # Linha 6 - Total
        ttk.Label(edit_frame, text="Total(R$):", font=('Arial', 10, 'bold')).grid(
            row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_total_edit = ttk.Entry(edit_frame, width=20, state='readonly', font=('Arial', 10, 'bold'))
        self.entry_total_edit.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Frame de botões
        btn_frame = ttk.Frame(edit_frame)
        btn_frame.grid(row=7, column=0, columnspan=4, pady=(5, 5))

        btn_salvar = ttk.Button(btn_frame, text="Salvar Alterações",
                            command=self.salvar_alteracoes,
                            style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                            command=self.limpar_campos_edicao)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Configura cálculo automático do total
        campos_valores = [
            self.entry_mao_de_obra_edit, self.entry_alimentacao_edit, self.entry_hospedagem_edit,
            self.entry_viagem_edit, self.entry_seguranca_trabalho_edit, self.entry_material_edit,
            self.entry_equipamento_edit, self.entry_andaime_edit, self.entry_documentacao_edit,
            self.entry_outros_edit
        ]
        
        for campo in campos_valores:
            campo.bind('<KeyRelease>', self.calcular_total_edicao)

    def criar_aba_exclusao(self):
        # Container principal
        main_frame = ttk.Frame(self.aba_exclusao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Orçamento para Exclusão ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        # Campo de busca
        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_excluir = ttk.Entry(busca_frame, width=25)
        self.entry_busca_excluir.grid(row=0, column=1, padx=5, pady=5)

        # Botão de busca
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_orcamento_exclusao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Treeview para mostrar o orçamento encontrado
        columns = ("OS", "Data", "Total")
        self.tree_exclusao = ttk.Treeview(busca_frame, columns=columns, show="headings", height=1)
        
        # Configuração das colunas
        for col in columns:
            self.tree_exclusao.heading(col, text=col)
            self.tree_exclusao.column(col, width=120)
        
        self.tree_exclusao.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Frame de confirmação
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=(10, 0))

        # Botão de exclusão (inicialmente desabilitado)
        self.btn_excluir = ttk.Button(confirm_frame, text="Excluir Orçamento", 
                                    command=self.confirmar_exclusao,
                                    state='disabled',
                                    style='Danger.TButton')
        self.btn_excluir.pack(pady=10)

        # Status
        self.status_label_exclusao = ttk.Label(main_frame, text="", foreground='red')
        self.status_label_exclusao.pack()

        # Bind para tecla Enter
        self.entry_busca_excluir.bind('<Return>', lambda e: self.buscar_orcamento_exclusao())

    def criar_aba_visualizacao(self):
        form_frame = ttk.LabelFrame(self.aba_visualizacao, text=" Visualizar Orçamento", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Container principal
        main_frame = ttk.Frame(self.aba_visualizacao)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Seção de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Orçamento ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_visualizar = ttk.Entry(busca_frame, width=25)
        self.entry_busca_visualizar.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_orcamento_visualizacao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Seção de visualização
        view_frame = ttk.LabelFrame(main_frame, text=" Detalhes do Orçamento ", padding=15)
        view_frame.pack(fill=tk.BOTH, expand=True)

        # Configuração do grid
        for i in range(10):  # 10 linhas
            view_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(4):  # 4 colunas
            view_frame.grid_columnconfigure(j, weight=1)

        # Linha 0 - N° OS e Data
        ttk.Label(view_frame, text="N° OS Projeto:", font=('Arial', 10)).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_os_view.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(view_frame, text="Data Orçamento:", font=('Arial', 10)).grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_data_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_data_view.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Linha 1 - Mão de Obra e Alimentação
        ttk.Label(view_frame, text="Mão de Obra(R$):", font=('Arial', 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_mao_de_obra_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_mao_de_obra_view.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(view_frame, text="Alimentação(R$):", font=('Arial', 10)).grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_alimentacao_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_alimentacao_view.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Linha 2 - Hospedagem e Viagem
        ttk.Label(view_frame, text="Hospedagem(R$):", font=('Arial', 10)).grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_hospedagem_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_hospedagem_view.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(view_frame, text="Viagem(R$):", font=('Arial', 10)).grid(
            row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_viagem_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_viagem_view.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Linha 3 - Segurança e Material
        ttk.Label(view_frame, text="Segurança Trabalho(R$):", font=('Arial', 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_seguranca_trabalho_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_seguranca_trabalho_view.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(view_frame, text="Material(R$):", font=('Arial', 10)).grid(
            row=3, column=2, sticky="e", padx=5, pady=5)
        self.entry_material_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_material_view.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # Linha 4 - Equipamento e Andaime
        ttk.Label(view_frame, text="Equipamento(R$):", font=('Arial', 10)).grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_equipamento_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_equipamento_view.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(view_frame, text="Andaime(R$):", font=('Arial', 10)).grid(
            row=4, column=2, sticky="e", padx=5, pady=5)
        self.entry_andaime_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_andaime_view.grid(row=4, column=3, sticky="w", padx=5, pady=5)

        # Linha 5 - Documentação e Outros
        ttk.Label(view_frame, text="Documentação(R$):", font=('Arial', 10)).grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_documentacao_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_documentacao_view.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(view_frame, text="Outros(R$):", font=('Arial', 10)).grid(
            row=5, column=2, sticky="e", padx=5, pady=5)
        self.entry_outros_view = ttk.Entry(view_frame, width=20, state='readonly')
        self.entry_outros_view.grid(row=5, column=3, sticky="w", padx=5, pady=5)

        # Linha 6 - Total
        ttk.Label(view_frame, text="Total(R$):", font=('Arial', 10, 'bold')).grid(
            row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_total_view = ttk.Entry(view_frame, width=20, state='readonly', font=('Arial', 10, 'bold'))
        self.entry_total_view.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Bind para tecla Enter
        self.entry_busca_visualizar.bind('<Return>', lambda e: self.buscar_orcamento_visualizacao())

    # --- MÉTODOS PRINCIPAIS ---
    def calcular_total(self, event=None):
        """Calcula o total automaticamente na aba de cadastro"""
        try:
            total = Decimal(0)
            
            # Soma todos os valores dos campos
            campos = [
                self.entry_mao_de_obra, self.entry_alimentacao, self.entry_hospedagem,
                self.entry_viagem, self.entry_seguranca_trabalho, self.entry_material,
                self.entry_equipamento, self.entry_andaime, self.entry_documentacao,
                self.entry_outros
            ]
            
            for campo in campos:
                valor = campo.get().replace(',', '.').strip()
                if valor:
                    total += Decimal(valor)
            
            # Atualiza o campo total
            self.entry_total.config(state='normal')
            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, f"R$ {total:.2f}")
            self.entry_total.config(state='readonly')
            
        except (InvalidOperation, ValueError):
            # Se algum valor não puder ser convertido, mostra total como zero
            self.entry_total.config(state='normal')
            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, "R$ 0.00")
            self.entry_total.config(state='readonly')

    def calcular_total_edicao(self, event=None):
        """Calcula o total automaticamente na aba de edição"""
        try:
            total = Decimal(0)
            
            # Soma todos os valores dos campos
            campos = [
                self.entry_mao_de_obra_edit, self.entry_alimentacao_edit, self.entry_hospedagem_edit,
                self.entry_viagem_edit, self.entry_seguranca_trabalho_edit, self.entry_material_edit,
                self.entry_equipamento_edit, self.entry_andaime_edit, self.entry_documentacao_edit,
                self.entry_outros_edit
            ]
            
            for campo in campos:
                valor = campo.get().replace(',', '.').strip()
                if valor:
                    total += Decimal(valor)
            
            # Atualiza o campo total
            self.entry_total_edit.config(state='normal')
            self.entry_total_edit.delete(0, tk.END)
            self.entry_total_edit.insert(0, f"R$ {total:.2f}")
            self.entry_total_edit.config(state='readonly')
            
        except (InvalidOperation, ValueError):
            # Se algum valor não puder ser convertido, mostra total como zero
            self.entry_total_edit.config(state='normal')
            self.entry_total_edit.delete(0, tk.END)
            self.entry_total_edit.insert(0, "R$ 0.00")
            self.entry_total_edit.config(state='readonly')
    
    def salvar_orcamento(self):
        """Salva um novo orçamento no banco de dados"""
        try:
            # Validação básica
            if not self.entry_os.get():
                messagebox.showwarning("Aviso", "N° OS é obrigatório!")
                return

            # Converter valores monetários
            campos = {
                'mao_de_obra': self.entry_mao_de_obra.get(),
                'alimentacao': self.entry_alimentacao.get(),
                'hospedagem': self.entry_hospedagem.get(),
                'viagem': self.entry_viagem.get(),
                'seguranca_trabalho': self.entry_seguranca_trabalho.get(),
                'material': self.entry_material.get(),
                'equipamento': self.entry_equipamento.get(),
                'andaime': self.entry_andaime.get(),
                'documentacao': self.entry_documentacao.get(),
                'outros': self.entry_outros.get()
            }

            valores = {}
            total = Decimal(0)
            
            for campo, valor in campos.items():
                try:
                    valores[campo] = Decimal(valor.replace(',', '.')) if valor else Decimal(0)
                    total += valores[campo]
                except InvalidOperation:
                    messagebox.showerror("Erro", f"Valor inválido no campo {campo.replace('_', ' ')}")
                    return

            # Converter data
            try:
                data_orcamento = datetime.strptime(self.entry_data.get(), '%d/%m/%Y').date()
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                return

            # Inserir no banco de dados
            self.cursor.execute("""
                INSERT INTO orcamentos (
                    numero_os_projeto, data_orcamento, mao_de_obra, alimentacao,
                    hospedagem, viagem, seguranca_trabalho, material, equipamento,
                    andaime, documentacao, outros
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                self.entry_os.get(),
                data_orcamento,
                valores['mao_de_obra'],
                valores['alimentacao'],
                valores['hospedagem'],
                valores['viagem'],
                valores['seguranca_trabalho'],
                valores['material'],
                valores['equipamento'],
                valores['andaime'],
                valores['documentacao'],
                valores['outros']
            ))

            self.conn.commit()
            messagebox.showinfo("Sucesso", "Orçamento cadastrado com sucesso!")
            self.limpar_campos_cadastro()

        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar orçamento:\n{str(e)}")

    def buscar_orcamento_para_alteracao(self):
        """Busca um orçamento para edição"""
        os_numero = self.entry_busca_os_alt.get()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um número de OS!")
            return

        try:
            self.cursor.execute("""
                SELECT 
                    id_orcamento,
                    numero_os_projeto, 
                    data_orcamento, 
                    mao_de_obra, 
                    alimentacao,
                    hospedagem, 
                    viagem, 
                    seguranca_trabalho, 
                    material, 
                    equipamento,
                    andaime, 
                    documentacao, 
                    outros,
                    total
                FROM orcamentos 
                WHERE numero_os_projeto = %s
            """, (os_numero,))
            orcamento = self.cursor.fetchone()

            if orcamento:
                # Preenche a treeview de visualização rápida
                self.tree_orcamento.delete(*self.tree_orcamento.get_children())
                self.tree_orcamento.insert("", "end", values=(
                    orcamento[1],  # numero_os_projeto
                    orcamento[2].strftime('%d/%m/%Y') if orcamento[2] else "",  # data_orcamento
                    f"R$ {float(orcamento[13]):.2f}" if orcamento[13] else "R$ 0.00"  # total
                ))

                # Preenche os campos de edição
                self.preencher_campos_edicao(orcamento)
            else:
                messagebox.showinfo("Info", "Orçamento não encontrado!")

        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar orçamento:\n{str(e)}")

    def preencher_campos_edicao(self, orcamento):
        """Preenche os campos da aba de edição com os dados do orçamento"""
        # Dados básicos
        self.entry_os_edit.config(state='normal')
        self.entry_os_edit.delete(0, tk.END)
        self.entry_os_edit.insert(0, orcamento[1])  # numero_os_projeto (índice 1)
        self.entry_os_edit.config(state='readonly')

        # Data
        self.entry_data_edit.delete(0, tk.END)
        self.entry_data_edit.insert(0, orcamento[2].strftime('%d/%m/%Y') if orcamento[2] else "")

        # Campos de valores 
        campos = [
            ('mao_de_obra', 3),
            ('alimentacao', 4),
            ('hospedagem', 5),
            ('viagem', 6),
            ('seguranca_trabalho', 7),
            ('material', 8),
            ('equipamento', 9),
            ('andaime', 10),
            ('documentacao', 11),
            ('outros', 12)
        ]

        for campo, idx in campos:
            entry = getattr(self, f"entry_{campo}_edit")
            entry.delete(0, tk.END)
            entry.insert(0, f"{float(orcamento[idx]):.2f}" if orcamento[idx] is not None else "0.00")

        # Total (índice 13)
        self.entry_total_edit.config(state='normal')
        self.entry_total_edit.delete(0, tk.END)
        self.entry_total_edit.insert(0, f"R$ {float(orcamento[13]):.2f}" if orcamento[13] is not None else "R$ 0.00")
        self.entry_total_edit.config(state='readonly')

    def salvar_alteracoes(self):
        """Salva as alterações do orçamento no banco de dados"""
        try:
            numero_os = self.entry_os_edit.get()
            if not numero_os:
                messagebox.showwarning("Aviso", "Nenhum orçamento selecionado!")
                return

            # Converter valores monetários
            campos = {
                'mao_de_obra': self.entry_mao_de_obra_edit.get(),
                'alimentacao': self.entry_alimentacao_edit.get(),
                'hospedagem': self.entry_hospedagem_edit.get(),
                'viagem': self.entry_viagem_edit.get(),
                'seguranca_trabalho': self.entry_seguranca_trabalho_edit.get(),
                'material': self.entry_material_edit.get(),
                'equipamento': self.entry_equipamento_edit.get(),
                'andaime': self.entry_andaime_edit.get(),
                'documentacao': self.entry_documentacao_edit.get(),
                'outros': self.entry_outros_edit.get()
            }

            valores = {}
            total = Decimal(0)
            
            for campo, valor in campos.items():
                try:
                    valores[campo] = Decimal(valor.replace(',', '.')) if valor else Decimal(0)
                    total += valores[campo]
                except InvalidOperation:
                    messagebox.showerror("Erro", f"Valor inválido no campo {campo.replace('_', ' ')}")
                    return

            # Converter data
            try:
                data_orcamento = datetime.strptime(self.entry_data_edit.get(), '%d/%m/%Y').date()
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                return

            # Atualizar no banco de dados
            self.cursor.execute("""
                UPDATE orcamentos SET
                    data_orcamento = %s,
                    mao_de_obra = %s,
                    alimentacao = %s,
                    hospedagem = %s,
                    viagem = %s,
                    seguranca_trabalho = %s,
                    material = %s,
                    equipamento = %s,
                    andaime = %s,
                    documentacao = %s,
                    outros = %s
                WHERE numero_os_projeto = %s
            """, (
                data_orcamento,
                valores['mao_de_obra'],
                valores['alimentacao'],
                valores['hospedagem'],
                valores['viagem'],
                valores['seguranca_trabalho'],
                valores['material'],
                valores['equipamento'],
                valores['andaime'],
                valores['documentacao'],
                valores['outros'],
                numero_os
            ))

            self.conn.commit()
            messagebox.showinfo("Sucesso", "Orçamento atualizado com sucesso!")

        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar orçamento:\n{str(e)}")

    def buscar_orcamento_exclusao(self):
        """Busca um orçamento para exclusão"""
        os_numero = self.entry_busca_excluir.get()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um número de OS!")
            return

        try:
            self.cursor.execute("""
                SELECT numero_os_projeto, data_orcamento, total
                FROM orcamentos WHERE numero_os_projeto = %s
            """, (os_numero,))
            orcamento = self.cursor.fetchone()

            if orcamento:
                self.tree_exclusao.delete(*self.tree_exclusao.get_children())
                self.tree_exclusao.insert("", "end", values=(
                    orcamento[0],  # numero_os
                    orcamento[1].strftime('%d/%m/%Y'),  # data_orcamento
                    f"R$ {orcamento[2]:.2f}"  # total
                ))
                self.btn_excluir.config(state='normal')
            else:
                messagebox.showinfo("Info", "Orçamento não encontrado!")
                self.btn_excluir.config(state='disabled')

        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar orçamento:\n{str(e)}")

    def confirmar_exclusao(self):
        """Confirma e executa a exclusão do orçamento"""
        os_numero = self.entry_busca_excluir.get()
        if not os_numero:
            return

        if messagebox.askyesno("Confirmar", f"Excluir orçamento {os_numero}?"):
            try:
                self.cursor.execute("DELETE FROM orcamentos WHERE numero_os_projeto = %s", (os_numero,))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Orçamento excluído com sucesso!")
                self.limpar_campos_exclusao()
            except psycopg2.Error as e:
                self.conn.rollback()
                messagebox.showerror("Erro", f"Falha ao excluir orçamento:\n{str(e)}")

    def buscar_orcamento_visualizacao(self):
        """Busca um orçamento para visualização detalhada"""
        os_numero = self.entry_busca_visualizar.get()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um número de OS!")
            return

        try:
            # Primeiro limpa todos os campos
            self.limpar_campos_visualizacao()

            self.cursor.execute("""
                SELECT 
                    numero_os_projeto, 
                    data_orcamento, 
                    mao_de_obra, 
                    alimentacao,
                    hospedagem, 
                    viagem, 
                    seguranca_trabalho, 
                    material, 
                    equipamento,
                    andaime, 
                    documentacao, 
                    outros,
                    total
                FROM orcamentos WHERE numero_os_projeto = %s
            """, (os_numero,))
            orcamento = self.cursor.fetchone()

            if orcamento:
                print("Dados retornados:", orcamento)  # Debug
                
                # Preenche os campos básicos
                self.entry_os_view.config(state='normal')
                self.entry_os_view.delete(0, tk.END)
                self.entry_os_view.insert(0, orcamento[0])  # numero_os_projeto
                self.entry_os_view.config(state='readonly')

                self.entry_data_view.config(state='normal')
                self.entry_data_view.delete(0, tk.END)
                # Verifica se é uma data antes de formatar
                if orcamento[1] and hasattr(orcamento[1], 'strftime'):
                    self.entry_data_view.insert(0, orcamento[1].strftime('%d/%m/%Y'))
                else:
                    self.entry_data_view.insert(0, "")
                self.entry_data_view.config(state='readonly')
                self.entry_data_view.config(state='readonly')

                # Preenche os campos de valores
                campos = [
                    ('mao_de_obra', 2),
                    ('alimentacao', 3),
                    ('hospedagem', 4),
                    ('viagem', 5),
                    ('seguranca_trabalho', 6),
                    ('material', 7),
                    ('equipamento', 8),
                    ('andaime', 9),
                    ('documentacao', 10),
                    ('outros', 11)
                ]

                for campo, idx in campos:
                    entry = getattr(self, f"entry_{campo}_view")
                    entry.config(state='normal')
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{orcamento[idx]:.2f}")
                    entry.config(state='readonly')

                # Total
                self.entry_total_view.config(state='normal')
                self.entry_total_view.delete(0, tk.END)
                self.entry_total_view.insert(0, f"R$ {orcamento[12]:.2f}")
                self.entry_total_view.config(state='readonly')
            else:
                messagebox.showinfo("Info", "Orçamento não encontrado!")

        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar orçamento:\n{str(e)}")

    def limpar_campos_cadastro(self):
        """Limpa todos os campos da aba de cadastro"""
        for widget in self.aba_cadastro.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
        
        # Restaura valores padrão
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        
        campos_valores = [
            self.entry_mao_de_obra, self.entry_alimentacao, self.entry_hospedagem,
            self.entry_viagem, self.entry_seguranca_trabalho, self.entry_material,
            self.entry_equipamento, self.entry_andaime, self.entry_documentacao,
            self.entry_outros
        ]
        
        for campo in campos_valores:
            campo.delete(0, tk.END)
            campo.insert(0, "0.00")
        
        self.entry_total.config(state='normal')
        self.entry_total.delete(0, tk.END)
        self.entry_total.insert(0, "R$ 0.00")
        self.entry_total.config(state='readonly')
        self.entry_os.delete(0, tk.END)

    def limpar_campos_edicao(self):
        """Limpa todos os campos da aba de edição"""
        self.tree_orcamento.delete(*self.tree_orcamento.get_children())
        self.entry_busca_os_alt.delete(0, tk.END)
        
        for widget in self.aba_alteracao.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
        
        self.entry_os_edit.config(state='normal')
        self.entry_os_edit.delete(0, tk.END)
        self.entry_os_edit.config(state='readonly')

    def limpar_campos_exclusao(self):
        """Limpa todos os campos da aba de exclusão"""
        self.entry_busca_excluir.delete(0, tk.END)
        self.tree_exclusao.delete(*self.tree_exclusao.get_children())
        self.btn_excluir.config(state='disabled')
        self.status_label_exclusao.config(text="")

    def limpar_campos_visualizacao(self):
        """Limpa todos os campos da aba de visualização"""
        self.entry_busca_visualizar.delete(0, tk.END)
        
        for widget in self.aba_visualizacao.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.config(state='normal')
                widget.delete(0, tk.END)
                widget.config(state='readonly')

    def __del__(self):
        pass