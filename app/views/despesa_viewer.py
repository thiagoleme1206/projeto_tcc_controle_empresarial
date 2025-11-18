import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.services.despesa_service import DespesaService
from app.models.despesa_model import Despesa

class DespesaViewer:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.root.title("💸 Gestão de Despesas")
        self.root.geometry("1100x500")
        self.usuario = usuario_logado
        self.service = DespesaService()

        self.acesso_total = self.usuario.grupo in ["financeiro", "ti"]
        self.leitura_apenas = self.usuario.grupo == "gerencia"

        if not (self.acesso_total or self.leitura_apenas):
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            self.root.destroy()
            return

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_despesas()

    def criar_widgets(self):
        ttk.Label(self.frame, text="💸 Despesas Cadastradas", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("ID", "OS", "Data", "Total")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, pady=10)

        botoes = ttk.Frame(self.frame)
        botoes.pack(fill="x", pady=5)

        ttk.Button(botoes, text="🔄 Atualizar", command=self.carregar_despesas).pack(side="left", padx=5)

        if self.acesso_total:
            ttk.Button(botoes, text="➕ Nova Despesa", command=self.cadastrar_despesa).pack(side="left", padx=5)
            ttk.Button(botoes, text="✏️ Editar Despesa", command=self.editar_despesa).pack(side="left", padx=5)
            self.entry_os_busca = ttk.Entry(botoes, width=15)
            self.entry_os_busca.pack(side="left", padx=5)
            ttk.Button(botoes, text="🔍 Buscar por OS", command=self.buscar_por_os).pack(side="left", padx=5)
            ttk.Button(botoes, text="🗑️ Excluir Despesa", command=self.excluir_despesa).pack(side="left", padx=5)

    def carregar_despesas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        despesas = self.service.listar_despesas()
        for d in despesas:
            self.tree.insert("", "end", values=(d.id_despesa, d.numero_os_projeto, d.data_despesa.strftime("%Y-%m-%d"), f"R$ {d.total:.2f}"))

    def cadastrar_despesa(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Despesa")
        janela.geometry("500x750")
        janela.grab_set()

        campos = {}

        def adicionar_campo(label_text, row):
            ttk.Label(janela, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(janela, width=40)
            entry.grid(row=row, column=1, padx=10, pady=5)
            campos[label_text] = entry

        adicionar_campo("Número da OS", 0)
        adicionar_campo("Data da Despesa (AAAA-MM-DD)", 1)
        adicionar_campo("Observação", 2)

        campos_valores = ["Mão de Obra", "Alimentação", "Hospedagem", "Viagem", "Segurança do Trabalho",
                          "Material", "Equipamento", "Andaime", "Documentação", "Outros"]

        for i, nome in enumerate(campos_valores, start=3):
            adicionar_campo(nome, i)

        def salvar():
            try:
                numero_os = int(campos["Número da OS"].get().strip())
                if not self.service.validar_os_existente(numero_os):
                    raise ValueError("OS não localizada no sistema.")

                data_str = campos["Data da Despesa (AAAA-MM-DD)"].get().strip()
                try:
                    data_despesa = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida - formato correto: yyyy-mm-dd")

                observacao = campos["Observação"].get().strip()

                def get_valor(nome):
                    val = campos[nome].get().strip()
                    if not val:
                        return 0.0
                    try:
                        return float(val)
                    except ValueError:
                        raise ValueError(f"Valor inválido em '{nome}'.")

                despesa = Despesa(
                    numero_os_projeto=numero_os,
                    data_despesa=data_despesa,
                    observacao=observacao,
                    mao_de_obra=get_valor("Mão de Obra"),
                    alimentacao=get_valor("Alimentação"),
                    hospedagem=get_valor("Hospedagem"),
                    viagem=get_valor("Viagem"),
                    seguranca_trabalho=get_valor("Segurança do Trabalho"),
                    material=get_valor("Material"),
                    equipamento=get_valor("Equipamento"),
                    andaime=get_valor("Andaime"),
                    documentacao=get_valor("Documentação"),
                    outros=get_valor("Outros")
                )

                id_despesa = self.service.criar_despesa(despesa)
                messagebox.showinfo("Sucesso", f"Despesa cadastrada com sucesso! ID: {id_despesa}")
                janela.destroy()
                self.carregar_despesas()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Despesa", command=salvar).grid(row=len(campos_valores) + 3, column=0, columnspan=2, pady=20)

    def editar_despesa(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma despesa para editar.")
            return

        valores = self.tree.item(item, "values")
        id_despesa = valores[0]
        despesa = self.service.buscar_por_id(id_despesa)

        if not despesa:
            messagebox.showerror("Erro", "Despesa não encontrada.")
            return

        janela = tk.Toplevel(self.root)
        janela.title(f"Editar Despesa ID {id_despesa}")
        janela.geometry("500x750")
        janela.grab_set()

        campos = {}

        def adicionar_campo(label_text, valor, row):
            ttk.Label(janela, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(janela, width=40)
            entry.insert(0, str(valor))
            entry.grid(row=row, column=1, padx=10, pady=5)
            campos[label_text] = entry

        adicionar_campo("Data da Despesa (AAAA-MM-DD)", despesa.data_despesa.strftime("%Y-%m-%d"), 0)
        adicionar_campo("Observação", despesa.observacao or "", 1)

        campos_valores = [
            ("Mão de Obra", despesa.mao_de_obra),
            ("Alimentação", despesa.alimentacao),
            ("Hospedagem", despesa.hospedagem),
            ("Viagem", despesa.viagem),
            ("Segurança do Trabalho", despesa.seguranca_trabalho),
            ("Material", despesa.material),
            ("Equipamento", despesa.equipamento),
            ("Andaime", despesa.andaime),
            ("Documentação", despesa.documentacao),
            ("Outros", despesa.outros)
        ]

        for i, (nome, valor) in enumerate(campos_valores, start=2):
            adicionar_campo(nome, valor, i)

        def salvar():
            try:
                data_str = campos["Data da Despesa (AAAA-MM-DD)"].get().strip()
                try:
                    despesa.data_despesa = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida - formato correto: yyyy-mm-dd")

                despesa.observacao = campos["Observação"].get().strip()

                def get_valor(nome):
                    val = campos[nome].get().strip()
                    if not val:
                        return 0.0
                    try:
                        return float(val)
                    except ValueError:
                        raise ValueError(f"Valor inválido em '{nome}'.")

                despesa.mao_de_obra = get_valor("Mão de Obra")
                despesa.alimentacao = get_valor("Alimentação")
                despesa.hospedagem = get_valor("Hospedagem")
                despesa.viagem = get_valor("Viagem")
                despesa.seguranca_trabalho = get_valor("Segurança do Trabalho")
                despesa.material = get_valor("Material")
                despesa.equipamento = get_valor("Equipamento")
                despesa.andaime = get_valor("Andaime")
                despesa.documentacao = get_valor("Documentação")
                despesa.outros = get_valor("Outros")

                self.service.atualizar_despesa(despesa)
                messagebox.showinfo("Sucesso", f"Despesa ID {id_despesa} atualizada com sucesso.")
                janela.destroy()
                self.carregar_despesas()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Alterações", command=salvar).grid(row=len(campos_valores) + 2, column=0, columnspan=2, pady=20)

    def buscar_por_os(self):
        os_texto = self.entry_os_busca.get().strip()

        if not os_texto.isdigit():
            messagebox.showerror("Erro", "Número da OS inválido. Digite apenas números.")
            return

        numero_os = int(os_texto)
        despesa = self.service.buscar_por_os(numero_os)

        if not despesa:
            messagebox.showinfo("Nenhum Resultado", "Nenhuma despesa encontrada para esta OS.")
            return

        # Limpa o grid
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Adiciona apenas a despesa encontrada
        self.tree.insert("", "end", values=(
            despesa.id_despesa,
            despesa.numero_os_projeto,
            despesa.data_despesa.strftime("%Y-%m-%d"),
            f"R$ {despesa.total:.2f}"
        ))

    def excluir_despesa(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma despesa para excluir.")
            return

        valores = self.tree.item(item, "values")
        id_despesa = valores[0]

        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir esta despesa?")
        if not confirmar:
            return

        try:
            sucesso = self.service.excluir_despesa(id_despesa)
            if sucesso:
                messagebox.showinfo("Sucesso", "Despesa excluída com sucesso.")
                self.carregar_despesas()
            else:
                messagebox.showerror("Erro", "Falha ao excluir a despesa. Verifique o ID.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir despesa:\n{e}")
