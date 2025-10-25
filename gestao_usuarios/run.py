import tkinter as tk
from tkinter import messagebox
import psycopg2
from criar_usuario import abrir_tela_criar_usuario
from alterar_usuario import abrir_tela_alterar_usuario
from psycopg2 import sql

DB_CONFIG = {
    "dbname": "projeto_final",
    "user": "",
    "password": "",
    "host": "localhost",
    "port": "5432"
}

def conectar_banco():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        messagebox.showerror("Erro de conexão", str(e))
        return None

def buscar_usuarios():
    conn = conectar_banco()
    if conn is None:
        return

    texto_busca = entry_busca.get().strip()
    filtro = filtro_selecionado.get()

    query = "SELECT id, nome, login, nivel_acesso, ativo, email FROM usuarios WHERE TRUE"
    params = []

    if filtro == "nome" and texto_busca:
        query += " AND nome ILIKE %s"
        params.append(f"%{texto_busca}%")
    elif filtro == "login" and texto_busca:
        query += " AND login ILIKE %s"
        params.append(f"%{texto_busca}%")
    elif filtro == "nivel" and texto_busca:
        query += " AND nivel_acesso ILIKE %s"
        params.append(f"%{texto_busca}%")
    elif filtro == "ativo":
        query += " AND ativo = TRUE"

    try:
        cur = conn.cursor()
        cur.execute(query, params)
        resultados = cur.fetchall()
        cur.close()
        conn.close()
        atualizar_grid(resultados)
    except Exception as e:
        messagebox.showerror("Erro ao buscar", str(e))

def inativar(id_usuario):
    conn = conectar_banco()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT ativo, login FROM usuarios WHERE id = %s", (id_usuario,))
        resultado = cur.fetchone()
        ativo_inativo = resultado[0]
        login_usuario = resultado[1]

        novo_valor = not ativo_inativo
        cur.execute("UPDATE usuarios SET ativo = %s WHERE id = %s", (novo_valor, id_usuario))
        
        if novo_valor:
            cur.execute(sql.SQL("ALTER ROLE {} LOGIN").format(sql.Identifier(login_usuario)))
        else:
            cur.execute(sql.SQL("ALTER ROLE {} NOLOGIN").format(sql.Identifier(login_usuario)))
        
        conn.commit()
        cur.close()
        conn.close()

        estado = "ativado" if novo_valor else "inativado"
        messagebox.showinfo("Sucesso", f"Usuário {id_usuario} {estado} com sucesso!")
        buscar_usuarios()
    except Exception as e:
        messagebox.showerror("Erro ao alterar", str(e))

def deletar_usuario(id_usuario):
    conn = conectar_banco()
    if conn is None:
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT login FROM usuarios WHERE id = %s", (id_usuario,))
        resultado = cur.fetchone()
        if not resultado:
            messagebox.showerror("Erro", "Usuário não encontrado!")
            return

        login_usuario = resultado[0]

        confirmar = messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o usuário '{login_usuario}'?")
        if not confirmar:
            return

        # Reatribuir objetos para outro usuário (postgres)
        cur.execute(sql.SQL("SELECT tablename FROM pg_tables WHERE tableowner = %s"), (login_usuario,))
        tabelas = cur.fetchall()
        for tabela in tabelas:
            cur.execute(sql.SQL("ALTER TABLE {} OWNER TO postgres").format(sql.Identifier(tabela[0])))

        # Revogar todas permissões
        cur.execute(sql.SQL("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM {}").format(sql.Identifier(login_usuario)))
        cur.execute(sql.SQL("DROP OWNED BY {} CASCADE").format(sql.Identifier(login_usuario)))

        # Deleta da tabela interna
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
        # Deleta o role no PostgreSQL
        cur.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(login_usuario)))

        conn.commit()
        cur.close()
        conn.close()

        messagebox.showinfo("Sucesso", f"Usuário '{login_usuario}' deletado com sucesso!")
        buscar_usuarios()

    except Exception as e:
        messagebox.showerror("Erro ao deletar", str(e))

def atualizar_grid(dados):
    for widget in frame_grid.winfo_children():
        widget.destroy()

    headers = ["ID", "Nome", "Login", "Nível", "Ativo", "Email"]
    for col, header in enumerate(headers):
        tk.Label(frame_grid, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=25).grid(row=0, column=col)

    for i, row in enumerate(dados, start=1):
        for j, value in enumerate(row):
            tk.Label(frame_grid, text=value, borderwidth=1, relief="solid", width=25).grid(row=i, column=j)

        btn_editar = tk.Button(frame_grid, text="Editar", bg="orange", width=12, command=lambda uid=row[0]: abrir_tela_alterar_usuario(uid, buscar_usuarios))
        btn_inativar = tk.Button(frame_grid, text="Inativar/Ativar", bg="red", fg="white", width=12, command=lambda uid=row[0]: inativar(uid))
        btn_deletar = tk.Button(frame_grid, text="Deletar", bg="darkred", fg="white", width=12, command=lambda uid=row[0]: deletar_usuario(uid))

        btn_editar.grid(row=i, column=len(row))
        btn_inativar.grid(row=i, column=len(row)+1)
        btn_deletar.grid(row=i, column=len(row)+2)

# Interface principal
control_central = tk.Tk()
control_central.title("Controle de Usuários")
control_central.geometry("1700x700")

frame_grid = tk.Frame(control_central)
frame_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

frame_filtros = tk.Frame(control_central)
frame_filtros.pack(fill=tk.X, padx=10, pady=10)

entry_busca = tk.Entry(frame_filtros, width=30)
entry_busca.grid(row=0, column=0, padx=5, sticky="w")

filtro_selecionado = tk.StringVar(value="nome")

tk.Radiobutton(frame_filtros, text="Nome", variable=filtro_selecionado, value="nome").grid(row=0, column=1, padx=5)
tk.Radiobutton(frame_filtros, text="Login", variable=filtro_selecionado, value="login").grid(row=0, column=2, padx=5)
tk.Radiobutton(frame_filtros, text="Nível de Acesso", variable=filtro_selecionado, value="nivel").grid(row=0, column=3, padx=5)
tk.Radiobutton(frame_filtros, text="Somente Ativos", variable=filtro_selecionado, value="ativo").grid(row=0, column=4, padx=5)

btn_buscar = tk.Button(frame_filtros, text="Buscar", command=buscar_usuarios, bg="blue", fg="white")
btn_buscar.grid(row=0, column=5, padx=10)

btn_criar_usuario = tk.Button(frame_filtros, text="Criar novo usuário", command=lambda: abrir_tela_criar_usuario(buscar_usuarios), bg="green", fg="white")
btn_criar_usuario.grid(row=0, column=8, padx=10)

buscar_usuarios()
control_central.mainloop()

