import tkinter as tk
from tkinter import ttk, messagebox
from app.services.cliente_service import ClienteService
from app.services.auditoria_service import AuditoriaService

class ClienteViewer:
    def __init__(self, root, usuario_logado):
        self.usuario_logado = usuario_logado
        self.grupo = usuario_logado.grupo

        if self.grupo not in ["financeiro", "ti"]:
            messagebox.showerror("Acesso Negado", "❌ Você não tem permissão para acessar este módulo.")
            return

        self.root = tk.Toplevel(root)
        self.root.title("💼 Gestão de Clientes")
        self.root.geometry("700x400")

        self.service = ClienteService()
        self.auditoria = AuditoriaService()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_clientes()

    def criar_widgets(self):
        ttk.Label(self.frame, text="💼 Cadastro de Clientes", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("ID", "CPF/CNPJ", "Nome")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=10)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col != "ID" else 50)
        self.tree.pack(fill="both", expand=True, pady=10)

        botoes = ttk.Frame(self.frame)
        botoes.pack(pady=10)

        ttk.Button(botoes, text="➕ Novo Cliente", command=self.cadastrar_cliente).pack(side="left", padx=5)
        ttk.Button(botoes, text="✏️ Editar", command=self.editar_cliente).pack(side="left", padx=5)
        ttk.Button(botoes, text="❌ Excluir", command=self.excluir_cliente).pack(side="left", padx=5)

    def carregar_clientes(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        clientes = self.service.listar_clientes()
        for c in clientes:
            self.tree.insert("", "end", values=(c.id_cliente, c.cpf_cnpj, c.nome))

    def cadastrar_cliente(self):
        self.abrir_formulario()

    def editar_cliente(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Selecione", "Selecione um cliente para editar.")
            return
        cliente_data = self.tree.item(selecionado[0])['values']
        self.abrir_formulario(cliente_data)

    def excluir_cliente(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir.")
            return

        valores = self.tree.item(item)["values"]
        id_cliente = valores[0]

        confirm = messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o cliente ID {id_cliente}?")
        if not confirm:
            return

        try:
            resultado = self.service.excluir_cliente(id_cliente)
            if resultado:
                messagebox.showinfo("Sucesso", "🗑️ Cliente excluído com sucesso.")
                self.carregar_clientes()
            else:
                messagebox.showwarning("Aviso", "Cliente não encontrado.")
        except ValueError as ve:
            messagebox.showerror("Erro", str(ve))
        except Exception as e:
            messagebox.showerror("Erro inesperado", f"Ocorreu um erro: {e}")

    def abrir_formulario(self, cliente_data=None):
        win = tk.Toplevel(self.root)
        win.title("Editar Cliente" if cliente_data else "Novo Cliente")
        win.geometry("350x200")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text="CPF/CNPJ:").pack()
        cpf_entry = ttk.Entry(win, width=40)
        cpf_entry.pack(pady=5)

        ttk.Label(win, text="Nome:").pack()
        nome_entry = ttk.Entry(win, width=40)
        nome_entry.pack(pady=5)

        if cliente_data:
            cpf_entry.insert(0, cliente_data[1])
            nome_entry.insert(0, cliente_data[2])

        def salvar():
            cpf = cpf_entry.get().strip()
            nome = nome_entry.get().strip()

            if not cpf or not nome:
                messagebox.showwarning("Campos obrigatórios", "Informe CPF/CNPJ e Nome.")
                return

            try:
                if cliente_data:
                    self.service.atualizar_cliente(cliente_data[0], cpf, nome)
                    self.auditoria.registrar_acao(
                        self.usuario_logado.login, "UPDATE", "clientes", f"Cliente atualizado: {nome}"
                    )
                else:
                    self.service.criar_cliente(cpf, nome)
                    self.auditoria.registrar_acao(
                        self.usuario_logado.login, "INSERT", "clientes", f"Cliente cadastrado: {nome}"
                    )
                self.carregar_clientes()
                win.destroy()
                messagebox.showinfo("Sucesso", "Cliente salvo com sucesso.")
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(win, text="Salvar", command=salvar).pack(pady=10)
