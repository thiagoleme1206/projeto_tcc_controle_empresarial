from app.database.db_connection import DatabaseConnection
from app.models.usuario_model import Usuario

class UsuarioRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def buscar_por_login(self, login):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, login, senha, grupo, ativo FROM usuarios WHERE login = %s AND ativo=true" , (login,))
        row = cursor.fetchone()
        return Usuario(*row) if row else None

    def criar_usuario(self, usuario):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nome, login, senha, grupo, ativo)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario.nome, usuario.login, usuario.senha_hash, usuario.grupo, usuario.ativo))
        self.conn.commit()
