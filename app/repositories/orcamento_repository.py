from app.database.db_connection import DatabaseConnection
from app.models.orcamento_model import Orcamento

class OrcamentoRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def criar(self, orcamento: Orcamento):
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO orcamentos (
                numero_os_projeto, data_orcamento,
                mao_de_obra, alimentacao, hospedagem, viagem, seguranca_trabalho,
                material, equipamento, andaime, documentacao, outros
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_orcamento
        """, (
            orcamento.numero_os,
            orcamento.data_orcamento,
            orcamento.mao_de_obra,
            orcamento.alimentacao,
            orcamento.hospedagem,
            orcamento.viagem,
            orcamento.seguranca_trabalho,
            orcamento.material,
            orcamento.equipamento,
            orcamento.andaime,
            orcamento.documentacao,
            orcamento.outros
        ))

        id_orcamento = cursor.fetchone()[0]
        self.conn.commit()
        return id_orcamento

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orcamentos ORDER BY id_orcamento DESC")
        rows = cursor.fetchall()

        return [
            Orcamento(
                numero_os=row[1],
                data_orcamento=row[2],
                mao_de_obra=row[3],
                alimentacao=row[4],
                hospedagem=row[5],
                viagem=row[6],
                seguranca_trabalho=row[7],
                material=row[8],
                equipamento=row[9],
                andaime=row[10],
                documentacao=row[11],
                outros=row[12],
                id_orcamento=row[0]
            )
            for row in rows
        ]

    def buscar_por_os(self, numero_os: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orcamentos WHERE numero_os_projeto = %s", (numero_os,))
        row = cursor.fetchone()
        if not row:
            return None

        return Orcamento(
            numero_os=row[1],
            data_orcamento=row[2],
            mao_de_obra=row[3],
            alimentacao=row[4],
            hospedagem=row[5],
            viagem=row[6],
            seguranca_trabalho=row[7],
            material=row[8],
            equipamento=row[9],
            andaime=row[10],
            documentacao=row[11],
            outros=row[12],
            id_orcamento=row[0]
        )

    def buscar_por_id(self, id_orcamento: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orcamentos WHERE id_orcamento = %s", (id_orcamento,))
        row = cursor.fetchone()
        if not row:
            return None

        return Orcamento(
            numero_os=row[1],
            data_orcamento=row[2],
            mao_de_obra=row[3],
            alimentacao=row[4],
            hospedagem=row[5],
            viagem=row[6],
            seguranca_trabalho=row[7],
            material=row[8],
            equipamento=row[9],
            andaime=row[10],
            documentacao=row[11],
            outros=row[12],
            id_orcamento=row[0]
        )

    def atualizar(self, orcamento: Orcamento):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE orcamentos SET
                numero_os_projeto = %s,
                data_orcamento = %s,
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
            WHERE id_orcamento = %s
        """, (
            orcamento.numero_os,
            orcamento.data_orcamento,
            orcamento.mao_de_obra,
            orcamento.alimentacao,
            orcamento.hospedagem,
            orcamento.viagem,
            orcamento.seguranca_trabalho,
            orcamento.material,
            orcamento.equipamento,
            orcamento.andaime,
            orcamento.documentacao,
            orcamento.outros,
            orcamento.id_orcamento
        ))
        self.conn.commit()

    def excluir(self, id_orcamento: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM orcamentos WHERE id_orcamento = %s", (id_orcamento,))
        self.conn.commit()
        return cursor.rowcount > 0
