import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

class ModuloDespesa:
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

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Adicionando abas de alteração e exclusão
        self.aba_cadastro = ttk.Frame(self.notebook)
        self.aba_alteracao = ttk.Frame(self.notebook)
        self.aba_exclusao = ttk.Frame(self.notebook)
        self.aba_visualizacao = ttk.Frame(self.notebook)

        self.notebook.add(self.aba_cadastro, text="Cadastrar")
        self.notebook.add(self.aba_alteracao, text="Alterar")
        self.notebook.add(self.aba_exclusao, text="Excluir")
        self.notebook.add(self.aba_visualizacao, text="Visualizar")

        self.criar_aba_cadastro()
        self.criar_aba_alteracao()
        self.criar_aba_exclusao()
        self.criar_aba_visualizacao()

    def criar_aba_cadastro(self):
        """Cria a interface da aba de cadastro de despesas"""
        form_frame = ttk.LabelFrame(self.aba_cadastro, text=" Cadastro de Despesa", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Grid configuration (3 columns)
        for i in range(13):  # 13 rows
            form_frame.grid_rowconfigure(i, weight=1)
        for j in range(3):   # 3 columns
            form_frame.grid_columnconfigure(j, weight=1)

        # Row 0 - OS Number and Date
        ttk.Label(form_frame, text="N° OS Projeto:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os = ttk.Entry(form_frame, width=20)
        self.entry_os.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Data Despesa:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_data = ttk.Entry(form_frame, width=20)
        self.entry_data.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Row 1 - Observation
        ttk.Label(form_frame, text="Observação:", font=('Arial', 10)).grid(
            row=1, column=0, sticky="ne", padx=5, pady=5)
        self.entry_observacao = tk.Text(form_frame, width=50, height=4)
        self.entry_observacao.grid(row=1, column=1, columnspan=3, sticky="we", padx=5, pady=5)

        # Expense categories (rows 2-11)
        categories = [
            ("Mão de Obra(R$):", "entry_mao_de_obra"),
            ("Alimentação(R$):", "entry_alimentacao"),
            ("Hospedagem(R$):", "entry_hospedagem"),
            ("Viagem(R$):", "entry_viagem"),
            ("Segurança do Trabalho(R$):", "entry_seguranca"),
            ("Material(R$):", "entry_material"),
            ("Equipamento(R$):", "entry_equipamento"),
            ("Andaime(R$):", "entry_andaime"),
            ("Documentação(R$):", "entry_documentacao"),
            ("Outros(R$):", "entry_outros")
        ]

        for i, (label, field) in enumerate(categories, start=2):
            ttk.Label(form_frame, text=label).grid(
                row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=20)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entry.insert(0, "0.00")
            setattr(self, field, entry)

        # Row 12 - Total
        ttk.Label(form_frame, text="Total(R$):", font=('Arial', 10, 'bold')).grid(
            row=12, column=0, sticky="e", padx=5, pady=5)
        self.entry_total = ttk.Entry(form_frame, width=20, state='readonly', 
                                   font=('Arial', 10, 'bold'))
        self.entry_total.grid(row=12, column=1, sticky="w", padx=5, pady=5)
        self.entry_total.insert(0, "R$ 0.00")

        # Button frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=13, column=0, columnspan=4, pady=(15, 5))

        # Save button
        btn_salvar = ttk.Button(btn_frame, text="Salvar Despesa", 
                              command=self.salvar_despesa,
                              style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        # Clear button
        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                              command=self.limpar_campos)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Bind automatic calculation
        for field in [f"entry_{cat}" for cat in [
            'mao_de_obra', 'alimentacao', 'hospedagem', 'viagem',
            'seguranca', 'material', 'equipamento', 'andaime',
            'documentacao', 'outros'
        ]]:
            getattr(self, field).bind('<KeyRelease>', self.calcular_total)

    def criar_aba_alteracao(self):
        """Cria a interface da aba de alteração de despesas seguindo o padrão do módulo de projetos"""
        # Container principal
        main_frame = ttk.Frame(self.aba_alteracao)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Seção de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Despesa ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="N° OS:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os_alteracao = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os_alteracao.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_despesa_para_alteracao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Visualização rápida da despesa encontrada
        self.tree_despesas_alteracao = ttk.Treeview(busca_frame, 
                                                columns=("OS", "Data", "Total"),
                                                show="headings",
                                                height=5)
        self.tree_despesas_alteracao.heading("OS", text="N° OS")
        self.tree_despesas_alteracao.heading("Data", text="Data")
        self.tree_despesas_alteracao.heading("Total", text="Total")
        self.tree_despesas_alteracao.column("OS", width=100)
        self.tree_despesas_alteracao.column("Data", width=100)
        self.tree_despesas_alteracao.column("Total", width=100)
        self.tree_despesas_alteracao.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        self.tree_despesas_alteracao.bind("<<TreeviewSelect>>", self.selecionar_despesa_alteracao)

        # Seção de edição com notebook para abas
        edit_frame = ttk.LabelFrame(main_frame, text=" Editar Despesa ", padding=15)
        edit_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook para as abas de edição
        edit_notebook = ttk.Notebook(edit_frame)
        edit_notebook.pack(fill=tk.BOTH, expand=True)

        # Aba Dados Básicos
        tab_basicos = ttk.Frame(edit_notebook)
        edit_notebook.add(tab_basicos, text="Dados Básicos")

        # Campos básicos 
        ttk.Label(tab_basicos, text="N° OS:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os_edit = ttk.Entry(tab_basicos, state='readonly')
        self.entry_os_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="Data Despesa:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_data_edit = ttk.Entry(tab_basicos)
        self.entry_data_edit.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(tab_basicos, text="Observação:").grid(row=2, column=0, sticky="ne", padx=5, pady=5)
        self.entry_observacao_edit = tk.Text(tab_basicos, width=40, height=4)
        self.entry_observacao_edit.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        # Aba Valores
        tab_valores = ttk.Frame(edit_notebook)
        edit_notebook.add(tab_valores, text="Valores")

        # Categorias de despesas organizadas em 2 colunas
        left_frame = ttk.Frame(tab_valores)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_frame = ttk.Frame(tab_valores)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # Categorias da esquerda
        categories_left = [
            ("Mão de Obra(R$):", "entry_mao_de_obra_edit"),
            ("Alimentação(R$):", "entry_alimentacao_edit"),
            ("Hospedagem(R$):", "entry_hospedagem_edit"),
            ("Viagem(R$):", "entry_viagem_edit"),
            ("Segurança(R$):", "entry_seguranca_edit")
        ]

        for i, (label, field) in enumerate(categories_left):
            ttk.Label(left_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(left_frame, width=20)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entry.insert(0, "0.00")
            setattr(self, field, entry)
            entry.bind('<KeyRelease>', self.calcular_total_edicao)

        # Categorias da direita
        categories_right = [
            ("Material(R$):", "entry_material_edit"),
            ("Equipamento(R$):", "entry_equipamento_edit"),
            ("Andaime(R$):", "entry_andaime_edit"),
            ("Documentação(R$):", "entry_documentacao_edit"),
            ("Outros(R$):", "entry_outros_edit")
        ]

        for i, (label, field) in enumerate(categories_right):
            ttk.Label(right_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(right_frame, width=20)
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            entry.insert(0, "0.00")
            setattr(self, field, entry)
            entry.bind('<KeyRelease>', self.calcular_total_edicao)

        # Total (na parte inferior direita)
        ttk.Label(right_frame, text="Total(R$):", font=('Arial', 10, 'bold')).grid(
            row=5, column=0, sticky="e", padx=5, pady=5)
        self.entry_total_edit = ttk.Entry(right_frame, width=20, state='readonly', 
                                        font=('Arial', 10, 'bold'))
        self.entry_total_edit.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        self.entry_total_edit.insert(0, "R$ 0.00")

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

        # Inicialmente desabilita a edição até selecionar uma despesa
        self.habilitar_edicao(False)

    def criar_aba_exclusao(self):
        """Cria a interface da aba de exclusão de despesas"""
        main_frame = ttk.Frame(self.aba_exclusao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Despesa para Exclusão ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os_exclusao = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os_exclusao.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                             command=self.buscar_despesa_exclusao,
                             style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Treeview para resultados
        columns = ("OS", "Data", "Total")
        self.tree_despesas_exclusao = ttk.Treeview(busca_frame, columns=columns, show="headings", height=3)
        for col in columns:
            self.tree_despesas_exclusao.heading(col, text=col)
            self.tree_despesas_exclusao.column(col, width=100)
        self.tree_despesas_exclusao.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Botão de exclusão
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_excluir = ttk.Button(btn_frame, text="Excluir Despesa", 
                                   command=self.confirmar_exclusao,
                                   state='disabled',
                                   style='Danger.TButton')
        self.btn_excluir.pack(pady=10)

    def criar_aba_visualizacao(self):
        """Cria a interface da aba de visualização de despesas"""
        main_frame = ttk.Frame(self.aba_visualizacao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Search frame
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Despesas ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        # OS filter
        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os.grid(row=0, column=1, padx=5, pady=5)

        # Search button
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                             command=self.buscar_despesas,
                             style='Accent.TButton')
        btn_buscar.grid(row=0, column=6, padx=10)

        # Results treeview
        columns = ("OS", "Data", "Observação", "Total")
        self.tree_despesas = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.tree_despesas.heading(col, text=col)
            self.tree_despesas.column(col, width=120)
        
        self.tree_despesas.pack(fill=tk.BOTH, expand=True)

        # Bind double click to show details
        self.tree_despesas.bind("<Double-1>", self.mostrar_detalhes)

    def calcular_total(self, event=None):
        """Calcula o total automaticamente"""
        try:
            total = 0.0
            for field in [
                'mao_de_obra', 'alimentacao', 'hospedagem', 'viagem',
                'seguranca', 'material', 'equipamento', 'andaime',
                'documentacao', 'outros'
            ]:
                value = getattr(self, f"entry_{field}").get()
                total += float(value) if value else 0.0
            
            self.entry_total.config(state='normal')
            self.entry_total.delete(0, tk.END)
            self.entry_total.insert(0, f"R$ {total:.2f}")
            self.entry_total.config(state='readonly')
            
        except ValueError:
            pass

    def limpar_campos(self):
        """Limpa todos os campos da aba de cadastro"""
        self.entry_os.delete(0, tk.END)
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.entry_observacao.delete("1.0", tk.END)
        
        for field in [
            'mao_de_obra', 'alimentacao', 'hospedagem', 'viagem',
            'seguranca', 'material', 'equipamento', 'andaime',
            'documentacao', 'outros'
        ]:
            entry = getattr(self, f"entry_{field}")
            entry.delete(0, tk.END)
            entry.insert(0, "0.00")
        
        self.entry_total.config(state='normal')
        self.entry_total.delete(0, tk.END)
        self.entry_total.insert(0, "R$ 0.00")
        self.entry_total.config(state='readonly')

    def salvar_despesa(self):
        """Salva uma nova despesa no banco de dados"""
        # Basic validation
        if not self.entry_os.get():
            messagebox.showwarning("Aviso", "N° OS do projeto é obrigatório!")
            self.entry_os.focus_set()
            return
            
        if not self.entry_data.get():
            messagebox.showwarning("Aviso", "Data da despesa é obrigatória!")
            self.entry_data.focus_set()
            return

        try:
            # Convert values
            data_despesa = datetime.strptime(self.entry_data.get(), '%d/%m/%Y').date()
            observacao = self.entry_observacao.get("1.0", tk.END).strip()
            
            values = {
                'numero_os_projeto': self.entry_os.get(),
                'data_despesa': data_despesa,
                'observacao': observacao if observacao else None,
                'mao_de_obra': float(self.entry_mao_de_obra.get() or 0),
                'alimentacao': float(self.entry_alimentacao.get() or 0),
                'hospedagem': float(self.entry_hospedagem.get() or 0),
                'viagem': float(self.entry_viagem.get() or 0),
                'seguranca_trabalho': float(self.entry_seguranca.get() or 0),
                'material': float(self.entry_material.get() or 0),
                'equipamento': float(self.entry_equipamento.get() or 0),
                'andaime': float(self.entry_andaime.get() or 0),
                'documentacao': float(self.entry_documentacao.get() or 0),
                'outros': float(self.entry_outros.get() or 0)
            }

            # Insert into database
            self.cursor.execute("""
                INSERT INTO despesas (
                    numero_os_projeto, data_despesa, observacao,
                    mao_de_obra, alimentacao, hospedagem, viagem,
                    seguranca_trabalho, material, equipamento,
                    andaime, documentacao, outros
                ) VALUES (
                    %(numero_os_projeto)s, %(data_despesa)s, %(observacao)s,
                    %(mao_de_obra)s, %(alimentacao)s, %(hospedagem)s, %(viagem)s,
                    %(seguranca_trabalho)s, %(material)s, %(equipamento)s,
                    %(andaime)s, %(documentacao)s, %(outros)s
                )
            """, values)
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Despesa cadastrada com sucesso!")
            self.limpar_campos()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar despesa:\n{str(e)}")

    def buscar_despesa_para_alteracao(self):
        """Busca despesas para edição"""
        os_numero = self.entry_busca_os_alteracao.get().strip()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um N° OS!")
            return

        try:
            self.tree_despesas_alteracao.delete(*self.tree_despesas_alteracao.get_children())
            
            self.cursor.execute("""
                SELECT numero_os_projeto, data_despesa, total
                FROM despesas WHERE numero_os_projeto = %s
                ORDER BY data_despesa DESC
            """, (os_numero,))
            
            despesas = self.cursor.fetchall()
            
            if despesas:
                for despesa in despesas:
                    self.tree_despesas_alteracao.insert("", "end", values=(
                        despesa[0],
                        despesa[1].strftime('%d/%m/%Y'),
                        f"R$ {despesa[2]:.2f}"
                    ))
            else:
                messagebox.showinfo("Info", "Nenhuma despesa encontrada!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar despesas:\n{str(e)}")

    def selecionar_despesa_alteracao(self, event):
        """Carrega os dados da despesa selecionada para edição"""
        item = self.tree_despesas_alteracao.selection()
        if not item:
            return
            
        os_numero = self.tree_despesas_alteracao.item(item, 'values')[0]
        data_despesa = self.tree_despesas_alteracao.item(item, 'values')[1]
        
        try:
            self.cursor.execute("""
                SELECT * FROM despesas 
                WHERE numero_os_projeto = %s AND data_despesa = %s
            """, (os_numero, datetime.strptime(data_despesa, '%d/%m/%Y').date()))
            
            despesa = self.cursor.fetchone()
            
            if despesa:
                self.despesa_selecionada = despesa[0]  # id_despesa
                self.preencher_campos_edicao(despesa)
                self.habilitar_edicao(True)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar despesa:\n{str(e)}")

    def preencher_campos_edicao(self, despesa):
        """Preenche os campos com os dados da despesa"""
        self.entry_os_edit.config(state='normal')
        self.entry_os_edit.delete(0, tk.END)
        self.entry_os_edit.insert(0, despesa[1])  # numero_os_projeto
        self.entry_os_edit.config(state='readonly')
        
        self.entry_data_edit.delete(0, tk.END)
        self.entry_data_edit.insert(0, despesa[2].strftime('%d/%m/%Y'))  # data_despesa
        
        self.entry_observacao_edit.delete("1.0", tk.END)
        self.entry_observacao_edit.insert("1.0", despesa[3] or "")  # observacao
        
        # Preenche os valores das categorias
        categorias = [
            self.entry_mao_de_obra_edit,
            self.entry_alimentacao_edit,
            self.entry_hospedagem_edit,
            self.entry_viagem_edit,
            self.entry_seguranca_edit,
            self.entry_material_edit,
            self.entry_equipamento_edit,
            self.entry_andaime_edit,
            self.entry_documentacao_edit,
            self.entry_outros_edit
        ]
        
        for entry, valor in zip(categorias, despesa[4:14]):  # campos de valores
            entry.delete(0, tk.END)
            entry.insert(0, f"{valor:.2f}")
        
        # Atualiza o total
        self.calcular_total_edicao()

    def habilitar_edicao(self, habilitar):
        """Habilita ou desabilita os campos de edição"""
        estado = 'normal' if habilitar else 'disabled'
        
        self.entry_data_edit.config(state=estado)
        self.entry_observacao_edit.config(state=estado)
        
        for field in [
            'mao_de_obra', 'alimentacao', 'hospedagem', 'viagem',
            'seguranca', 'material', 'equipamento', 'andaime',
            'documentacao', 'outros'
        ]:
            getattr(self, f"entry_{field}_edit").config(state=estado)

    def calcular_total_edicao(self, event=None):
        """Calcula o total na aba de edição"""
        try:
            total = 0.0
            for field in [
                'mao_de_obra', 'alimentacao', 'hospedagem', 'viagem',
                'seguranca', 'material', 'equipamento', 'andaime',
                'documentacao', 'outros'
            ]:
                value = getattr(self, f"entry_{field}_edit").get()
                total += float(value) if value else 0.0
            
            self.entry_total_edit.config(state='normal')
            self.entry_total_edit.delete(0, tk.END)
            self.entry_total_edit.insert(0, f"R$ {total:.2f}")
            self.entry_total_edit.config(state='readonly')
            
        except ValueError:
            pass

    def limpar_campos_edicao(self):
        """Limpa todos os campos da aba de edição"""
        self.despesa_selecionada = None
        self.entry_os_edit.config(state='normal')
        self.entry_os_edit.delete(0, tk.END)
        self.entry_os_edit.config(state='readonly')
        
        self.entry_data_edit.delete(0, tk.END)
        self.entry_observacao_edit.delete("1.0", tk.END)
        
        for field in [
            'mao_de_obra', 'alimentacao', 'hospedagem', 'viagem',
            'seguranca', 'material', 'equipamento', 'andaime',
            'documentacao', 'outros'
        ]:
            entry = getattr(self, f"entry_{field}_edit")
            entry.delete(0, tk.END)
            entry.insert(0, "0.00")
        
        self.entry_total_edit.config(state='normal')
        self.entry_total_edit.delete(0, tk.END)
        self.entry_total_edit.insert(0, "R$ 0.00")
        self.entry_total_edit.config(state='readonly')
        
        self.habilitar_edicao(False)

    def salvar_alteracoes(self):
        """Salva as alterações da despesa no banco de dados"""
        if not self.despesa_selecionada:
            messagebox.showwarning("Aviso", "Nenhuma despesa selecionada!")
            return
            
        # Validação básica
        if not self.entry_data_edit.get():
            messagebox.showwarning("Aviso", "Data da despesa é obrigatória!")
            self.entry_data_edit.focus_set()
            return

        try:
            # Converter valores
            data_despesa = datetime.strptime(self.entry_data_edit.get(), '%d/%m/%Y').date()
            observacao = self.entry_observacao_edit.get("1.0", tk.END).strip()
            
            values = {
                'id': self.despesa_selecionada,
                'data_despesa': data_despesa,
                'observacao': observacao if observacao else None,
                'mao_de_obra': float(self.entry_mao_de_obra_edit.get() or 0),
                'alimentacao': float(self.entry_alimentacao_edit.get() or 0),
                'hospedagem': float(self.entry_hospedagem_edit.get() or 0),
                'viagem': float(self.entry_viagem_edit.get() or 0),
                'seguranca_trabalho': float(self.entry_seguranca_edit.get() or 0),
                'material': float(self.entry_material_edit.get() or 0),
                'equipamento': float(self.entry_equipamento_edit.get() or 0),
                'andaime': float(self.entry_andaime_edit.get() or 0),
                'documentacao': float(self.entry_documentacao_edit.get() or 0),
                'outros': float(self.entry_outros_edit.get() or 0)
            }

            # Atualiza no banco de dados
            self.cursor.execute("""
                UPDATE despesas SET
                    data_despesa = %(data_despesa)s,
                    observacao = %(observacao)s,
                    mao_de_obra = %(mao_de_obra)s,
                    alimentacao = %(alimentacao)s,
                    hospedagem = %(hospedagem)s,
                    viagem = %(viagem)s,
                    seguranca_trabalho = %(seguranca_trabalho)s,
                    material = %(material)s,
                    equipamento = %(equipamento)s,
                    andaime = %(andaime)s,
                    documentacao = %(documentacao)s,
                    outros = %(outros)s
                WHERE id_despesa = %(id)s
            """, values)
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Despesa atualizada com sucesso!")
            
            # Atualiza a lista de despesas
            self.buscar_despesa_para_alteracao()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar despesa:\n{str(e)}")

    # ========== MÉTODOS PARA EXCLUSÃO ==========
    def buscar_despesa_exclusao(self):
        """Busca despesas para exclusão"""
        os_numero = self.entry_busca_os_exclusao.get().strip()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um N° OS!")
            return

        try:
            self.tree_despesas_exclusao.delete(*self.tree_despesas_exclusao.get_children())
            
            self.cursor.execute("""
                SELECT numero_os_projeto, data_despesa, total
                FROM despesas WHERE numero_os_projeto = %s
                ORDER BY data_despesa DESC
            """, (os_numero,))
            
            despesas = self.cursor.fetchall()
            
            if despesas:
                for despesa in despesas:
                    self.tree_despesas_exclusao.insert("", "end", values=(
                        despesa[0],
                        despesa[1].strftime('%d/%m/%Y'),
                        f"R$ {despesa[2]:.2f}"
                    ))
                self.btn_excluir.config(state='normal')
            else:
                messagebox.showinfo("Info", "Nenhuma despesa encontrada!")
                self.btn_excluir.config(state='disabled')
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar despesas:\n{str(e)}")
            self.btn_excluir.config(state='disabled')

    def confirmar_exclusao(self):
        """Confirma e executa a exclusão da despesa"""
        item = self.tree_despesas_exclusao.selection()
        if not item:
            messagebox.showwarning("Aviso", "Nenhuma despesa selecionada!")
            return
            
        os_numero = self.tree_despesas_exclusao.item(item, 'values')[0]
        data_despesa = self.tree_despesas_exclusao.item(item, 'values')[1]
        
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir a despesa da OS {os_numero} de {data_despesa}?"):
            return
            
        try:
            self.cursor.execute("""
                DELETE FROM despesas 
                WHERE numero_os_projeto = %s AND data_despesa = %s
            """, (os_numero, datetime.strptime(data_despesa, '%d/%m/%Y').date()))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Despesa excluída com sucesso!")
            
            # Atualiza a lista
            self.buscar_despesa_exclusao()
            
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao excluir despesa:\n{str(e)}")

    def buscar_despesas(self):
        """Busca despesas com base nos filtros"""
        os_numero = self.entry_busca_os.get().strip()

        try:
            # Clear previous results
            self.tree_despesas.delete(*self.tree_despesas.get_children())
            
            # Build query
            query = """
                SELECT numero_os_projeto, data_despesa, 
                       COALESCE(observacao, ''), total
                FROM despesas
                WHERE 1=1 
            """
            params = []
            
            if os_numero:
                query += " AND numero_os_projeto = %s"
                params.append(os_numero)
            
            query += " ORDER BY data_despesa DESC"
            
            self.cursor.execute(query, params)
            despesas = self.cursor.fetchall()
            
            if despesas:
                for despesa in despesas:
                    self.tree_despesas.insert("", "end", values=(
                        despesa[0],
                        despesa[1].strftime('%d/%m/%Y'),
                        despesa[2],
                        f"R$ {despesa[3]:.2f}"
                    ))
            else:
                messagebox.showinfo("Info", "Nenhuma despesa encontrada com os filtros informados!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar despesas:\n{str(e)}")

    def mostrar_detalhes(self, event):
        """Mostra os detalhes da despesa selecionada"""
        item = self.tree_despesas.selection()
        if not item:
            return
            
        os_numero = self.tree_despesas.item(item, 'values')[0]
        
        try:
            self.cursor.execute("""
                SELECT * FROM despesas WHERE numero_os_projeto = %s
            """, (os_numero,))
            despesa = self.cursor.fetchone()
            
            if despesa:
                # Create detail window
                detail_window = tk.Toplevel(self.parent)
                detail_window.title(f"Detalhes da Despesa - OS {os_numero}")
                detail_window.geometry("500x600")
                
                # Create notebook for details
                notebook = ttk.Notebook(detail_window)
                notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                # Basic info tab
                tab_basicos = ttk.Frame(notebook)
                notebook.add(tab_basicos, text="Informações Básicas")
                
                # Basic fields
                ttk.Label(tab_basicos, text="N° OS Projeto:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
                ttk.Label(tab_basicos, text=despesa[1]).grid(row=0, column=1, sticky="w", padx=5, pady=5)
                
                ttk.Label(tab_basicos, text="Data Despesa:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
                ttk.Label(tab_basicos, text=despesa[2].strftime('%d/%m/%Y')).grid(row=1, column=1, sticky="w", padx=5, pady=5)
                
                ttk.Label(tab_basicos, text="Observação:").grid(row=2, column=0, sticky="ne", padx=5, pady=5)
                observacao = tk.Text(tab_basicos, width=50, height=4, wrap=tk.WORD)
                observacao.grid(row=2, column=1, sticky="we", padx=5, pady=5)
                observacao.insert("1.0", despesa[3] or "")
                observacao.config(state='disabled')
                
                # Values tab
                tab_valores = ttk.Frame(notebook)
                notebook.add(tab_valores, text="Valores")
                
                categories = [
                    ("Mão de Obra:", despesa[4]),
                    ("Alimentação:", despesa[5]),
                    ("Hospedagem:", despesa[6]),
                    ("Viagem:", despesa[7]),
                    ("Segurança do Trabalho:", despesa[8]),
                    ("Material:", despesa[9]),
                    ("Equipamento:", despesa[10]),
                    ("Andaime:", despesa[11]),
                    ("Documentação:", despesa[12]),
                    ("Outros:", despesa[13]),
                    ("TOTAL:", despesa[14])
                ]
                
                for i, (label, value) in enumerate(categories):
                    ttk.Label(tab_valores, text=label, font='Arial 10 bold' if label == "TOTAL:" else 'Arial 10').grid(
                        row=i, column=0, sticky="e", padx=5, pady=5)
                    ttk.Label(tab_valores, text=f"R$ {value:.2f}").grid(
                        row=i, column=1, sticky="w", padx=5, pady=5)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao obter detalhes:\n{str(e)}")

    def __del__(self):
        pass