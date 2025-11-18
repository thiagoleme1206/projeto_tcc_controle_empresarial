# app/controllers/menu_auditoria_controller.py

from app.services.auditoria_service import AuditoriaService
from datetime import datetime

def menu_auditoria(usuario_logado):
    if usuario_logado.grupo != "ti":
        print("\n\u274c Acesso negado. M\u00f3dulo restrito ao grupo TI.")
        return

    service = AuditoriaService()

    while True:
        print("\n=== M\u00f3dulo de Auditoria ===")
        print("1. Consultar logs por data")
        print("2. Consultar logs por usu\u00e1rio")
        print("0. Voltar")
        opcao = input("Escolha uma op\u00e7\u00e3o: ").strip()

        if opcao == "1":
            data_str = input("Digite a data (DD/MM/AAAA): ").strip()
            try:
                data_formatada = datetime.strptime(data_str, "%d/%m/%Y").date()
                logs = service.consultar_por_data(data_formatada)
                exibir_logs(logs)
            except ValueError:
                print("\u274c Data inv\u00e1lida.")

        elif opcao == "2":
            login = input("Digite o login do usu\u00e1rio: ").strip()
            logs = service.consultar_por_usuario(login)
            exibir_logs(logs)

        elif opcao == "0":
            break
        else:
            print("\u274c Op\u00e7\u00e3o inv\u00e1lida.")

def exibir_logs(logs):
    if not logs:
        print("\nNenhum log encontrado.")
        return

    print("\nLogs encontrados:")
    for log in logs:
        data = log[4].strftime("%d/%m/%Y %H:%M:%S")
        print(f"Usuário: {log[0]} | Ação: {log[1]} | Módulo: {log[2]} | Descrição: {log[3]} | Data: {data}")

