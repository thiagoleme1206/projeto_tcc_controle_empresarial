# app/services/usuario_service.py

from app.database.db_connection import DatabaseConnection
from app.utils.cripto_utils import hash_senha
import psycopg2

class UsuarioService:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def criar_usuario(self, nome, login, senha, grupo):
        """Cria um novo usuário com senha criptografada e grupo definido."""
        senha_hash = hash_senha(senha)

        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (nome, login, senha, grupo, ativo)
                VALUES (%s, %s, %s, %s, TRUE)
            """, (nome, login, senha_hash, grupo))
            self.conn.commit()
        except psycopg2.IntegrityError:
            self.conn.rollback()
            raise ValueError("❌ Login já existente.")
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"❌ Erro ao criar usuário: {e}")
        finally:
            cursor.close()

    def alterar_usuario(self, login, nome=None, grupo=None, senha=None):
        """Permite alterar nome, grupo ou senha de um usuário."""
        cursor = self.conn.cursor()

        campos = []
        valores = []

        if nome:
            campos.append("nome = %s")
            valores.append(nome)
        if grupo:
            campos.append("grupo = %s")
            valores.append(grupo)
        if senha:
            campos.append("senha = %s")
            valores.append(hash_senha(senha))

        if not campos:
            raise ValueError("Nenhum campo informado para atualização.")

        query = f"UPDATE usuarios SET {', '.join(campos)} WHERE login = %s"
        valores.append(login)

        cursor.execute(query, tuple(valores))
        self.conn.commit()
        cursor.close()

    def ativar_inativar_usuario(self, login, ativo):
        """Ativa ou inativa um usuário, atualizando apenas o campo 'ativo'."""
        cursor = self.conn.cursor()

        # Verifica se o usuário existe
        cursor.execute("SELECT 1 FROM usuarios WHERE login = %s", (login,))
        if not cursor.fetchone():
            cursor.close()
            raise ValueError("Usuário não encontrado.")

        try:
            cursor.execute("""
                UPDATE usuarios
                SET ativo = %s
                WHERE login = %s
            """, (ativo, login))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar status do usuário: {e}")
        finally:
            cursor.close()

    def consultar_usuarios(self, ativo=None, nome=None, login=None, grupo=None):
        """Consulta usuários com filtros opcionais."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM usuarios WHERE TRUE"
        params = []

        if ativo is not None:
            query += " AND ativo = %s"
            params.append(ativo)
        if nome:
            query += " AND nome ILIKE %s"
            params.append(f"%{nome}%")
        if login:
            query += " AND login ILIKE %s"
            params.append(f"%{login}%")
        if grupo:
            query += " AND grupo = %s"
            params.append(grupo)

        query += " ORDER BY id ASC"

        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()
        cursor.close()
        return resultados

    def buscar_usuario_por_login(self, login):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE login = %s", (login,))
        return cursor.fetchone()
    
    def excluir_usuario(self, login):
        """Marca o usuário como inativo e altera seu grupo para 'inativos'."""
        cursor = self.conn.cursor()

        # Verifica se o usuário existe
        cursor.execute("SELECT 1 FROM usuarios WHERE login = %s", (login,))
        if not cursor.fetchone():
            cursor.close()
            raise ValueError("Usuário não encontrado.")

        try:
            cursor.execute("""
                UPDATE usuarios
                SET ativo = FALSE, grupo = 'inativos'
                WHERE login = %s
            """, (login,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao excluir (inativar) usuário: {e}")
        finally:
            cursor.close()