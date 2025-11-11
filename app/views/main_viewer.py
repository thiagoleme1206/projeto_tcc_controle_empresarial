import tkinter as tk
from tkinter import ttk, messagebox

MODULOS_DISPONIVEIS = {
    "estoque": "📦 Gestão de Estoque",
    "estoque_consulta": "🔍 Consulta de Estoque",
    "propostas": "🧾 Gestão de Propostas",
    "propostas_consulta": "🔍 Consulta de Propostas",
    "lista_materiais": "📐 Lista de Materiais",
    "projetos": "💰 Gestão de Projetos",
    "projetos_consulta": "🔍 Consulta de Projetos",
    "relatorios": "📊 Relatórios",
    "usuarios": "👥 Gestão de Usuários",
    "logs": "📄 Logs do Sistema",
    "chatbot": "🤖 ChatBot (Gemini)"
}

PERMISSOES_GRUPO = {
    "estoquista": ["estoque", "chatbot"],
    "vendedor": ["propostas", "estoque_consulta", "chatbot"],
    "engenheiro": ["propostas_consulta", "estoque_consulta", "lista_materiais", "chatbot"],
    "financeiro": ["projetos", "chatbot"],
    "gerencia": ["propostas_consulta", "projetos_consulta", "relatorios", "chatbot"],
    "ti": ["*"],  # acesso total
    "inativos": []  # sem acesso
}

class MainViewer:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title("Sistema Missão Impossível")
        largura = 650
        altura = 400

        # Obtém as dimensões da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calcula as coordenadas para centralizar
        x = (screen_width // 2) - (largura // 2)
        y = (screen_height // 2) - (altura // 2)

        # Define tamanho e posição centralizada
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.configure(bg="#f0f2f5")
        self.create_widgets()

    def create_widgets(self):
        # Cabeçalho
        cabecalho = ttk.Label(self.root, text=f"Bem-vindo, {self.usuario.nome}!", font=("Helvetica", 18, "bold"), background="#f0f2f5")
        cabecalho.pack(pady=(20, 5))

        sub = ttk.Label(self.root, text="Selecione um módulo para acessar:", font=("Helvetica", 12), background="#f0f2f5")
        sub.pack(pady=(0, 20))

        # Área dos botões
        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack()

        permissoes = self.get_modulos_permitidos()

        # Grid 3xN para botões
        colunas = 3
        for i, modulo in enumerate(permissoes):
            nome = MODULOS_DISPONIVEIS.get(modulo, modulo)
            btn = ttk.Button(frame_botoes, text=nome, width=30, command=lambda m=modulo: self.abrir_modulo(m))
            linha = i // colunas
            coluna = i % colunas
            btn.grid(row=linha, column=coluna, padx=10, pady=10)

        # Botão de sair
        sair_btn = ttk.Button(self.root, text="Sair", command=self.root.quit)
        sair_btn.pack(pady=30)

    def get_modulos_permitidos(self):
        grupo = self.usuario.grupo
        permissoes = PERMISSOES_GRUPO.get(grupo, [])
        if "*" in permissoes:
            permissoes = list(MODULOS_DISPONIVEIS.keys())
        else:
            if "chatbot" not in permissoes:
                permissoes.append("chatbot")
        return permissoes

    def abrir_modulo(self, modulo):
        nome = MODULOS_DISPONIVEIS.get(modulo, modulo)

        if modulo == "projetos":
            self.menu_projetos()
        elif modulo == "chatbot":
            from app.views.chatbot_viewer import ChatbotViewer
            nova_janela = tk.Toplevel(self.root)
            ChatbotViewer(nova_janela)
        elif modulo == "logs":
            from app.views.auditoria_viewer import AuditoriaViewer
            nova_janela = tk.Toplevel(self.root)
            AuditoriaViewer(nova_janela, self.usuario)
        elif modulo == "relatorios":
            from app.views.relatorio_viewer import RelatorioViewer
            nova_janela = tk.Toplevel(self.root)
            RelatorioViewer(nova_janela, self.usuario)
        elif modulo == "usuarios":
            from app.views.usuario_viewer import UsuarioViewer
            UsuarioViewer(self.root, self.usuario)
        elif modulo == "propostas":
            from app.views.proposta_viewer import PropostaViewer
            PropostaViewer(self.root, self.usuario)
        elif modulo == "propostas_consulta":
            from app.views.proposta_consulta_viewer import PropostaConsultaViewer
            PropostaConsultaViewer(self.root, self.usuario)
        elif modulo == "lista_materiais":
            from app.views.lista_materiais_viewer import ListaMateriaisViewer
            ListaMateriaisViewer(self.root, self.usuario)
        elif modulo == "clientes":
            from app.views.cliente_viewer import ClienteViewer
            ClienteViewer(self.root, self.usuario)
        elif modulo == "estoque":
            from app.views.estoque_viewer import EstoqueViewer
            EstoqueViewer(self.root, self.usuario)
        elif modulo == "estoque_consulta":
            from app.views.consultaestoqueviewer import ConsultaEstoqueViewer
            ConsultaEstoqueViewer(self.root, self.usuario)
        elif modulo == "projetos_consulta":
            from app.views.consulta_projetos_viewer import ConsultaProjetosViewer
            ConsultaProjetosViewer(self.root, self.usuario)
        else:
            messagebox.showinfo("Módulo", f"Abrindo módulo: {nome} (a implementar)")

    def menu_projetos(self):
        projetos_janela = tk.Toplevel(self.root)
        projetos_janela.title("💰 Gestão de Projetos")

        # Centralizar na tela
        largura = 400
        altura = 300
        screen_width = projetos_janela.winfo_screenwidth()
        screen_height = projetos_janela.winfo_screenheight()
        x = (screen_width // 2) - (largura // 2)
        y = (screen_height // 2) - (altura // 2)

        projetos_janela.geometry(f"{largura}x{altura}+{x}+{y}")
        projetos_janela.configure(bg="#f0f2f5")

        # Cabeçalho
        ttk.Label(
            projetos_janela,
            text="💰 Gestão de Projetos",
            font=("Helvetica", 16, "bold"),
            background="#f0f2f5"
        ).pack(pady=(20, 10))

        # Opções do menu de gestão de projetos
        opcoes = [
            ("📋 Gestão de Projetos", lambda: self.abrir_projetos()),
            ("👥 Gestão de Clientes", lambda: self.abrir_clientes()),
            ("🧾 Gestão de Orçamentos", lambda: self.abrir_orcamentos()),
            ("💸 Gestão de Despesas", lambda: self.abrir_despesas()),
            ("💰 Gestão de Receitas", lambda: self.abrir_receitas())
        ]

        for texto, comando in opcoes:
            btn = ttk.Button(projetos_janela, text=texto, width=30, command=comando)
            btn.pack(pady=5)

    def abrir_clientes(self):
        from app.views.cliente_viewer import ClienteViewer
        ClienteViewer(self.root, self.usuario)

    def abrir_projetos(self):
        """Abre o módulo de Gestão de Projetos principal"""

        from app.views.projetos_viewer import ProjetoViewer
        nova_janela = tk.Toplevel(self.root)
        ProjetoViewer(nova_janela, self.usuario)

    def abrir_orcamentos(self):
        from app.views.orcamento_viewer import OrcamentoViewer
        OrcamentoViewer(tk.Toplevel(self.root), self.usuario)
    
    def abrir_despesas(self):
        from app.views.despesa_viewer import DespesaViewer
        DespesaViewer(tk.Toplevel(self.root), self.usuario)

    def abrir_receitas(self):
        from app.views.receita_viewer import ReceitaViewer
        ReceitaViewer(tk.Toplevel(self.root), self.usuario)
