import tkinter as tk
from tkinter import ttk, messagebox
from app.services.proposta_service import PropostaService

class PropostaViewer:
    def __init__(self, root, usuario_logado):
        self.usuario_logado = usuario_logado
        self.acesso_total = usuario_logado.grupo in ["vendedor", "ti"]

        self.root = tk.Toplevel(root)
        self.root.title("📄 Gestão de Propostas")
        self.root.geometry("1500x450")

        self.service = PropostaService()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.create_widgets()
        self.carregar_propostas()

    def create_widgets(self):
        ttk.Label(self.frame, text="📄 Propostas Cadastradas", font=("Helvetica", 14)).pack(pady=5)

        colunas = ("ID", "Título", "Descrição", "Valor", "Status")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        # Botões
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="🔄 Atualizar Lista", command=self.carregar_propostas).grid(row=0, column=0, padx=5)

        if self.acesso_total:
            ttk.Button(btn_frame, text="➕ Nova Proposta", command=self.abrir_criar).grid(row=0, column=1, padx=5)
            ttk.Button(btn_frame, text="✏️ Editar", command=self.abrir_editar).grid(row=0, column=2, padx=5)
            ttk.Button(btn_frame, text="🗑️ Excluir", command=self.excluir).grid(row=0, column=3, padx=5)

    def carregar_propostas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        propostas = self.service.listar_propostas()
        for p in propostas:
            self.tree.insert("", "end", values=(p.id, p.titulo, p.descricao, f"R${p.valor:.2f}", p.status))

    def abrir_criar(self):
        self.abrir_formulario_proposta("Criar Nova Proposta")

    def abrir_editar(self):
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma proposta.")
            return

        dados = self.tree.item(selecionado)["values"]
        self.abrir_formulario_proposta("Editar Proposta", proposta_id=dados[0])

    def abrir_formulario_proposta(self, titulo, proposta_id=None):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("400x400")

        # Campos
        ttk.Label(win, text="Título:").pack()
        titulo_entry = ttk.Entry(win)
        titulo_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(win, text="Descrição:").pack()
        descricao_entry = tk.Text(win, height=4)
        descricao_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(win, text="Valor (R$):").pack()
        valor_entry = ttk.Entry(win)
        valor_entry.pack(fill="x", padx=10, pady=5)

        ttk.Label(win, text="Status:").pack()
        status_combobox = ttk.Combobox(win, values=["pendente", "aprovada", "rejeitada"], state="readonly")
        status_combobox.pack(fill="x", padx=10, pady=5)
        status_combobox.set("pendente")

        # Se for edição, preencher os campos
        if proposta_id:
            proposta = self.service.repo.buscar_por_id(proposta_id)
            if proposta:
                titulo_entry.insert(0, proposta.titulo)
                descricao_entry.insert("1.0", proposta.descricao)
                valor_entry.insert(0, str(proposta.valor))
                status_combobox.set(proposta.status)

        def salvar():
            titulo_valor = titulo_entry.get().strip()
            descricao_valor = descricao_entry.get("1.0", "end").strip()
            status_valor = status_combobox.get()
            try:
                valor_valor = float(valor_entry.get().strip())
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido.")
                return

            if not titulo_valor or not descricao_valor:
                messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
                return

            try:
                if proposta_id:
                    self.service.atualizar_proposta(proposta_id, titulo_valor, descricao_valor, valor_valor, status_valor)
                    messagebox.showinfo("Sucesso", "Proposta atualizada.")
                else:
                    self.service.cadastrar_proposta(titulo_valor, descricao_valor, valor_valor, status_valor)
                    messagebox.showinfo("Sucesso", "Proposta criada.")
                win.destroy()
                self.carregar_propostas()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(win, text="Salvar", command=salvar).pack(pady=10)

    def excluir(self):
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma proposta.")
            return

        dados = self.tree.item(selecionado)["values"]
        proposta_id = dados[0]

        if messagebox.askyesno("Confirmar", f"Deseja excluir a proposta ID {proposta_id}?"):
            try:
                self.service.deletar_proposta(proposta_id)
                messagebox.showinfo("Sucesso", "Proposta excluída.")
                self.carregar_propostas()
            except Exception as e:
                messagebox.showerror("Erro", str(e))
