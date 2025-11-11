import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.services.orcamento_service import OrcamentoService
from app.models.orcamento_model import Orcamento

class OrcamentoViewer:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.root.title("📑 Gestão de Orçamentos")
        self.root.geometry("1100x500")
        self.usuario = usuario_logado
        self.service = OrcamentoService()

        self.acesso_total = self.usuario.grupo in ["financeiro", "ti"]
        self.leitura_apenas = self.usuario.grupo == "gerencia"

        if not (self.acesso_total or self.leitura_apenas):
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            self.root.destroy()
            return

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_orcamentos()

    def criar_widgets(self):
        ttk.Label(self.frame, text="📑 Orçamentos Cadastrados", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("ID", "OS", "Data", "Total")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, pady=10)

        botoes = ttk.Frame(self.frame)
        botoes.pack(fill="x", pady=5)

        ttk.Button(botoes, text="🔄 Atualizar", command=self.carregar_orcamentos).pack(side="left", padx=5)

        if self.acesso_total:
            ttk.Button(botoes, text="➕ Novo Orçamento", command=self.cadastrar_orcamento).pack(side="left", padx=5)
            filtro_frame = ttk.Frame(self.frame)
            filtro_frame.pack(pady=5, fill="x")

            ttk.Label(filtro_frame, text="Buscar por OS:").pack(side="left", padx=(0, 5))
            self.entrada_busca_os = ttk.Entry(filtro_frame, width=20)
            self.entrada_busca_os.pack(side="left", padx=(0, 5))
            ttk.Button(filtro_frame, text="🔍 Buscar", command=self.buscar_por_os).pack(side="left", padx=(0, 10))
            ttk.Button(botoes, text="✏️ Editar Orçamento", command=self.editar_orcamento).pack(side="left", padx=5)
            ttk.Button(botoes, text="🗑️ Excluir Orçamento", command=self.excluir_orcamento).pack(side="left", padx=5)

    def carregar_orcamentos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        orcamentos = self.service.listar_orcamentos()
        for o in orcamentos:
            self.tree.insert("", "end", values=(o.id_orcamento, o.numero_os, o.data_orcamento.strftime("%Y-%m-%d"), f"R$ {o.total:.2f}"))

    def cadastrar_orcamento(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Orçamento")
        janela.geometry("500x700")
        janela.grab_set()

        campos = {}

        def adicionar_campo(label_text, row):
            ttk.Label(janela, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(janela, width=40)
            entry.grid(row=row, column=1, padx=10, pady=5)
            campos[label_text] = entry

        adicionar_campo("Número da OS", 0)
        adicionar_campo("Data do Orçamento (AAAA-MM-DD)", 1)
        campos_valores = ["Mão de Obra", "Alimentação", "Hospedagem", "Viagem", "Segurança do Trabalho",
                          "Material", "Equipamento", "Andaime", "Documentação", "Outros"]

        for i, nome in enumerate(campos_valores, start=2):
            adicionar_campo(nome, i)

        def salvar():
            try:
                numero_os = int(campos["Número da OS"].get().strip())
                if not self.service.validar_os_existe(numero_os):
                    raise ValueError("OS não localizada no sistema.")

                data_str = campos["Data do Orçamento (AAAA-MM-DD)"].get().strip()
                try:
                    data_orcamento = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida - formato: YYYY-MM-DD")

                def get_valor(nome):
                    val = campos[nome].get().strip()
                    if not val:
                        return 0.0
                    try:
                        return float(val)
                    except ValueError:
                        raise ValueError(f"Valor inválido em '{nome}'.")

                orcamento = Orcamento(
                    numero_os=numero_os,
                    data_orcamento=data_orcamento,
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

                id_gerado = self.service.criar_orcamento(orcamento)
                messagebox.showinfo("Sucesso", f"Orçamento cadastrado com sucesso! ID: {id_gerado}")
                janela.destroy()
                self.carregar_orcamentos()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Orçamento", command=salvar).grid(row=len(campos_valores) + 2, column=0, columnspan=2, pady=20)

    def editar_orcamento(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um orçamento para editar.")
            return

        valores = self.tree.item(item, "values")
        id_orcamento = valores[0]
        orcamento = self.service.buscar_por_id(id_orcamento)

        if not orcamento:
            messagebox.showerror("Erro", "Orçamento não encontrado.")
            return

        janela = tk.Toplevel(self.root)
        janela.title(f"Editar Orçamento ID {id_orcamento}")
        janela.geometry("500x700")
        janela.grab_set()

        campos = {}

        def adicionar_campo(label_text, valor, row):
            ttk.Label(janela, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(janela, width=40)
            entry.insert(0, str(valor))
            entry.grid(row=row, column=1, padx=10, pady=5)
            campos[label_text] = entry

        adicionar_campo("Data do Orçamento (AAAA-MM-DD)", orcamento.data_orcamento.strftime("%Y-%m-%d"), 0)
        campos_valores = [
            ("Mão de Obra", orcamento.mao_de_obra),
            ("Alimentação", orcamento.alimentacao),
            ("Hospedagem", orcamento.hospedagem),
            ("Viagem", orcamento.viagem),
            ("Segurança do Trabalho", orcamento.seguranca_trabalho),
            ("Material", orcamento.material),
            ("Equipamento", orcamento.equipamento),
            ("Andaime", orcamento.andaime),
            ("Documentação", orcamento.documentacao),
            ("Outros", orcamento.outros)
        ]

        for i, (nome, valor) in enumerate(campos_valores, start=1):
            adicionar_campo(nome, valor, i)

        def salvar():
            try:
                data_str = campos["Data do Orçamento (AAAA-MM-DD)"].get().strip()
                try:
                    orcamento.data_orcamento = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida - formato: YYYY-MM-DD")

                def get_valor(nome):
                    val = campos[nome].get().strip()
                    if not val:
                        return 0.0
                    try:
                        return float(val)
                    except ValueError:
                        raise ValueError(f"Valor inválido em '{nome}'.")

                orcamento.mao_de_obra = get_valor("Mão de Obra")
                orcamento.alimentacao = get_valor("Alimentação")
                orcamento.hospedagem = get_valor("Hospedagem")
                orcamento.viagem = get_valor("Viagem")
                orcamento.seguranca_trabalho = get_valor("Segurança do Trabalho")
                orcamento.material = get_valor("Material")
                orcamento.equipamento = get_valor("Equipamento")
                orcamento.andaime = get_valor("Andaime")
                orcamento.documentacao = get_valor("Documentação")
                orcamento.outros = get_valor("Outros")

                self.service.atualizar_orcamento(orcamento)
                messagebox.showinfo("Sucesso", f"Orçamento ID {id_orcamento} atualizado com sucesso.")
                janela.destroy()
                self.carregar_orcamentos()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Alterações", command=salvar).grid(row=len(campos_valores) + 1, column=0, columnspan=2, pady=20)

    def excluir_orcamento(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um orçamento para excluir.")
            return

        valores = self.tree.item(item, "values")
        id_orcamento = valores[0]

        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este orçamento?")
        if not confirmar:
            return

        try:
            sucesso = self.service.excluir_orcamento(id_orcamento)
            if sucesso:
                messagebox.showinfo("Sucesso", "Orçamento excluído com sucesso.")
                self.carregar_orcamentos()
            else:
                messagebox.showerror("Erro", "Falha ao excluir o orçamento. Verifique o ID.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir orçamento:\n{e}")


    def buscar_por_os(self):
        os_texto = self.entrada_busca_os.get().strip()

        if not os_texto.isdigit():
            messagebox.showwarning("Aviso", "Digite um número de OS válido (somente números).")
            return

        numero_os = int(os_texto)
        orcamento = self.service.buscar_por_os(numero_os)

        for i in self.tree.get_children():
            self.tree.delete(i)

        if orcamento:
            self.tree.insert("", "end", values=(
                orcamento.id_orcamento,
                orcamento.numero_os,
                orcamento.data_orcamento.strftime("%Y-%m-%d"),
                f"R$ {orcamento.total:.2f}"
            ))
        else:
            messagebox.showinfo("Resultado", f"Nenhum orçamento encontrado para OS {numero_os}.")