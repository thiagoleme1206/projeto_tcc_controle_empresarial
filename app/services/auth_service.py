import bcrypt
from app.repositories.usuario_repository import UsuarioRepository

class AuthService:
    def __init__(self):
        self.repo = UsuarioRepository()

    def autenticar(self, login, senha):
        usuario = self.repo.buscar_por_login(login)
        if usuario and usuario.ativo:
            if bcrypt.checkpw(senha.encode('utf-8'), usuario.senha_hash.encode('utf-8')):
                return usuario
        return None

    def cadastrar_usuario(self, nome, login, senha, grupo):
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        from app.models.usuario_model import Usuario
        usuario = Usuario(None, nome, login, senha_hash, grupo)
        self.repo.criar_usuario(usuario)
        return usuario
