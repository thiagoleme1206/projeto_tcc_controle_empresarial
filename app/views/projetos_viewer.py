import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from app.services.projeto_service import ProjetoService
from app.models.projeto_model import Projeto
from app.services.auditoria_service import AuditoriaService

class ProjetoViewer:
    def __init__(self, root, usuario_logado):
        self.root = root
        self.root.title("📋 Gestão de Projetos")
        self.root.geometry("1100x500")
        self.usuario = usuario_logado
        self.service = ProjetoService()

        self.acesso_total = self.usuario.grupo in ["financeiro", "ti"]
        self.consulta_apenas = self.usuario.grupo == "gerencia"

        if not (self.acesso_total or self.consulta_apenas):
            messagebox.showerror("Acesso Negado", "Você não tem permissão para acessar este módulo.")
            self.root.destroy()
            return

        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.criar_widgets()
        self.carregar_projetos()

    def criar_widgets(self):
        ttk.Label(self.frame, text="📋 Projetos Cadastrados", font=("Helvetica", 16, "bold")).pack(pady=10)

        colunas = ("OS", "Tipo", "Cliente", "Data OS", "Status")
        self.tree = ttk.Treeview(self.frame, columns=colunas, show="headings", height=15)

        for col in colunas:
            self.tree.heading(col, text=col)
            if col == "Cliente":
                self.tree.column(col, width=250)
            elif col == "Tipo":
                self.tree.column(col, width=180)
            elif col == "Data OS":
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=80)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Barra inferior de ações
        botoes = ttk.Frame(self.frame)
        botoes.pack(fill="x", pady=5)

        ttk.Button(botoes, text="🔄 Atualizar", command=self.carregar_projetos).pack(side="left", padx=5)

        if self.acesso_total:
            ttk.Button(botoes, text="➕ Novo Projeto", command=self.cadastrar_projeto).pack(side="left", padx=5)
            ttk.Button(botoes, text="✏️ Editar Projeto", command=self.editar_projeto).pack(side="left", padx=5)
            filtro_frame = ttk.Frame(self.frame)
            filtro_frame.pack(pady=5, fill="x")

            ttk.Label(filtro_frame, text="Buscar por OS:").pack(side="left", padx=(0, 5))
            self.entrada_os = ttk.Entry(filtro_frame, width=20)
            self.entrada_os.pack(side="left", padx=(0, 5))
            ttk.Button(filtro_frame, text="🔍 Buscar", command=self.buscar_por_os).pack(side="left", padx=(0, 10))
            ttk.Button(botoes, text="🗑️ Excluir Projeto", command=self.excluir_projeto).pack(side="left", padx=5)

    def carregar_projetos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        projetos = self.service.listar_projetos()
        for p in projetos:
            self.tree.insert("", "end", values=(p.numero_os, p.tipo, p.cliente_nome, p.data_os.strftime("%Y-%m-%d"), p.status))

    def cadastrar_projeto(self):    
        service = ProjetoService()
        auditoria = AuditoriaService()

        janela = tk.Toplevel(self.root)
        janela.title("Cadastrar Projeto")
        janela.geometry("500x600")
        janela.grab_set()

        campos = {}

        def adicionar_campo(label_text, row, tipo="entry", values=None):
            ttk.Label(janela, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            if tipo == "entry":
                entry = ttk.Entry(janela, width=40)
                entry.grid(row=row, column=1, padx=10, pady=5)
                campos[label_text] = entry
            elif tipo == "combo":
                combo = ttk.Combobox(janela, values=values, state="readonly", width=37)
                combo.grid(row=row, column=1, padx=10, pady=5)
                campos[label_text] = combo

        # Campos
        adicionar_campo("Tipo de Projeto", 0)
        adicionar_campo("ID do Cliente", 1)
        adicionar_campo("Data da OS (AAAA-MM-DD)", 2)
        adicionar_campo("Número da Proposta", 3)
        adicionar_campo("Valor do Serviço", 4)
        adicionar_campo("Valor do Material", 5)
        adicionar_campo("Endereço da Obra", 6)
        adicionar_campo("Cidade da Obra", 7)
        adicionar_campo("Estado (UF)", 8)
        adicionar_campo("Contato", 9)
        adicionar_campo("Status", 10, tipo="combo", values=[
            "Em andamento", "Finalizado", "Cancelado", "Em análise de proposta", "Pausado"
        ])

        def salvar():
            try:
                tipo = campos["Tipo de Projeto"].get().strip()
                if not tipo or tipo.isnumeric():
                    raise ValueError("Tipo inválido")

                id_cliente = int(campos["ID do Cliente"].get().strip())
                cliente = service.cliente_repo.buscar_por_id(id_cliente)
                if not cliente:
                    raise ValueError("Cliente não encontrado")

                # 🔍 Validação da data
                data_os_str = campos["Data da OS (AAAA-MM-DD)"].get().strip()
                if not data_os_str:
                    raise ValueError("Data inválida - formato: yyyy-mm-dd")
                try:
                    data_os = datetime.strptime(data_os_str, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError("Data inválida - formato: yyyy-mm-dd")

                numero_proposta = campos["Número da Proposta"].get().strip()
                if not numero_proposta:
                    raise ValueError("Número da proposta é obrigatório")

                # 🔍 Validação dos valores numéricos
                valor_servico_str = campos["Valor do Serviço"].get().strip()
                valor_material_str = campos["Valor do Material"].get().strip()
                if not valor_servico_str or not valor_material_str:
                    raise ValueError("Valor serviço ou material inválidos")
                try:
                    valor_servico = float(valor_servico_str)
                    valor_material = float(valor_material_str)
                except ValueError:
                    raise ValueError("Valor serviço ou material inválidos")

                total = valor_servico + valor_material

                endereco_obra = campos["Endereço da Obra"].get().strip()
                cidade_obra = campos["Cidade da Obra"].get().strip()
                estado_obra = campos["Estado (UF)"].get().strip().upper()
                contato = campos["Contato"].get().strip()
                status = campos["Status"].get()
                if not status:
                    raise ValueError("Selecione um status válido")

                projeto = Projeto(
                    numero_os=None,
                    tipo=tipo,
                    id_cliente=id_cliente,
                    cliente_nome=cliente.nome,
                    cliente_cpf_cnpj=cliente.cpf_cnpj,
                    data_os=data_os,
                    numero_proposta=numero_proposta,
                    valor_servico=valor_servico,
                    valor_material=valor_material,
                    total=total,
                    endereco_obra=endereco_obra,
                    cidade_obra=cidade_obra,
                    estado_obra=estado_obra,
                    contato=contato,
                    nome_responsavel=self.usuario.nome,
                    status=status
                )

                numero_os = service.criar_projeto(projeto)

                auditoria.registrar_acao(
                    self.usuario.login,
                    "INSERT",
                    "projetos",
                    f"Projeto cadastrado - OS {numero_os}, Cliente '{cliente.nome}'"
                )

                messagebox.showinfo("Sucesso", f"Projeto cadastrado com sucesso!\nOS: {numero_os}")
                janela.destroy()
                self.carregar_projetos()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        # Botão salvar
        salvar_btn = ttk.Button(janela, text="Salvar Projeto", command=salvar)
        salvar_btn.grid(row=11, column=0, columnspan=2, pady=20)

    def editar_projeto(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um projeto para editar.")
            return

        valores = self.tree.item(item, "values")
        numero_os = valores[0]

        projeto = self.service.buscar_por_os(numero_os)
        if not projeto:
            messagebox.showerror("Erro", f"Projeto OS {numero_os} não encontrado.")
            return

        janela = tk.Toplevel(self.root)
        janela.title(f"Editar Projeto - OS {numero_os}")
        janela.geometry("500x600")
        janela.grab_set()

        campos = {}

        def adicionar_campo(label_text, valor_inicial, row, tipo="entry", values=None):
            ttk.Label(janela, text=label_text).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            if tipo == "entry":
                entry = ttk.Entry(janela, width=40)
                entry.insert(0, str(valor_inicial) if valor_inicial is not None else "")
                entry.grid(row=row, column=1, padx=10, pady=5)
                campos[label_text] = entry
            elif tipo == "combo":
                combo = ttk.Combobox(janela, values=values, state="readonly", width=37)
                combo.set(valor_inicial)
                combo.grid(row=row, column=1, padx=10, pady=5)
                campos[label_text] = combo

        adicionar_campo("Tipo de Projeto", projeto.tipo, 0)
        adicionar_campo("Número da Proposta", projeto.numero_proposta, 1)
        adicionar_campo("Valor do Serviço", projeto.valor_servico, 2)
        adicionar_campo("Valor do Material", projeto.valor_material, 3)
        adicionar_campo("Endereço da Obra", projeto.endereco_obra, 4)
        adicionar_campo("Cidade da Obra", projeto.cidade_obra, 5)
        adicionar_campo("Estado (UF)", projeto.estado_obra, 6)
        adicionar_campo("Contato", projeto.contato, 7)
        adicionar_campo("Status", projeto.status, 8, tipo="combo", values=[
            "Em andamento", "Finalizado", "Cancelado", "Em análise de proposta", "Pausado"
        ])

        def salvar_edicao():
            try:
                tipo = campos["Tipo de Projeto"].get().strip()
                if not tipo or tipo.isnumeric():
                    raise ValueError("Tipo de projeto inválido.")

                numero_proposta = campos["Número da Proposta"].get().strip()
                if not numero_proposta:
                    raise ValueError("Número da proposta é obrigatório.")

                valor_servico_str = campos["Valor do Serviço"].get().strip()
                valor_material_str = campos["Valor do Material"].get().strip()
                if not valor_servico_str or not valor_material_str:
                    raise ValueError("Valor do serviço ou material não pode estar vazio.")

                try:
                    valor_servico = float(valor_servico_str)
                    valor_material = float(valor_material_str)
                except ValueError:
                    raise ValueError("Valor do serviço ou material deve ser numérico.")

                endereco = campos["Endereço da Obra"].get().strip()
                cidade = campos["Cidade da Obra"].get().strip()
                estado = campos["Estado (UF)"].get().strip().upper()
                contato = campos["Contato"].get().strip()
                status = campos["Status"].get()

                if not all([endereco, cidade, estado, contato, status]):
                    raise ValueError("Todos os campos devem estar preenchidos.")

                # Atualiza os dados no objeto projeto
                projeto.tipo = tipo
                projeto.numero_proposta = numero_proposta
                projeto.valor_servico = valor_servico
                projeto.valor_material = valor_material
                projeto.total = valor_servico + valor_material
                projeto.endereco_obra = endereco
                projeto.cidade_obra = cidade
                projeto.estado_obra = estado
                projeto.contato = contato
                projeto.status = status

                self.service.atualizar_projeto(projeto)

                AuditoriaService().registrar_acao(
                    self.usuario.login,
                    "UPDATE",
                    "projetos",
                    f"Projeto OS {numero_os} atualizado."
                )

                messagebox.showinfo("Sucesso", f"Projeto OS {numero_os} atualizado com sucesso.")
                janela.destroy()
                self.carregar_projetos()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Salvar Alterações", command=salvar_edicao).grid(row=9, column=0, columnspan=2, pady=20)

    def excluir_projeto(self):
        # Seleciona projeto
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um projeto para excluir.")
            return

        valores = self.tree.item(item, "values")
        try:
            numero_os = int(valores[0])
        except Exception:
            messagebox.showerror("Erro", "ID da OS inválido.")
            return

        # Confirma exclusão
        confirmar = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o projeto OS {numero_os}?")
        if not confirmar:
            return

        try:
            sucesso = self.service.excluir_projeto(numero_os)
            if sucesso:
                # Registrar auditoria
                AuditoriaService().registrar_acao(
                    self.usuario.login,
                    "DELETE",
                    "projetos",
                    f"Projeto OS {numero_os} excluído."
                )
                messagebox.showinfo("Sucesso", f"✅ Projeto OS {numero_os} excluído com sucesso.")
                self.carregar_projetos()
            else:
                messagebox.showerror("Erro", f"❌ Projeto OS {numero_os} não encontrado.")
        except Exception as e:
            # Tentativa de identificar erro de FK/integreidade para mensagem mais amigável
            msg = str(e)
            low = msg.lower()
            if "foreign key" in low or "referenced" in low or "violat" in low:
                messagebox.showerror(
                    "Erro ao excluir",
                    "❌ Não foi possível excluir o projeto porque existem registros vinculados (orcamentos, despesas ou receitas). "
                    "Remova ou desassocie os registros vinculados antes de excluir."
                )
            else:
                messagebox.showerror("Erro", f"Erro ao excluir projeto: {msg}")

    def buscar_por_os(self):
        entrada = self.entrada_os.get().strip()

        if not entrada.isdigit():
            messagebox.showwarning("Aviso", "Digite um número de OS válido (somente números).")
            return

        numero_os = int(entrada)
        projeto = self.service.buscar_por_os(numero_os)

        for i in self.tree.get_children():
            self.tree.delete(i)

        if projeto:
            self.tree.insert("", "end", values=(
                projeto.numero_os,
                projeto.tipo,
                projeto.cliente_nome,
                projeto.data_os.strftime("%Y-%m-%d"),
                projeto.status
            ))
        else:
            messagebox.showinfo("Sem Resultados", f"Nenhum projeto encontrado para OS {numero_os}.")