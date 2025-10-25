import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from psycopg2 import sql
import bcrypt

# -------------------- Configuração do Banco --------------------
DB_CONFIG = {
    "dbname": "projeto_final",
    "user": "",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

# -------------------- Conexão --------------------
def conectar_banco():
    """Abre uma conexão com o PostgreSQL usando as configurações definidas."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        messagebox.showerror("Erro de conexão", f"Não foi possível conectar ao banco:\n{e}")
        return None

# -------------------- Tela Alterar Usuário --------------------
def abrir_tela_alterar_usuario(id_usuario, callback_atualizar=None):
    """
    Abre a tela para alterar um usuário já existente.
    Recebe o ID do usuário e opcionalmente uma função callback para atualizar a lista de usuários na tela principal.
    """

    # ---- Busca os dados do usuário no banco ----
    conn = conectar_banco()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, login, senha_hash, nivel_acesso, email, ativo
            FROM usuarios WHERE id = %s
        """, (id_usuario,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao buscar usuário:\n{e}")
        return

    # Se não encontrou usuário, mostra erro
    if not usuario:
        messagebox.showerror("Erro", "Usuário não encontrado!")
        return

    # Desempacota os dados do banco em variáveis
    id_usuario, nome_db, login_db, senha_hash_db, nivel_db, email_db, ativo_db = usuario

    # -------------------- Interface Tkinter --------------------
    tela = tk.Toplevel()
    tela.title(f"Alterar Usuário - {login_db}")
    tela.geometry("1000x700")

    # Cria o notebook (abas)
    notebook = ttk.Notebook(tela)
    notebook.pack(fill='both', expand=True)

    aba_cadastro = tk.Frame(notebook)          # Aba com os dados cadastrais
    aba_permissoes_tabelas = tk.Frame(notebook)  # Aba para gerenciar permissões

    notebook.add(aba_cadastro, text="Alterar Usuário")
    notebook.add(aba_permissoes_tabelas, text="Permissões")

    # -------------------- Aba Cadastro --------------------
    # Campos de texto para edição das informações básicas do usuário
    tk.Label(aba_cadastro, text="Nome:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_nome = tk.Entry(aba_cadastro, width=40)
    entry_nome.insert(0, nome_db)  # Preenche com valor atual
    entry_nome.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Login:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_login = tk.Entry(aba_cadastro, width=40)
    entry_login.insert(0, login_db)
    entry_login.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Senha (deixe em branco para não alterar):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_senha = tk.Entry(aba_cadastro, show="*", width=40)
    entry_senha.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="E-mail:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    entry_email = tk.Entry(aba_cadastro, width=40)
    if email_db:
        entry_email.insert(0, email_db)
    entry_email.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(aba_cadastro, text="Nível de Acesso:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
    combo_nivel = ttk.Combobox(aba_cadastro, values=["usuario", "admin"], state="readonly", width=37, justify="center")
    combo_nivel.set(nivel_db)
    combo_nivel.grid(row=4, column=1, padx=10, pady=5)

    # Checkbox para marcar se o usuário está ativo
    ativo_var = tk.BooleanVar(value=ativo_db)
    tk.Checkbutton(aba_cadastro, text="Ativo", variable=ativo_var).grid(row=5, column=1, sticky="w", padx=10, pady=5)

    # -------------------- Aba Permissões --------------------
    def criar_checkbuttons(base_row, col, tabela_nome):
        """
        Cria os checkboxes de permissões (SELECT, INSERT, UPDATE, DELETE) para cada tabela.
        Retorna as variáveis associadas a cada checkbox.
        """
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

    # Dicionário que mapeia cada tabela para suas variáveis de permissões
    permissoes_vars = {
        "receitas": criar_checkbuttons(5, 0, "receitas"),
        "propostas": criar_checkbuttons(10, 0, "propostas"),
        "projetos": criar_checkbuttons(5, 2, "projetos"),
        "produto": criar_checkbuttons(10, 2, "produtos"),
        "orcamentos": criar_checkbuttons(5, 4, "orcamentos"),
        "movimentacao": criar_checkbuttons(10, 4, "movimentacao"),
        "lote": criar_checkbuttons(5, 6, "lote"),
        "lista_materiais": criar_checkbuttons(10, 6, "materiais"),
        "despesas": criar_checkbuttons(5, 8, "despesas"),
        "clientes": criar_checkbuttons(10, 8, "clientes"),
    }

    # -------------------- Carregar permissões existentes --------------------
    def carregar_permissoes():
        """Consulta no banco as permissões atuais do usuário e marca os checkboxes de acordo."""
        conn = conectar_banco()
        if conn is None:
            return
        cur = conn.cursor()
        try:
            for tabela, (s_var, i_var, u_var, d_var) in permissoes_vars.items():
                # Pergunta ao PostgreSQL quais privilégios o usuário tem nesta tabela
                cur.execute(sql.SQL(
                    "SELECT privilege_type FROM information_schema.role_table_grants WHERE grantee = %s AND table_name = %s"
                ), (login_db, tabela))

                perms = [r[0] for r in cur.fetchall()]  # Lista com permissões, ex: ["SELECT", "UPDATE"]

                # Atualiza checkboxes
                s_var.set("SELECT" in perms)
                i_var.set("INSERT" in perms)
                u_var.set("UPDATE" in perms)
                d_var.set("DELETE" in perms)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar permissões:\n{e}")
        finally:
            cur.close()
            conn.close()

    carregar_permissoes()  # Chama logo ao abrir a tela

    # -------------------- Função salvar alterações --------------------
    def salvar_alteracoes():
        """Salva as alterações feitas no cadastro do usuário (nome, login, senha, nível, ativo)."""
        nome = entry_nome.get()
        login_novo = entry_login.get()
        senha = entry_senha.get()
        email = entry_email.get()
        nivel = combo_nivel.get()
        ativo = ativo_var.get()

        # Validação simples
        if not nome or not login_novo:
            messagebox.showwarning("Aviso", "Nome e Login são obrigatórios!")
            return

        conn = conectar_banco()
        if conn is None:
            return
        cur = conn.cursor()

        try:
            # Se o login foi alterado, renomeia a ROLE no PostgreSQL
            if login_db != login_novo:
                cur.execute(sql.SQL("ALTER ROLE {} RENAME TO {}")
                            .format(sql.Identifier(login_db), sql.Identifier(login_novo)))

            # Atualiza a senha se foi informada
            if senha:
                cur.execute(sql.SQL("ALTER ROLE {} WITH PASSWORD %s")
                            .format(sql.Identifier(login_novo)), [senha])
                senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            else:
                senha_hash = senha_hash_db  # mantém a senha antiga

            # Ajusta privilégios de superuser conforme nível de acesso
            if nivel == "admin":
                cur.execute(sql.SQL("ALTER ROLE {} WITH SUPERUSER CREATEDB CREATEROLE")
                            .format(sql.Identifier(login_novo)))
            else:
                cur.execute(sql.SQL("ALTER ROLE {} WITH NOSUPERUSER NOCREATEDB NOCREATEROLE")
                            .format(sql.Identifier(login_novo)))

            # Atualiza os dados na tabela usuarios
            cur.execute("""
                UPDATE usuarios
                   SET nome=%s, login=%s, senha_hash=%s, nivel_acesso=%s, email=%s, ativo=%s
                 WHERE id=%s
            """, (nome, login_novo, senha_hash, nivel, email if email else None, ativo, id_usuario))

            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            tela.destroy()  # Fecha a tela de edição

            # Chama a função de atualizar grid, se veio do controle central
            if callback_atualizar:
                callback_atualizar()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar usuário:\n{e}")
        finally:
            cur.close()
            conn.close()

    # Botão salvar na aba de cadastro
    btn_salvar = tk.Button(aba_cadastro, text="Salvar Alterações", command=salvar_alteracoes, bg="green", fg="white", width=20)
    btn_salvar.grid(row=15, column=0, columnspan=2, pady=20)

    # -------------------- Função aplicar permissões --------------------
    def aplicar_permissoes():
        """Aplica as permissões marcadas/desmarcadas nos checkboxes para o usuário."""
        login_atual = entry_login.get()
        conn = conectar_banco()
        if conn is None:
            return
        cur = conn.cursor()
        try:
            for tabela, (s_var, i_var, u_var, d_var) in permissoes_vars.items():
                for acao, var in zip(["SELECT", "INSERT", "UPDATE", "DELETE"], [s_var, i_var, u_var, d_var]):
                    if var.get():
                        # Concede permissão
                        cur.execute(sql.SQL("GRANT {} ON TABLE {} TO {}")
                                    .format(sql.SQL(acao), sql.Identifier(tabela), sql.Identifier(login_atual)))
                    else:
                        # Revoga permissão
                        cur.execute(sql.SQL("REVOKE {} ON TABLE {} FROM {}")
                                    .format(sql.SQL(acao), sql.Identifier(tabela), sql.Identifier(login_atual)))
            conn.commit()
            messagebox.showinfo("Sucesso", f"Permissões aplicadas para {login_atual}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar permissões:\n{e}")
        finally:
            cur.close()
            conn.close()

    # Botão aplicar permissões na aba
    btn_aplicar = tk.Button(aba_permissoes_tabelas, text="Aplicar Permissões", command=aplicar_permissoes, bg="blue", fg="white", width=25)
    btn_aplicar.grid(row=20, column=0, columnspan=10, pady=30)

    tela.grab_set()  # Mantém foco nesta janela até ser fechada

