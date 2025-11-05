import tkinter as tk
from tkinter import messagebox, ttk, Frame
import psycopg2
from psycopg2 import sql
import bcrypt
import os

# -------------------- Configuração do Banco --------------------
# Configuração do banco de dados
DB_CONFIG = {
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT")
}

# -------------------- Conexão --------------------
def conectar_banco():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        messagebox.showerror("Erro de conexão", f"Não foi possível conectar ao banco:\n{e}")
        return None

# -------------------- Criação da tabela usuarios --------------------
def criar_tabela():
    conn = conectar_banco()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                login VARCHAR(50) UNIQUE NOT NULL,
                senha_hash VARCHAR(255) NOT NULL,
                nivel_acesso VARCHAR(20) NOT NULL DEFAULT 'usuario',
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                email VARCHAR(100),
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_login TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar tabela: {e}")

# -------------------- Função para abrir tela de cadastro --------------------
def abrir_tela_criar_usuario(callback_atualizar=None):
    def criar_usuario():
        nome = entry_nome.get()
        login = entry_login.get()
        senha = entry_senha.get()
        senha_nova = entry_senha_nova.get()
        email = entry_email.get()
        nivel_acesso = combo_nivel.get()

        if not nome or not login or not senha:
            messagebox.showwarning("Aviso", "Nome, Login e Senha são obrigatórios!")
            return

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        if senha != senha_nova:
            messagebox.showwarning("Aviso", "Senha e confirmar senha estão diferentes!")
            return

        conn = conectar_banco()
        if conn is None:
            return

        try:
            cur = conn.cursor()

            # Criação da role no PostgreSQL
            try:
                cur.execute(sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(
                    sql.Identifier(login)), [senha])

                if nivel_acesso == "admin":
                    cur.execute(sql.SQL("ALTER ROLE {} WITH SUPERUSER CREATEDB CREATEROLE").format(
                        sql.Identifier(login)))
                else:
                    cur.execute(sql.SQL("ALTER ROLE {} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE").format(
                        sql.Identifier(login)))
            except Exception as e:
                messagebox.showwarning("Aviso", f"O role '{login}' pode já existir no banco.\nDetalhes: {e}")

            # Insert na tabela usuarios
            query = sql.SQL("""
                INSERT INTO usuarios (nome, login, senha_hash, nivel_acesso, email)
                VALUES (%s, %s, %s, %s, %s)
            """)
            cur.execute(query, (nome, login, senha_hash, nivel_acesso, email if email else None))

            # 🔑 Concede permissão de SELECT na tabela usuarios ao novo usuário
            cur.execute(
                sql.SQL("GRANT SELECT ON TABLE usuarios TO {};")
                .format(sql.Identifier(login))
            )

            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("Sucesso", f"Usuário {login} criado no banco e na tabela com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário:\n{e}")

        if callback_atualizar:
            callback_atualizar()

    def aplicar_permissoes():
        login = entry_login.get()
        if not login:
            messagebox.showwarning("Aviso", "Informe o login do usuário antes de aplicar permissões!")
            return

        permissoes = {
            "receitas": {
                "SELECT": select_receitas_var.get(),
                "INSERT": insert_receitas_var.get(),
                "UPDATE": update_receitas_var.get(),
                "DELETE": delete_receitas_var.get()
            },
            "propostas": {
                "SELECT": select_propostas_var.get(),
                "INSERT": insert_propostas_var.get(),
                "UPDATE": update_propostas_var.get(),
                "DELETE": delete_propostas_var.get()
            },
            "projetos": {
                "SELECT": select_projetos_var.get(),
                "INSERT": insert_projetos_var.get(),
                "UPDATE": update_projetos_var.get(),
                "DELETE": delete_projetos_var.get()
            },
            "produto": {
                "SELECT": select_produto_var.get(),
                "INSERT": insert_produto_var.get(),
                "UPDATE": update_produto_var.get(),
                "DELETE": delete_produto_var.get()
            },
            "orcamentos": {
                "SELECT": select_orcamentos_var.get(),
                "INSERT": insert_orcamentos_var.get(),
                "UPDATE": update_orcamentos_var.get(),
                "DELETE": delete_orcamentos_var.get()
            },
            "movimentacao": {
                "SELECT": select_movimentacao_var.get(),
                "INSERT": insert_movimentacao_var.get(),
                "UPDATE": update_movimentacao_var.get(),
                "DELETE": delete_movimentacao_var.get()
            },
            "lote": {
                "SELECT": select_lote_var.get(),
                "INSERT": insert_lote_var.get(),
                "UPDATE": update_lote_var.get(),
                "DELETE": delete_lote_var.get()
            },
            "lista_materiais": {
                "SELECT": select_lista_materiais_var.get(),
                "INSERT": insert_lista_materiais_var.get(),
                "UPDATE": update_lista_materiais_var.get(),
                "DELETE": delete_lista_materiais_var.get()
            },
            "despesas": {
                "SELECT": select_depesas_var.get(),
                "INSERT": insert_depesas_var.get(),
                "UPDATE": update_depesas_var.get(),
                "DELETE": delete_depesas_var.get()
            },
            "clientes": {
                "SELECT": select_clientes_var.get(),
                "INSERT": insert_clientes_var.get(),
                "UPDATE": update_clientes_var.get(),
                "DELETE": delete_clientes_var.get()
            }
        }

        conn = conectar_banco()
        if conn is None:
            return
        cur = conn.cursor()

        try:
            for tabela, acoes in permissoes.items():
                for acao, permitido in acoes.items():
                    if permitido:
                        cur.execute(
                            sql.SQL("GRANT {} ON TABLE {} TO {};")
                            .format(sql.SQL(acao), sql.Identifier(tabela), sql.Identifier(login))
                        )
                    else:
                        cur.execute(
                            sql.SQL("REVOKE {} ON TABLE {} FROM {};")
                            .format(sql.SQL(acao), sql.Identifier(tabela), sql.Identifier(login))
                        )
            conn.commit()
            messagebox.showinfo("Sucesso", f"Permissões aplicadas para {login}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar permissões:\n{e}")
        finally:
            cur.close()
            conn.close()

    # -------------------- Interface Tkinter --------------------
    tela_login = tk.Toplevel()  # toplevel usado para abrir janela filha
    tela_login.title("Cadastro de Usuário")
    tela_login.geometry("1000x700")

    # Função chamada ao fechar a janela
    def on_close():
        if callback_atualizar:
            callback_atualizar()
        tela_login.destroy()

    # Vincula o evento de fechar a janela (X vermelho)
    tela_login.protocol("WM_DELETE_WINDOW", on_close)

    # Notebook
    notebook = ttk.Notebook(tela_login)
    notebook.pack(fill='both', expand=True)

    aba_cadastro = tk.Frame(notebook)
    aba_permissoes_tabelas = tk.Frame(notebook)

    notebook.add(aba_cadastro, text="Cadastro de Usuário")
    notebook.add(aba_permissoes_tabelas, text="Gerenciamento de permissões")

    # -------------------- Aba Cadastro --------------------
    tk.Label(aba_cadastro, text="Nome:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_nome = tk.Entry(aba_cadastro, width=40)
    entry_nome.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Login:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_login = tk.Entry(aba_cadastro, width=40)
    entry_login.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Senha:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_senha = tk.Entry(aba_cadastro, show="*", width=40)
    entry_senha.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Confirmar Senha:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    entry_senha_nova = tk.Entry(aba_cadastro, show="*", width=40)
    entry_senha_nova.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="E-mail (opcional):").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    entry_email = tk.Entry(aba_cadastro, width=40)
    entry_email.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Nível de Acesso:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
    combo_nivel = ttk.Combobox(aba_cadastro, values=["usuario", "admin"], state="readonly", width=37, justify="center")
    combo_nivel.set("usuario")
    combo_nivel.grid(row=5, column=1, padx=10, pady=5)

    btn_criar = tk.Button(aba_cadastro, text="Criar Usuário", command=criar_usuario, bg="green", fg="white", width=20)
    btn_criar.grid(row=15, column=0, columnspan=2, pady=20)

    # -------------------- Aba Permissões --------------------
    def criar_checkbuttons(base_row, col, tabela_nome):
        tk.Label(aba_permissoes_tabelas, text=f"Tabela {tabela_nome}").grid(
            row=base_row, column=col, columnspan=2, pady=(15, 5), padx=10, sticky="w"
        )

        select_var = tk.BooleanVar()
        insert_var = tk.BooleanVar()
        update_var = tk.BooleanVar()
        delete_var = tk.BooleanVar()

        tk.Checkbutton(aba_permissoes_tabelas, text="Select", variable=select_var).grid(row=base_row+1, column=col, padx=15, pady=5, sticky="w")
        tk.Checkbutton(aba_permissoes_tabelas, text="Insert", variable=insert_var).grid(row=base_row+2, column=col, padx=15, pady=5, sticky="w")
        tk.Checkbutton(aba_permissoes_tabelas, text="Update", variable=update_var).grid(row=base_row+3, column=col, padx=15, pady=5, sticky="w")
        tk.Checkbutton(aba_permissoes_tabelas, text="Delete", variable=delete_var).grid(row=base_row+4, column=col, padx=15, pady=5, sticky="w")

        return select_var, insert_var, update_var, delete_var

    # Criando checkboxes para cada tabela
    select_receitas_var, insert_receitas_var, update_receitas_var, delete_receitas_var = criar_checkbuttons(5, 0, "receitas")
    select_propostas_var, insert_propostas_var, update_propostas_var, delete_propostas_var = criar_checkbuttons(10, 0, "propostas")
    select_projetos_var, insert_projetos_var, update_projetos_var, delete_projetos_var = criar_checkbuttons(5, 2, "projetos")
    select_produto_var, insert_produto_var, update_produto_var, delete_produto_var = criar_checkbuttons(10, 2, "produtos")
    select_orcamentos_var, insert_orcamentos_var, update_orcamentos_var, delete_orcamentos_var = criar_checkbuttons(5, 4, "orcamento")
    select_movimentacao_var, insert_movimentacao_var, update_movimentacao_var, delete_movimentacao_var = criar_checkbuttons(10, 4, "movimentacao")
    select_lote_var, insert_lote_var, update_lote_var, delete_lote_var = criar_checkbuttons(5, 6, "lote")
    select_lista_materiais_var, insert_lista_materiais_var, update_lista_materiais_var, delete_lista_materiais_var = criar_checkbuttons(10, 6, "materiais")
    select_depesas_var, insert_depesas_var, update_depesas_var, delete_depesas_var = criar_checkbuttons(5, 8, "despesas")
    select_clientes_var, insert_clientes_var, update_clientes_var, delete_clientes_var = criar_checkbuttons(10, 8, "clientes")

    # Botão aplicar permissões
    btn_aplicar = tk.Button(aba_permissoes_tabelas, text="Aplicar Permissões", command=aplicar_permissoes, bg="blue", fg="white", width=25)
    btn_aplicar.grid(row=20, column=0, columnspan=10, pady=30)

    # Inicialização
    criar_tabela()
    tela_login.grab_set()  # Trava foco nesta janela até fechar
