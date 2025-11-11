# app/repositories/receita_repository.py

from app.database.db_connection import DatabaseConnection
from app.models.receita_model import Receita

class ReceitaRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def criar(self, receita: Receita):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO receitas (
                numero_os_projeto, data_receita, nf, cliente,
                valor_servico, valor_material, imposto, icms, valor_liquido
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_receita
        """, (
            receita.numero_os_projeto,
            receita.data_receita,
            receita.nf,
            receita.cliente,
            receita.valor_servico,
            receita.valor_material,
            receita.imposto,
            receita.icms,
            receita.valor_liquido
        ))
        id_receita = cursor.fetchone()[0]
        self.conn.commit()
        return id_receita

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM receitas ORDER BY id_receita DESC")
        rows = cursor.fetchall()
        return [Receita(*row[1:], id_receita=row[0]) for row in rows]

    def buscar_por_os(self, numero_os_projeto: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM receitas WHERE numero_os_projeto = %s", (numero_os_projeto,))
        row = cursor.fetchone()
        return Receita(*row[1:], id_receita=row[0]) if row else None

    def buscar_por_id(self, id_receita: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM receitas WHERE id_receita = %s", (id_receita,))
        row = cursor.fetchone()
        return Receita(*row[1:], id_receita=row[0]) if row else None

    def atualizar(self, receita: Receita):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE receitas SET
                numero_os_projeto = %s,
                data_receita = %s,
                nf = %s,
                cliente = %s,
                valor_servico = %s,
                valor_material = %s,
                imposto = %s,
                icms = %s,
                valor_liquido = %s
            WHERE id_receita = %s
        """, (
            receita.numero_os_projeto,
            receita.data_receita,
            receita.nf,
            receita.cliente,
            receita.valor_servico,
            receita.valor_material,
            receita.imposto,
            receita.icms,
            receita.valor_liquido,
            receita.id_receita
        ))
        self.conn.commit()

    def excluir(self, id_receita: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM receitas WHERE id_receita = %s", (id_receita,))
        self.conn.commit()
        return cursor.rowcount > 0
