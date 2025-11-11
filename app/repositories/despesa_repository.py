from app.database.db_connection import DatabaseConnection
from app.models.despesa_model import Despesa

class DespesaRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def criar(self, despesa: Despesa):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO despesas (
                numero_os_projeto, data_despesa, observacao,
                mao_de_obra, alimentacao, hospedagem, viagem, seguranca_trabalho,
                material, equipamento, andaime, documentacao, outros
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_despesa
        """, (
            despesa.numero_os_projeto,
            despesa.data_despesa,
            despesa.observacao,
            despesa.mao_de_obra,
            despesa.alimentacao,
            despesa.hospedagem,
            despesa.viagem,
            despesa.seguranca_trabalho,
            despesa.material,
            despesa.equipamento,
            despesa.andaime,
            despesa.documentacao,
            despesa.outros
        ))
        id_despesa = cursor.fetchone()[0]
        self.conn.commit()
        return id_despesa

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM despesas ORDER BY id_despesa DESC")
        rows = cursor.fetchall()
        return [Despesa(*row[:-1]) for row in rows]  # ✅ ordem do banco = ordem do model

    def buscar_por_os(self, numero_os_projeto: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM despesas WHERE numero_os_projeto = %s", (numero_os_projeto,))
        row = cursor.fetchone()
        return Despesa(*row[:-1]) if row else None

    def buscar_por_id(self, id_despesa: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM despesas WHERE id_despesa = %s", (id_despesa,))
        row = cursor.fetchone()
        return Despesa(*row[:-1]) if row else None

    def atualizar(self, despesa: Despesa):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE despesas SET
                numero_os_projeto = %s,
                data_despesa = %s,
                observacao = %s,
                mao_de_obra = %s,
                alimentacao = %s,
                hospedagem = %s,
                viagem = %s,
                seguranca_trabalho = %s,
                material = %s,
                equipamento = %s,
                andaime = %s,
                documentacao = %s,
                outros = %s
            WHERE id_despesa = %s
        """, (
            despesa.numero_os_projeto,
            despesa.data_despesa,
            despesa.observacao,
            despesa.mao_de_obra,
            despesa.alimentacao,
            despesa.hospedagem,
            despesa.viagem,
            despesa.seguranca_trabalho,
            despesa.material,
            despesa.equipamento,
            despesa.andaime,
            despesa.documentacao,
            despesa.outros,
            despesa.id_despesa
        ))
        self.conn.commit()

    def excluir(self, id_despesa: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM despesas WHERE id_despesa = %s", (id_despesa,))
        self.conn.commit()
        return cursor.rowcount > 0
