# app/controllers/login_controller.py

from app.services.auth_service import AuthService
from app.services.auditoria_service import AuditoriaService

def exibir_menu_login():
    auth = AuthService()
    auditoria = AuditoriaService()  # ✅ Instancia o serviço de auditoria

    print("=== Login ===")
    login = input("Login: ").strip()
    senha = input("Senha: ").strip()

    usuario = auth.autenticar(login, senha)

    if usuario:
        print(f"✅ Bem-vindo, {usuario.nome} ({usuario.grupo})")

        # ✅ Registrar sucesso de login
        auditoria.registrar_acao(
            usuario.login,
            "LOGIN",
            "autenticacao",
            f"Usuário '{usuario.login}' autenticado com sucesso."
        )

        return usuario  # devolve o usuário autenticado

    else:
        print("❌ Login inválido ou usuário inativo.")

        # ✅ Registrar tentativa de login falha
        auditoria.registrar_acao(
            login,
            "LOGIN_FALHOU",
            "autenticacao",
            f"Tentativa de login falhou para o usuário '{login}'."
        )
