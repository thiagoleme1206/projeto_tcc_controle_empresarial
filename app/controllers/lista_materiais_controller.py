from app.services.lista_materiais_service import ListaMateriaisService
from app.models.lista_materiais_model import ItemListaMateriais
from app.repositories.produto_repository import ProdutoRepository

def menu_lista_materiais(usuario):
    service = ListaMateriaisService()

    while True:
        print("\n=== Lista de Materiais ===")
        print("1. Criar nova lista")
        print("2. Listar listas existentes")
        print("3. Detalhar uma lista")
        print("4. Excluir uma lista")
        print("5. Alterar lista existente")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            os_ref = input("OS de referência: ")
            observacao = input("Observação: ")
            itens = []

            while True:
                print("\nAdicionando item à lista...")
                produto_id = int(input("ID do produto: "))
                produto_repo = ProdutoRepository()
                produto = produto_repo.buscar_por_id(produto_id)

                if not produto:
                    print("❌ Produto não encontrado.")
                    continue

                nome_produto = produto.nome
                unidade = produto.unidade
                preco_unitario = produto.preco_unitario
                quantidade = float(input("Quantidade: "))
                obs_item = input("Observação (opcional): ")

                item = ItemListaMateriais(
                    id=None,
                    id_lista=None,
                    produto_id=produto_id,
                    nome_produto=nome_produto,
                    quantidade=quantidade,
                    unidade=unidade,
                    preco_unitario=preco_unitario,
                    observacao=obs_item
                )
                itens.append(item)

                continuar = input("Adicionar outro item? (s/n): ").lower()
                if continuar != "s":
                    break

            id_lista = service.criar_lista(os_ref, usuario.nome, observacao, itens)
            print(f"✅ Lista criada com ID {id_lista}")

        elif opcao == "2":
            listas = service.listar_listas()
            for lista in listas:
                print(f"[{lista.id_lista}] OS: {lista.os_referencia} | Responsável: {lista.responsavel} | Criado em: {lista.data_criacao}")

        elif opcao == "3":
            id_lista = int(input("ID da lista: "))
            itens = service.buscar_itens(id_lista)
            if itens:
                for item in itens:
                    print(f"ID Item: {item.id} | Produto: {item.nome_produto} | Qtde: {item.quantidade} {item.unidade} | R$ {item.preco_unitario}")
            else:
                print("❌ Nenhum item encontrado.")

        elif opcao == "4":
            id_lista = int(input("ID da lista a excluir: "))
            service.excluir_lista(id_lista)
            print("🗑️ Lista excluída com sucesso.")

        elif opcao == "5":
            alterar_lista(service)

        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")

def lista_existe(service, id_lista):
            listas = service.listar_listas()
            return any(lista.id_lista == id_lista for lista in listas)

def alterar_lista(service):
    from app.repositories.produto_repository import ProdutoRepository
    from app.models.lista_materiais_model import ItemListaMateriais

    print("\n=== Alterar Lista de Materiais ===")
    print("1. Adicionar item")
    print("2. Remover item")
    print("3. Alterar quantidade de item")
    print("4. Alterar preço unitário de item")
    print("0. Voltar")
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        id_lista = int(input("ID da lista que deseja alterar: "))

        if not lista_existe(service, id_lista):
            print(f"❌ A lista com ID {id_lista} não existe.")
            print("🔍 Listas disponíveis:")
            listas = service.listar_listas()
            for lista in listas:
                print(f"- ID {lista.id_lista}: OS {lista.os_referencia}")
            return

        produto_id = int(input("ID do produto: "))
        produto_repo = ProdutoRepository()
        produto = produto_repo.buscar_por_id(produto_id)

        if not produto:
            print("❌ Produto não encontrado.")
            return

        nome_produto = produto.nome
        unidade = produto.unidade
        quantidade = float(input("Quantidade: "))

        # Verifica estoque disponível
        if quantidade > produto.quantidade:
            print(f"❌ Estoque insuficiente! Disponível: {produto.quantidade} {unidade}")
            return

        preco_unitario = float(input("Preço unitário: "))
        obs_item = input("Observação (opcional): ")

        novo_item = ItemListaMateriais(
            id=None,
            id_lista=id_lista,
            produto_id=produto_id,
            nome_produto=nome_produto,
            quantidade=quantidade,
            unidade=unidade,
            preco_unitario=preco_unitario,
            observacao=obs_item
        )

        service.repo.adicionar_item(novo_item)
        produto_repo.atualizar_quantidade(produto_id, produto.quantidade - quantidade)
        print("✅ Item adicionado com sucesso e estoque atualizado!")

    elif opcao == "2":
        id_lista = int(input("ID da lista: "))

        if not lista_existe(service, id_lista):
            print(f"❌ A lista com ID {id_lista} não existe.")
            print("🔍 Listas disponíveis:")
            listas = service.listar_listas()
            for lista in listas:
                print(f"- ID {lista.id_lista}: OS {lista.os_referencia}")
            return

        id_item = int(input("ID do item a remover: "))
        itens = service.buscar_itens(id_lista)

        item_encontrado = next((item for item in itens if item.id == id_item), None)

        if not item_encontrado:
            print(f"❌ Item com ID {id_item} não encontrado na lista {id_lista}.")
            print("🔍 Itens nesta lista:")
            for item in itens:
                print(f"- ID {item.id}: {item.nome_produto} ({item.quantidade} {item.unidade})")
            return

        service.remover_item(id_item)
        print("🗑️ Item removido com sucesso.")

    elif opcao == "3":
        id_lista = int(input("ID da lista: "))

        if not lista_existe(service, id_lista):
            print(f"❌ A lista com ID {id_lista} não existe.")
            print("🔍 Listas disponíveis:")
            listas = service.listar_listas()
            for lista in listas:
                print(f"- ID {lista.id_lista}: OS {lista.os_referencia}")
            return

        id_item = int(input("ID do item que deseja alterar: "))
        itens = service.buscar_itens(id_lista)
        item_encontrado = next((item for item in itens if item.id == id_item), None)

        if not item_encontrado:
            print(f"❌ Item com ID {id_item} não encontrado na lista {id_lista}.")
            print("🔍 Itens nesta lista:")
            for item in itens:
                print(f"- ID {item.id}: {item.nome_produto} ({item.quantidade} {item.unidade})")
            return

        nova_qtde = float(input("Nova quantidade: "))
        service.atualizar_quantidade(id_item, nova_qtde)
        print("✅ Quantidade atualizada.")

    elif opcao == "4":
        id_lista = int(input("ID da lista: "))

        if not lista_existe(service, id_lista):
            print(f"❌ A lista com ID {id_lista} não existe.")
            print("🔍 Listas disponíveis:")
            listas = service.listar_listas()
            for lista in listas:
                print(f"- ID {lista.id_lista}: OS {lista.os_referencia}")
            return

        id_item = int(input("ID do item que deseja alterar: "))
        itens = service.buscar_itens(id_lista)
        item_encontrado = next((item for item in itens if item.id == id_item), None)

        if not item_encontrado:
            print(f"❌ Item com ID {id_item} não encontrado na lista {id_lista}.")
            print("🔍 Itens nesta lista:")
            for item in itens:
                print(f"- ID {item.id}: {item.nome_produto} ({item.quantidade} {item.unidade})")
            return

        novo_valor = float(input("Novo preço unitário: "))
        service.atualizar_preco(id_item, novo_valor)
        print("✅ Preço unitário atualizado.")

    elif opcao == "0":
        return
    else:
        print("❌ Opção inválida.")

