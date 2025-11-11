from app.database.db_connection import DatabaseConnection
from app.models.proposta_model import Proposta

class PropostaRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def listar_todas(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, titulo, descricao, valor, status, criado_em FROM propostas")
        rows = cursor.fetchall()
        return [Proposta(*row) for row in rows]

    def buscar_por_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, titulo, descricao, valor, status, criado_em FROM propostas WHERE id = %s", (id,))
        row = cursor.fetchone()
        return Proposta(*row) if row else None

    def inserir(self, proposta):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO propostas (titulo, descricao, valor, status)
            VALUES (%s, %s, %s, %s)
        """, (proposta.titulo, proposta.descricao, proposta.valor, proposta.status))
        self.conn.commit()

    def atualizar(self, proposta):
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE propostas
                SET titulo = %s, descricao = %s, valor = %s, status = %s
                WHERE id = %s
            """, (proposta.titulo, proposta.descricao, proposta.valor, proposta.status, proposta.id))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Erro ao atualizar proposta: {e}")
        finally:
            cursor.close()

    def deletar(self, id):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM propostas WHERE id = %s", (id,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"Erro ao excluir proposta: {e}")
        finally:
            cursor.close()