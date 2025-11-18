from app.utils.cripto_utils import hash_senha
from app.repositories.usuario_repository import UsuarioRepository

class UsuarioService:
    def __init__(self):
        self.repo = UsuarioRepository()

    # ---------------------------------------------------------------------
    # Criar usuário
    # ---------------------------------------------------------------------
    def criar_usuario(self, nome, login, senha, grupo):
        if not nome or not login or not senha:
            raise ValueError("Nome, login e senha são obrigatórios.")

        senha_hash = hash_senha(senha)

        try:
            from app.models.usuario_model import Usuario
            usuario = Usuario(id=None, nome=nome, login=login, senha=senha_hash, grupo=grupo, ativo=True)
            self.repo.criar_usuario(usuario)
        except Exception as e:
            # O repository já trata erro de UNIQUE
            raise ValueError(str(e))

    # ---------------------------------------------------------------------
    # Alterar usuário
    # ---------------------------------------------------------------------
    def alterar_usuario(self, login, nome=None, grupo=None, senha=None):
        usuario = self.repo.buscar_por_login(login)
        if not usuario:
            raise ValueError("Usuário não encontrado.")

        campos = {}

        if nome:
            campos['nome'] = nome

        if grupo:
            campos['grupo'] = grupo

        if senha:
            campos['senha'] = hash_senha(senha)

        if not campos:
            raise ValueError("Nenhum campo informado para atualização.")

        # Repository com UPDATE dinâmico
        self.repo.atualizar_usuario(login, campos)

    # ---------------------------------------------------------------------
    # Ativar / Inativar usuário
    # ---------------------------------------------------------------------
    def ativar_inativar_usuario(self, login, ativo: bool):
        usuario = self.repo.buscar_por_login(login)
        if not usuario:
            raise ValueError("Usuário não encontrado.")

        self.repo.atualizar_usuario(login, {"ativo": ativo})

    # ---------------------------------------------------------------------
    # Consultar usuários
    # ---------------------------------------------------------------------
    def consultar_usuarios(self, ativo=None, nome=None, login=None, grupo=None):
        filtros = {
            "ativo": ativo,
            "nome": nome,
            "login": login,
            "grupo": grupo,
        }

        return self.repo.consultar(filtros)

    # ---------------------------------------------------------------------
    # Buscar por login
    # ---------------------------------------------------------------------
    def buscar_usuario_por_login(self, login):
        return self.repo.buscar_por_login(login)

    # ---------------------------------------------------------------------
    # Excluir (inativar) usuário
    # ---------------------------------------------------------------------
    def excluir_usuario(self, login):
        usuario = self.repo.buscar_por_login(login)
        if not usuario:
            raise ValueError("Usuário não encontrado.")

        # marca como inativo e muda grupo
        self.repo.atualizar_usuario(login, {
            "ativo": False,
            "grupo": "inativos"
        })
