import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.services.receita_service import ReceitaService
from app.repositories.projeto_repository import ProjetoRepository
from app.models.receita_model import Receita

class ReceitaViewer:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.root.title("💰 Gestão de Receitas")
        self.root.geometry("1100x500")
        self.usuario = usuario_logado

        self.acesso_total = self.usuario.grupo in ["financeiro", "ti"]
        self.leitura_apenas = self.usuario.grupo == "gerencia"

        if not (self.acesso_total or self.leitura_apenas):
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            self.root.destroy()
            return

        self.service = ReceitaService()
        self.projeto_repo = ProjetoRepository()

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_receitas()

    def criar_widgets(self):
        ttk.Label(self.frame, text="💰 Receitas Cadastradas", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("ID", "OS", "Cliente", "Data", "Total Líquido")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, pady=10)

        filtro_frame = ttk.Frame(self.frame)
        filtro_frame.pack(fill="x", pady=5)

        ttk.Label(filtro_frame, text="Buscar por OS:").pack(side="left", padx=5)
        self.entrada_os = ttk.Entry(filtro_frame, width=20)
        self.entrada_os.pack(side="left")
        ttk.Button(filtro_frame, text="🔍 Buscar", command=self.buscar_por_os).pack(side="left", padx=5)

        botoes = ttk.Frame(self.frame)
        botoes.pack(fill="x", pady=5)

        ttk.Button(botoes, text="🔄 Atualizar", command=self.carregar_receitas).pack(side="left", padx=5)

        if self.acesso_total:
            ttk.Button(botoes, text="➕ Nova Receita", command=self.cadastrar_receita).pack(side="left", padx=5)
            ttk.Button(botoes, text="✏️ Alterar Receita", command=self.editar_receita).pack(side="left", padx=5)
            ttk.Button(botoes, text="🗑️ Excluir Receita", command=self.excluir_receita).pack(side="left", padx=5)

    def carregar_receitas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        receitas = self.service.listar_receitas()
        for r in receitas:
            self.tree.insert("", "end", values=(r.id_receita, r.numero_os_projeto, r.cliente, r.data_receita.strftime("%Y-%m-%d"), f"R$ {r.valor_liquido:.2f}"))

    def buscar_por_os(self):
        try:
            numero_os = int(self.entrada_os.get().strip())
            receita = self.service.buscar_por_os(numero_os)
            for i in self.tree.get_children():
                self.tree.delete(i)
            if receita:
                self.tree.insert("", "end", values=(
                    receita.id_receita,
                    receita.numero_os_projeto,
                    receita.cliente,
                    receita.data_receita.strftime("%Y-%m-%d"),
                    f"R$ {receita.valor_liquido:.2f}"
                ))
            else:
                messagebox.showinfo("Aviso", "Nenhuma receita encontrada para esta OS.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def cadastrar_receita(self):
        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Receita")
        janela.geometry("400x500")
        janela.grab_set()

        campos = {}

        def adicionar(label, row):
            ttk.Label(janela, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(janela, width=30)
            entry.grid(row=row, column=1, padx=10, pady=5)
            campos[label] = entry

        adicionar("Número da OS", 0)
        adicionar("Data da Receita (AAAA-MM-DD)", 1)
        adicionar("Número da Nota Fiscal (NF)", 2)
        adicionar("Valor do Serviço", 3)
        adicionar("Valor do Material", 4)
        adicionar("Imposto (%)", 5)
        adicionar("ICMS (%)", 6)

        def salvar():
            try:
                numero_os = int(campos["Número da OS"].get().strip())
                projeto = self.projeto_repo.buscar_por_os(numero_os)
                if not projeto:
                    raise ValueError("❌ OS não localizada. Validar OS.")
                cliente = projeto.cliente_nome

                data_str = campos["Data da Receita (AAAA-MM-DD)"].get().strip()
                if not data_str:
                    raise ValueError("Data inválida, formato correto - yyyy-mm-dd")
                try:
                    data_receita = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida, formato correto - yyyy-mm-dd")

                nf = campos["Número da Nota Fiscal (NF)"].get().strip()
                if not nf or not nf.isdigit():
                    raise ValueError("Número da NF inválido. Use apenas números.")

                def get_float(label):
                    val = campos[label].get().strip()
                    return float(val) if val else 0.0

                valor_servico = get_float("Valor do Serviço")
                valor_material = get_float("Valor do Material")

                if valor_servico and valor_material:
                    raise ValueError("Preencha apenas valor do serviço OU material, não ambos.")
                if not valor_servico and not valor_material:
                    raise ValueError("Preencha ao menos um valor: serviço ou material.")

                imposto = get_float("Imposto (%)")
                icms = get_float("ICMS (%)") if valor_material else 0.0

                valor_bruto = valor_servico or valor_material
                valor_liquido = valor_bruto - (valor_bruto * (imposto + icms) / 100)

                receita = Receita(
                    numero_os_projeto=numero_os,
                    data_receita=data_receita,
                    nf=nf,
                    cliente=cliente,
                    valor_servico=valor_servico,
                    valor_material=valor_material,
                    imposto=imposto,
                    icms=icms,
                    valor_liquido=valor_liquido
                )

                id_receita = self.service.criar_receita(receita)
                messagebox.showinfo("Sucesso", f"Receita criada com sucesso! ID: {id_receita}")
                janela.destroy()
                self.carregar_receitas()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Receita", command=salvar).grid(row=8, column=0, columnspan=2, pady=20)

    def editar_receita(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma receita para editar.")
            return

        valores = self.tree.item(item, "values")
        id_receita = int(valores[0])  # 🔧 conversão para int
        receita = self.service.buscar_por_id(id_receita)

        if not receita:
            messagebox.showerror("Erro", "Receita não encontrada.")
            return

        janela = tk.Toplevel(self.root)
        janela.title(f"Editar Receita ID {id_receita}")
        janela.geometry("420x500")
        janela.grab_set()

        campos = {}

        def adicionar(label, valor, row, read_only=False):
            ttk.Label(janela, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(janela, width=30)
            entry.insert(0, str(valor))
            entry.grid(row=row, column=1, padx=10, pady=5)
            if read_only:
                entry.config(state="disabled")
            campos[label] = entry

        adicionar("Data da Receita (AAAA-MM-DD)", receita.data_receita.strftime("%Y-%m-%d"), 0)
        adicionar("NF", receita.nf, 1)
        adicionar("Cliente", receita.cliente, 2)
        adicionar("Valor do Serviço", receita.valor_servico or 0.0, 3)
        adicionar("Valor do Material", receita.valor_material or 0.0, 4)
        adicionar("Imposto (%)", receita.imposto or 0.0, 5)
        adicionar("ICMS (%)", receita.icms or 0.0, 6)

        def salvar():
            try:
                from datetime import datetime

                # Parse campos
                data_str = campos["Data da Receita (AAAA-MM-DD)"].get().strip()
                try:
                    receita.data_receita = datetime.strptime(data_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida - formato correto: yyyy-mm-dd")

                receita.nf = campos["NF"].get().strip()
                receita.cliente = campos["Cliente"].get().strip()

                def get_float(nome):
                    val = campos[nome].get().strip()
                    return float(val) if val else 0.0

                receita.valor_servico = get_float("Valor do Serviço")
                receita.valor_material = get_float("Valor do Material")
                receita.imposto = get_float("Imposto (%)")
                receita.icms = get_float("ICMS (%)")

                if receita.valor_servico and receita.valor_material:
                    raise ValueError("Preencha apenas o valor do serviço OU o valor do material.")
                if not receita.valor_servico and not receita.valor_material:
                    raise ValueError("Preencha pelo menos o valor do serviço OU do material.")

                valor_bruto = receita.valor_servico or receita.valor_material
                receita.valor_liquido = valor_bruto - (valor_bruto * (receita.imposto + receita.icms) / 100)

                # Atualiza no banco
                self.service.atualizar_receita(receita)
                messagebox.showinfo("Sucesso", "Receita atualizada com sucesso.")
                janela.destroy()
                self.carregar_receitas()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Alterações", command=salvar).grid(row=7, column=0, columnspan=2, pady=20)

    def excluir_receita(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione uma receita para excluir.")
            return

        valores = self.tree.item(item, "values")
        id_receita = valores[0]

        confirmar = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir esta receita?")
        if not confirmar:
            return

        try:
            sucesso = self.service.excluir_receita(id_receita)
            if sucesso:
                messagebox.showinfo("Sucesso", "Receita excluída com sucesso.")
                self.carregar_receitas()
            else:
                messagebox.showerror("Erro", "Falha ao excluir a receita. Verifique o ID.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir receita:\n{e}")
