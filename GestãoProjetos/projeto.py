import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime
from validate_docbr import CPF, CNPJ
from decimal import Decimal

class ModuloProjeto:
    def __init__(self, parent_frame, conn_config, conn=None, usuario_logado=None):
        self.parent = parent_frame
        self.conn_config = conn_config
        self.conn = conn   
        self.cursor = self.conn.cursor() if conn else None
        self.usuario_logado = usuario_logado
        
        # Não crie uma nova conexão se já foi fornecida
        if not self.conn:
            self.criar_conexao()

        # Definir os tipos disponíveis ANTES de criar a interface
        self.tipos_disponiveis = [
            "Engenharia - Pessoa Jurídica",
            "Solar - Pessoa Jurídica",
            "Médica - Pessoa Jurídica",
            "Automação - Pessoa Jurídica",
            "Engenharia - Pessoa Física",
            "Solar - Pessoa Física",
            "Médica - Pessoa Física",
            "Automação - Pessoa Física"
        ]
        
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

        # Cria os frames das abas PRIMEIRO
        self.aba_cadastro = ttk.Frame(self.notebook)
        self.aba_alteracao = ttk.Frame(self.notebook) 
        self.aba_exclusao = ttk.Frame(self.notebook)
        self.aba_visualizacao = ttk.Frame(self.notebook)

        # Adiciona as abas ao notebook 
        self.notebook.add(self.aba_cadastro, text="Cadastrar")
        self.notebook.add(self.aba_alteracao, text="Alterar")
        self.notebook.add(self.aba_exclusao, text="Excluir")

        # Configura o conteúdo de CADA ABA (sem recriar os frames)
        self.criar_aba_cadastro()
        self.criar_aba_alteracao()
        self.criar_aba_exclusao()
        self.criar_aba_visualizacao()

    def criar_notebook(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def criar_aba_cadastro(self):
        form_frame = ttk.LabelFrame(self.aba_cadastro, text=" Cadastro", padding=20)
        form_frame.pack(fill=tk.X, padx=20, pady=15)

        # Frame principal do formulário
        form_frame = ttk.LabelFrame(self.aba_cadastro, text=" Cadastro de Projeto", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Configuração do grid
        for i in range(8):  # 8 linhas
            form_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for j in range(4):  # 4 colunas
            form_frame.grid_columnconfigure(j, weight=1)

        # Linha 0 - N° OS e Tipo
        ttk.Label(form_frame, text="N° OS:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os = ttk.Entry(form_frame, width=20)
        self.entry_os.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Tipo:*").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.tipo_var = tk.StringVar()
        tipo_combobox = ttk.Combobox(form_frame, 
                                    textvariable=self.tipo_var,
                                    values=self.tipos_disponiveis,  
                                    state="readonly",
                                    width=30)
        tipo_combobox.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Linha 1 - Cliente e CPF/CNPJ
        ttk.Label(form_frame, text="Cliente:*", font=('Arial', 10, 'bold')).grid(
        row=1, column=0, sticky="e", padx=5, pady=5)
    
        self.cliente_var = tk.StringVar()
        self.combo_cliente = ttk.Combobox(form_frame, 
                                        textvariable=self.cliente_var,
                                        width=40,
                                        postcommand=self.atualizar_lista_clientes)
        self.combo_cliente.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.combo_cliente.bind('<<ComboboxSelected>>', self.preencher_cpf_cnpj_automatico)

        # Mantenha o campo CPF/CNPJ 
        ttk.Label(form_frame, text="CPF/CNPJ:*", font=('Arial', 10, 'bold')).grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_cpfcnpj = ttk.Entry(form_frame, width=30, state='readonly')
        self.entry_cpfcnpj.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="CPF/CNPJ:*", font=('Arial', 10, 'bold')).grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_cpfcnpj = ttk.Entry(form_frame, width=30)
        self.entry_cpfcnpj.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Linha 2 - Data OS e N° Proposta
        ttk.Label(form_frame, text="Data OS:*", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_data = ttk.Entry(form_frame, width=20)
        self.entry_data.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))

        ttk.Label(form_frame, text="N° Proposta:*", font=('Arial', 10, 'bold')).grid(
            row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_proposta = ttk.Entry(form_frame, width=30)
        self.entry_proposta.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # Linha 3 - Valores (Serviço, Material)
        ttk.Label(form_frame, text="R$ Serviço:", font=('Arial', 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_servico = ttk.Entry(form_frame, width=20)
        self.entry_servico.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="R$ Material:", font=('Arial', 10)).grid(
            row=3, column=2, sticky="e", padx=5, pady=5)
        self.entry_material = ttk.Entry(form_frame, width=30)
        self.entry_material.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # Linha 4 - Total e Endereço
        ttk.Label(form_frame, text="R$ Total:", font=('Arial', 10)).grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_total = ttk.Entry(form_frame, width=20, state='readonly')
        self.entry_total.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Endereço:", font=('Arial', 10)).grid(
            row=4, column=2, sticky="e", padx=5, pady=5)
        self.entry_endereco = ttk.Entry(form_frame, width=30)
        self.entry_endereco.grid(row=4, column=3, sticky="w", padx=5, pady=5)

        # Linha 5 - Cidade e Estado
        ttk.Label(form_frame, text="Cidade:", font=('Arial', 10)).grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_cidade = ttk.Entry(form_frame, width=20)
        self.entry_cidade.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Estado:", font=('Arial', 10)).grid(
            row=5, column=2, sticky="e", padx=5, pady=5)
        self.entry_estado = ttk.Entry(form_frame, width=30)
        self.entry_estado.grid(row=5, column=3, sticky="w", padx=5, pady=5)

        # Linha 6 - Contato e Nome
        ttk.Label(form_frame, text="Contato:", font=('Arial', 10)).grid(
            row=6, column=0, sticky="e", padx=5, pady=5)
        self.entry_contato = ttk.Entry(form_frame, width=20)
        self.entry_contato.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Nome Contato:", font=('Arial', 10)).grid(
            row=6, column=2, sticky="e", padx=5, pady=5)
        self.entry_nome = ttk.Entry(form_frame, width=30)
        self.entry_nome.grid(row=6, column=3, sticky="w", padx=5, pady=5)

        # Frame para botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=7, column=0, columnspan=4, pady=(15, 5))

        # Botão Salvar
        btn_salvar = ttk.Button(btn_frame, text="Salvar Projeto", 
                            command=self.salvar_projeto,
                            style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        # Botão Limpar
        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                            command=self.limpar_campos)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Configura cálculo automático do total
        self.entry_servico.bind('<KeyRelease>', self.calcular_total)
        self.entry_material.bind('<KeyRelease>', self.calcular_total)

        # Configura validação de CPF/CNPJ
        self.entry_cpfcnpj.bind('<FocusOut>', self.validar_documento)

    def criar_aba_alteracao(self):
        form_frame = ttk.LabelFrame(self.aba_alteracao, text=" Alterar", padding=20)
        form_frame.pack(fill=tk.X, padx=20, pady=15)

        # Container principal
        main_frame = ttk.Frame(self.aba_alteracao)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Seção de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Projeto ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="N° OS:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_projeto_para_alteracao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Visualização rápida do projeto encontrado
        self.tree_projeto = ttk.Treeview(busca_frame, 
                                    columns=("OS", "Cliente", "Data", "Status"),
                                    show="headings",
                                    height=1)
        self.tree_projeto.heading("OS", text="N° OS")
        self.tree_projeto.heading("Cliente", text="Cliente")
        self.tree_projeto.heading("Data", text="Data OS")
        self.tree_projeto.heading("Status", text="Status")
        self.tree_projeto.column("OS", width=100)
        self.tree_projeto.column("Cliente", width=200)
        self.tree_projeto.column("Data", width=100)
        self.tree_projeto.column("Status", width=100)
        self.tree_projeto.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Seção de edição
        edit_frame = ttk.LabelFrame(main_frame, text=" Editar Projeto ", padding=15)
        edit_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook para agrupar os campos
        edit_notebook = ttk.Notebook(edit_frame)
        edit_notebook.pack(fill=tk.BOTH, expand=True)

        # Aba Dados Básicos
        tab_basicos = ttk.Frame(edit_notebook)
        edit_notebook.add(tab_basicos, text="Dados Básicos")

        # Campos básicos (2 colunas)
        ttk.Label(tab_basicos, text="N° OS:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os_edit = ttk.Entry(tab_basicos, state='readonly')
        self.entry_os_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="Tipo:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.tipo_var_edit = tk.StringVar()
        ttk.Combobox(tab_basicos, textvariable=self.tipo_var_edit,
                    values=self.tipos_disponiveis, state="readonly").grid(
                    row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="Cliente:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_cliente_edit = ttk.Entry(tab_basicos)
        self.entry_cliente_edit.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="CPF/CNPJ:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_cpfcnpj_edit = ttk.Entry(tab_basicos)
        self.entry_cpfcnpj_edit.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="Data OS:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_data_edit = ttk.Entry(tab_basicos)
        self.entry_data_edit.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="N° Proposta:").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_proposta_edit = ttk.Entry(tab_basicos)
        self.entry_proposta_edit.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Aba Valores
        tab_valores = ttk.Frame(edit_notebook)
        edit_notebook.add(tab_valores, text="Valores")

        ttk.Label(tab_valores, text="R$ Serviço:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_servico_edit = ttk.Entry(tab_valores)
        self.entry_servico_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_valores, text="R$ Material:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_material_edit = ttk.Entry(tab_valores)
        self.entry_material_edit.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_valores, text="R$ Total:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_total_edit = ttk.Entry(tab_valores, state='readonly')
        self.entry_total_edit.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Aba Localização
        tab_local = ttk.Frame(edit_notebook)
        edit_notebook.add(tab_local, text="Localização")

        ttk.Label(tab_local, text="Endereço:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_endereco_edit = ttk.Entry(tab_local, width=40)
        self.entry_endereco_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_local, text="Cidade:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_cidade_edit = ttk.Entry(tab_local)
        self.entry_cidade_edit.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_local, text="Estado:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_estado_edit = ttk.Entry(tab_local, width=5)
        self.entry_estado_edit.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Aba Contato
        tab_contato = ttk.Frame(edit_notebook)
        edit_notebook.add(tab_contato, text="Contato")

        ttk.Label(tab_contato, text="Telefone:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_contato_edit = ttk.Entry(tab_contato)
        self.entry_contato_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_contato, text="Nome Contato:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome_edit = ttk.Entry(tab_contato)
        self.entry_nome_edit.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_contato, text="Status:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.status_var_edit = tk.StringVar()
        ttk.Combobox(tab_contato, textvariable=self.status_var_edit,
                    values=["Ativo", "Cancelado", "Concluído", "Pendente"],
                    state="readonly").grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Frame de botões
        btn_frame = ttk.Frame(edit_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        btn_salvar = ttk.Button(btn_frame, text="Salvar Alterações",
                            command=self.salvar_alteracoes,
                            style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                            command=self.limpar_campos_edicao)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Configurar bindings
        self.entry_servico_edit.bind('<KeyRelease>', self.calcular_total_edicao)
        self.entry_material_edit.bind('<KeyRelease>', self.calcular_total_edicao)
        self.entry_cpfcnpj_edit.bind('<FocusOut>', self.validar_documento_edicao)

    def criar_aba_exclusao(self):
        form_frame = ttk.LabelFrame(self.aba_exclusao, text=" Excluir", padding=20)
        form_frame.pack(fill=tk.X, padx=20, pady=15)

        # Container principal
        main_frame = ttk.Frame(self.aba_exclusao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Projeto para Exclusão ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        # Campo de busca
        ttk.Label(busca_frame, text="N° OS:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_excluir = ttk.Entry(busca_frame, width=25)
        self.entry_busca_excluir.grid(row=0, column=1, padx=5, pady=5)

        # Botão de busca
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_projeto_exclusao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Treeview para mostrar o projeto encontrado
        columns = ("OS", "Cliente", "Data OS", "Tipo", "Status")
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
        self.btn_excluir = ttk.Button(confirm_frame, text="Excluir Projeto", 
                                    command=self.confirmar_exclusao,
                                    state='disabled',
                                    style='Danger.TButton')
        self.btn_excluir.pack(pady=10)

        # Status
        self.status_label_exclusao = ttk.Label(main_frame, text="", foreground='red')
        self.status_label_exclusao.pack()

        # Bind para tecla Enter
        self.entry_busca_excluir.bind('<Return>', lambda e: self.buscar_projeto_exclusao())

    def criar_aba_visualizacao(self):
        self.aba_visualizacao = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_visualizacao, text="Buscar OS")

        # Container principal
        main_frame = ttk.Frame(self.aba_visualizacao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Ordem de Serviço ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        # Campo de busca
        ttk.Label(busca_frame, text="Número da OS:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os.grid(row=0, column=1, padx=5, pady=5)

        # Botão de busca
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_os_completa,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Área de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text=" Detalhes da OS ", padding=15)
        resultados_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook para os detalhes
        self.detalhes_notebook = ttk.Notebook(resultados_frame)
        self.detalhes_notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de informações básicas
        tab_basicos = ttk.Frame(self.detalhes_notebook)
        self.detalhes_notebook.add(tab_basicos, text="Informações Básicas")

        # Campos básicos (2 colunas)
        campos_basicos = [
            ("N° OS:", "entry_os_view"),
            ("Tipo:", "entry_tipo_view"),
            ("Cliente:", "entry_cliente_view"),
            ("CPF/CNPJ:", "entry_cpfcnpj_view"),
            ("Data OS:", "entry_data_view"),
            ("N° Proposta:", "entry_proposta_view"),
            ("Status:", "entry_status_view")
        ]

        for i, (label, var_name) in enumerate(campos_basicos):
            ttk.Label(tab_basicos, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(tab_basicos, state='readonly')
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            setattr(self, var_name, entry)  # Cria atributo dinâmico

        # Aba de valores
        tab_valores = ttk.Frame(self.detalhes_notebook)
        self.detalhes_notebook.add(tab_valores, text="Valores")

        campos_valores = [
            ("R$ Serviço:", "entry_servico_view"),
            ("R$ Material:", "entry_material_view"),
            ("R$ Total:", "entry_total_view")
        ]

        for i, (label, var_name) in enumerate(campos_valores):
            ttk.Label(tab_valores, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(tab_valores, state='readonly')
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            setattr(self, var_name, entry)

        # Aba de localização
        tab_local = ttk.Frame(self.detalhes_notebook)
        self.detalhes_notebook.add(tab_local, text="Localização")

        campos_local = [
            ("Endereço:", "entry_endereco_view"),
            ("Cidade:", "entry_cidade_view"),
            ("Estado:", "entry_estado_view")
        ]

        for i, (label, var_name) in enumerate(campos_local):
            ttk.Label(tab_local, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(tab_local, state='readonly')
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            setattr(self, var_name, entry)

        # Aba de contato
        tab_contato = ttk.Frame(self.detalhes_notebook)
        self.detalhes_notebook.add(tab_contato, text="Contato")

        campos_contato = [
            ("Telefone:", "entry_contato_view"),
            ("Responsável:", "entry_responsavel_view")
        ]

        for i, (label, var_name) in enumerate(campos_contato):
            ttk.Label(tab_contato, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(tab_contato, state='readonly')
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            setattr(self, var_name, entry)

        # Configurar bind para Enter
        self.entry_busca_os.bind('<Return>', lambda e: self.buscar_os_completa())

    # --- MÉTODOS PRINCIPAIS ---
    def carregar_dados(self):
        try:
            self.cursor.execute("""
                SELECT 
                    numero_os, tipo, cliente_nome, cliente_cpf_cnpj,
                    TO_CHAR(data_os, 'DD/MM/YYYY'), numero_proposta,
                    valor_servico, valor_material, total, status
                FROM projetos
                ORDER BY data_os DESC
            """)
            dados = self.cursor.fetchall()

            # Limpa e recarrega a treeview
            self.tree.delete(*self.tree.get_children())
            for projeto in dados:
                self.tree.insert("", tk.END, values=projeto)

        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar projetos:\n{str(e)}")
           
    def atualizar_lista_clientes(self):
        """Busca clientes no banco de dados para o autocomplete"""
        termo = self.cliente_var.get()
        try:
            if termo:
                self.cursor.execute("""
                    SELECT nome, cpf_cnpj FROM clientes 
                    WHERE nome ILIKE %s
                    ORDER BY nome
                    LIMIT 20
                """, (f'%{termo}%',))
            else:
                self.cursor.execute("""
                    SELECT nome, cpf_cnpj FROM clientes 
                    ORDER BY nome
                    LIMIT 20
                """)
            
            clientes = self.cursor.fetchall()
            # Formata como "Nome - CPF/CNPJ" para exibição
            clientes_formatados = [f"{c[0]} - {c[1]}" for c in clientes]
            self.combo_cliente['values'] = clientes_formatados
            
            # Armazena os dados completos para uso posterior
            self.clientes_disponiveis = clientes
            
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar clientes:\n{str(e)}")

    def preencher_cpf_cnpj_automatico(self, event=None):
        """Preenche automaticamente o CPF/CNPJ quando seleciona um cliente"""
        selecionado = self.combo_cliente.current()
        if selecionado >= 0 and hasattr(self, 'clientes_disponiveis'):
            # Limpa e preenche o CPF/CNPJ
            self.entry_cpfcnpj.config(state='normal')
            self.entry_cpfcnpj.delete(0, tk.END)
            self.entry_cpfcnpj.insert(0, self.clientes_disponiveis[selecionado][1])
            self.entry_cpfcnpj.config(state='readonly')

    def obter_id_do_cliente_selecionado(self, index):
        """Obtém o ID do cliente selecionado no combobox"""
        try:
            cpf_cnpj = self.clientes_disponiveis[index][1]
            self.cursor.execute("SELECT id_cliente FROM clientes WHERE cpf_cnpj = %s", (cpf_cnpj,))
            return self.cursor.fetchone()[0]
        except (psycopg2.Error, IndexError) as e:
            messagebox.showerror("Erro", f"Falha ao obter ID do cliente:\n{str(e)}")
            return None


    def salvar_projeto(self):
        # Validação básica
        if not self.cliente_var.get() or self.combo_cliente.current() == -1:
            messagebox.showwarning("Aviso", "Selecione um cliente válido!")
            return
        
        # Obtém o ID do cliente selecionado
        selecionado = self.combo_cliente.current()
        if not hasattr(self, 'clientes_disponiveis') or selecionado >= len(self.clientes_disponiveis):
            messagebox.showwarning("Aviso", "Cliente não encontrado!")
            return
        
        id_cliente = self.obter_id_do_cliente_selecionado(selecionado)
        if id_cliente is None:
            return

        try:
            # Verificar se a proposta existe
            numero_proposta = self.entry_proposta.get()
            if numero_proposta:
                self.cursor.execute("SELECT 1 FROM propostas WHERE numero_proposta = %s", (numero_proposta,))
                if not self.cursor.fetchone():
                    if not messagebox.askyesno("Aviso", "Número de proposta não encontrado. Deseja continuar mesmo assim?"):
                        return

            # Restante do código de salvamento...
            valor_servico = Decimal(self.entry_servico.get() or 0)
            valor_material = Decimal(self.entry_material.get() or 0)
            total = valor_servico + valor_material

            self.cursor.execute("""
                INSERT INTO projetos (
                    numero_os, tipo, id_cliente, cliente_nome, cliente_cpf_cnpj,
                    data_os, numero_proposta, valor_servico, valor_material,
                    total, endereco_obra, cidade_obra, estado_obra,
                    contato, nome_responsavel, status
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, 'Ativo'
                )
            """, (
                self.entry_os.get(),
                self.tipo_var.get(),
                id_cliente,  # Usando o ID obtido
                self.combo_cliente.get(),
                self.entry_cpfcnpj.get(),
                datetime.strptime(self.entry_data.get(), '%d/%m/%Y').date(),
                self.entry_proposta.get() or None, 
                valor_servico,
                valor_material,
                total,
                self.entry_endereco.get() or None,
                self.entry_cidade.get() or None,
                self.entry_estado.get() or None,
                self.entry_contato.get() or None,
                self.entry_nome.get() or None
            ))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Projeto cadastrado com sucesso!")
            self.limpar_campos()
            self.entry_os.delete(0, tk.END),
            self.combo_cliente.delete(0, tk.END),
            self.entry_cpfcnpj.delete(0, tk.END),
            self.entry_proposta.delete(0, tk.END), 
            self.entry_endereco.delete(0, tk.END),
            self.entry_cidade.delete(0, tk.END),
            self.entry_estado.delete(0, tk.END),
            self.entry_contato.delete(0, tk.END),
            self.entry_nome.delete(0, tk.END)
            self.carregar_dados()

        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar projeto:\n{str(e)}")

    def limpar_campos(self):
        self.entry_os.delete(0, tk.END),
        self.combo_cliente.delete(0, tk.END),
        self.entry_cpfcnpj.delete(0, tk.END),
        self.entry_material.delete(0, tk.END),
        self.entry_servico.delete(0, tk.END),
        self.entry_total.delete(0, tk.END),
        self.entry_cpfcnpj.delete(0, tk.END),
        self.entry_proposta.delete(0, tk.END), 
        self.entry_endereco.delete(0, tk.END),
        self.entry_cidade.delete(0, tk.END),
        self.entry_estado.delete(0, tk.END),
        self.entry_contato.delete(0, tk.END),
        self.entry_nome.delete(0, tk.END)

    def buscar_projeto_para_alteracao(self):
        os_numero = self.entry_busca_os.get()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um número de OS!")
            return
        
        try:
            # Limpa a treeview
            self.tree_projeto.delete(*self.tree_projeto.get_children())
            
            # Busca no banco de dados
            self.cursor.execute("""
                SELECT numero_os, cliente_nome, data_os, status
                FROM projetos WHERE numero_os = %s
            """, (os_numero,))
            projeto = self.cursor.fetchone()
            
            if projeto:
                # Preenche a visualização rápida
                self.tree_projeto.insert("", "end", values=projeto)
                
                # Busca todos os dados do projeto
                self.cursor.execute("""
                    SELECT * FROM projetos WHERE numero_os = %s
                """, (os_numero,))
                projeto_completo = self.cursor.fetchone()
                
                # Preenche os campos do formulário
                self.preencher_campos_edicao(projeto_completo)
            else:
                messagebox.showinfo("Info", "Projeto não encontrado!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar projeto:\n{str(e)}")

    def preencher_campos_edicao(self, projeto):
        """Preenche todos os campos com os dados do projeto"""
        # Dados Básicos
        self.entry_os_edit.config(state='normal')
        self.entry_os_edit.delete(0, tk.END)
        self.entry_os_edit.insert(0, projeto[0])  # numero_os
        self.entry_os_edit.config(state='readonly')
        
        self.tipo_var_edit.set(projeto[1])  # tipo
        self.entry_cliente_edit.delete(0, tk.END)
        self.entry_cliente_edit.insert(0, projeto[3])  # cliente_nome
        self.entry_cpfcnpj_edit.delete(0, tk.END)
        self.entry_cpfcnpj_edit.insert(0, projeto[4])  # cliente_cpf_cnpj
        
        # Formata a data
        data_formatada = projeto[5].strftime('%d/%m/%Y')  # data_os
        self.entry_data_edit.delete(0, tk.END)
        self.entry_data_edit.insert(0, data_formatada)
        
        self.entry_proposta_edit.delete(0, tk.END)
        self.entry_proposta_edit.insert(0, projeto[6] or "")  # numero_proposta
        
        # Valores
        self.entry_servico_edit.delete(0, tk.END)
        self.entry_servico_edit.insert(0, projeto[7] or "")  # valor_servico
        
        self.entry_material_edit.delete(0, tk.END)
        self.entry_material_edit.insert(0, projeto[8] or "")  # valor_material
        
        total = (projeto[7] or 0) + (projeto[8] or 0)  # valor_servico + valor_material
        self.entry_total_edit.config(state='normal')
        self.entry_total_edit.delete(0, tk.END)
        self.entry_total_edit.insert(0, f"R$ {total:.2f}")
        self.entry_total_edit.config(state='readonly')
        
        # Localização
        self.entry_endereco_edit.delete(0, tk.END)
        self.entry_endereco_edit.insert(0, projeto[10] or "")  # endereco_obra
        
        self.entry_cidade_edit.delete(0, tk.END)
        self.entry_cidade_edit.insert(0, projeto[11] or "")  # cidade_obra
        
        self.entry_estado_edit.delete(0, tk.END)
        self.entry_estado_edit.insert(0, projeto[12] or "")  # estado_obra
        
        # Contato
        self.entry_contato_edit.delete(0, tk.END)
        self.entry_contato_edit.insert(0, projeto[13] or "")  # contato
        
        self.entry_nome_edit.delete(0, tk.END)
        self.entry_nome_edit.insert(0, projeto[14] or "")  # nome_responsavel
        
        self.status_var_edit.set(projeto[15])  # status

    def salvar_alteracoes(self):
        try:
            # Obter o número da OS (campo readonly)
            numero_os = self.entry_os_edit.get()
            if not numero_os:
                messagebox.showwarning("Aviso", "Nenhum projeto selecionado!")
                return

            # Validar campos obrigatórios
            campos_obrigatorios = {
                "Tipo": self.tipo_var_edit.get(),
                "Cliente": self.entry_cliente_edit.get(),
                "CPF/CNPJ": self.entry_cpfcnpj_edit.get(),
                "Data OS": self.entry_data_edit.get()
            }
            
            campos_faltantes = [campo for campo, valor in campos_obrigatorios.items() if not valor]
            if campos_faltantes:
                messagebox.showwarning("Aviso", f"Campos obrigatórios faltando:\n{', '.join(campos_faltantes)}")
                return

            # Validar CPF/CNPJ
            if not self.validar_cpf_cnpj(self.entry_cpfcnpj_edit.get()):
                messagebox.showwarning("Aviso", "CPF/CNPJ inválido!")
                return

            # Converter valores monetários
            try:
                valor_servico = float(self.entry_servico_edit.get() or 0)
                valor_material = float(self.entry_material_edit.get() or 0)
                total = valor_servico + valor_material
            except ValueError:
                messagebox.showerror("Erro", "Valores monetários inválidos!")
                return

            # Converter data
            try:
                data_os = datetime.strptime(self.entry_data_edit.get(), '%d/%m/%Y').date()
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
                return

            # Atualizar no banco de dados
            self.cursor.execute("""
                UPDATE projetos SET
                    tipo = %s,
                    cliente_nome = %s,
                    cliente_cpf_cnpj = %s,
                    data_os = %s,
                    numero_proposta = %s,
                    valor_servico = %s,
                    valor_material = %s,
                    total = %s,
                    endereco_obra = %s,
                    cidade_obra = %s,
                    estado_obra = %s,
                    contato = %s,
                    nome_responsavel = %s,
                    status = %s
                WHERE numero_os = %s
            """, (
                self.tipo_var_edit.get(),
                self.entry_cliente_edit.get(),
                self.entry_cpfcnpj_edit.get(),
                data_os,
                self.entry_proposta_edit.get() or None,
                valor_servico,
                valor_material,
                total,
                self.entry_endereco_edit.get() or None,
                self.entry_cidade_edit.get() or None,
                self.entry_estado_edit.get() or None,
                self.entry_contato_edit.get() or None,
                self.entry_nome_edit.get() or None,
                self.status_var_edit.get(),
                numero_os
            ))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Projeto atualizado com sucesso!")
            self.carregar_dados()  # Atualiza a visualização

        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar projeto:\n{str(e)}")

    def limpar_campos_edicao(self):
        """Limpa todos os campos da aba de edição"""
        self.tree_projeto.delete(*self.tree_projeto.get_children())
        self.entry_busca_os.delete(0, tk.END)
        
        """Limpa todos os campos do formulário"""
        for widget in self.aba_cadastro.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                widget.set('')
        
        self.entry_os_edit.config(state='normal')
        self.entry_os_edit.delete(0, tk.END)
        self.entry_os_edit.config(state='readonly')

    def buscar_projeto_exclusao(self):
        os_numero = self.entry_busca_excluir.get()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um número de OS!")
            return
        
        try:
            self.cursor.execute("""
                SELECT numero_os, cliente_nome, data_os, tipo, status
                FROM projetos WHERE numero_os = %s
            """, (os_numero,))
            projeto = self.cursor.fetchone()
            
            if projeto:
                self.tree_exclusao.delete(*self.tree_exclusao.get_children())
                self.tree_exclusao.insert("", "end", values=projeto)
                self.btn_excluir.config(state='normal')
                self.status_label_exclusao.config(text="")
            else:
                messagebox.showinfo("Info", "Projeto não encontrado!")
                self.btn_excluir.config(state='disabled')
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar projeto:\n{str(e)}")

    def confirmar_exclusao(self):
        os_numero = self.entry_busca_excluir.get()
        if not os_numero:
            return
        
        # Mostrar mensagem de processamento
        self.status_label_exclusao.config(text="Processando...", foreground="blue")
        self.parent.update()  # Força atualização da interface
        
        try:
            # Verificar se existem registros dependentes
            self.cursor.execute("SELECT 1 FROM projetos WHERE numero_os = %s", (os_numero,))
            if not self.cursor.fetchone():
                messagebox.showinfo("Info", "Projeto não encontrado!")
                return
                
            if messagebox.askyesno("Confirmar Exclusão", 
                                f"Tem certeza que deseja excluir a OS {os_numero}?"):
                self.cursor.execute("DELETE FROM projetos WHERE numero_os = %s", (os_numero,))
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Projeto excluído com sucesso!")
                self.limpar_campos_exclusao()
                
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao excluir projeto:\n{str(e)}")
        finally:
            self.status_label_exclusao.config(text="")

    def limpar_campos_exclusao(self):
        self.entry_busca_excluir.delete(0, tk.END)
        self.tree_exclusao.delete(*self.tree_exclusao.get_children())
        self.btn_excluir.config(state='disabled')
        self.status_label_exclusao.config(text="")

    def buscar_os_completa(self, event=None):
        """Busca uma OS completa e exibe todos os detalhes na aba de visualização"""
        os_numero = self.entry_busca_os.get().strip()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um número de OS!")
            return

        try:
            # Limpa os campos antes de nova busca
            self.limpar_campos_visualizacao()
            
            # Busca no banco de dados
            self.cursor.execute("""
                SELECT 
                    numero_os, tipo, cliente_nome, cliente_cpf_cnpj,
                    TO_CHAR(data_os, 'DD/MM/YYYY'), numero_proposta,
                    valor_servico, valor_material, total, status,
                    endereco_obra, cidade_obra, estado_obra,
                    contato, nome_responsavel
                FROM projetos 
                WHERE numero_os = %s
            """, (os_numero,))
            
            projeto = self.cursor.fetchone()

            if projeto:
                # Preenche os campos básicos
                campos_basicos = [
                    (self.entry_os_view, projeto[0]),         # numero_os
                    (self.entry_tipo_view, projeto[1]),       # tipo
                    (self.entry_cliente_view, projeto[2]),    # cliente_nome
                    (self.entry_cpfcnpj_view, projeto[3]),    # cliente_cpf_cnpj
                    (self.entry_data_view, projeto[4]),       # data_os
                    (self.entry_proposta_view, projeto[5]),   # numero_proposta
                    (self.entry_status_view, projeto[9])      # status
                ]
                
                for campo, valor in campos_basicos:
                    campo.config(state='normal')
                    campo.delete(0, tk.END)
                    campo.insert(0, valor or "")
                    campo.config(state='readonly')

                # Preenche os valores monetários
                valor_servico = projeto[6] if projeto[6] else 0
                valor_material = projeto[7] if projeto[7] else 0
                total = valor_servico + valor_material

                campos_valores = [
                    (self.entry_servico_view, f"R$ {valor_servico:.2f}"),
                    (self.entry_material_view, f"R$ {valor_material:.2f}"),
                    (self.entry_total_view, f"R$ {total:.2f}")
                ]
                
                for campo, valor in campos_valores:
                    campo.config(state='normal')
                    campo.delete(0, tk.END)
                    campo.insert(0, valor)
                    campo.config(state='readonly')

                # Preenche localização
                campos_localizacao = [
                    (self.entry_endereco_view, projeto[10]),  # endereco_obra
                    (self.entry_cidade_view, projeto[11]),    # cidade_obra
                    (self.entry_estado_view, projeto[12])     # estado_obra
                ]
                
                for campo, valor in campos_localizacao:
                    campo.config(state='normal')
                    campo.delete(0, tk.END)
                    campo.insert(0, valor or "")
                    campo.config(state='readonly')

                # Preenche contatos
                campos_contato = [
                    (self.entry_contato_view, projeto[13]),  # contato
                    (self.entry_responsavel_view, projeto[14]) # nome_responsavel
                ]
                
                for campo, valor in campos_contato:
                    campo.config(state='normal')
                    campo.delete(0, tk.END)
                    campo.insert(0, valor or "")
                    campo.config(state='readonly')

                # Seleciona a primeira aba
                self.detalhes_notebook.select(0)
            else:
                messagebox.showinfo("Informação", "OS não encontrada!")

        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar OS:\n{str(e)}")

    def limpar_campos_visualizacao(self):
        """Limpa todos os campos da aba de visualização"""
        campos = [
            self.entry_os_view, self.entry_tipo_view, self.entry_cliente_view,
            self.entry_cpfcnpj_view, self.entry_data_view, self.entry_proposta_view,
            self.entry_status_view, self.entry_servico_view, self.entry_material_view,
            self.entry_total_view, self.entry_endereco_view, self.entry_cidade_view,
            self.entry_estado_view, self.entry_contato_view, self.entry_responsavel_view
        ]
        
        for campo in campos:
            campo.config(state='normal')
            campo.delete(0, tk.END)
            campo.config(state='readonly')
        
    def calcular_total(self, event=None):
        try:
            servico = float(self.entry_servico.get() or 0)
            material = float(self.entry_material.get() or 0)
            total = servico + material
            self.entry_total.config(state='normal')
            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, f"R$ {total:.2f}")
            self.entry_total.config(state='readonly')
        except ValueError:
            pass

    def calcular_total_edicao(self, event=None):
        """Calcula o total automaticamente na aba de edição"""
        try:
            # Obtém valores dos campos (tratando valores vazios como 0)
            servico = float(self.entry_servico_edit.get() or 0)
            material = float(self.entry_material_edit.get() or 0)
            total = servico + material
            
            # Atualiza o campo total (formatado como moeda)
            self.entry_total_edit.config(state='normal')
            self.entry_total_edit.delete(0, tk.END)
            self.entry_total_edit.insert(0, f"R$ {total:.2f}")
            self.entry_total_edit.config(state='readonly')
            
        except ValueError:
            # Se a conversão falhar, limpa o campo total
            self.entry_total_edit.config(state='normal')
            self.entry_total_edit.delete(0, tk.END)
            self.entry_total_edit.config(state='readonly')

    def validar_documento(self, event=None):
        """Valida CPF/CNPJ ao sair do campo"""
        documento = self.entry_cpfcnpj.get()
        if documento and not self.validar_cpf_cnpj(documento):
            messagebox.showwarning("Aviso", "CPF/CNPJ inválido!")
            self.entry_cpfcnpj.focus_set()

    def validar_documento_edicao(self, event=None):
        """Valida CPF/CNPJ na aba de edição"""
        documento = self.entry_cpfcnpj_edit.get()
        if documento and not self.validar_cpf_cnpj(documento):
            messagebox.showwarning("Aviso", "CPF/CNPJ inválido!")
            self.entry_cpfcnpj_edit.focus_set()
    
    def validar_cpf_cnpj(self, documento):
        """Valida CPF ou CNPJ"""
        documento = ''.join(filter(str.isdigit, documento))
        
        if len(documento) == 11:
            cpf = CPF()
            return cpf.validate(documento)
        elif len(documento) == 14:
            cnpj = CNPJ()
            return cnpj.validate(documento)
        return False

    def __del__(self):
        pass