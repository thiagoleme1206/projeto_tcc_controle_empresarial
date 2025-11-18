import bcrypt
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario_model import Usuario


class AuthService:

    def __init__(self):
        self.repo = UsuarioRepository()

    # ============================
    #           LOGIN
    # ============================
    def autenticar(self, login: str, senha: str):
        """
        Autentica um usuário. Retorna o objeto Usuario se sucesso,
        retorna None se falhar.
        """
        if not login or not senha:
            return None

        usuario = self.repo.buscar_por_login(login)

        if not usuario:
            return None

        if not usuario.ativo:
            return None

        if not bcrypt.checkpw(senha.encode("utf-8"), usuario.senha_hash.encode("utf-8")):
            return None

        return usuario

    # ============================
    #       CADASTRAR USUÁRIO
    # ============================
    def cadastrar_usuario(self, nome: str, login: str, senha: str, grupo: str):
        """
        Cadastra usuário com validação básica.
        """
        self._validar_dados(nome, login, senha, grupo)

        senha_hash = self._hash_senha(senha)

        usuario = Usuario(
            None,       # id
            nome,
            login,
            senha_hash,
            grupo,
            ativo=True
        )

        self.repo.criar_usuario(usuario)
        return usuario

    # ============================
    #     MÉTODOS AUXILIARES
    # ============================
    def _hash_senha(self, senha: str) -> str:
        return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _validar_dados(self, nome, login, senha, grupo):
        if not nome:
            raise ValueError("Nome é obrigatório.")
        if not login:
            raise ValueError("Login é obrigatório.")
        if not senha or len(senha) < 4:
            raise ValueError("Senha deve ter pelo menos 4 caracteres.")
        if not grupo:
            raise ValueError("Grupo é obrigatório.")
