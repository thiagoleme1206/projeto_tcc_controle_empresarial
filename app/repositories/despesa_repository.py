from app.models.despesa_model import Despesa
from app.repositories.base_repository import BaseRepository

class DespesaRepository(BaseRepository):

    def criar(self, despesa: Despesa):
        row = self.execute("""
            INSERT INTO despesas (
                numero_os_projeto, data_despesa, observacao,
                mao_de_obra, alimentacao, hospedagem, viagem, seguranca_trabalho,
                material, equipamento, andaime, documentacao, outros
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_despesa
        """,
        (
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
        ),
        fetchone=True,
        commit=True)

        return row[0]

    def listar_todos(self):
        rows = self.execute(
            "SELECT * FROM despesas ORDER BY id_despesa DESC",
            fetchall=True
        )
        return [Despesa(*row[:-1]) for row in rows]

    def buscar_por_os(self, numero_os_projeto: int):
        row = self.execute(
            "SELECT * FROM despesas WHERE numero_os_projeto = %s",
            (numero_os_projeto,),
            fetchone=True
        )
        return Despesa(*row[:-1]) if row else None

    def buscar_por_id(self, id_despesa: int):
        row = self.execute(
            "SELECT * FROM despesas WHERE id_despesa = %s",
            (id_despesa,),
            fetchone=True
        )
        return Despesa(*row[:-1]) if row else None

    def atualizar(self, despesa: Despesa):
        result = self.execute("""
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
            RETURNING id_despesa
        """,
        (
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
        ),
        fetchone=True,
        commit=True)

        return result is not None

    def excluir(self, id_despesa: int):
        result = self.execute(
            "DELETE FROM despesas WHERE id_despesa = %s RETURNING id_despesa",
            (id_despesa,),
            fetchone=True,
            commit=True
        )
        return result is not None
