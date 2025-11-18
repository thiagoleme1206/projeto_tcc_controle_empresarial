from app.models.usuario_model import Usuario
from app.repositories.base_repository import BaseRepository

class UsuarioRepository(BaseRepository):

    def buscar_por_login(self, login: str):
        row = self.execute(
            """
            SELECT id, nome, login, senha, grupo, ativo
            FROM usuarios
            WHERE login = %s AND ativo = TRUE
            """,
            (login,),
            fetchone=True
        )

        return Usuario(*row) if row else None

    def criar_usuario(self, usuario: Usuario):
        self.execute(
            """
            INSERT INTO usuarios (nome, login, senha, grupo, ativo)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                usuario.nome,
                usuario.login,
                usuario.senha_hash,
                usuario.grupo,
                usuario.ativo
            ),
            commit=True
        )
