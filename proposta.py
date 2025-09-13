import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psycopg2
from datetime import datetime
import os
import sys

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "database": "projeto_final",
    "user": "postgres",
    "password": "",
    "port": "5432"
}

def conectar_banco():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados:\n{str(e)}")
        return None

def criar_tabela_se_nao_existir():
    conn = conectar_banco()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'propostas'
            );
        """)
        tabela_existe = cursor.fetchone()[0]
        
        if not tabela_existe:
            cursor.execute("""
                CREATE TABLE propostas (
                    proposta_id SERIAL PRIMARY KEY,
                    numero_proposta VARCHAR(20) NOT NULL UNIQUE,
                    data_proposta DATE NOT NULL,
                    cliente VARCHAR(100) NOT NULL,
                    setor VARCHAR(50) NOT NULL,
                    descricao_servico TEXT NOT NULL,
                    responsavel_venda VARCHAR(100) NOT NULL,
                    indicacao VARCHAR(100),
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_proposta_numero ON propostas(numero_proposta);
                CREATE INDEX idx_proposta_cliente ON propostas(cliente);
                CREATE INDEX idx_proposta_responsavel ON propostas(responsavel_venda);
            """)
            conn.commit()
            
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar tabela: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# Verifica e cria a tabela ao iniciar o sistema
criar_tabela_se_nao_existir()

from datetime import datetime

def gerar_numero_proposta():
    hoje = datetime.today()
    dia = hoje.day
    mes = hoje.month
    ano = hoje.year % 100  # dois dígitos
    
    conn = conectar_banco()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        
        # Busca o maior ID de proposta na tabela
        cursor.execute("SELECT MAX(proposta_id) FROM propostas")
        resultado = cursor.fetchone()
        maior_id = resultado[0] if resultado[0] is not None else 0
        
        sequencial = maior_id 
        
        # Formata a data como YYMMDD e adiciona o sequencial
        return f"{ano:02d}{mes:02d}{dia:02d}/{sequencial}"
    except Exception as e:
        print(f"Erro ao gerar número de proposta: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def carregar_dados_banco(tree):
    try:
        tree.delete(*tree.get_children())
        
        conn = conectar_banco()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                TO_CHAR(data_proposta, 'DD/MM/YYYY') AS data_formatada,
                numero_proposta,
                cliente,
                setor,
                descricao_servico,
                responsavel_venda,
                COALESCE(indicacao, '') AS indicacao
            FROM propostas
            ORDER BY data_proposta DESC, numero_proposta DESC
        """)
        
        row_count = 0
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)
            row_count += 1
            
        
        
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
        messagebox.showerror("Erro", f"Não foi possível carregar os dados:\n{str(e)}")
    finally:
        if conn:
            conn.close()

def salvar_dados(entry_cliente, setor_var, entry_descricao, entry_responsavel, entry_indicacao, status_label, notebook, tree):
    cliente = entry_cliente.get().strip()
    setor = setor_var.get().strip()
    descricao = entry_descricao.get("1.0", "end-1c").strip()
    responsavel = entry_responsavel.get().strip()
    indicacao = entry_indicacao.get().strip()  

    if not cliente:
        status_label.config(text="O campo Cliente é obrigatório!", foreground="red")
        entry_cliente.focus()
        return
    if not setor:
        status_label.config(text="O campo Setor é obrigatório!", foreground="red")
        return
    if not descricao:
        status_label.config(text="O campo Descrição é obrigatório!", foreground="red")
        entry_descricao.focus()
        return
    if not responsavel:
        status_label.config(text="O campo Responsável é obrigatório!", foreground="red")
        entry_responsavel.focus()
        return

    try:
        numero_proposta = gerar_numero_proposta()
        if not numero_proposta:
            raise Exception("Não foi possível gerar o número da proposta")
            
        data_atual = datetime.today().date()
        
        conn = conectar_banco()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO propostas (
                numero_proposta, data_proposta, cliente, setor, 
                descricao_servico, responsavel_venda, indicacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            numero_proposta, data_atual, cliente, setor, 
            descricao, responsavel, indicacao if indicacao else None
        ))
        
        conn.commit()
        
        entry_cliente.delete(0, "end")
        setor_var.set("Solar")
        entry_descricao.delete("1.0", "end")
        entry_responsavel.delete(0, "end")
        entry_indicacao.delete(0, "end") 
        
        mensagem = f"Dados salvos com sucesso! Nº da Proposta: {numero_proposta}"
        status_label.config(text=mensagem, foreground="green")

        carregar_dados_banco(tree)

    except Exception as e:
        error_msg = f"Erro ao salvar: {str(e)}"
        print(error_msg)
        status_label.config(text=error_msg, foreground="red")
    finally:
        if conn:
            conn.close()

def buscar_proposta_para_alteracao(entry_busca, tree_alteracao, entry_cliente_alt, setor_var_alt, 
                                 entry_descricao_alt, entry_responsavel_alt, entry_indicacao_alt, status_label_alt):
    proposta_busca = entry_busca.get().strip()
    if not proposta_busca:
        status_label_alt.config(text="Digite um número de proposta para buscar.", foreground="red")
        return None

    try:
        conn = conectar_banco()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                TO_CHAR(data_proposta, 'DD/MM/YYYY') AS data_formatada,
                numero_proposta,
                cliente,
                setor,
                descricao_servico,
                responsavel_venda,
                COALESCE(indicacao, '') AS indicacao
            FROM propostas
            WHERE numero_proposta = %s
        """, (proposta_busca,))
        
        proposta = cursor.fetchone()
        
        tree_alteracao.delete(*tree_alteracao.get_children())
        
        if proposta:
            tree_alteracao.insert("", tk.END, values=proposta)
            
            entry_cliente_alt.delete(0, tk.END)
            entry_cliente_alt.insert(0, proposta[2])
            
            setor_var_alt.set(proposta[3] or "Solar")
            
            entry_descricao_alt.delete("1.0", tk.END)
            entry_descricao_alt.insert("1.0", proposta[4])
            
            entry_responsavel_alt.delete(0, tk.END)
            entry_responsavel_alt.insert(0, proposta[5])
            
            entry_indicacao_alt.delete(0, tk.END)
            entry_indicacao_alt.insert(0, proposta[6])
            
            status_label_alt.config(text=f"Proposta {proposta_busca} encontrada", foreground="green")
            return proposta_busca
        else:
            status_label_alt.config(text=f"Proposta {proposta_busca} não encontrada.", foreground="red")
            return None
            
    except Exception as e:
        status_label_alt.config(text=f"Erro: {str(e)}", foreground="red")
        return None
    finally:
        if conn:
            conn.close()

def salvar_alteracao(numero_proposta, entry_cliente_alt, setor_var_alt, 
                    entry_descricao_alt, entry_responsavel_alt, entry_indicacao_alt, status_label_alt):
    if not numero_proposta:
        status_label_alt.config(text="Busque uma proposta primeiro.", foreground="red")
        return

    cliente = entry_cliente_alt.get().strip()
    setor = setor_var_alt.get().strip()
    descricao = entry_descricao_alt.get("1.0", tk.END).strip()
    responsavel = entry_responsavel_alt.get().strip()
    indicacao = entry_indicacao_alt.get().strip()  

    if not cliente or not setor or not descricao or not responsavel:
        status_label_alt.config(text="Preencha todos os campos obrigatórios!", foreground="red")
        return

    try:
        conn = conectar_banco()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE propostas
            SET 
                cliente = %s,
                setor = %s,
                descricao_servico = %s,
                responsavel_venda = %s,
                indicacao = %s
            WHERE numero_proposta = %s
        """, (cliente, setor, descricao, responsavel, indicacao if indicacao else None, numero_proposta))
        
        conn.commit()
        status_label_alt.config(text="Alterações salvas com sucesso!", foreground="green")
        
        entry_cliente_alt.delete(0, tk.END)
        setor_var_alt.set("Solar")
        entry_descricao_alt.delete("1.0", tk.END)
        entry_responsavel_alt.delete(0, tk.END)
        entry_indicacao_alt.delete(0, tk.END)  
            
    except Exception as e:
        status_label_alt.config(text=f"Erro: {str(e)}", foreground="red")
    finally:
        if conn:
            conn.close()

def buscar_apenas_para_exclusao(entry_busca, tree, status_label):
    proposta_busca = entry_busca.get().strip()
    if not proposta_busca:
        status_label.config(text="Digite um número de proposta para buscar.", foreground="red")
        return None

    try:
        conn = conectar_banco()
        if conn is None:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                TO_CHAR(data_proposta, 'DD/MM/YYYY') AS data_formatada,
                numero_proposta,
                cliente,
                setor,
                descricao_servico,
                responsavel_venda,
                COALESCE(indicacao, '') AS indicacao
            FROM propostas
            WHERE numero_proposta = %s
        """, (proposta_busca,))
        
        proposta = cursor.fetchone()
        
        tree.delete(*tree.get_children())
        
        if proposta:
            tree.insert("", tk.END, values=proposta)
            status_label.config(text=f"Proposta {proposta_busca} encontrada", foreground="green")
            return proposta_busca
        else:
            status_label.config(text=f"Proposta {proposta_busca} não encontrada.", foreground="red")
            return None
            
    except Exception as e:
        status_label.config(text=f"Erro: {str(e)}", foreground="red")
        return None
    finally:
        if conn:
            conn.close()

def excluir_proposta(entry_busca_exc, tree_exclusao, status_label_exc):
    proposta_busca = entry_busca_exc.get().strip()
    if not proposta_busca:
        status_label_exc.config(text="Digite um número de proposta para excluir.", foreground="red")
        return

    try:
        conn = conectar_banco()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                TO_CHAR(data_proposta, 'DD/MM/YYYY') AS data_formatada,
                numero_proposta,
                cliente,
                setor,
                descricao_servico,
                responsavel_venda,
                COALESCE(indicacao, '') AS indicacao
            FROM propostas
            WHERE numero_proposta = %s
        """, (proposta_busca,))
        
        proposta = cursor.fetchone()
        
        if not proposta:
            status_label_exc.config(text=f"Proposta {proposta_busca} não encontrada.", foreground="red")
            return
        
        tree_exclusao.delete(*tree_exclusao.get_children())
        tree_exclusao.insert("", tk.END, values=proposta)
        
        if not messagebox.askyesno("Confirmar Exclusão", 
                                 f"Tem certeza que deseja excluir a proposta {proposta_busca}?\nEsta ação não pode ser desfeita."):
            return
        
        cursor.execute("DELETE FROM propostas WHERE numero_proposta = %s", (proposta_busca,))
        conn.commit()
        
        status_label_exc.config(text=f"Proposta {proposta_busca} excluída com sucesso!", foreground="green")
        entry_busca_exc.delete(0, tk.END)
        tree_exclusao.delete(*tree_exclusao.get_children())
            
    except Exception as e:
        status_label_exc.config(text=f"Erro: {str(e)}", foreground="red")
    finally:
        if conn:
            conn.close()

def buscar_por_cliente(entry_busca, tree, status_label):
    cliente_busca = entry_busca.get().strip().lower()
    if not cliente_busca:
        status_label.config(text="Digite um nome de cliente para buscar.", foreground="red")
        return

    try:
        conn = conectar_banco()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                TO_CHAR(data_proposta, 'DD/MM/YYYY') AS data_formatada,
                numero_proposta,
                cliente,
                setor,
                descricao_servico,
                responsavel_venda,
                COALESCE(indicacao, '') AS indicacao
            FROM propostas
            WHERE LOWER(cliente) LIKE %s
            ORDER BY data_proposta DESC, numero_proposta DESC
        """, (f"%{cliente_busca}%",))
        
        tree.delete(*tree.get_children())
        
        encontrou = False
        for proposta in cursor.fetchall():
            tree.insert("", tk.END, values=proposta)
            encontrou = True
        
        if encontrou:
            status_label.config(text=f"Propostas encontradas para clientes com '{cliente_busca}'.", foreground="green")
        else:
            status_label.config(text=f"Nenhuma proposta encontrada para clientes com '{cliente_busca}'.", foreground="red")
            
    except Exception as e:
        status_label.config(text=f"Erro: {str(e)}", foreground="red")
    finally:
        if conn:
            conn.close()

# Configuração da janela principal
janela = tk.Tk()
janela.title("Sistema de Gestão de Propostas - AVL")
janela.geometry("1100x700")  
janela.configure(bg='#f0f0f0')

# Adição ícone
try:
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(application_path, "logo.ico")
    janela.iconbitmap(icon_path)
    print(f"Ícone carregado de: {icon_path}")
except Exception as e:
    print(f"Erro ao carregar o ícone: {str(e)}")
    try:
        janela.iconbitmap("icone.ico")
    except:
        print("Fallback também falhou. Continuando sem ícone.")

# Estilo
style = ttk.Style()
style.configure('TFrame', background='#f0f0f0')
style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
style.configure('TButton', font=('Arial', 10))
style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

# Parte 1: Cabeçalho
header_frame = ttk.Frame(janela, style='TFrame')
header_frame.pack(fill=tk.X, padx=10, pady=10)

ttk.Label(header_frame, text="Sistema de Gestão de Propostas", style='Header.TLabel').pack(side=tk.LEFT)
ttk.Label(header_frame, text=f"Data: {datetime.today().strftime('%d/%m/%Y')}", style='TLabel').pack(side=tk.RIGHT)

# Criando o notebook (abas)
notebook = ttk.Notebook(janela)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Aba 1: Cadastro
aba_cadastro = ttk.Frame(notebook)
notebook.add(aba_cadastro, text="Cadastrar")

# Configuração do Frame de Cadastro
form_frame = ttk.LabelFrame(aba_cadastro, text=" Cadastro de Nova Proposta ", padding=20)
form_frame.pack(fill=tk.X, padx=20, pady=15)

form_frame.columnconfigure(1, weight=1)
form_frame.rowconfigure(1, weight=1)

# Campo Cliente
ttk.Label(form_frame, text="Cliente:*", font=('Arial', 10, 'bold')).grid(
    row=0, column=0, sticky="e", padx=5, pady=5)
entry_cliente = ttk.Entry(form_frame, width=40)
entry_cliente.grid(row=0, column=1, sticky="we", padx=5, pady=5)

# Campo Setor
ttk.Label(form_frame, text="Setor:*", font=('Arial', 10, 'bold')).grid(
    row=0, column=2, sticky="e", padx=(15,5), pady=5)
setor_var = tk.StringVar(value="Solar")
setor_menu = ttk.Combobox(form_frame, textvariable=setor_var, values=["Solar", "Indústria", "Comércio", "Residência"], width=15, state="readonly")
setor_menu.grid(row=0, column=3, sticky="w", padx=5, pady=5)

# Campo Descrição
ttk.Label(form_frame, text="Descrição do Serviço:*", font=('Arial', 10, 'bold')).grid(
    row=1, column=0, sticky="ne", padx=5, pady=5)

desc_frame = ttk.Frame(form_frame)
desc_frame.grid(row=1, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)

entry_descricao = tk.Text(desc_frame, width=60, height=6, font=('Arial', 10), wrap=tk.WORD, relief="solid", borderwidth=1)
entry_descricao.pack(fill=tk.BOTH, expand=True)

# Campo Responsável
ttk.Label(form_frame, text="Responsável:*", font=('Arial', 10, 'bold')).grid(
    row=2, column=0, sticky="e", padx=5, pady=5)
entry_responsavel = ttk.Entry(form_frame, width=40)
entry_responsavel.grid(row=2, column=1, sticky="w", padx=5, pady=5)

# Campo Indicação
ttk.Label(form_frame, text="Indicação:", font=('Arial', 10, 'bold')).grid(
    row=3, column=0, sticky="e", padx=5, pady=5)
entry_indicacao = ttk.Entry(form_frame, width=40)
entry_indicacao.grid(row=3, column=1, sticky="w", padx=5, pady=5)

# Botão Salvar
btn_frame = ttk.Frame(form_frame)
btn_frame.grid(row=4, column=0, columnspan=4, pady=(10,0))  
btn_salvar = ttk.Button(btn_frame, text="Salvar Proposta", command=lambda: salvar_dados(
    entry_cliente, setor_var, entry_descricao,
    entry_responsavel, entry_indicacao, status_label, notebook,
    tree), width=20)
btn_salvar.pack()

status_label = ttk.Label(form_frame, text="", foreground='green')
status_label.grid(row=5, column=0, columnspan=4)  

colunas_grid = ("DATA", "PROPOSTA", "CLIENTE", "SETOR", "DESCRIÇÃO DE SERVIÇO", "RESPONSÁVEL VENDA", "INDICAÇÃO")

# Aba 3: Exclusão
aba_exclusao = ttk.Frame(notebook)
notebook.add(aba_exclusao, text="Excluir")

# Frame de busca na aba de exclusão
frame_busca_exc = ttk.LabelFrame(aba_exclusao, text=" Buscar Proposta para Exclusão ", padding=10)
frame_busca_exc.pack(fill=tk.X, padx=20, pady=10)

ttk.Label(frame_busca_exc, text="Número da Proposta:").grid(row=0, column=0, padx=5, pady=5)
entry_busca_exc = ttk.Entry(frame_busca_exc, width=25)
entry_busca_exc.grid(row=0, column=1, padx=5, pady=5)

btn_buscar_exc = ttk.Button(frame_busca_exc, text="Buscar", width=10,
                          command=lambda: buscar_apenas_para_exclusao(
                              entry_busca_exc, tree_exclusao, status_label_exc
                          ))
btn_buscar_exc.grid(row=0, column=2, padx=(10,5), pady=5)

# Frame de resultados da busca
result_frame_exc = ttk.Frame(frame_busca_exc)
result_frame_exc.grid(row=1, column=0, columnspan=3, sticky="we", pady=(10,0))

tree_exclusao = ttk.Treeview(result_frame_exc, columns=colunas_grid, show="headings", height=1)

# Configuração das colunas
tree_exclusao.column("DATA", width=100, anchor=tk.CENTER)
tree_exclusao.column("PROPOSTA", width=80, anchor=tk.CENTER)
tree_exclusao.column("CLIENTE", width=150, anchor=tk.W)
tree_exclusao.column("SETOR", width=80, anchor=tk.CENTER)
tree_exclusao.column("DESCRIÇÃO DE SERVIÇO", width=250, anchor=tk.W)
tree_exclusao.column("RESPONSÁVEL VENDA", width=120, anchor=tk.CENTER)
tree_exclusao.column("INDICAÇÃO", width=120, anchor=tk.CENTER) 

# Cabeçalhos
for col in colunas_grid:
    tree_exclusao.heading(col, text=col)

tree_exclusao.pack(fill=tk.X)
xscroll_exc = ttk.Scrollbar(result_frame_exc, orient=tk.HORIZONTAL, command=tree_exclusao.xview)
xscroll_exc.pack(fill=tk.X)
tree_exclusao.configure(xscrollcommand=xscroll_exc.set)

# Botão Excluir
btn_frame_exc = ttk.Frame(frame_busca_exc)
btn_frame_exc.grid(row=2, column=0, columnspan=3, pady=(10,0))
btn_excluir = ttk.Button(btn_frame_exc, text="Excluir Proposta", width=20,
                        command=lambda: excluir_proposta(entry_busca_exc, tree_exclusao, status_label_exc))
btn_excluir.pack()

status_label_exc = ttk.Label(frame_busca_exc, text="", foreground='green')
status_label_exc.grid(row=3, column=0, columnspan=3, pady=(5,0))

# Aba 4: Visualização
aba_visualizacao = ttk.Frame(notebook)
notebook.add(aba_visualizacao, text="Visualizar")

# Grid de propostas
grid_frame = ttk.Frame(aba_visualizacao)
grid_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Treeview com barra de rolagem
tree_scroll = ttk.Scrollbar(grid_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
tree = ttk.Treeview(grid_frame, columns=colunas_grid, show="headings", yscrollcommand=tree_scroll.set, height=15)

# Configuração das colunas
tree.column("DATA", width=120, anchor=tk.CENTER)
tree.column("PROPOSTA", width=100, anchor=tk.CENTER)
tree.column("CLIENTE", width=180, anchor=tk.W)
tree.column("SETOR", width=100, anchor=tk.CENTER)
tree.column("DESCRIÇÃO DE SERVIÇO", width=300, anchor=tk.W)
tree.column("RESPONSÁVEL VENDA", width=120, anchor=tk.CENTER)
tree.column("INDICAÇÃO", width=120, anchor=tk.W)  

# Cabeçalhos
for col in colunas_grid:
    tree.heading(col, text=col)

tree.pack(fill=tk.BOTH, expand=True)
tree_scroll.config(command=tree.yview)

# Botão de atualização
btn_atualizar_frame = ttk.Frame(aba_visualizacao)
btn_atualizar_frame.pack(fill=tk.X, padx=15, pady=(0,10))

btn_atualizar = ttk.Button(btn_atualizar_frame, text="Atualizar Dados", 
                          command=lambda: carregar_dados_banco(tree))
btn_atualizar.pack(side=tk.RIGHT)

# Carrega os dados iniciais
carregar_dados_banco(tree)

# Aba 5: Pesquisar Proposta 
aba_pesquisa = ttk.Frame(notebook)
notebook.add(aba_pesquisa, text="Pesquisar por Cliente")

# Frame de busca
frame_busca_pesquisa = ttk.LabelFrame(aba_pesquisa, text=" Buscar Propostas por Cliente ", padding=10)
frame_busca_pesquisa.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Campo de busca 
ttk.Label(frame_busca_pesquisa, text="Nome do Cliente:").grid(row=0, column=0, padx=5, pady=5)
entry_busca_pesquisa = ttk.Entry(frame_busca_pesquisa, width=25)
entry_busca_pesquisa.grid(row=0, column=1, padx=5, pady=5)

# Botão de busca
btn_buscar_pesquisa = ttk.Button(frame_busca_pesquisa, text="Buscar", width=10)
btn_buscar_pesquisa.grid(row=0, column=2, padx=(10, 5), pady=5)

# Treeview para resultados (com altura maior para múltiplos registros)
tree_pesquisa = ttk.Treeview(
    frame_busca_pesquisa, 
    columns=colunas_grid, 
    show="headings", 
    height=6 
)
tree_pesquisa.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

# Configuração das colunas 
tree_pesquisa.column("DATA", width=100, anchor=tk.CENTER)
tree_pesquisa.column("PROPOSTA", width=80, anchor=tk.CENTER)
tree_pesquisa.column("CLIENTE", width=150, anchor=tk.W)
tree_pesquisa.column("SETOR", width=80, anchor=tk.CENTER)
tree_pesquisa.column("DESCRIÇÃO DE SERVIÇO", width=250, anchor=tk.W)
tree_pesquisa.column("RESPONSÁVEL VENDA", width=120, anchor=tk.CENTER)
tree_pesquisa.column("INDICAÇÃO", width=120, anchor=tk.CENTER)

# Cabeçalhos
for col in colunas_grid:
    tree_pesquisa.heading(col, text=col)

# Barras de rolagem
scroll_y = ttk.Scrollbar(frame_busca_pesquisa, orient=tk.VERTICAL, command=tree_pesquisa.yview)
scroll_y.grid(row=1, column=3, sticky="ns")
tree_pesquisa.configure(yscrollcommand=scroll_y.set)

scroll_x = ttk.Scrollbar(frame_busca_pesquisa, orient=tk.HORIZONTAL, command=tree_pesquisa.xview)
scroll_x.grid(row=2, column=0, columnspan=3, sticky="ew")
tree_pesquisa.configure(xscrollcommand=scroll_x.set)

# Status label
status_label_pesquisa = ttk.Label(frame_busca_pesquisa, text="", foreground='green')
status_label_pesquisa.grid(row=3, column=0, columnspan=3, pady=(5, 0))

# Configurar comando do botão de busca
btn_buscar_pesquisa.config(command=lambda: buscar_por_cliente(
    entry_busca_pesquisa, tree_pesquisa, status_label_pesquisa
))

frame_edicao = ttk.LabelFrame(frame_busca_pesquisa, text=" Editar Proposta Selecionada ", padding=10)
frame_edicao.grid(row=4, column=0, columnspan=4, sticky="we", pady=(15,5))

# Campos de edição (inicialmente desativados)
ttk.Label(frame_edicao, text="Cliente:*", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="e", padx=5, pady=5)
entry_cliente_edit = ttk.Entry(frame_edicao, width=40, state='disabled')
entry_cliente_edit.grid(row=0, column=1, sticky="we", padx=5, pady=5)

ttk.Label(frame_edicao, text="Setor:*", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky="e", padx=(15,5), pady=5)
setor_var_edit = tk.StringVar(value="Solar")
setor_menu_edit = ttk.Combobox(frame_edicao, textvariable=setor_var_edit, 
                             values=["Solar", "Indústria", "Comércio", "Residência"], 
                             width=15, state="disabled")
setor_menu_edit.grid(row=0, column=3, sticky="w", padx=5, pady=5)

ttk.Label(frame_edicao, text="Descrição:*", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="ne", padx=5, pady=5)
entry_descricao_edit = tk.Text(frame_edicao, width=60, height=6, font=('Arial', 10), 
                              wrap=tk.WORD, relief="solid", borderwidth=1, state='disabled')
entry_descricao_edit.grid(row=1, column=1, columnspan=3, sticky="we", padx=5, pady=5)

ttk.Label(frame_edicao, text="Responsável:*", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_responsavel_edit = ttk.Entry(frame_edicao, width=40, state='disabled')
entry_responsavel_edit.grid(row=2, column=1, sticky="w", padx=5, pady=5)

ttk.Label(frame_edicao, text="Indicação:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky="e", padx=5, pady=5)
entry_indicacao_edit = ttk.Entry(frame_edicao, width=40, state='disabled')
entry_indicacao_edit.grid(row=3, column=1, sticky="w", padx=5, pady=5)

# Botão Salvar
btn_salvar_edit = ttk.Button(frame_edicao, text="Salvar Alterações", state='disabled')
btn_salvar_edit.grid(row=4, column=0, columnspan=4, pady=(10,0))

# Variável para armazenar a proposta selecionada
proposta_selecionada = None

# Função para habilitar edição quando selecionar uma proposta
def on_proposta_select(event):
    global proposta_selecionada
    
    selected_item = tree_pesquisa.selection()
    if not selected_item:
        return
        
    item = tree_pesquisa.item(selected_item[0])
    proposta_selecionada = item['values'][1]  # Número da proposta
    
    # Habilitar campos
    entry_cliente_edit.config(state='normal')
    setor_menu_edit.config(state='readonly')
    entry_descricao_edit.config(state='normal')
    entry_responsavel_edit.config(state='normal')
    entry_indicacao_edit.config(state='normal')
    btn_salvar_edit.config(state='normal')
    
    # Preencher campos
    entry_cliente_edit.delete(0, tk.END)
    entry_cliente_edit.insert(0, item['values'][2])
    setor_var_edit.set(item['values'][3])
    entry_descricao_edit.delete('1.0', tk.END)
    entry_descricao_edit.insert('1.0', item['values'][4])
    entry_responsavel_edit.delete(0, tk.END)
    entry_responsavel_edit.insert(0, item['values'][5])
    entry_indicacao_edit.delete(0, tk.END)
    entry_indicacao_edit.insert(0, item['values'][6] if item['values'][6] else "")

# Função para salvar as alterações
def salvar_alteracao_pesquisa():
    if not proposta_selecionada:
        messagebox.showerror("Erro", "Nenhuma proposta selecionada")
        return
        
    cliente = entry_cliente_edit.get().strip()
    setor = setor_var_edit.get().strip()
    descricao = entry_descricao_edit.get("1.0", "end-1c").strip()
    responsavel = entry_responsavel_edit.get().strip()
    indicacao = entry_indicacao_edit.get().strip()
    
    if not cliente or not setor or not descricao or not responsavel:
        messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
        return
        
    try:
        conn = conectar_banco()
        if conn is None:
            return
            
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE propostas
            SET 
                cliente = %s,
                setor = %s,
                descricao_servico = %s,
                responsavel_venda = %s,
                indicacao = %s
            WHERE numero_proposta = %s
        """, (cliente, setor, descricao, responsavel, indicacao if indicacao else None, proposta_selecionada))
        
        conn.commit()
        messagebox.showinfo("Sucesso", "Alterações salvas com sucesso!")
        
        # Atualizar a lista
        buscar_por_cliente(entry_busca_pesquisa, tree_pesquisa, status_label_pesquisa)
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    finally:
        if conn:
            conn.close()

# Configurar eventos
tree_pesquisa.bind('<<TreeviewSelect>>', on_proposta_select)
btn_salvar_edit.config(command=salvar_alteracao_pesquisa)

janela.mainloop()