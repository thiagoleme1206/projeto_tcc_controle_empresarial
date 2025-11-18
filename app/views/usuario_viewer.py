import tkinter as tk
from tkinter import ttk, messagebox
from app.services.usuario_service import UsuarioService
from app.services.auditoria_service import AuditoriaService

class UsuarioViewer:
    def __init__(self, root, usuario_logado):
        self.root = tk.Toplevel(root)
        self.root.title("Controle de Usuários")
        self.root.geometry("900x600")
        self.usuario_logado = usuario_logado

        if usuario_logado.grupo != "ti":
            messagebox.showerror("Acesso Negado", "Este módulo é restrito ao grupo TI.")
            self.root.destroy()
            return

        self.service = UsuarioService()
        self.auditoria = AuditoriaService()

        self.frame_topo = ttk.Frame(self.root)
        self.frame_topo.pack(fill="x", pady=10)

        self.frame_grid = ttk.Frame(self.root)
        self.frame_grid.pack(fill="both", expand=True)

        self.usuarios = []
        self.filtro_tipo = tk.StringVar(value="nome")

        self.criar_menu_busca()
        self.carregar_usuarios()

    def criar_menu_busca(self):
        self.entrada_filtro = ttk.Entry(self.frame_topo, width=40)
        self.entrada_filtro.pack(side="left", padx=5)

        filtros = [("Nome", "nome"), ("Login", "login"), ("Grupo", "grupo"), ("Somente Ativos", "ativos")]
        for label, value in filtros:
            ttk.Radiobutton(self.frame_topo, text=label, variable=self.filtro_tipo, value=value).pack(side="left", padx=2)

        ttk.Button(self.frame_topo, text="Buscar", command=self.buscar).pack(side="left", padx=5)
        ttk.Button(self.frame_topo, text="Criar novo usuário", command=self.criar_usuario).pack(side="left", padx=10)

    def carregar_usuarios(self, usuarios=None):
        for widget in self.frame_grid.winfo_children():
            widget.destroy()

        if usuarios is None:
            usuarios = self.service.consultar_usuarios()

        self.usuarios = usuarios

        headers = ["ID", "Nome", "Login", "Grupo", "Ativo", "", "", ""]
        for col, text in enumerate(headers):
            ttk.Label(self.frame_grid, text=text, font=("Helvetica", 10, "bold")).grid(row=0, column=col, padx=5, pady=5)

        for row, u in enumerate(usuarios, start=1):
            id_, nome, login, _, grupo, ativo = u
            dados = [id_, nome, login, grupo, "Sim" if ativo else "Não"]

            for col, val in enumerate(dados):
                entry = ttk.Entry(self.frame_grid, width=18)
                entry.insert(0, val)
                entry.config(state="readonly")
                entry.grid(row=row, column=col, padx=2, pady=2)

            ttk.Button(self.frame_grid, text="Editar", command=lambda u=u: self.alterar_usuario(u)).grid(row=row, column=5)
            ttk.Button(self.frame_grid, text="Inativar/Ativar", command=lambda u=u: self.toggle_usuario(u)).grid(row=row, column=6)
            ttk.Button(self.frame_grid, text="Excluir", command=lambda u=u: self.confirmar_exclusao_usuario(u)).grid(row=row, column=7)

    def buscar(self):
        filtro = self.entrada_filtro.get()
        tipo = self.filtro_tipo.get()
        try:
            if tipo == "nome":
                usuarios = self.service.consultar_usuarios(nome=filtro)
            elif tipo == "login":
                usuarios = self.service.consultar_usuarios(login=filtro)
            elif tipo == "grupo":
                usuarios = self.service.consultar_usuarios(grupo=filtro)
            elif tipo == "ativos":
                usuarios = self.service.consultar_usuarios(ativo=True)
            else:
                usuarios = self.service.consultar_usuarios()
            self.carregar_usuarios(usuarios)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar: {e}")

    def criar_usuario(self):
        win = tk.Toplevel(self.root)
        win.title("Criar Novo Usuário")
        win.geometry("400x350")  # janela maior

        campos = ["Nome", "Login", "Senha", "Confirmar Senha"]
        entradas = []
        for campo in campos:
            ttk.Label(win, text=campo).pack()
            ent = ttk.Entry(win, show="*" if "senha" in campo.lower() else None)
            ent.pack()
            entradas.append(ent)

        ttk.Label(win, text="Grupo").pack()
        combo_grupo = ttk.Combobox(win, values=["estoquista", "vendedor", "engenheiro", "financeiro", "gerencia", "ti"])
        combo_grupo.pack()

        def salvar():
            nome, login, senha, confirmar = [e.get() for e in entradas]
            grupo = combo_grupo.get()
            if senha != confirmar:
                messagebox.showerror("Erro", "Senhas não conferem.")
                return
            try:
                self.service.criar_usuario(nome, login, senha, grupo)
                self.auditoria.registrar_acao(self.usuario_logado.login, "INSERT", "usuarios",
                                              f"Usuário '{login}' criado no grupo '{grupo}'.")
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso.")
                win.destroy()
                self.carregar_usuarios()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(win, text="Salvar", command=salvar).pack(pady=10)

    def alterar_usuario(self, usuario):
        win = tk.Toplevel(self.root)
        win.title(f"Editar {usuario[2]}")
        win.geometry("400x350")  # nova dimensão da janela

        ttk.Label(win, text=f"Editar Usuário: {usuario[2]}", font=("Helvetica", 12)).pack(pady=10)

        # Nome
        ttk.Label(win, text="Nome").pack()
        entry_nome = ttk.Entry(win)
        entry_nome.insert(0, usuario[1])
        entry_nome.pack()

        # Grupo - dropdown com os grupos válidos
        ttk.Label(win, text="Grupo").pack()
        grupos = ["estoquista", "vendedor", "engenheiro", "financeiro", "gerencia", "ti"]
        combo_grupo = ttk.Combobox(win, values=grupos)
        combo_grupo.set(usuario[4])  # grupo atual como default
        combo_grupo.pack()

        # Nova senha
        ttk.Label(win, text="Nova Senha").pack()
        entry_senha = ttk.Entry(win, show="*")
        entry_senha.pack()

        # Confirmar nova senha
        ttk.Label(win, text="Confirmar Senha").pack()
        entry_confirmar = ttk.Entry(win, show="*")
        entry_confirmar.pack()

        def salvar():
            novo_nome = entry_nome.get().strip()
            novo_grupo = combo_grupo.get().strip()
            senha = entry_senha.get().strip()
            confirmar = entry_confirmar.get().strip()

            if senha and senha != confirmar:
                messagebox.showerror("Erro", "Senhas não conferem.")
                return

            try:
                self.service.alterar_usuario(
                    login=usuario[2],
                    nome=novo_nome if novo_nome != usuario[1] else None,
                    grupo=novo_grupo if novo_grupo != usuario[4] else None,
                    senha=senha if senha else None
                )
                self.auditoria.registrar_acao(self.usuario_logado.login, "UPDATE", "usuarios",
                                              f"Usuário '{usuario[2]}' alterado.")
                messagebox.showinfo("Sucesso", "Usuário atualizado.")
                win.destroy()
                self.carregar_usuarios()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(win, text="Salvar", command=salvar).pack(pady=15)

    def toggle_usuario(self, usuario):
        try:
            ativo = usuario[5]
            novo_status = not ativo
            self.service.ativar_inativar_usuario(usuario[2], novo_status)
            status_txt = "ativado" if novo_status else "inativado"
            self.auditoria.registrar_acao(self.usuario_logado.login, "UPDATE", "usuarios",
                                          f"Usuário '{usuario[2]}' foi {status_txt}.")
            self.carregar_usuarios()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar status: {e}")

    def confirmar_exclusao_usuario(self, usuario):
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir '{usuario[2]}'?"):
            try:
                self.service.excluir_usuario(usuario[2])
                self.auditoria.registrar_acao(self.usuario_logado.login, "DELETE", "usuarios",
                                              f"Usuário '{usuario[2]}' foi marcado como inativo.")
                messagebox.showinfo("Sucesso", "Usuário excluído.")
                self.carregar_usuarios()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {e}")
