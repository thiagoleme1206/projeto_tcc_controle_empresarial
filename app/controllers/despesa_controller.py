# app/controllers/despesa_controller.py

from app.models.despesa_model import Despesa
from app.services.despesa_service import DespesaService
from datetime import datetime
from app.database.db_connection import DatabaseConnection

def solicitar_data(msg="Data (AAAA-MM-DD): "):
    while True:
        entrada = input(msg).strip()

        if not entrada:
            print("❌ A data é obrigatória.")
            continue

        try:
            data = datetime.strptime(entrada, "%Y-%m-%d").date()
            return data
        except ValueError:
            print("❌ Formato inválido. Use o formato AAAA-MM-DD.")

def menu_despesas(usuario):
    grupo = usuario.grupo
    acesso_total = grupo in ["financeiro", "ti"]
    leitura_apenas = grupo == "gerencia"

    if not (acesso_total or leitura_apenas):
        print("🚫 Você não tem permissão para acessar o módulo de despesas.")
        return

    service = DespesaService()

    def get_valor_input(label):
        valor = input(f"{label}: ").strip()
        return float(valor) if valor else 0.0

    while True:
        print("\n=== Módulo: Gestão de Despesas ===")
        if acesso_total:
            print("1. Cadastrar nova despesa")
            print("2. Listar despesas")
            print("3. Buscar por número de OS")
            print("4. Atualizar despesa")
            print("5. Excluir despesa")
        elif leitura_apenas:
            print("1. Listar despesas")
            print("2. Buscar por número de OS")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        try:
            if opcao == "1" and acesso_total:
                numero_os_input = input("Número da OS do projeto: ").strip()
                if not numero_os_input.isdigit():
                    print("❌ Número da OS inválido.")
                    return
                numero_os = int(numero_os_input)
                conn = DatabaseConnection().get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM projetos WHERE numero_os = %s", (numero_os,))
                if not cursor.fetchone():
                    print("❌ OS não localizada.")
                    return
                data_orcamento = solicitar_data("Data da despesa (AAAA-MM-DD): ")
                observacao = input("Observações: ").strip()

                despesa = Despesa(
                    numero_os_projeto=numero_os,
                    data_despesa=data_orcamento,
                    observacao=observacao,
                    mao_de_obra=get_valor_input("Mão de obra"),
                    alimentacao=get_valor_input("Alimentação"),
                    hospedagem=get_valor_input("Hospedagem"),
                    viagem=get_valor_input("Viagem"),
                    seguranca_trabalho=get_valor_input("Segurança do trabalho"),
                    material=get_valor_input("Material"),
                    equipamento=get_valor_input("Equipamento"),
                    andaime=get_valor_input("Andaime"),
                    documentacao=get_valor_input("Documentação"),
                    outros=get_valor_input("Outros")
                )

                id_despesa = service.criar_despesa(despesa)
                print(f"✅ Despesa cadastrada com sucesso. ID: {id_despesa}")

            elif opcao == "2":
                despesas = service.listar_despesas()
                if not despesas:
                    print("📭 Nenhuma despesa encontrada.")
                else:
                    for d in despesas:
                        print(f"ID {d.id_despesa} | OS {d.numero_os_projeto} | Data: {d.data_despesa} | Total: R$ {d.total:.2f}")

            elif opcao == "3":
                entrada = input("Número da OS para buscar: ").strip()

                if not entrada.isdigit():
                    print("❌ Número da OS inválido. Insira apenas números.")
                    return  # ou continue, se estiver dentro de um loop

                numero_os = int(entrada)
                despesa = service.buscar_por_os(numero_os)
                if despesa:
                    print(f"\n📄 Despesa encontrada (ID {despesa.id_despesa}):")
                    print(f"Data: {despesa.data_despesa} | Total: R$ {despesa.total:.2f}")
                else:
                    print("❌ Despesa não encontrada.")

            elif opcao == "4" and acesso_total:
                entrada = input("ID da despesa a atualizar: ").strip()
                if not entrada.isdigit():
                    print("❌ ID inválido. Insira apenas números.")
                    return  # ou continue, se estiver dentro de um loop

                id_despesa = int(entrada)
                despesa = service.buscar_por_id(id_despesa)
                if not despesa:
                    print("❌ Despesa não encontrada.")
                    continue

                print("🔁 Atualize os valores (pressione Enter para manter):")

                def atualizar_valor(campo, valor_atual):
                    entrada = input(f"{campo} [{valor_atual}]: ").strip()
                    return float(entrada) if entrada else valor_atual

                despesa.mao_de_obra = atualizar_valor("Mão de obra", despesa.mao_de_obra)
                despesa.alimentacao = atualizar_valor("Alimentação", despesa.alimentacao)
                despesa.hospedagem = atualizar_valor("Hospedagem", despesa.hospedagem)
                despesa.viagem = atualizar_valor("Viagem", despesa.viagem)
                despesa.seguranca_trabalho = atualizar_valor("Segurança do trabalho", despesa.seguranca_trabalho)
                despesa.material = atualizar_valor("Material", despesa.material)
                despesa.equipamento = atualizar_valor("Equipamento", despesa.equipamento)
                despesa.andaime = atualizar_valor("Andaime", despesa.andaime)
                despesa.documentacao = atualizar_valor("Documentação", despesa.documentacao)
                despesa.outros = atualizar_valor("Outros", despesa.outros)

                service.atualizar_despesa(despesa)
                print("✅ Despesa atualizada com sucesso.")

            elif opcao == "5" and acesso_total:
                entrada = input("ID da despesa a excluir: ").strip()
                if not entrada.isdigit():
                    print("❌ ID inválido. Insira apenas números.")
                    return  # ou continue, se estiver dentro de um loop

                id_despesa = int(entrada)
                confirm = input("Tem certeza que deseja excluir? (s/n): ").lower()
                if confirm == "s":
                    if service.excluir_despesa(id_despesa):
                        print("🗑️ Despesa excluída com sucesso.")
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
