# app/services/auditoria_service.py

from app.database.db_connection import DatabaseConnection
from datetime import datetime

class AuditoriaService:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def registrar_acao(self, nome_usuario, acao, modulo, descricao=None):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO auditoria (nome_usuario, acao, modulo, descricao, data_hora)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome_usuario, acao, modulo, descricao, datetime.now()))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Erro ao registrar auditoria: {e}")
        finally:
            cursor.close()

    def consultar_por_usuario(self, nome_usuario):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT nome_usuario, acao, modulo, descricao, data_hora
                FROM auditoria
                WHERE nome_usuario ILIKE %s
                ORDER BY data_hora DESC
            """, (f"%{nome_usuario.strip()}%",))
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Erro ao consultar auditoria: {e}")
        finally:
            cursor.close()

    def consultar_por_data(self, data_hora):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT nome_usuario, acao, modulo, descricao, data_hora
                FROM auditoria
                WHERE data_hora::date = %s
                ORDER BY data_hora DESC
            """, (data_hora,))  # ✅ vírgula aqui transforma em tupla
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Erro ao consultar auditoria por data: {e}")
        finally:
            cursor.close()
