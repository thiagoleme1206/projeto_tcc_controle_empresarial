# app/controllers/cliente_controller.py

from app.services.cliente_service import ClienteService
from app.services.auditoria_service import AuditoriaService

def menu_clientes(usuario):
    service = ClienteService()
    auditoria = AuditoriaService()

    while True:
        print("\n=== Gestão de Clientes ===")
        print("1. Cadastrar novo cliente")
        print("2. Listar clientes")
        print("3. Atualizar cliente")
        print("4. Excluir cliente")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        # ---------------- CADASTRAR CLIENTE ----------------
        if opcao == "1":
            cpf_cnpj = input("CPF ou CNPJ: ").strip()
            nome = input("Nome do cliente: ").strip()

            try:
                service.criar_cliente(cpf_cnpj, nome)
                print("✅ Cliente cadastrado com sucesso.")
                auditoria.registrar_acao(
                    usuario.login,
                    "INSERT",
                    "clientes",
                    f"Cliente cadastrado: {nome} ({cpf_cnpj})"
                )
            except ValueError as e:
                print(f"❌ Erro: {e}")

        # ---------------- LISTAR CLIENTES ----------------
        elif opcao == "2":
            clientes = service.listar_clientes()
            if not clientes:
                print("❌ Nenhum cliente encontrado.")
            else:
                print("\n📋 Lista de Clientes:")
                for c in clientes:
                    print(f"[{c.id_cliente}] {c.nome} | CPF/CNPJ: {c.cpf_cnpj}")

        # ---------------- ATUALIZAR CLIENTE ----------------
        elif opcao == "3":
            try:
                id_cliente = int(input("ID do cliente a atualizar: "))
            except ValueError:
                print("❌ ID inválido.")
                continue

            cliente = service.buscar_cliente(id_cliente)
            if not cliente:
                print("❌ Cliente não encontrado.")
                continue

            print(f"Editando cliente: {cliente.nome} ({cliente.cpf_cnpj})")
            cpf_cnpj = input(f"Novo CPF/CNPJ [{cliente.cpf_cnpj}]: ").strip() or cliente.cpf_cnpj
            nome = input(f"Novo nome [{cliente.nome}]: ").strip() or cliente.nome

            try:
                service.atualizar_cliente(id_cliente, cpf_cnpj, nome)
                print("✅ Cliente atualizado com sucesso.")
                auditoria.registrar_acao(
                    usuario.login,
                    "UPDATE",
                    "clientes",
                    f"Cliente atualizado: {nome} (ID: {id_cliente})"
                )
            except ValueError as e:
                print(f"❌ Erro: {e}")

        # ---------------- EXCLUIR CLIENTE ----------------
        elif opcao == "4":
            try:
                id_cliente = int(input("ID do cliente a excluir: "))
            except ValueError:
                print("❌ ID inválido.")
                continue

            confirmado = input("Tem certeza que deseja excluir? (s/n): ").lower()
            if confirmado == "s":
                resultado = service.excluir_cliente(id_cliente)
                if resultado:
                    print("🗑️ Cliente excluído com sucesso.")
                    auditoria.registrar_acao(
                        usuario.login,
                        "DELETE",
                        "clientes",
                        f"Cliente excluído: ID {id_cliente}"
                    )
                else:
                    print("❌ Cliente não encontrado.")
            else:
                print("🚫 Exclusão cancelada.")

        # ---------------- VOLTAR ----------------
        elif opcao == "0":
            break

        else:
            print("❌ Opção inválida.")
