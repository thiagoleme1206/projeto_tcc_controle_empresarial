import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime

class ModuloClientes:
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

        # Cria o notebook (abas)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cria as abas
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
        """Cria a interface da aba de cadastro de clientes"""
        form_frame = ttk.LabelFrame(self.aba_cadastro, text=" Cadastro de Cliente", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Grid configuration (2 columns)
        for i in range(3):  # 3 rows
            form_frame.grid_rowconfigure(i, weight=1)
        for j in range(2):  # 2 columns
            form_frame.grid_columnconfigure(j, weight=1)

        # Row 0 - CPF/CNPJ
        ttk.Label(form_frame, text="CPF/CNPJ:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_cpf_cnpj = ttk.Entry(form_frame, width=30)
        self.entry_cpf_cnpj.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Row 1 - Nome
        ttk.Label(form_frame, text="Nome:*", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome = ttk.Entry(form_frame, width=30)
        self.entry_nome.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Button frame
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(15, 5))

        # Save button
        btn_salvar = ttk.Button(btn_frame, text="Salvar Cliente", 
                              command=self.salvar_cliente,
                              style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        # Clear button
        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                              command=self.limpar_campos_cadastro)
        btn_limpar.pack(side=tk.LEFT, padx=5)

    def criar_aba_alteracao(self):
        """Cria a interface da aba de alteração de clientes"""
        main_frame = ttk.Frame(self.aba_alteracao)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Seção de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Cliente ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="CPF/CNPJ ou Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_alteracao = ttk.Entry(busca_frame, width=30)
        self.entry_busca_alteracao.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                             command=self.buscar_clientes_para_alteracao,
                             style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Treeview para resultados
        columns = ("ID", "CPF/CNPJ", "Nome")
        self.tree_clientes_alteracao = ttk.Treeview(busca_frame, columns=columns, show="headings", height=5)
        
        # Configuração das colunas
        self.tree_clientes_alteracao.heading("ID", text="ID")
        self.tree_clientes_alteracao.column("ID", width=50, anchor='center')
        self.tree_clientes_alteracao.heading("CPF/CNPJ", text="CPF/CNPJ")
        self.tree_clientes_alteracao.heading("Nome", text="Nome")
        
        self.tree_clientes_alteracao.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        self.tree_clientes_alteracao.bind("<<TreeviewSelect>>", self.selecionar_cliente_alteracao)

        # Seção de edição
        self.frame_edicao = ttk.LabelFrame(main_frame, text=" Editar Cliente ", padding=15)
        self.frame_edicao.pack(fill=tk.BOTH, expand=True)

        # Campos de edição
        ttk.Label(self.frame_edicao, text="CPF/CNPJ:*", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_cpf_cnpj_edit = ttk.Entry(self.frame_edicao, width=30)
        self.entry_cpf_cnpj_edit.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(self.frame_edicao, text="Nome:*", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_nome_edit = ttk.Entry(self.frame_edicao, width=30)
        self.entry_nome_edit.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Botões
        btn_frame = ttk.Frame(self.frame_edicao)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(15, 5))

        btn_salvar = ttk.Button(btn_frame, text="Salvar Alterações",
                             command=self.salvar_alteracoes,
                             style='Accent.TButton')
        btn_salvar.pack(side=tk.LEFT, padx=5)

        btn_limpar = ttk.Button(btn_frame, text="Limpar Campos",
                             command=self.limpar_campos_edicao)
        btn_limpar.pack(side=tk.LEFT, padx=5)

        # Inicialmente desabilita a edição
        self.habilitar_edicao(False)

    def criar_aba_exclusao(self):
        """Cria a interface da aba de exclusão de clientes"""
        main_frame = ttk.Frame(self.aba_exclusao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Cliente para Exclusão ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="CPF/CNPJ ou Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_exclusao = ttk.Entry(busca_frame, width=30)
        self.entry_busca_exclusao.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                             command=self.buscar_clientes_exclusao,
                             style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Treeview para resultados
        columns = ("ID", "CPF/CNPJ", "Nome")
        self.tree_clientes_exclusao = ttk.Treeview(busca_frame, columns=columns, show="headings", height=5)
        
        # Configuração das colunas
        self.tree_clientes_exclusao.heading("ID", text="ID")
        self.tree_clientes_exclusao.column("ID", width=50, anchor='center')
        self.tree_clientes_exclusao.heading("CPF/CNPJ", text="CPF/CNPJ")
        self.tree_clientes_exclusao.heading("Nome", text="Nome")
        
        self.tree_clientes_exclusao.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10, 0))

        # Botão de exclusão
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_excluir = ttk.Button(btn_frame, text="Excluir Cliente", 
                                   command=self.confirmar_exclusao,
                                   state='disabled',
                                   style='Danger.TButton')
        self.btn_excluir.pack(pady=10)

    def criar_aba_visualizacao(self):
        """Cria a interface da aba de visualização de clientes"""
        main_frame = ttk.Frame(self.aba_visualizacao, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame de busca
        busca_frame = ttk.LabelFrame(main_frame, text=" Buscar Clientes ", padding=15)
        busca_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(busca_frame, text="CPF/CNPJ ou Nome:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_busca_visualizacao = ttk.Entry(busca_frame, width=30)
        self.entry_busca_visualizacao.grid(row=0, column=1, padx=5, pady=5)

        btn_buscar = ttk.Button(busca_frame, text="Buscar", 
                             command=self.buscar_clientes_visualizacao,
                             style='Accent.TButton')
        btn_buscar.grid(row=0, column=2, padx=10)

        # Treeview para resultados
        columns = ("ID", "CPF/CNPJ", "Nome")
        self.tree_clientes_visualizacao = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # Configuração das colunas
        self.tree_clientes_visualizacao.heading("ID", text="ID")
        self.tree_clientes_visualizacao.column("ID", width=50, anchor='center')
        self.tree_clientes_visualizacao.heading("CPF/CNPJ", text="CPF/CNPJ")
        self.tree_clientes_visualizacao.heading("Nome", text="Nome")
        
        # Barra de rolagem
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree_clientes_visualizacao.yview)
        self.tree_clientes_visualizacao.configure(yscrollcommand=scrollbar.set)
        
        self.tree_clientes_visualizacao.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ========== MÉTODOS PARA CADASTRO ==========
    def limpar_campos_cadastro(self):
        """Limpa todos os campos da aba de cadastro"""
        self.entry_cpf_cnpj.delete(0, tk.END)
        self.entry_nome.delete(0, tk.END)

    def salvar_cliente(self):
        """Salva um novo cliente no banco de dados"""
        cpf_cnpj = self.entry_cpf_cnpj.get().strip()
        nome = self.entry_nome.get().strip()

        # Validação básica
        if not cpf_cnpj:
            messagebox.showwarning("Aviso", "CPF/CNPJ é obrigatório!")
            self.entry_cpf_cnpj.focus_set()
            return
            
        if not nome:
            messagebox.showwarning("Aviso", "Nome é obrigatório!")
            self.entry_nome.focus_set()
            return

        try:
            # Verifica se o CPF/CNPJ já existe
            self.cursor.execute("SELECT id_cliente FROM clientes WHERE cpf_cnpj = %s", (cpf_cnpj,))
            if self.cursor.fetchone():
                messagebox.showwarning("Aviso", "Já existe um cliente com este CPF/CNPJ!")
                return

            # Insere no banco de dados
            self.cursor.execute("""
                INSERT INTO clientes (cpf_cnpj, nome)
                VALUES (%s, %s)
            """, (cpf_cnpj, nome))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.limpar_campos_cadastro()
            
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar cliente:\n{str(e)}")

    # ========== MÉTODOS PARA ALTERAÇÃO ==========
    def buscar_clientes_para_alteracao(self):
        """Busca clientes para edição"""
        termo = self.entry_busca_alteracao.get().strip()
        if not termo:
            messagebox.showwarning("Aviso", "Digite um CPF/CNPJ ou nome para buscar!")
            return

        try:
            self.tree_clientes_alteracao.delete(*self.tree_clientes_alteracao.get_children())
            
            # Busca por CPF/CNPJ ou nome
            self.cursor.execute("""
                SELECT id_cliente, cpf_cnpj, nome 
                FROM clientes 
                WHERE cpf_cnpj LIKE %s OR nome ILIKE %s
                ORDER BY nome
            """, (f"%{termo}%", f"%{termo}%"))
            
            clientes = self.cursor.fetchall()
            
            if clientes:
                for cliente in clientes:
                    self.tree_clientes_alteracao.insert("", "end", values=cliente)
            else:
                messagebox.showinfo("Info", "Nenhum cliente encontrado!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar clientes:\n{str(e)}")

    def selecionar_cliente_alteracao(self, event):
        """Carrega os dados do cliente selecionado para edição"""
        item = self.tree_clientes_alteracao.selection()
        if not item:
            return
            
        id_cliente = self.tree_clientes_alteracao.item(item, 'values')[0]
        
        try:
            self.cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
            cliente = self.cursor.fetchone()
            
            if cliente:
                self.cliente_selecionado = cliente[0]  # id_cliente
                self.preencher_campos_edicao(cliente)
                self.habilitar_edicao(True)
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar cliente:\n{str(e)}")

    def preencher_campos_edicao(self, cliente):
        """Preenche os campos com os dados do cliente"""
        self.entry_cpf_cnpj_edit.delete(0, tk.END)
        self.entry_cpf_cnpj_edit.insert(0, cliente[1])  # cpf_cnpj
        
        self.entry_nome_edit.delete(0, tk.END)
        self.entry_nome_edit.insert(0, cliente[2])  # nome

    def habilitar_edicao(self, habilitar):
        """Habilita ou desabilita os campos de edição"""
        estado = 'normal' if habilitar else 'disabled'
        self.entry_cpf_cnpj_edit.config(state=estado)
        self.entry_nome_edit.config(state=estado)

    def limpar_campos_edicao(self):
        """Limpa todos os campos da aba de edição"""
        self.cliente_selecionado = None
        self.entry_cpf_cnpj_edit.delete(0, tk.END)
        self.entry_nome_edit.delete(0, tk.END)
        self.habilitar_edicao(False)

    def salvar_alteracoes(self):
        """Salva as alterações do cliente no banco de dados"""
        if not self.cliente_selecionado:
            messagebox.showwarning("Aviso", "Nenhum cliente selecionado!")
            return
            
        cpf_cnpj = self.entry_cpf_cnpj_edit.get().strip()
        nome = self.entry_nome_edit.get().strip()

        # Validação básica
        if not cpf_cnpj:
            messagebox.showwarning("Aviso", "CPF/CNPJ é obrigatório!")
            self.entry_cpf_cnpj_edit.focus_set()
            return
            
        if not nome:
            messagebox.showwarning("Aviso", "Nome é obrigatório!")
            self.entry_nome_edit.focus_set()
            return

        try:
            # Verifica se o CPF/CNPJ já existe em outro cliente
            self.cursor.execute("""
                SELECT id_cliente FROM clientes 
                WHERE cpf_cnpj = %s AND id_cliente != %s
            """, (cpf_cnpj, self.cliente_selecionado))
            
            if self.cursor.fetchone():
                messagebox.showwarning("Aviso", "Já existe outro cliente com este CPF/CNPJ!")
                return

            # Atualiza no banco de dados
            self.cursor.execute("""
                UPDATE clientes SET
                    cpf_cnpj = %s,
                    nome = %s
                WHERE id_cliente = %s
            """, (cpf_cnpj, nome, self.cliente_selecionado))
            
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            
            # Atualiza a lista de clientes
            self.buscar_clientes_para_alteracao()
            
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar cliente:\n{str(e)}")

    # ========== MÉTODOS PARA EXCLUSÃO ==========
    def buscar_clientes_exclusao(self):
        """Busca clientes para exclusão"""
        termo = self.entry_busca_exclusao.get().strip()
        if not termo:
            messagebox.showwarning("Aviso", "Digite um CPF/CNPJ ou nome para buscar!")
            return

        try:
            self.tree_clientes_exclusao.delete(*self.tree_clientes_exclusao.get_children())
            
            # Busca por CPF/CNPJ ou nome
            self.cursor.execute("""
                SELECT id_cliente, cpf_cnpj, nome 
                FROM clientes 
                WHERE cpf_cnpj LIKE %s OR nome ILIKE %s
                ORDER BY nome
            """, (f"%{termo}%", f"%{termo}%"))
            
            clientes = self.cursor.fetchall()
            
            if clientes:
                for cliente in clientes:
                    self.tree_clientes_exclusao.insert("", "end", values=cliente)
                self.btn_excluir.config(state='normal')
            else:
                messagebox.showinfo("Info", "Nenhum cliente encontrado!")
                self.btn_excluir.config(state='disabled')
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar clientes:\n{str(e)}")
            self.btn_excluir.config(state='disabled')

    def confirmar_exclusao(self):
        """Confirma e executa a exclusão do cliente"""
        item = self.tree_clientes_exclusao.selection()
        if not item:
            messagebox.showwarning("Aviso", "Nenhum cliente selecionado!")
            return
            
        id_cliente = self.tree_clientes_exclusao.item(item, 'values')[0]
        nome = self.tree_clientes_exclusao.item(item, 'values')[2]
        
        # Verifica se o cliente está vinculado a algum projeto
        try:
            self.cursor.execute("""
                SELECT COUNT(*) FROM projetos 
                WHERE id_cliente = %s
            """, (id_cliente,))
            
            if self.cursor.fetchone()[0] > 0:
                messagebox.showwarning("Aviso", 
                    "Este cliente possui projetos vinculados e não pode ser excluído!")
                return
        
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao verificar vínculos:\n{str(e)}")
            return

        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o cliente {nome}?"):
            return
            
        try:
            self.cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
            
            # Atualiza a lista
            self.buscar_clientes_exclusao()
            
        except psycopg2.Error as e:
            self.conn.rollback()
            messagebox.showerror("Erro", f"Falha ao excluir cliente:\n{str(e)}")

    # ========== MÉTODOS PARA VISUALIZAÇÃO ==========
    def buscar_clientes_visualizacao(self):
        """Busca clientes para visualização"""
        termo = self.entry_busca_visualizacao.get().strip()
        
        try:
            self.tree_clientes_visualizacao.delete(*self.tree_clientes_visualizacao.get_children())
            
            if termo:
                # Busca filtrada
                self.cursor.execute("""
                    SELECT id_cliente, cpf_cnpj, nome 
                    FROM clientes 
                    WHERE cpf_cnpj LIKE %s OR nome ILIKE %s
                    ORDER BY nome
                """, (f"%{termo}%", f"%{termo}%"))
            else:
                # Todos os clientes
                self.cursor.execute("""
                    SELECT id_cliente, cpf_cnpj, nome 
                    FROM clientes 
                    ORDER BY nome
                """)
            
            clientes = self.cursor.fetchall()
            
            if clientes:
                for cliente in clientes:
                    self.tree_clientes_visualizacao.insert("", "end", values=cliente)
            elif termo:
                messagebox.showinfo("Info", "Nenhum cliente encontrado com o filtro informado!")
                
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao buscar clientes:\n{str(e)}")

    def __del__(self):
        pass