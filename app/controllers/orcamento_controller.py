from app.models.orcamento_model import Orcamento
from app.services.orcamento_service import OrcamentoService
from datetime import datetime

def menu_orcamentos(usuario):
    grupo = usuario.grupo
    acesso_total = grupo in ["financeiro", "ti"]
    leitura_apenas = grupo == "gerencia"

    if not (acesso_total or leitura_apenas):
        print("🚫 Você não tem permissão para acessar o módulo de orçamentos.")
        return

    service = OrcamentoService()

    while True:
        print("\n=== Módulo: Gestão de Orçamentos ===")
        if acesso_total:
            print("1. Cadastrar novo orçamento")
            print("2. Listar orçamentos")
            print("3. Buscar por número de OS")
            print("4. Atualizar orçamento")
            print("5. Excluir orçamento")
        elif leitura_apenas:
            print("1. Listar orçamentos")
            print("2. Buscar por número de OS")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        try:
            if opcao == "1" and acesso_total:
                numero_os = int(input("Número da OS do projeto: "))

                # ✅ Validação antes de criar
                if not service.validar_os_existe(numero_os):
                    print("❌ OS não localizada no sistema.")
                    continue

                data_str = input("Data do orçamento (AAAA-MM-DD): ")
                data_orcamento = datetime.strptime(data_str, "%Y-%m-%d").date()

                def get_valor(msg):
                    val = input(f"{msg}: ").strip()
                    try:
                        return float(val) if val else 0.0
                    except ValueError:
                        print("❌ Valor inválido, usando 0 como padrão.")
                        return 0.0

                orcamento = Orcamento(
                    numero_os=numero_os,
                    data_orcamento=data_orcamento,
                    mao_de_obra=get_valor("Mão de obra"),
                    alimentacao=get_valor("Alimentação"),
                    hospedagem=get_valor("Hospedagem"),
                    viagem=get_valor("Viagem"),
                    seguranca_trabalho=get_valor("Segurança do trabalho"),
                    material=get_valor("Material"),
                    equipamento=get_valor("Equipamento"),
                    andaime=get_valor("Andaime"),
                    documentacao=get_valor("Documentação"),
                    outros=get_valor("Outros")
                )

                id_gerado = service.criar_orcamento(orcamento)
                print(f"✅ Orçamento cadastrado com sucesso. ID: {id_gerado}")

            elif opcao == "2":
                orcamentos = service.listar_orcamentos()
                if not orcamentos:
                    print("📭 Nenhum orçamento encontrado.")
                else:
                    for o in orcamentos:
                        print(f"ID {o.id_orcamento} | OS {o.numero_os} | Data: {o.data_orcamento} | Total: R$ {o.total:.2f}")

            elif opcao == "3":
                numero_os = int(input("Número da OS para buscar: "))
                orcamento = service.buscar_por_os(numero_os)
                if orcamento:
                    print(f"\n🧾 Orçamento encontrado (ID {orcamento.id_orcamento}):")
                    print(f"Data: {orcamento.data_orcamento} | Total: R$ {orcamento.total:.2f}")
                else:
                    print("❌ Orçamento não encontrado.")

            elif opcao == "4" and acesso_total:
                id_orcamento = int(input("ID do orçamento a atualizar: "))
                orcamento = service.buscar_por_id(id_orcamento)
                if not orcamento:
                    print("❌ Orçamento não encontrado.")
                    continue

                def atualizar_valor(campo, valor_atual):
                    entrada = input(f"{campo} [{valor_atual}]: ").strip()
                    try:
                        return float(entrada) if entrada else 0.0
                    except ValueError:
                        print("❌ Valor inválido, mantendo 0.")
                        return 0.0

                print("🔄 Atualize os campos (pressione Enter para manter):")
                orcamento.mao_de_obra = atualizar_valor("Mão de obra", orcamento.mao_de_obra)
                orcamento.alimentacao = atualizar_valor("Alimentação", orcamento.alimentacao)
                orcamento.hospedagem = atualizar_valor("Hospedagem", orcamento.hospedagem)
                orcamento.viagem = atualizar_valor("Viagem", orcamento.viagem)
                orcamento.seguranca_trabalho = atualizar_valor("Segurança do trabalho", orcamento.seguranca_trabalho)
                orcamento.material = atualizar_valor("Material", orcamento.material)
                orcamento.equipamento = atualizar_valor("Equipamento", orcamento.equipamento)
                orcamento.andaime = atualizar_valor("Andaime", orcamento.andaime)
                orcamento.documentacao = atualizar_valor("Documentação", orcamento.documentacao)
                orcamento.outros = atualizar_valor("Outros", orcamento.outros)

                service.atualizar_orcamento(orcamento)
                print("✅ Orçamento atualizado com sucesso.")

            elif opcao == "5" and acesso_total:
                id_orcamento = int(input("ID do orçamento a excluir: "))
                confirm = input("Tem certeza? (s/n): ").lower()
                if confirm == "s":
                    if service.excluir_orcamento(id_orcamento):
                        print("🗑️ Orçamento excluído.")
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
