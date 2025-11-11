# app/controllers/relatorio_controller.py

from app.services.relatorio_service import RelatorioService
from app.services.auditoria_service import AuditoriaService  # ✅ Importar auditoria

def menu_relatorios(usuario):
    if usuario.grupo not in ["ti", "gerencia"]:
        print("❌ Acesso negado. Este módulo é restrito à TI e Gerência.")
        return

    auditoria = AuditoriaService()  # ✅ Instanciar serviço de auditoria

    while True:
        print("\n=== Módulo de Relatórios ===")
        print("1. Gerar relatório por número da OS")
        print("0. Voltar")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            numero_os = input("🔎 Digite o número da OS: ")
            try:
                relatorio_service = RelatorioService()
                relatorio_service.gerar_relatorio_por_os(numero_os)

                # ✅ Registrar ação na auditoria
                auditoria.registrar_acao(
                    usuario.login,                # nome do usuário
                    "RELATORIO_GERADO",           # tipo da ação
                    "relatorios",                 # módulo
                    f"Relatório gerado para OS {numero_os}"
                )

            except ValueError as ve:
                print(f"❌ {ve}")
            except Exception as e:
                print(f"❌ Erro inesperado ao gerar o relatório: {e}")
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida.")
