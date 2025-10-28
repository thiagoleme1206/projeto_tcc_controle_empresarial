import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psycopg2
from datetime import datetime
from fpdf import FPDF
import json

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
            if item.lower().startswith(self.get().lower()):
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
        
        if len(event.keysym) == 1:
            self.autocomplete()

class SistemaListaMateriais:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Lista de Materiais")
        self.root.geometry("900x700")
        
        # Configuração do banco de dados
        self.db_config = {
            'host': 'localhost',
            'database': 'projeto_final',
            'user': 'postgres',
            'password': 'Edu1Sal2',
            'port': '5432'
        }
        
        # Dados da lista
        self.itens_lista = []
        self.total_geral = 0.0
        self.produtos_disponiveis = []  
        self.dados_produtos = {} 
        
        # Criar widgets
        self.criar_widgets()
        self.carregar_produtos()
 
    
    def conectar_banco(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{str(e)}")
            return None
    
    def criar_widgets(self):
        # Notebook (abas principais)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba 1: Criação de Lista
        self.aba_criacao = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_criacao, text="Criar Lista")
        self.criar_aba_criacao()
        
        # Aba 2: Adição de Valores
        self.aba_valores = ttk.Frame(self.notebook)
        self.notebook.add(self.aba_valores, text="Adicionar Valores")
        self._criar_aba_valores()

    def criar_aba_criacao(self):
        # Frame principal
        main_frame = ttk.Frame(self.aba_criacao)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame de busca e adição
        frame_busca = ttk.LabelFrame(main_frame, text="Adicionar Itens")
        frame_busca.pack(fill=tk.X, padx=5, pady=5)
        
        # Campo de busca de produto
        ttk.Label(frame_busca, text="Buscar Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_produto = AutocompleteCombobox(frame_busca, width=60)
        self.combo_produto.grid(row=0, column=1, padx=5, pady=5, sticky="ew", columnspan=2)
        
        # Campos para quantidade e valor unitário
        ttk.Label(frame_busca, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_quantidade = ttk.Entry(frame_busca)
        self.entry_quantidade.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.label_unidade = ttk.Label(frame_busca, text="")
        self.label_unidade.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_busca, text="Valor Unitário:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_valor = ttk.Entry(frame_busca)
        self.entry_valor.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Botão para adicionar
        btn_frame_adicionar = ttk.Frame(frame_busca)
        btn_frame_adicionar.grid(row=3, column=0, columnspan=3, pady=5)

        ttk.Button(btn_frame_adicionar, text="Adicionar à Lista", command=self.adicionar_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_adicionar, text="Excluir Selecionado", command=self.excluir_item).pack(side=tk.LEFT, padx=5)
        
        # Frame da lista de itens
        frame_lista = ttk.LabelFrame(main_frame, text="Itens da Lista")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para mostrar os itens
        columns = ('ID', 'Produto', 'Quantidade', 'Valor', 'Total')
        self.tree_itens = ttk.Treeview(frame_lista, columns=columns, show='headings')
        
        # Configurar colunas
        self.tree_itens.heading('ID', text="", anchor=tk.W)
        self.tree_itens.heading('Produto', text='Produto')
        self.tree_itens.heading('Quantidade', text='Quantidade')
        self.tree_itens.heading('Valor', text='Valor Unitário')
        self.tree_itens.heading('Total', text='Total')
        
        self.tree_itens.column('ID', width=0, stretch=tk.NO)
        self.tree_itens.column('Produto', width=300, anchor='w')
        self.tree_itens.column('Quantidade', width=100, anchor='e')
        self.tree_itens.column('Valor', width=120, anchor='e')
        self.tree_itens.column('Total', width=120, anchor='e')
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_itens.yview)
        hsb = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree_itens.xview)
        self.tree_itens.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree_itens.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configurar expansão
        frame_lista.grid_rowconfigure(0, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        # Frame de informações adicionais
        frame_info = ttk.LabelFrame(main_frame, text="Informações da Lista")
        frame_info.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_info, text="Responsável:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_responsavel = ttk.Entry(frame_info)
        self.entry_responsavel.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Linha da OS/Proposta com botão de busca
        frame_referencia = ttk.Frame(frame_info)
        frame_referencia.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(frame_referencia, text="OS/Proposta:").pack(side=tk.LEFT, padx=5)
        self.entry_referencia = ttk.Entry(frame_referencia)
        self.entry_referencia.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        btn_buscar = ttk.Button(frame_referencia, text="Buscar", command=self.buscar_lista_existente, width=10)
        btn_buscar.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_info, text="Observações:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.text_observacoes = tk.Text(frame_info, height=4, width=40)
        self.text_observacoes.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Frame de total e botões
        frame_rodape = ttk.Frame(main_frame)
        frame_rodape.pack(fill=tk.X, padx=5, pady=5)
        
        # Label do total
        self.label_total = ttk.Label(frame_rodape, text="Total: R$ 0,00", font=('Arial', 10, 'bold'))
        self.label_total.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame dos botões
        btn_frame = ttk.Frame(frame_rodape)
        btn_frame.pack(side=tk.RIGHT)
        
        # Botões
        ttk.Button(btn_frame, text="Limpar Lista", command=self.limpar_lista).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar Lista", command=self.salvar_lista).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Gerar PDF", command=self.gerar_pdf).pack(side=tk.LEFT, padx=5)

    def _criar_aba_valores(self):
        # Frame principal
        main_frame = ttk.Frame(self.aba_valores)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de busca
        frame_busca = ttk.LabelFrame(main_frame, text="Buscar Lista")
        frame_busca.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_busca, text="OS/Proposta:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_busca_referencia = ttk.Entry(frame_busca)
        self.entry_busca_referencia.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        btn_buscar = ttk.Button(frame_busca, text="Buscar", command=self.buscar_lista_por_referencia)
        btn_buscar.grid(row=0, column=2, padx=5, pady=5)
        
        # Frame de informações
        frame_info = ttk.LabelFrame(main_frame, text="Informações da Lista")
        frame_info.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_info, text="Responsável:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_responsavel_valores = ttk.Entry(frame_info)
        self.entry_responsavel_valores.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_info, text="OS/Proposta:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_referencia_valores = ttk.Entry(frame_info)
        self.entry_referencia_valores.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_info, text="Observações:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.text_observacoes_valores = tk.Text(frame_info, height=4, width=40)
        self.text_observacoes_valores.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Frame da lista
        frame_lista = ttk.LabelFrame(main_frame, text="Itens da Lista")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview
        columns = ('ID', 'Produto', 'Quantidade', 'Valor', 'Total')
        self.tree_itens_valores = ttk.Treeview(frame_lista, columns=columns, show='headings')
        
        # Configuração das colunas
        for col in columns:
            self.tree_itens_valores.heading(col, text=col)
            self.tree_itens_valores.column(col, width=100, anchor='e')
        
        self.tree_itens_valores.column('Produto', width=250, anchor='w')
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree_itens_valores.yview)
        hsb = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree_itens_valores.xview)
        self.tree_itens_valores.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid
        self.tree_itens_valores.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Frame de valores
        frame_valores = ttk.Frame(main_frame)
        frame_valores.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame_valores, text="Valor Unitário:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_valor_unitario = ttk.Entry(frame_valores, width=15)
        self.entry_valor_unitario.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        btn_frame_valores = ttk.Frame(frame_valores)
        btn_frame_valores.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        ttk.Button(btn_frame_valores, text="Atualizar Valor", command=self.atualizar_valor).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame_valores, text="Excluir Selecionado", command=self.excluir_item_valores).pack(side=tk.LEFT, padx=5)
        
        # Frame de rodapé
        frame_rodape = ttk.Frame(main_frame)
        frame_rodape.pack(fill=tk.X, padx=5, pady=5)
        
        # Label do total
        self.label_total_valores = ttk.Label(frame_rodape, text="Total: R$ 0.00", font=('Arial', 10, 'bold'))
        self.label_total_valores.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame dos botões
        btn_frame = ttk.Frame(frame_rodape)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Limpar", command=self.limpar_lista_valores).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Atualizar Lista", command=self.salvar_valores).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Gerar PDF", command=self.gerar_pdf_valores).pack(side=tk.LEFT, padx=5)
    
    def carregar_produtos(self):
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_produto, nome, unidade_medida FROM produto ORDER BY nome")
            produtos = cursor.fetchall()
            
            # Lista de produtos para o combobox (armazenamos o nome exato)
            self.produtos_disponiveis = [p[1] for p in produtos]
            self.combo_produto.set_completion_list(self.produtos_disponiveis)
            
            # Dicionário para mapear nomes (em minúsculo) para dados completos
            self.dados_produtos = {p[1].lower(): {'id': p[0], 'nome_exato': p[1], 'unidade': p[2]} for p in produtos}
            
            # Configuração adicional para melhorar a usabilidade
            self.combo_produto.bind('<<ComboboxSelected>>', self._preencher_nome_exato)
            self.combo_produto.bind('<<ComboboxSelected>>', self._atualizar_unidade_medida)
            
        except psycopg2.Error as e:
            messagebox.showerror("Erro", f"Falha ao carregar produtos:\n{str(e)}")
        finally:
            conn.close()

    def _preencher_nome_exato(self, event):
        """Garante que o nome exato do produto seja usado quando selecionado da lista"""
        selected = self.combo_produto.get()
        if selected.lower() in self.dados_produtos:
            nome_exato = self.dados_produtos[selected.lower()]['nome_exato']
            self.combo_produto.set(nome_exato)

    def _atualizar_unidade_medida(self, event):
        """Atualiza o label da unidade quando um produto é selecionado"""
        produto_selecionado = self.combo_produto.get().strip()
        if produto_selecionado:
            chave = produto_selecionado.lower()
            if chave in self.dados_produtos:
                unidade = self.dados_produtos[chave]['unidade']
                self.label_unidade.config(text=unidade)
    
    def adicionar_item(self):
        # Obtém o texto do combobox
        texto_produto = self.combo_produto.get().strip()
        
        if not texto_produto:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
        
        # Verifica se o produto existe
        chave_produto = texto_produto.lower()
        
        if chave_produto not in self.dados_produtos:
            # Tenta encontrar correspondência exata
            for nome in self.produtos_disponiveis:
                if nome.lower() == chave_produto:
                    texto_produto = nome
                    chave_produto = texto_produto.lower()
                    self.combo_produto.set(texto_produto)
                    break
            else:
                messagebox.showwarning("Aviso", "Produto não encontrado! Selecione um produto da lista.")
                return
        
        try:
            # Obtém os dados do produto
            produto = self.dados_produtos[chave_produto]
            
            # Atualiza o label com a unidade de medida
            self.label_unidade.config(text=produto['unidade'])
            
            # Validação dos campos numéricos
            quantidade = float(self.entry_quantidade.get().strip())
            valor = float(self.entry_valor.get().strip())
            
            # Cálculos
            total = quantidade * valor
            
            # Adiciona à treeview
            self.tree_itens.insert('', tk.END, values=(
                produto['id'],
                f"{produto['nome_exato']} ({produto['unidade']})",
                f"{quantidade:.2f}",
                f"R$ {valor:.2f}",
                f"R$ {total:.2f}"
            ))
            
            # Adiciona à lista interna
            self.itens_lista.append({
                'id_produto': produto['id'],
                'produto': produto['nome_exato'],
                'unidade': produto['unidade'],
                'quantidade': quantidade,
                'valor': valor,
                'total': total
            })
            
            # Atualiza o total geral
            self.total_geral += total
            self.label_total.config(text=f"Total: R$ {self.total_geral:.2f}")
            
            # Limpa os campos
            self.entry_quantidade.delete(0, tk.END)
            self.entry_valor.delete(0, tk.END)
            self.combo_produto.set('')
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e valor devem ser números válidos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao adicionar item:\n{str(e)}")
    
    def limpar_lista(self):
        # Limpar treeview
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
        
        # Limpar lista interna
        self.itens_lista = []
        self.total_geral = 0.0
        self.label_total.config(text="Total: R$ 0,00")
        
        # Limpar campos de informação (exceto OS/Proposta)
        self.entry_responsavel.delete(0, tk.END)
        self.text_observacoes.delete('1.0', tk.END)
        self.label_unidade.config(text="")
        
        # Limpar ID de lista existente se houver
        if hasattr(self, 'lista_existente_id'):
            del self.lista_existente_id
    
    def salvar_lista(self):
        # Validar dados
        responsavel = self.entry_responsavel.get().strip()
        if not responsavel:
            messagebox.showwarning("Aviso", "Informe o responsável pela lista!")
            return
            
        if not self.itens_lista:
            messagebox.showwarning("Aviso", "Adicione itens à lista antes de salvar!")
            return
            
        # Preparar dados
        referencia = self.entry_referencia.get().strip()
        observacoes = self.text_observacoes.get('1.0', tk.END).strip()
        
        conn = self.conectar_banco()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Se for uma lista existente, atualiza
            if hasattr(self, 'lista_existente_id'):
                cursor.execute("""
                    UPDATE lista_materiais 
                    SET itens = %s, 
                        responsavel = %s,
                        os_referencia = %s,
                        observacao = %s
                    WHERE id_lista = %s
                """, (
                    json.dumps(self.itens_lista),
                    responsavel,
                    referencia if referencia else None,
                    observacoes if observacoes else None,
                    self.lista_existente_id
                ))
                mensagem = "Lista atualizada com sucesso!"
            else:
                # Caso contrário, insere nova lista
                cursor.execute("""
                    INSERT INTO lista_materiais (itens, responsavel, observacao, os_referencia)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id_lista
                """, (
                    json.dumps(self.itens_lista),
                    responsavel,
                    observacoes if observacoes else None,
                    referencia if referencia else None
                ))
                self.lista_existente_id = cursor.fetchone()[0]
                mensagem = f"Lista salva com sucesso!\nID: {self.lista_existente_id}"
            
            conn.commit()
            messagebox.showinfo("Sucesso", mensagem)
            
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao salvar lista:\n{str(e)}")
        finally:
            conn.close()
    
    def gerar_pdf(self):
        if not self.itens_lista:
            messagebox.showwarning("Aviso", "Adicione itens à lista antes de gerar o PDF!")
            return
            
        # Configurar PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Título
        pdf.cell(0, 10, 'Lista de Materiais', 0, 1, 'C')
        pdf.ln(10)
        
        # Informações
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
        
        responsavel = self.entry_responsavel.get().strip()
        if responsavel:
            pdf.cell(0, 6, f"Responsável: {responsavel}", 0, 1)
        
        referencia = self.entry_referencia.get().strip()
        if referencia:
            pdf.cell(0, 6, f"OS/Proposta: {referencia}", 0, 1)
        
        pdf.ln(10)
        
        # Cabeçalho da tabela
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(100, 8, 'Produto', 1, 0, 'C')
        pdf.cell(25, 8, 'Quantidade', 1, 0, 'C')
        pdf.cell(30, 8, 'Valor Unit.', 1, 0, 'C')
        pdf.cell(30, 8, 'Total', 1, 1, 'C')
        
        # Itens
        pdf.set_font('Arial', '', 10)
        for item in self.itens_lista:
            pdf.cell(100, 8, f"{item['produto']} ({item['unidade']})", 1, 0)
            pdf.cell(25, 8, f"{item['quantidade']:.2f}", 1, 0, 'R')
            pdf.cell(30, 8, f"R$ {item['valor']:.2f}", 1, 0, 'R')
            pdf.cell(30, 8, f"R$ {item['total']:.2f}", 1, 1, 'R')
        
        # Total
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(155, 8, 'TOTAL GERAL:', 1, 0, 'R')
        pdf.cell(30, 8, f"R$ {self.total_geral:.2f}", 1, 1, 'R')
        
        # Observações
        observacoes = self.text_observacoes.get('1.0', tk.END).strip()
        if observacoes:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Observações:', 0, 1)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, observacoes)
        
        # Salvar arquivo
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Salvar Lista como PDF",
                initialfile=f"lista_materiais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            
            if file_path:
                pdf.output(file_path)
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\n{file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{str(e)}")

    def buscar_lista_por_referencia(self):
        referencia = self.entry_busca_referencia.get().strip()
        if not referencia:
            messagebox.showwarning("Aviso", "Informe uma OS/Referência para buscar!")
            return
        
        conn = self.conectar_banco()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_lista, itens, responsavel, os_referencia, observacao 
                FROM lista_materiais 
                WHERE os_referencia = %s
                ORDER BY data_criacao DESC
                LIMIT 1
            """, (referencia,))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                messagebox.showinfo("Informação", "Nenhuma lista encontrada com esta referência!")
                return
            
            # Limpa a treeview
            for item in self.tree_itens_valores.get_children():
                self.tree_itens_valores.delete(item)
            
            # Carrega os itens
            itens = json.loads(resultado[1]) if isinstance(resultado[1], str) else resultado[1]
            
            # Preenche os campos de informação
            self.entry_responsavel_valores.delete(0, tk.END)
            self.entry_responsavel_valores.insert(0, resultado[2] or "")
            
            self.entry_referencia_valores.delete(0, tk.END)
            self.entry_referencia_valores.insert(0, resultado[3] or "")
            
            self.text_observacoes_valores.delete('1.0', tk.END)
            self.text_observacoes_valores.insert('1.0', resultado[4] or "")
            
            # Calcula o total
            total_geral = 0.0
            
            for item in itens:
                valor = item.get('valor', 0)
                quantidade = item.get('quantidade', 0)
                total = valor * quantidade
                total_geral += total
                
                self.tree_itens_valores.insert('', tk.END, values=(
                    item['id_produto'],
                    f"{item['produto']} ({item['unidade']})",
                    f"{quantidade:.2f}",
                    f"R$ {valor:.2f}",
                    f"R$ {total:.2f}"
                ))
            
            # Atualiza o total
            self.label_total_valores.config(text=f"Total: R$ {total_geral:.2f}")
            
            # Armazena o ID da lista para atualização
            self.lista_atual_id = resultado[0]
            self.lista_atual_itens = itens
            self.calcular_total_valores()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao buscar lista:\n{str(e)}")
        finally:
            conn.close()

    def atualizar_valor(self):
        selecionado = self.tree_itens_valores.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para atualizar!")
            return
        
        try:
            # Obtém o novo valor do campo de entrada
            novo_valor_str = self.entry_valor_unitario.get().strip()
            
            # Converte para float, tratando tanto . quanto , como separador decimal
            novo_valor = float(novo_valor_str.replace(",", "."))
            
            if novo_valor < 0:
                raise ValueError("O valor não pode ser negativo")
                
            # Obtém os valores atuais da linha selecionada
            item = self.tree_itens_valores.item(selecionado)
            valores = list(item['values'])
            
            # Converte a quantidade para float (já removendo formatação se existir)
            quantidade_str = valores[2].replace("R$ ", "").replace(",", ".")
            quantidade = float(quantidade_str)
            
            # Calcula o novo total
            total = quantidade * novo_valor
            
            # Formata os valores para exibição
            valor_formatado = f"R$ {novo_valor:,.2f}".replace(",", "X").replace("X", ".")
            total_formatado = f"R$ {total:,.2f}".replace(",", "X").replace("X", ".")
            
            # Atualiza a treeview
            valores[3] = valor_formatado
            valores[4] = total_formatado
            self.tree_itens_valores.item(selecionado, values=valores)
            
            # Atualiza a lista em memória
            item_id = int(valores[0])
            for item in self.lista_atual_itens:
                if item['id_produto'] == item_id:
                    item['valor'] = novo_valor
                    item['total'] = total
                    break
            
            # Recalcula e atualiza o total geral
            self.atualizar_total_geral_valores()
            
            # Limpa o campo de valor
            self.entry_valor_unitario.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")

    def atualizar_total_geral_valores(self):
        total_geral = 0.0
        
        # Soma todos os totais dos itens na lista em memória
        for item in self.lista_atual_itens:
            total_geral += item['total']
        
        # Atualiza o label com o total formatado
        total_formatado = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.label_total_valores.config(text=f"Total: {total_formatado}")

    def atualizar_valor_no_banco(self, item_id, novo_valor):
        conn = self.conectar_banco()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Primeiro obtém a lista atual
            cursor.execute("SELECT itens FROM lista_materiais WHERE id_lista = %s", (self.lista_atual_id,))
            itens = json.loads(cursor.fetchone()[0])
            
            # Atualiza o valor no item correspondente
            for item in itens:
                if str(item['id_produto']) == self.tree_itens_valores.item(item_id, 'values')[0]:
                    item['valor'] = novo_valor
                    if 'total' in item:
                        item['total'] = item['quantidade'] * novo_valor
                    break
            
            # Atualiza no banco de dados
            cursor.execute("""
                UPDATE lista_materiais 
                SET itens = %s 
                WHERE id_lista = %s
            """, (json.dumps(itens), self.lista_atual_id))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Valor atualizado com sucesso!")
            
        except psycopg2.Error as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar valor:\n{str(e)}")
        finally:
            conn.close()

    def calcular_total_valores(self):
        total_geral = 0.0
        
        # Itera sobre todos os itens na lista em memória (mais confiável que a treeview)
        for item in self.lista_atual_itens:
            total_geral += item.get('total', 0)
        
        # Atualiza o label com o total formatado corretamente
        total_formatado = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.label_total_valores.config(text=f"Total: {total_formatado}")

    def salvar_valores(self):
        if not hasattr(self, 'lista_atual_id'):
            messagebox.showwarning("Aviso", "Nenhuma lista carregada para atualizar!")
            return
        
        responsavel = self.entry_responsavel_valores.get().strip()
        if not responsavel:
            messagebox.showwarning("Aviso", "Informe o responsável pela lista!")
            return
        
        conn = self.conectar_banco()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Prepara os dados
            referencia = self.entry_referencia_valores.get().strip()
            observacoes = self.text_observacoes_valores.get('1.0', tk.END).strip()
            
            # Atualiza a lista no banco de dados
            cursor.execute("""
                UPDATE lista_materiais 
                SET itens = %s, 
                    responsavel = %s,
                    os_referencia = %s,
                    observacao = %s
                WHERE id_lista = %s
            """, (
                json.dumps(self.lista_atual_itens),
                responsavel,
                referencia if referencia else None,
                observacoes if observacoes else None,
                self.lista_atual_id
            ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Lista atualizada com sucesso!")
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar lista:\n{str(e)}")
        finally:
            conn.close()

    def limpar_lista_valores(self):
        for item in self.tree_itens_valores.get_children():
            self.tree_itens_valores.delete(item)
        
        self.entry_responsavel_valores.delete(0, tk.END)
        self.entry_referencia_valores.delete(0, tk.END)
        self.text_observacoes_valores.delete('1.0', tk.END)
        self.entry_valor_unitario.delete(0, tk.END)
        self.label_total_valores.config(text="Total: R$ 0.00")
        
        if hasattr(self, 'lista_atual_id'):
            del self.lista_atual_id
        if hasattr(self, 'lista_atual_itens'):
            del self.lista_atual_itens

    def gerar_pdf_valores(self):
        if not hasattr(self, 'lista_atual_id') or not hasattr(self, 'lista_atual_itens'):
            messagebox.showwarning("Aviso", "Nenhuma lista carregada para gerar PDF!")
            return
        
        try:
            # Configurar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            
            # Título
            pdf.cell(0, 10, 'Lista de Materiais', 0, 1, 'C')
            pdf.ln(10)
            
            # Informações da lista
            pdf.set_font('Arial', '', 10)
            
            # Data e hora de geração
            pdf.cell(0, 6, f"Data de geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
            
            # Responsável
            responsavel = self.entry_responsavel_valores.get().strip()
            if responsavel:
                pdf.cell(0, 6, f"Responsável: {responsavel}", 0, 1)
            
            # Referência/OS
            referencia = self.entry_referencia_valores.get().strip()
            if referencia:
                pdf.cell(0, 6, f"OS/Proposta: {referencia}", 0, 1)
            
            pdf.ln(10)
            
            # Cabeçalho da tabela
            pdf.set_font('Arial', 'B', 10)
            col_widths = [15, 95, 25, 25, 25]
            headers = ['ID', 'Produto', 'Quantidade', 'Valor Unit.', 'Total']
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8, header, 1, 0, 'C')
            pdf.ln()
            
            # Itens da lista
            pdf.set_font('Arial', '', 9)
            total_geral = 0.0
            
            for item in self.lista_atual_itens:
                # ID
                pdf.cell(col_widths[0], 8, str(item['id_produto']), 1, 0, 'C')
                
                # Produto e unidade
                produto_text = f"{item['produto']} ({item['unidade']})"
                pdf.cell(col_widths[1], 8, produto_text, 1, 0)
                
                # Quantidade
                quantidade = item.get('quantidade', 0)
                pdf.cell(col_widths[2], 8, f"{quantidade:.2f}", 1, 0, 'R')
                
                # Valor Unitário
                valor = item.get('valor', 0)
                pdf.cell(col_widths[3], 8, f"R$ {valor:.2f}", 1, 0, 'R')
                
                # Total
                total = valor * quantidade
                pdf.cell(col_widths[4], 8, f"R$ {total:.2f}", 1, 1, 'R')
                
                total_geral += total
            
            # Total Geral
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(sum(col_widths[:4]), 8, 'TOTAL GERAL:', 1, 0, 'R')
            pdf.cell(col_widths[4], 8, f"R$ {total_geral:.2f}", 1, 1, 'R')
            
            # Observações
            observacoes = self.text_observacoes_valores.get('1.0', tk.END).strip()
            if observacoes:
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, 'Observações:', 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 6, observacoes)
            
            # Salvar arquivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Salvar Lista com Valores",
                initialfile=f"lista_valores_{referencia}_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
            if file_path:
                pdf.output(file_path)
                messagebox.showinfo("Sucesso", f"PDF gerado com sucesso:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{str(e)}")

    def excluir_item(self):
        selecionado = self.tree_itens.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para excluir!")
            return
        
        # Obtém os valores do item selecionado
        valores = self.tree_itens.item(selecionado, 'values')
        
        try:
            # Remove o item da treeview
            self.tree_itens.delete(selecionado)
            
            # Remove o item da lista interna
            id_produto = int(valores[0])
            for i, item in enumerate(self.itens_lista):
                if item['id_produto'] == id_produto:
                    # Subtrai o total do item do total geral
                    self.total_geral -= item['total']
                    # Remove o item da lista
                    self.itens_lista.pop(i)
                    break
            
            # Atualiza o total geral
            self.label_total.config(text=f"Total: R$ {self.total_geral:.2f}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir item:\n{str(e)}")

    def excluir_item_valores(self):
        selecionado = self.tree_itens_valores.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para excluir!")
            return
        
        # Obtém os valores do item selecionado
        valores = self.tree_itens_valores.item(selecionado, 'values')
        
        try:
            # Remove o item da treeview
            self.tree_itens_valores.delete(selecionado)
            
            # Remove o item da lista em memória
            id_produto = int(valores[0])
            for i, item in enumerate(self.lista_atual_itens):
                if item['id_produto'] == id_produto:
                    self.lista_atual_itens.pop(i)
                    break
            
            # Recalcula o total geral
            self.calcular_total_valores()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao excluir item:\n{str(e)}")

    def buscar_lista_existente(self):
        referencia = self.entry_referencia.get().strip()
        if not referencia:
            messagebox.showwarning("Aviso", "Informe uma OS/Proposta para buscar!")
            return
        
        conn = self.conectar_banco()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_lista, itens, responsavel, os_referencia, observacao 
                FROM lista_materiais 
                WHERE os_referencia = %s
                ORDER BY data_criacao DESC
                LIMIT 1
            """, (referencia,))
            
            resultado = cursor.fetchone()
            
            if not resultado:
                messagebox.showinfo("Informação", "Nenhuma lista encontrada com esta referência!")
                return
            
            # Limpa a lista atual
            self.limpar_lista()
            
            # Preenche os campos de informação
            self.entry_responsavel.delete(0, tk.END)
            self.entry_responsavel.insert(0, resultado[2] or "")
            
            # Não altera a referência (OS/Proposta) pois já está preenchida
            self.text_observacoes.delete('1.0', tk.END)
            self.text_observacoes.insert('1.0', resultado[4] or "")
            
            # Carrega os itens
            itens = json.loads(resultado[1]) if isinstance(resultado[1], str) else resultado[1]
            self.total_geral = 0.0
            
            for item in itens:
                self.tree_itens.insert('', tk.END, values=(
                    item['id_produto'],
                    f"{item['produto']} ({item['unidade']})",
                    f"{item['quantidade']:.2f}",
                    f"R$ {item['valor']:.2f}",
                    f"R$ {item['total']:.2f}"
                ))
                
                # Adiciona à lista interna
                self.itens_lista.append(item)
                self.total_geral += item['total']
            
            # Atualiza o total
            self.label_total.config(text=f"Total: R$ {self.total_geral:.2f}")
            
            # Armazena o ID da lista para possível atualização posterior
            self.lista_existente_id = resultado[0]
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao buscar lista:\n{str(e)}")
        finally:
            conn.close()

def main():
    root = tk.Tk()
    app = SistemaListaMateriais(root)
    root.mainloop()

if __name__ == "__main__":
    main()