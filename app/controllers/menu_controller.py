PERMISSOES_GRUPO = {
    "estoquista": ["estoque", "chatbot"],
    "vendedor": ["propostas", "estoque_consulta", "chatbot"],
    "engenheiro": ["propostas_consulta", "estoque_consulta", "lista_materiais", "chatbot"],
    "financeiro": ["projetos", "chatbot"],
    "gerencia": ["propostas_consulta", "projetos_consulta", "relatorios", "chatbot"],
    "ti": ["*"],  # acesso total
    "inativos": [] # sem acesso
}

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

def exibir_menu_modulos(usuario):
    grupo = usuario.grupo
    permissoes = PERMISSOES_GRUPO.get(grupo, [])

    if "*" in permissoes:
        permissoes = list(MODULOS_DISPONIVEIS.keys())
    else:
        if "chatbot" not in permissoes:
            permissoes.append("chatbot")

    print("\n=== Módulos disponíveis ===")
    opcoes = []
    for i, modulo in enumerate(permissoes, start=1):
        nome = MODULOS_DISPONIVEIS.get(modulo, modulo)
        print(f"{i}. {nome}")
        opcoes.append((i, modulo))

    escolha = input("\nEscolha um módulo para acessar (número): ")

    try:
        escolha = int(escolha)
        modulo_selecionado = opcoes[escolha - 1][1]
        print(f"\n👉 Acessando módulo: {MODULOS_DISPONIVEIS.get(modulo_selecionado)}\n")
        if modulo_selecionado == "estoque":
            from app.controllers.estoque_controller import menu_estoque
            menu_estoque(usuario)
        elif modulo_selecionado == "propostas":
            from app.controllers.proposta_controller import menu_propostas
            menu_propostas(usuario)
        elif modulo_selecionado == "lista_materiais":
            from app.controllers.lista_materiais_controller import menu_lista_materiais
            menu_lista_materiais(usuario)
        
        elif modulo_selecionado == "projetos":
            while True:
                print("\n=== Gestão de Projetos ===")
                print("1. Gestão de Projetos")
                print("2. Gestão de Clientes")
                print("3. Gestão de Orçamentos")
                print("4. Gestão de Despesas")
                print("5. Gestão de Receitas")
                print("0. Voltar")

                opcao = input("Escolha uma opção: ")

                if opcao == "1":
                    from app.controllers.projeto_controller import menu_projetos
                    menu_projetos(usuario)
                elif opcao == "2":
                    from app.controllers.cliente_controller import menu_clientes
                    menu_clientes(usuario)
                elif opcao == "3":
                    from app.controllers.orcamento_controller import menu_orcamentos
                    menu_orcamentos(usuario)
                elif opcao == "4":
                    from app.controllers.despesa_controller import menu_despesas
                    menu_despesas(usuario)
                elif opcao == "5":
                    from app.controllers.receita_controller import menu_receitas
                    menu_receitas(usuario)
                elif opcao == "0":
                    break
                else:
                    print("❌ Opção inválida.")

        elif modulo_selecionado == "relatorios":
            from app.controllers.relatorio_controller import menu_relatorios
            menu_relatorios(usuario)
        elif modulo_selecionado == "usuarios":
            from app.controllers.menu_usuario import menu_usuario
            menu_usuario(usuario)
        elif modulo_selecionado == "logs":
            from app.controllers.menu_auditoria_controller import menu_auditoria
            menu_auditoria(usuario)
        elif modulo_selecionado == "chatbot":
            from app.controllers.menu_chatbot_controller import menu_chatbot
            menu_chatbot(usuario)
        elif modulo_selecionado == "estoque":
            from app.controllers.estoque_controller import menu_estoque
            menu_estoque(usuario)
        else:
            print("⚠️ Módulo ainda não implementado.")
    except (ValueError, IndexError):
        print("❌ Escolha inválida.")
