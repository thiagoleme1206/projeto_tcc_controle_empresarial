from app.services.proposta_service import PropostaService

def menu_propostas(usuario):
    service = PropostaService()
    grupo = usuario.grupo
    acesso_total = grupo in ["vendedor", "ti"]
    acesso_consulta = grupo in ["vendedor", "ti", "engenheiro", "gerencia"]

    print("\n=== Módulo de Propostas ===")
    if acesso_total:
        print("1. Listar propostas")
        print("2. Cadastrar nova proposta")
        print("3. Atualizar proposta")
        print("4. Excluir proposta")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            listar_propostas(service)
        elif opcao == "2":
            cadastrar_proposta(service)
        elif opcao == "3":
            atualizar_proposta(service)
        elif opcao == "4":
            excluir_proposta(service)
        else:
            return
    if acesso_consulta:
        print("1. Listar propostas")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            listar_propostas(service)

def listar_propostas(service):
    propostas = service.listar_propostas()
    print("\n🧾 Lista de Propostas:\n")
    for p in propostas:
        print(f"ID: {p.id} | Título: {p.titulo} | Valor: R${p.valor:.2f} | Status: {p.status}")

def cadastrar_proposta(service):
    print("\n=== Nova Proposta ===")
    titulo = input("Título: ")
    descricao = input("Descrição: ")
    valor = float(input("Valor: "))
    status = input("Status (pendente/aprovada/rejeitada): ")
    service.cadastrar_proposta(titulo, descricao, valor, status)
    print("✅ Proposta cadastrada com sucesso!")

def atualizar_proposta(service):
    print("\n=== Atualizar Proposta ===")
    try:
        id = int(input("ID da proposta: "))
        proposta = service.repo.buscar_por_id(id)

        if not proposta:
            print("❌ Proposta não encontrada.")
            return

        titulo = input("Título: ")
        descricao = input("Descrição: ")
        valor = float(input("Valor: "))
        status = input("Status (pendente/aprovada/rejeitada): ")
        service.atualizar_proposta(id, titulo, descricao, valor, status)
        print("✅ Proposta atualizada com sucesso!")
    except ValueError:
        print("❌ Valor inválido. Verifique os campos e tente novamente.")


def excluir_proposta(service):
    print("\n=== Excluir Proposta ===")
    try:
        id = int(input("ID da proposta: "))
        proposta = service.repo.buscar_por_id(id)

        if not proposta:
            print("❌ Proposta não encontrada.")
            return

        service.deletar_proposta(id)
        print("🗑️ Proposta excluída com sucesso!")
    except ValueError:
        print("❌ ID inválido.")
