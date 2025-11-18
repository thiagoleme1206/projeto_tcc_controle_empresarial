from app.models.projeto_model import Projeto
from app.services.projeto_service import ProjetoService
from datetime import datetime
from app.services.auditoria_service import AuditoriaService

def menu_projetos(usuario):
    service = ProjetoService()
    auditoria = AuditoriaService()

    grupo = usuario.grupo
    acesso_total = grupo in ["financeiro", "ti"]
    consulta_apenas = grupo == "gerencia"

    while True:
        print("\n=== Módulo: Gestão de Projetos ===")

        if acesso_total:
            print("1. Cadastrar novo projeto")
            print("2. Listar projetos")
            print("3. Atualizar projeto")
            print("4. Excluir projeto")
        elif consulta_apenas:
            print("1. Listar projetos")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1" and acesso_total:
            try:
                while True:
                    tipo = input("Tipo de projeto: ").strip()
                    if not tipo:
                        print("❌ Tipo de projeto é obrigatório.")
                    elif tipo.isnumeric():
                        print("❌ Tipo de projeto não pode conter apenas números.")
                    else:
                        break
                id_cliente = int(input("ID do cliente: "))
                cliente = service.cliente_repo.buscar_por_id(id_cliente)

                if not cliente:
                    print("❌ Cliente não encontrado. Verifique o ID.")
                    continue

                cliente_nome = cliente.nome
                cliente_cpf_cnpj = cliente.cpf_cnpj
                data_os = input("Data da OS (AAAA-MM-DD): ")
                data_os = datetime.strptime(data_os, "%Y-%m-%d").date()

                numero_proposta = input("Número da proposta: ").strip()
                if not numero_proposta:
                    print("❌ Número da proposta é obrigatório.")
                    continue
                while True:
                    valor_servico_input = input("Valor do serviço: ").strip()
                    if not valor_servico_input:
                        print("❌ Valor do serviço é obrigatório.")
                        continue
                    try:
                        valor_servico = float(valor_servico_input)
                        break
                    except ValueError:
                        print("❌ Insira um valor numérico válido para o serviço.")
                # ✅ Valor do material (obrigatório e numérico)
                while True:
                    valor_material_input = input("Valor do material: ").strip()
                    if not valor_material_input:
                        print("❌ Valor do material é obrigatório.")
                        continue
                    try:
                        valor_material = float(valor_material_input)
                        break
                    except ValueError:
                        print("❌ Insira um valor numérico válido para o material.")
                total = valor_servico + valor_material
                endereco_obra = input("Endereço da obra: ").strip()
                cidade_obra = input("Cidade da obra: ").strip()
                estado_obra = input("Estado (UF): ").strip().upper()
                contato = input("Contato: ").strip()
                nome_responsavel = usuario.nome
                status_opcoes = {
                    "1": "Em andamento",
                    "2": "Finalizado",
                    "3": "Cancelado",
                    "4": "Em análise de proposta",
                    "5": "Pausado"
                }

                while True:
                    print("\nStatus disponíveis:")
                    for k, v in status_opcoes.items():
                        print(f"{k}. {v}")
                    
                    escolha = input("Escolha o status (número): ").strip()
                    status = status_opcoes.get(escolha)

                    if status:
                        break
                    else:
                        print("❌ Opção inválida. Tente novamente.")

                # ✅ Cria o objeto Projeto fora do while
                projeto = Projeto(
                    numero_os=None,  # número gerado automaticamente no banco
                    tipo=tipo,
                    id_cliente=id_cliente,
                    cliente_nome=cliente_nome,
                    cliente_cpf_cnpj=cliente_cpf_cnpj,
                    data_os=data_os,
                    numero_proposta=numero_proposta,
                    valor_servico=valor_servico,
                    valor_material=valor_material,
                    total=total,
                    endereco_obra=endereco_obra,
                    cidade_obra=cidade_obra,
                    estado_obra=estado_obra,
                    contato=contato,
                    nome_responsavel=nome_responsavel,
                    status=status
                )

                # ✅ Agora sim, cria no banco e mostra o número da OS
                numero_os = service.criar_projeto(projeto)
                print(f"✅ Projeto cadastrado com sucesso. Número OS: {numero_os}")
                auditoria.registrar_acao(
                usuario.login,
                "INSERT",
                "projetos",
                f"Projeto cadastrado - OS {numero_os}, Cliente '{cliente_nome}'"
                )

            except Exception as e:
                print(f"❌ Erro ao cadastrar projeto: {e}")

        elif opcao == "1" and consulta_apenas or opcao == "2":
            projetos = service.listar_projetos()
            if not projetos:
                print("❌ Nenhum projeto encontrado.")
            else:
                for p in projetos:
                    print(f"[OS {p.numero_os}] {p.tipo} | Cliente: {p.cliente_nome} | Data: {p.data_os} | Status: {p.status}")

        elif opcao == "3" and acesso_total:
            try:
                numero_os = int(input("Número da OS do projeto a atualizar: "))
                projeto = service.buscar_por_os(numero_os)

                if not projeto:
                    print("❌ Projeto não encontrado.")
                    continue

                projeto.numero_os = numero_os

                print(f"Editando projeto: OS {numero_os} | Cliente: {projeto.cliente_nome}")

                # Novo tipo com validação
                while True:
                    tipo = input(f"Tipo: ").strip() or projeto.tipo
                    if tipo.isnumeric():
                        print("❌ Tipo de projeto não pode conter apenas números.")
                    else:
                        break

                numero_proposta = input(f"Nº Proposta: ").strip() or projeto.numero_proposta
                valor_servico = float(input(f"Valor Serviço: ") or projeto.valor_servico)
                valor_material = float(input(f"Valor Material: ") or projeto.valor_material)
                endereco_obra = input(f"Endereço: ").strip() or projeto.endereco_obra
                cidade_obra = input(f"Cidade: ").strip() or projeto.cidade_obra
                estado_obra = input(f"Estado: ").strip().upper() or projeto.estado_obra
                contato = input(f"Contato: ").strip() or projeto.contato
                nome_responsavel = projeto.nome_responsavel  # Mantém o valor atual

                status_opcoes = {
                    "1": "Em andamento",
                    "2": "Finalizado",
                    "3": "Cancelado",
                    "4": "Em análise de proposta",
                    "5": "Pausado"
                }

                while True:
                    print("\nStatus disponíveis:")
                    for k, v in status_opcoes.items():
                        print(f"{k}. {v}")
                    status_input = input(f"Escolha o novo status: ").strip()
                    if not status_input:
                        status = projeto.status
                        break
                    status = status_opcoes.get(status_input)
                    if status:
                        break
                    else:
                        print("❌ Opção inválida. Tente novamente.")

                # Atualização dos dados no objeto
                projeto.tipo = tipo
                projeto.numero_proposta = numero_proposta
                projeto.valor_servico = valor_servico
                projeto.valor_material = valor_material
                projeto.total = valor_servico + valor_material
                projeto.endereco_obra = endereco_obra
                projeto.cidade_obra = cidade_obra
                projeto.estado_obra = estado_obra
                projeto.contato = contato
                projeto.nome_responsavel = nome_responsavel
                projeto.status = status

                service.atualizar_projeto(projeto)
                print("✅ Projeto atualizado com sucesso.")
                auditoria.registrar_acao(
                usuario.login,
                "UPDATE",
                "projetos",
                f"Projeto OS {numero_os} atualizado."
                )

            except Exception as e:
                print(f"❌ Erro ao atualizar: {e}")

        elif opcao == "4" and acesso_total:
            try:
                numero_os = int(input("Número da OS a excluir: "))
                confirmado = input("Tem certeza que deseja excluir? (s/n): ").lower()
                if confirmado == "s":
                    sucesso = service.excluir_projeto(numero_os)
                    if sucesso:
                        print("🗑️ Projeto excluído com sucesso.")
                        auditoria.registrar_acao(
                        usuario.login,
                        "DELETE",
                        "projetos",
                        f"Projeto OS {numero_os} excluído."
                    )
                    else:
                        print("❌ Projeto não encontrado.")
                else:
                    print("🚫 Exclusão cancelada.")
            except ValueError:
                print("❌ Número da OS inválido.")

        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")