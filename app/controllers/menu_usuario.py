# app/controllers/menu_usuario.py

from app.services.usuario_service import UsuarioService
from app.services.auditoria_service import AuditoriaService

def menu_usuario(logado):
    if logado.grupo != "ti":
        print("❌ Acesso negado. Módulo restrito ao grupo TI.")
        return

    service = UsuarioService()
    auditoria = AuditoriaService()

    while True:
        print("\n=== Módulo de Gestão de Usuários ===")
        print("1. Criar novo usuário")
        print("2. Alterar usuário")
        print("3. Ativar/Inativar usuário")
        print("4. Consultar usuários")
        print("5. Excluir usuário")
        print("0. Voltar")
        
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            while True:
                nome = input("Nome: ").strip()
                if not nome:
                    print("❌ Nome não pode ser vazio.")
                    continue

                login = input("Login: ").strip()
                if not login:
                    print("❌ Login não pode ser vazio.")
                    continue

                senha = input("Senha: ").strip()
                if not senha:
                    print("❌ Senha não pode ser vazia.")
                    continue

                confirmar = input("Confirmar senha: ").strip()
                if senha != confirmar:
                    print("❌ Senhas não conferem.")
                    continue

                print("\nSelecione o grupo do usuário:")
                grupos = ["estoquista", "vendedor", "engenheiro", "financeiro", "gerencia", "ti"]
                for idx, g in enumerate(grupos, 1):
                    print(f"{idx}. {g}")
                idx_grupo = input("Grupo: ").strip()
                if not idx_grupo.isdigit() or not (1 <= int(idx_grupo) <= len(grupos)):
                    print("❌ Grupo inválido.")
                    continue
                grupo = grupos[int(idx_grupo) - 1]

                service.criar_usuario(nome, login, senha, grupo)
                print("✅ Usuário criado com sucesso.")
                auditoria.registrar_acao(
                logado.login,
                "INSERT",
                "usuarios",
                f"Usuário '{login}' criado no grupo '{grupo}'."
                )
                break

        elif opcao == "2":
            login = input("Login do usuário a alterar: ").strip()

            # Verifica se o usuário existe antes de tentar qualquer alteração
            usuario_existente = service.buscar_usuario_por_login(login)
            if not usuario_existente:
                print("❌ Usuário não encontrado.")
                continue  # Volta ao menu

            print("Campos que podem ser alterados:")
            print("1. Nome")
            print("2. Grupo")
            print("3. Senha")
            campo = input("Escolha o campo: ").strip()

            if campo == "1":
                novo_nome = input("Novo nome: ").strip()
                service.alterar_usuario(login, nome=novo_nome)
                print("✅ Nome alterado com sucesso.")
                auditoria.registrar_acao(
                logado.login,
                "UPDATE",
                "usuarios",
                f"Nome do usuário '{login}' alterado para '{novo_nome}'."
                )

            elif campo == "2":
                print("\nSelecione o novo grupo:")
                grupos = ["estoquista", "vendedor", "engenheiro", "financeiro", "gerencia", "ti"]
                for idx, g in enumerate(grupos, 1):
                    print(f"{idx}. {g}")
                idx_grupo = input("Grupo: ").strip()
                if not idx_grupo.isdigit() or not (1 <= int(idx_grupo) <= len(grupos)):
                    print("❌ Grupo inválido.")
                    continue
                novo_grupo = grupos[int(idx_grupo) - 1]
                service.alterar_usuario(login, grupo=novo_grupo)
                print("✅ Grupo alterado com sucesso.")
                auditoria.registrar_acao(
                logado.login,
                "UPDATE",
                "usuarios",
                f"Nome do usuário '{login}' alterado para '{novo_grupo}'."
                )

            elif campo == "3":
                nova_senha = input("Nova senha: ").strip()
                confirmar = input("Confirmar senha: ").strip()
                if nova_senha != confirmar:
                    print("❌ Senhas não conferem.")
                    continue
                service.alterar_usuario(login, senha=nova_senha)
                print("✅ Senha alterada com sucesso.")
                auditoria.registrar_acao(
                logado.login,
                "UPDATE",
                "usuarios",
                f"Senha do usuário '{login}' foi atualizada."
                )

            else:
                print("❌ Opção inválida.")


        elif opcao == "3":
            login = input("Login do usuário: ").strip()

            usuario_existente = service.buscar_usuario_por_login(login)
            if not usuario_existente:
                print("❌ Usuário não encontrado.")
                continue

            print("\n1. Ativar usuário")
            print("2. Inativar usuário")
            escolha = input("Escolha uma opção: ").strip()

            if escolha == "1":
                ativo = True
            elif escolha == "2":
                ativo = False
            else:
                print("❌ Opção inválida.")
                continue

            service.ativar_inativar_usuario(login, ativo)
            print("✅ Status do usuário atualizado.")
            status = "ativado" if ativo else "inativado"
            auditoria.registrar_acao(
                logado.login,
                "UPDATE",
                "usuarios",
                f"Usuário '{login}' foi {status}."
            )

        elif opcao == "4":
            print("\n=== Filtros disponíveis ===")
            print("1. Somente ativos")
            print("2. Por nome")
            print("3. Por login")
            print("4. Por grupo")
            print("0. Voltar")

            filtro = input("Escolha o filtro: ").strip()

            if filtro == "1":
                usuarios = service.consultar_usuarios(ativo=True)
            elif filtro == "2":
                nome = input("Digite parte do nome: ").strip()
                usuarios = service.consultar_usuarios(nome=nome)
            elif filtro == "3":
                login = input("Digite parte do login: ").strip()
                usuarios = service.consultar_usuarios(login=login)
            elif filtro == "4":
                print("\nSelecione o grupo:")
                grupos = ["estoquista", "vendedor", "engenheiro", "financeiro", "gerencia", "ti", "inativos"]
                for idx, g in enumerate(grupos, 1):
                    print(f"{idx}. {g}")
                idx_grupo = input("Grupo: ").strip()
                if not idx_grupo.isdigit() or not (1 <= int(idx_grupo) <= len(grupos)):
                    print("❌ Grupo inválido.")
                    continue
                grupo = grupos[int(idx_grupo) - 1]
                usuarios = service.consultar_usuarios(grupo=grupo)
            elif filtro == "0":
                continue
            else:
                print("❌ Opção inválida.")
                continue

            print("\n📋 Usuários encontrados:")
            for u in usuarios:
                status = "Ativo" if u[5] else "Inativo"
                print(f"- ID: {u[0]} | Nome: {u[1]} | Login: {u[2]} | Grupo: {u[4]} | Status: {status}")

        elif opcao == "5":
            login = input("Login do usuário a excluir: ").strip()

            usuario_existente = service.buscar_usuario_por_login(login)
            if not usuario_existente:
                print("❌ Usuário não encontrado.")
                continue

            while True:
                confirmacao = input(f"Tem certeza que deseja excluir o usuário '{login}'? (s/n): ").strip().lower()
                if confirmacao in ["s", "n"]:
                    break
                else:
                    print("❌ Opção inválida. Digite 's' para sim ou 'n' para não.")

            if confirmacao == "s":
                try:
                    service.excluir_usuario(login)
                    print("✅ Usuário marcado como inativo com grupo 'inativos'.")
                    auditoria.registrar_acao(
                    logado.login,
                    "DELETE",
                    "usuarios",
                    f"Usuário '{login}' foi marcado como inativo (exclusão lógica)."
                    )
                except Exception as e:
                    print(f"❌ Erro: {e}")
            else:
                print("❎ Operação cancelada.")
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")
