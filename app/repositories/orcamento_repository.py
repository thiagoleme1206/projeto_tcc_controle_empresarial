from app.models.orcamento_model import Orcamento
from app.repositories.base_repository import BaseRepository

class OrcamentoRepository(BaseRepository):

    def criar(self, orcamento: Orcamento):
        row = self.execute("""
            INSERT INTO orcamentos (
                numero_os_projeto, data_orcamento,
                mao_de_obra, alimentacao, hospedagem, viagem, seguranca_trabalho,
                material, equipamento, andaime, documentacao, outros
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_orcamento
        """,
        (
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
        ),
        fetchone=True,
        commit=True)

        return row[0]

    def listar_todos(self):
        rows = self.execute(
            "SELECT * FROM orcamentos ORDER BY id_orcamento DESC",
            fetchall=True
        )

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
        row = self.execute(
            "SELECT * FROM orcamentos WHERE numero_os_projeto = %s",
            (numero_os,),
            fetchone=True
        )
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
        row = self.execute(
            "SELECT * FROM orcamentos WHERE id_orcamento = %s",
            (id_orcamento,),
            fetchone=True
        )
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
        result = self.execute("""
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
            RETURNING id_orcamento
        """,
        (
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
        ),
        fetchone=True,
        commit=True)

        return result is not None

    def excluir(self, id_orcamento: int):
        result = self.execute(
            "DELETE FROM orcamentos WHERE id_orcamento = %s RETURNING id_orcamento",
            (id_orcamento,),
            fetchone=True,
            commit=True
        )
        return result is not None
