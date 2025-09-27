import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

class ModuloReceita:
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
        self.notebook.add(self.aba_exclusao, text="Excluir")
        self.notebook.add(self.aba_visualizacao, text="Visualizar")

        # Configura o conteúdo de cada aba
        self.criar_aba_cadastro()
        self.criar_aba_exclusao()
        self.criar_aba_visualizacao()

    def criar_aba_cadastro(self):
        """Cria a interface da aba de cadastro de receitas"""
        form_frame = ttk.LabelFrame(self.aba_cadastro, text=" Cadastro de Receita", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Configuração do grid (4 colunas)
        for i in range(6):  # 6 linhas
            form_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):  # 4 colunas
            form_frame.grid_columnconfigure(j, weight=1)

        # Linha 0 - N° OS e Data
        ttk.Label(form_frame, text="N° OS Projeto:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_os = ttk.Entry(form_frame, width=20)
        self.entry_os.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Data Receita:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        self.entry_data = ttk.Entry(form_frame, width=20)
        self.entry_data.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))

        # Linha 1 - Nota Fiscal e Cliente
        ttk.Label(form_frame, text="Nota Fiscal:", font=('Arial', 10)).grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_nf = ttk.Entry(form_frame, width=20)
        self.entry_nf.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(form_frame, text="Cliente:*", font=('Arial', 10, 'bold')).grid(
            row=1, column=2, sticky="e", padx=5, pady=5)
        self.entry_cliente = ttk.Entry(form_frame, width=20, state='readonly')
        self.entry_cliente.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Linha 2 - Valores (Serviço e Material)
        ttk.Label(form_frame, text="Valor Serviço(R$):", font=('Arial', 10)).grid(
            row=2, column=0, sticky="e", padx=5, pady=5)
        self.entry_servico = ttk.Entry(form_frame, width=20)
        self.entry_servico.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_servico.insert(0, "0.00")

        ttk.Label(form_frame, text="Valor Material(R$):", font=('Arial', 10)).grid(
            row=2, column=2, sticky="e", padx=5, pady=5)
        self.entry_material = ttk.Entry(form_frame, width=20)
        self.entry_material.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.entry_material.insert(0, "0.00")

        # Linha 3 - Impostos (Imposto e ICMS)
        ttk.Label(form_frame, text="Imposto(%):", font=('Arial', 10)).grid(
            row=3, column=0, sticky="e", padx=5, pady=5)
        self.entry_imposto = ttk.Entry(form_frame, width=20)
        self.entry_imposto.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.entry_imposto.insert(0, "0.00")

        ttk.Label(form_frame, text="ICMS(%):", font=('Arial', 10)).grid(
            row=3, column=2, sticky="e", padx=5, pady=5)
        self.entry_icms = ttk.Entry(form_frame, width=20)
        self.entry_icms.grid(row=3, column=3, sticky="w", padx=5, pady=5)
        self.entry_icms.insert(0, "0.00")

        # Linha 4 - Valor Líquido
        ttk.Label(form_frame, text="Valor Líquido(R$):", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.entry_liquido = ttk.Entry(form_frame, width=20, state='readonly', 
                                     font=('Arial', 10, 'bold'))
        self.entry_liquido.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.entry_liquido.insert(0, "R$ 0.00")

        # Frame para botões
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(15, 5))

        # Botão Salvar
        btn_salvar = ttk.Button(btn_frame, text="Salvar Receita", 
                              command=self.salvar_receita,
                              style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        # Botão Limpar
        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                              command=self.limpar_campos_cadastro)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Configura cálculo automático do valor líquido
        campos_valores = [
            self.entry_servico, self.entry_material, 
            self.entry_imposto, self.entry_icms
        ]
        
        for campo in campos_valores:
            campo.bind('<KeyRelease>', self.calcular_liquido)

        # Busca cliente quando OS é informada
        self.entry_os.bind('<FocusOut>', self.buscar_cliente_por_os)

    def criar_aba_exclusao(self):
        """Cria a interface da aba de exclusão de receitas"""
        # Container principal
        main_frame = ttk.Frame(self.aba_exclusao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Receitas para Exclusão ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        # Campo de busca
        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_excluir = ttk.Entry(busca_frame, width=25)
        self.entry_busca_excluir.grid(row=0, column=1, padx=5, pady=5)

        # Botão de busca
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_receita_exclusao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Frame para Treeview e barra de rolagem
        tree_frame = ttk.Frame(busca_frame)
        tree_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        busca_frame.grid_rowconfigure(1, weight=1)
        busca_frame.grid_columnconfigure(0, weight=1)

        # Barra de rolagem vertical
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview para mostrar as receitas encontradas
        self.tree_exclusao = ttk.Treeview(tree_frame, 
                                        columns=("ID", "OS", "Cliente", "Data", "Valor"),
                                        show="headings",
                                        yscrollcommand=scrollbar.set,
                                        height=6)
        self.tree_exclusao.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_exclusao.yview)

        # Configuração das colunas (ocultando a coluna ID)
        self.tree_exclusao.heading("ID", text="ID")
        self.tree_exclusao.heading("OS", text="N° OS")
        self.tree_exclusao.heading("Cliente", text="Cliente")
        self.tree_exclusao.heading("Data", text="Data")
        self.tree_exclusao.heading("Valor", text="Valor Líquido")
        
        self.tree_exclusao.column("ID", width=0, stretch=tk.NO)  # Oculta a coluna
        self.tree_exclusao.column("OS", width=100)
        self.tree_exclusao.column("Cliente", width=200)
        self.tree_exclusao.column("Data", width=100)
        self.tree_exclusao.column("Valor", width=100)

        # Frame de confirmação
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=(10, 0))

        # Botão de exclusão (inicialmente desabilitado)
        self.btn_excluir = ttk.Button(confirm_frame, text="Excluir Receita Selecionada", 
                                command=self.confirmar_exclusao,
                                state='disabled',
                                style='Danger.TButton')
        self.btn_excluir.pack(pady=10)

        # Status
        self.status_label_exclusao = ttk.Label(main_frame, text="", foreground='red')
        self.status_label_exclusao.pack()

        # Bind para tecla Enter e seleção na Treeview
        self.entry_busca_excluir.bind('<Return>', lambda e: self.buscar_receita_exclusao())
        self.tree_exclusao.bind("<<TreeviewSelect>>", self.habilitar_botao_exclusao)

    def criar_aba_visualizacao(self):
        """Cria a interface da aba de visualização de receitas"""
        # Container principal
        main_frame = ttk.Frame(self.aba_visualizacao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Receitas ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        # Campo de busca
        ttk.Label(busca_frame, text="N° OS Projeto:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_os_visualizacao = ttk.Entry(busca_frame, width=25)
        self.entry_busca_os_visualizacao.grid(row=0, column=1, padx=5, pady=5)

        # Botão de busca
        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                            command=self.buscar_receitas_visualizacao,
                            style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Frame para Treeview e barra de rolagem
        tree_frame = ttk.Frame(busca_frame)
        tree_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        busca_frame.grid_rowconfigure(1, weight=1)
        busca_frame.grid_columnconfigure(0, weight=1)

        # Barra de rolagem vertical
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview para mostrar as receitas encontradas
        self.tree_visualizacao = ttk.Treeview(tree_frame, 
                                            columns=("ID", "OS", "Cliente", "Data", "Valor"),
                                            show="headings",
                                            yscrollcommand=scrollbar.set,
                                            height=6)
        self.tree_visualizacao.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree_visualizacao.yview)

        # Configuração das colunas (ocultando a coluna ID)
        self.tree_visualizacao.heading("ID", text="ID")
        self.tree_visualizacao.heading("OS", text="N° OS")
        self.tree_visualizacao.heading("Cliente", text="Cliente")
        self.tree_visualizacao.heading("Data", text="Data")
        self.tree_visualizacao.heading("Valor", text="Valor Líquido")
        
        self.tree_visualizacao.column("ID", width=0, stretch=tk.NO)  # Oculta a coluna
        self.tree_visualizacao.column("OS", width=100)
        self.tree_visualizacao.column("Cliente", width=200)
        self.tree_visualizacao.column("Data", width=100)
        self.tree_visualizacao.column("Valor", width=100)

        # Bind para tecla Enter e seleção na Treeview
        self.entry_busca_os_visualizacao.bind('<Return>', lambda e: self.buscar_receitas_visualizacao())
        self.tree_visualizacao.bind("<Double-1>", self.mostrar_detalhes_receita)

        # Área de detalhes
        self.detalhes_frame = ttk.LabelFrame(main_frame, text=" Detalhes da Receita ", padding=15)
        self.detalhes_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Notebook para os detalhes
        self.detalhes_notebook = ttk.Notebook(self.detalhes_frame)
        self.detalhes_notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de informações básicas
        tab_basicos = ttk.Frame(self.detalhes_notebook)
        self.detalhes_notebook.add(tab_basicos, text="Informações Básicas")

        # Campos básicos (2 colunas)
        campos_basicos = [
            ("N° OS Projeto:", "entry_os_view"),
            ("Data Receita:", "entry_data_view"),
            ("Nota Fiscal:", "entry_nf_view"),
            ("Cliente:", "entry_cliente_view")
        ]

        for i, (label, var_name) in enumerate(campos_basicos):
            ttk.Label(tab_basicos, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(tab_basicos, state='readonly')
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            setattr(self, var_name, entry)

        # Aba de valores
        tab_valores = ttk.Frame(self.detalhes_notebook)
        self.detalhes_notebook.add(tab_valores, text="Valores")

        campos_valores = [
            ("Valor Serviço(R$):", "entry_servico_view"),
            ("Valor Material(R$):", "entry_material_view"),
            ("Imposto(%):", "entry_imposto_view"),
            ("ICMS(%):", "entry_icms_view"),
            ("Valor Líquido(R$):", "entry_liquido_view")
        ]

        for i, (label, var_name) in enumerate(campos_valores):
            ttk.Label(tab_valores, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(tab_valores, state='readonly')
            entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            setattr(self, var_name, entry)

    # --- MÉTODOS PRINCIPAIS ---
    def buscar_cliente_por_os(self, event=None):
        """Busca o cliente associado a uma OS de projeto"""
        os_numero = self.entry_os.get().strip()
        if not os_numero:
            return

        try:
            self.cursor.execute("""
                SELECT cliente_nome FROM projetos WHERE numero_os = %s
            """, (os_numero,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                self.entry_cliente.config(state='normal')
                self.entry_cliente.delete(0, tk.END)
                self.entry_cliente.insert(0, resultado[0])
                self.entry_cliente.config(state='readonly')
            else:
                messagebox.showwarning("Aviso", "OS de projeto não encontrada!")
                self.entry_os.focus_set()
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar projeto:\n{str(e)}")

    def calcular_liquido(self, event=None):
        """Calcula o valor líquido automaticamente considerando impostos como percentuais"""
        try:
            # Obtém valores brutos
            servico = float(self.entry_servico.get() or 0)
            material = float(self.entry_material.get() or 0)
            perc_imposto = float(self.entry_imposto.get() or 0)  # Já é percentual (ex: 5.75 para 5.75%)
            perc_icms = float(self.entry_icms.get() or 0)        # Já é percentual (ex: 18.0 para 18%)

            # Validação: Serviço OU Material (não ambos)
            if servico and material:
                messagebox.showwarning("Aviso", "Informe apenas Serviço OU Material, não ambos!")
                return

            # Cálculo dos impostos
            if servico > 0:
                # Para serviços: imposto incide sobre o total, ICMS não incide
                valor_imposto = servico * (perc_imposto / 100)
                valor_icms = 0
                liquido = servico - valor_imposto
            elif material > 0:
                # Para materiais: imposto incide primeiro, depois ICMS sobre o valor reduzido
                valor_imposto = material * (perc_imposto / 100)
                base_icms = material - valor_imposto
                valor_icms = base_icms * (perc_icms / 100)
                liquido = material - valor_imposto - valor_icms
            else:
                liquido = 0

            # Atualiza a interface
            self.entry_liquido.config(state='normal')
            self.entry_liquido.delete(0, tk.END)
            self.entry_liquido.insert(0, f"R$ {liquido:.2f}")
            self.entry_liquido.config(state='readonly')
            
        except ValueError:
            # Se ocorrer erro na conversão, simplesmente ignora (mantém o valor atual)
            pass

    def salvar_receita(self):
        """Salva uma nova receita no banco de dados seguindo as novas regras"""
        # Validação básica
        if not self.entry_os.get():
            messagebox.showwarning("Aviso", "N° OS do projeto é obrigatório!")
            self.entry_os.focus_set()
            return
            
        if not self.entry_data.get():
            messagebox.showwarning("Aviso", "Data da receita é obrigatória!")
            self.entry_data.focus_set()
            return
            
        if not self.entry_cliente.get():
            messagebox.showwarning("Aviso", "Cliente não encontrado! Verifique o N° OS.")
            self.entry_os.focus_set()
            return

        try:
            # Converter valores monetários
            servico = float(self.entry_servico.get() or 0)
            material = float(self.entry_material.get() or 0)
            perc_imposto = float(self.entry_imposto.get() or 0)/100  # Converte porcentagem para decimal
            perc_icms = float(self.entry_icms.get() or 0)/100        # Converte porcentagem para decimal
            
            # Validação: Serviço OU Material (não ambos)
            if servico and material:
                messagebox.showwarning("Aviso", "Informe apenas Serviço OU Material, não ambos!")
                return

            if not (servico or material):
                messagebox.showwarning("Aviso", "Informe o valor do Serviço ou do Material!")
                return

            # Cálculo do valor líquido 
            if servico:
                valor_bruto = servico
                imposto_calculado = servico * perc_imposto
                icms_calculado = 0  # ICMS não incide sobre serviço
            else:
                valor_bruto = material
                imposto_calculado = material * perc_imposto
                valor_reduzido = material - imposto_calculado
                icms_calculado = valor_reduzido * perc_icms

            liquido_calculado = valor_bruto - imposto_calculado - icms_calculado

            # Converter data
            data_receita = datetime.strptime(self.entry_data.get(), '%d/%m/%Y').date()

            # Inserir no banco de dados
            self.cursor.execute("""
                INSERT INTO receitas (
                    numero_os_projeto, data_receita, nf, cliente,
                    valor_servico, valor_material, imposto, icms, valor_liquido
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """, (
                self.entry_os.get(),
                data_receita,
                self.entry_nf.get() or None,
                self.entry_cliente.get(),
                servico,
                material,
                imposto_calculado,
                icms_calculado,
                liquido_calculado
            ))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Receita cadastrada com sucesso!")
            self.limpar_campos_cadastro()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar receita:\n{str(e)}")

    def limpar_campos_cadastro(self):
        """Limpa todos os campos da aba de cadastro"""
        for widget in self.aba_cadastro.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
        
        # Restaura valores padrão
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, datetime.now().strftime('%d/%m/%Y'))

        self.entry_servico.delete(0, tk.END)
        self.entry_servico.insert(0, "0.00")

        self.entry_material.delete(0, tk.END)
        self.entry_material.insert(0, "0.00")

        self.entry_imposto.delete(0, tk.END)
        self.entry_imposto.insert(0, "0.00")

        self.entry_icms.delete(0, tk.END)
        self.entry_icms.insert(0, "0.00")

        self.entry_liquido.delete(0, tk.END)
        self.entry_liquido.config(state='normal')
        self.entry_liquido.delete(0, tk.END)
        self.entry_liquido.insert(0, "R$ 0.00")
        self.entry_liquido.config(state='readonly')

    def buscar_receita_exclusao(self):
        """Busca receitas para exclusão"""
        os_numero = self.entry_busca_excluir.get().strip()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um N° OS!")
            return

        try:
            self.tree_exclusao.delete(*self.tree_exclusao.get_children())
            
            # Consulta que traz o ID da receita (oculto) e demais informações
            self.cursor.execute("""
                SELECT id_receita, numero_os_projeto, cliente, data_receita, valor_liquido
                FROM receitas 
                WHERE numero_os_projeto = %s
                ORDER BY data_receita DESC
            """, (os_numero,))
            
            receitas = self.cursor.fetchall()
            
            if receitas:
                for receita in receitas:
                    self.tree_exclusao.insert("", "end", 
                                        values=(receita[0], receita[1], receita[2], 
                                                receita[3].strftime('%d/%m/%Y'), f"R$ {receita[4]:.2f}"),
                                        tags=(receita[0],))
                self.status_label_exclusao.config(text=f"Encontradas {len(receitas)} receitas")
            else:
                messagebox.showinfo("Info", "Nenhuma receita encontrada!")
                self.status_label_exclusao.config(text="Nenhuma receita encontrada")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar receitas:\n{str(e)}")
            self.status_label_exclusao.config(text="Erro na busca")

    def habilitar_botao_exclusao(self, event=None):
        """Habilita o botão de exclusão quando uma receita é selecionada"""
        item = self.tree_exclusao.selection()
        if item:
            self.btn_excluir.config(state='normal')
        else:
            self.btn_excluir.config(state='disabled')

    def confirmar_exclusao(self):
        """Confirma e executa a exclusão da receita selecionada"""
        item = self.tree_exclusao.selection()
        if not item:
            messagebox.showwarning("Aviso", "Nenhuma receita selecionada!")
            return
            
        # Obtém o ID da receita da coluna oculta
        id_receita = self.tree_exclusao.item(item, 'values')[0]
        os_numero = self.tree_exclusao.item(item, 'values')[1]
        data_receita = self.tree_exclusao.item(item, 'values')[3]
        
        # Confirmação
        if not messagebox.askyesno("Confirmar Exclusão", 
                                f"Tem certeza que deseja excluir a receita:\n\n"
                                f"OS: {os_numero}\n"
                                f"Data: {data_receita}\n"
                                f"Valor: {self.tree_exclusao.item(item, 'values')[4]}"):
            return
            
        try:
            # Executa a exclusão pelo ID
            self.cursor.execute("DELETE FROM receitas WHERE id_receita = %s", (id_receita,))
            self.conn.commit()
            
            messagebox.showinfo("Sucesso", "Receita excluída com sucesso!")
            
            # Atualiza a lista
            self.buscar_receita_exclusao()
            self.btn_excluir.config(state='disabled')
            
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao excluir receita:\n{str(e)}")

    def buscar_receitas_visualizacao(self):
        """Busca receitas para visualização"""
        os_numero = self.entry_busca_os_visualizacao.get().strip()
        if not os_numero:
            messagebox.showwarning("Aviso", "Digite um N° OS!")
            return

        try:
            self.tree_visualizacao.delete(*self.tree_visualizacao.get_children())
            
            # Consulta que traz o ID da receita (oculto) e demais informações
            self.cursor.execute("""
                SELECT id_receita, numero_os_projeto, cliente, data_receita, valor_liquido
                FROM receitas 
                WHERE numero_os_projeto = %s
                ORDER BY data_receita DESC
            """, (os_numero,))
            
            receitas = self.cursor.fetchall()
            
            if receitas:
                for receita in receitas:
                    self.tree_visualizacao.insert("", "end", 
                                            values=(receita[0], receita[1], receita[2], 
                                                    receita[3].strftime('%d/%m/%Y'), f"R$ {receita[4]:.2f}"),
                                            tags=(receita[0],))
            else:
                messagebox.showinfo("Info", "Nenhuma receita encontrada!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar receitas:\n{str(e)}")

    def mostrar_detalhes_receita(self, event):
        """Mostra os detalhes da receita selecionada"""
        item = self.tree_visualizacao.selection()
        if not item:
            return
            
        # Obtém o ID da receita da coluna oculta
        id_receita = self.tree_visualizacao.item(item, 'values')[0]
        
        try:
            # Busca todos os dados da receita
            self.cursor.execute("""
                SELECT * FROM receitas 
                WHERE id_receita = %s
            """, (id_receita,))
            
            receita = self.cursor.fetchone()
            
            if receita:
                # Preenche os campos básicos
                self.entry_os_view.config(state='normal')
                self.entry_os_view.delete(0, tk.END)
                self.entry_os_view.insert(0, receita[1])  # numero_os_projeto
                self.entry_os_view.config(state='readonly')
                
                # Formata a data
                data_formatada = receita[2].strftime('%d/%m/%Y')  # data_receita
                self.entry_data_view.config(state='normal')
                self.entry_data_view.delete(0, tk.END)
                self.entry_data_view.insert(0, data_formatada)
                self.entry_data_view.config(state='readonly')
                
                # Nota fiscal
                self.entry_nf_view.config(state='normal')
                self.entry_nf_view.delete(0, tk.END)
                self.entry_nf_view.insert(0, receita[3] or "")
                self.entry_nf_view.config(state='readonly')
                
                # Cliente
                self.entry_cliente_view.config(state='normal')
                self.entry_cliente_view.delete(0, tk.END)
                self.entry_cliente_view.insert(0, receita[4] or "")
                self.entry_cliente_view.config(state='readonly')
                
                # Preenche os valores
                self.entry_servico_view.config(state='normal')
                self.entry_servico_view.delete(0, tk.END)
                self.entry_servico_view.insert(0, f"R$ {receita[5]:.2f}")  # valor_servico
                self.entry_servico_view.config(state='readonly')
                
                self.entry_material_view.config(state='normal')
                self.entry_material_view.delete(0, tk.END)
                self.entry_material_view.insert(0, f"R$ {receita[6]:.2f}")  # valor_material
                self.entry_material_view.config(state='readonly')
                
                self.entry_imposto_view.config(state='normal')
                self.entry_imposto_view.delete(0, tk.END)
                self.entry_imposto_view.insert(0, f"R$ {receita[7]:.2f}")  # imposto
                self.entry_imposto_view.config(state='readonly')
                
                self.entry_icms_view.config(state='normal')
                self.entry_icms_view.delete(0, tk.END)
                self.entry_icms_view.insert(0, f"R$ {receita[8]:.2f}")  # icms
                self.entry_icms_view.config(state='readonly')
                
                self.entry_liquido_view.config(state='normal')
                self.entry_liquido_view.delete(0, tk.END)
                self.entry_liquido_view.insert(0, f"R$ {receita[9]:.2f}")  # valor_liquido
                self.entry_liquido_view.config(state='readonly')
                
            else:
                messagebox.showwarning("Aviso", "Receita não encontrada no banco de dados!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar receita:\n{str(e)}")

    def __del__(self):
        pass