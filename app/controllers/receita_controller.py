from datetime import datetime
from app.models.receita_model import Receita
from app.services.receita_service import ReceitaService
from app.repositories.projeto_repository import ProjetoRepository
from app.repositories.cliente_repository import ClienteRepository
from app.services.auditoria_service import AuditoriaService

def menu_receitas(usuario):
    grupo = usuario.grupo
    acesso_total = grupo in ["financeiro", "ti"]
    leitura_apenas = grupo == "gerencia"
    
    # Depois que o login for validado com sucesso:
    auditoria = AuditoriaService()
    auditoria.registrar_acao(usuario.login, "LOGIN", "login", "Usuário logado no sistema receitas")

    if not (acesso_total or leitura_apenas):
        print("🚫 Você não tem permissão para acessar o módulo de receitas.")
        return

    service = ReceitaService()
    projeto_repo = ProjetoRepository()
    cliente_repo = ClienteRepository()

    while True:
        print("\n=== Módulo: Gestão de Receitas ===")
        if acesso_total:
            print("1. Cadastrar nova receita")
            print("2. Listar receitas")
            print("3. Buscar por número de OS")
            print("4. Atualizar receita")
            print("5. Excluir receita")
        elif leitura_apenas:
            print("1. Listar receitas")
            print("2. Buscar por número de OS")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        try:
            if opcao == "1" and acesso_total:
                numero_os_str = input("Número da OS: ").strip()
                if not numero_os_str.isdigit():
                    print("❌ Número da OS inválido.")
                    continue
                numero_os = int(numero_os_str)

                projeto = projeto_repo.buscar_por_os(numero_os)
                if not projeto:
                    print("❌ OS não localizada.")
                    continue

                cliente = cliente_repo.buscar_por_id(projeto.id_cliente)
                if not cliente:
                    print("❌ Cliente vinculado à OS não encontrado.")
                    continue

                cliente_nome = cliente.nome

                # Data da receita
                while True:
                    data_str = input("Data da receita (AAAA-MM-DD): ").strip()
                    try:
                        data_receita = datetime.strptime(data_str, "%Y-%m-%d").date()
                        break
                    except ValueError:
                        print("❌ Data inválida. Use o formato correto (AAAA-MM-DD).")

                # NF
                nf = input("Número da nota fiscal (NF): ").strip()
                if not nf or not nf.strip().isdigit():
                    print("❌ Número da nota fiscal inválido. Use apenas números.")
                    continue

                # Valores (apenas um dos dois pode ser preenchido)
                def get_valor_float(msg):
                    val = input(f"{msg}: ").strip()
                    return float(val) if val else 0.0

                valor_servico = get_valor_float("Valor do serviço (preencher apenas um)")
                valor_material = get_valor_float("Valor do material (preencher apenas um)")

                if valor_servico and valor_material:
                    print("❌ Preencha apenas valor do serviço OU valor do material, não ambos.")
                    continue
                if not valor_servico and not valor_material:
                    print("❌ Você deve preencher pelo menos um valor.")
                    continue

                imposto = get_valor_float("Porcentagem de imposto (%)")
                icms = 0.0
                if valor_material:
                    icms = get_valor_float("Porcentagem de ICMS (%)")

                receita = Receita(
                    numero_os_projeto=numero_os,
                    data_receita=data_receita,
                    nf=nf,
                    cliente=cliente_nome,
                    valor_servico=valor_servico,
                    valor_material=valor_material,
                    imposto=imposto,
                    icms=icms
                )

                id_receita = service.criar_receita(receita)
                print(f"✅ Receita cadastrada com sucesso. ID: {id_receita}")

            elif opcao == "2":
                receitas = service.listar_receitas()
                if not receitas:
                    print("📭 Nenhuma receita encontrada.")
                else:
                    for r in receitas:
                        print(f"ID {r.id_receita} | OS {r.numero_os_projeto} | Cliente: {r.cliente} | Total Líquido: R$ {r.valor_liquido:.2f}")

            elif opcao == "3":
                numero_os_str = input("Número da OS para buscar: ").strip()
                if not numero_os_str.isdigit():
                    print("❌ Número da OS inválido.")
                    continue
                numero_os = int(numero_os_str)

                receita = service.buscar_por_os(numero_os)
                if receita:
                    print(f"\n📄 Receita encontrada (ID {receita.id_receita}):")
                    print(f"Data: {receita.data_receita} | Cliente: {receita.cliente} | Total Líquido: R$ {receita.valor_liquido:.2f}")
                else:
                    print("❌ Receita não encontrada.")

            elif opcao == "4" and acesso_total:
                id_str = input("ID da receita a atualizar: ").strip()
                if not id_str.isdigit():
                    print("❌ ID inválido.")
                    continue
                id_receita = int(id_str)

                receita = service.buscar_por_id(id_receita)
                if not receita:
                    print("❌ Receita não encontrada.")
                    continue

                def atualizar_float(campo, atual):
                    entrada = input(f"{campo} [{atual}]: ").strip()
                    return float(entrada) if entrada else atual

                receita.valor_servico = atualizar_float("Valor do serviço", receita.valor_servico)
                receita.valor_material = atualizar_float("Valor do material", receita.valor_material)
                receita.imposto = atualizar_float("Imposto (%)", receita.imposto)
                receita.icms = atualizar_float("ICMS (%)", receita.icms)

                service.atualizar_receita(receita)
                print("✅ Receita atualizada com sucesso.")

            elif opcao == "5" and acesso_total:
                id_str = input("ID da receita a excluir: ").strip()
                if not id_str.isdigit():
                    print("❌ ID inválido.")
                    continue
                id_receita = int(id_str)
                confirm = input("Tem certeza que deseja excluir? (s/n): ").lower()
                if confirm == "s":
                    if service.excluir_receita(id_receita):
                        print("🗑️ Receita excluída com sucesso.")
                    else:
                        print("❌ Não foi possível excluir. Verifique o ID.")
                else:
                    print("🚫 Exclusão cancelada.")

            elif opcao == "0":
                break
            else:
                print("❌ Opção inválida.")

        except Exception as e:
            print(f"❌ Erro: {e}")
