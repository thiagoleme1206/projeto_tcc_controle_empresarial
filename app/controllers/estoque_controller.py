from app.services.estoque_service import EstoqueService
from app.services.auditoria_service import AuditoriaService

def menu_estoque(usuario):
    auditoria = AuditoriaService()
    service = EstoqueService()
    grupo = usuario.grupo
    permissoes_grupo_total = grupo == "ti"

    print("\n=== Módulo de Estoque ===")

    if grupo == "estoquista" or permissoes_grupo_total:
        print("1. Listar produtos")
        print("2. Cadastrar novo produto")
        print("3. Atualizar produto")
        print("4. Excluir produto")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            listar_produtos(service, usuario,auditoria)
        elif opcao == "2":
            cadastrar_produto(service, usuario,auditoria)
        elif opcao == "3":
            atualizar_produto(service, usuario,auditoria)
        elif opcao == "4":
            deletar_produto(service, usuario,auditoria)
        elif opcao == "0":
            return
        else:
            print("❌ Opção inválida.")
    else:
        print("⚠️ Você só tem permissão para consultar o estoque.")
        print("1. Listar produtos")
        print("0. Voltar")
        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            listar_produtos(service)

# As funções abaixo estão FORA da menu_estoque, mas no mesmo arquivo

def listar_produtos(service):
    produtos = service.listar_produtos()
    print("\n📦 Lista de Produtos:\n")
    for p in produtos:
        print(f"ID: {p.id} | Nome: {p.nome} | Quantidade: {p.quantidade} {p.unidade} | Preço: R${p.preco_unitario:.2f}")

def cadastrar_produto(service, usuario, auditoria):
    print("\n=== Cadastrar Novo Produto ===")
    nome = input("Nome: ")
    descricao = input("Descrição: ")
    quantidade = int(input("Quantidade: "))
    unidade = input("Unidade: ")
    preco = float(input("Preço unitário: "))
    estoque_min = int(input("Estoque mínimo: "))
    
    service.cadastrar_produto(nome, descricao, quantidade, unidade, preco, estoque_min)
    print("✅ Produto cadastrado com sucesso!")

    auditoria.registrar_acao(
        usuario.login,
        "INSERT",
        "estoque",
        f"Produto cadastrado: {nome} (Qtd: {quantidade}, Preço: R${preco:.2f})"
    )

def atualizar_produto(service, usuario, auditoria):
    print("\n=== Atualizar Produto ===")
    try:
        id = int(input("ID do produto: "))
        produto = service.repo.buscar_por_id(id)

        if not produto:
            print("❌ Produto não encontrado.")
            return

        nome = input("Nome: ")
        descricao = input("Descrição: ")
        quantidade = int(input("Quantidade: "))
        unidade = input("Unidade: ")
        preco_unitario = float(input("Preço unitário: "))
        estoque_minimo = int(input("Estoque mínimo: "))

        service.atualizar_produto(id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo)
        print("✅ Produto atualizado com sucesso!")

        auditoria.registrar_acao(
            usuario.login,
            "UPDATE",
            "estoque",
            f"Produto ID {id} atualizado: {nome}"
        )
    except ValueError:
        print("❌ Valor inválido. Verifique os campos e tente novamente.")
    except ValueError:
        print("❌ Valor inválido. Verifique os campos e tente novamente.")

def deletar_produto(service, usuario, auditoria):
    print("\n=== Deletar Produto ===")
    try:
        id = int(input("ID do produto: "))
        produto = service.repo.buscar_por_id(id)

        if not produto:
            print("❌ Produto não encontrado.")
            return

        service.deletar_produto(id)
        print("🗑️ Produto deletado com sucesso!")

        auditoria.registrar_acao(
            usuario.login,
            "DELETE",
            "estoque",
            f"Produto ID {id} deletado: {produto.nome}"
        )
    except ValueError:
        print("❌ ID inválido. Digite um número.")

