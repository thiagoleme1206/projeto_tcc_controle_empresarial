from app.models.receita_model import Receita
from app.repositories.base_repository import BaseRepository

class ReceitaRepository(BaseRepository):

    def criar(self, receita: Receita):
        row = self.execute(
            """
            INSERT INTO receitas (
                numero_os_projeto, data_receita, nf, cliente,
                valor_servico, valor_material, imposto, icms, valor_liquido
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_receita
            """,
            (
                receita.numero_os_projeto,
                receita.data_receita,
                receita.nf,
                receita.cliente,
                receita.valor_servico,
                receita.valor_material,
                receita.imposto,
                receita.icms,
                receita.valor_liquido
            ),
            fetchone=True,
            commit=True
        )

        return row[0]

    def listar_todos(self):
        rows = self.execute(
            "SELECT * FROM receitas ORDER BY id_receita DESC",
            fetchall=True
        )

        return [
            Receita(
                numero_os_projeto=row[1],
                data_receita=row[2],
                nf=row[3],
                cliente=row[4],
                valor_servico=row[5],
                valor_material=row[6],
                imposto=row[7],
                icms=row[8],
                valor_liquido=row[9],
                id_receita=row[0]
            )
            for row in rows
        ]

    def buscar_por_os(self, numero_os_projeto: int):
        row = self.execute(
            "SELECT * FROM receitas WHERE numero_os_projeto = %s",
            (numero_os_projeto,),
            fetchone=True
        )

        if not row:
            return None

        return Receita(
            numero_os_projeto=row[1],
            data_receita=row[2],
            nf=row[3],
            cliente=row[4],
            valor_servico=row[5],
            valor_material=row[6],
            imposto=row[7],
            icms=row[8],
            valor_liquido=row[9],
            id_receita=row[0]
        )

    def buscar_por_id(self, id_receita: int):
        row = self.execute(
            "SELECT * FROM receitas WHERE id_receita = %s",
            (id_receita,),
            fetchone=True
        )

        if not row:
            return None

        return Receita(
            numero_os_projeto=row[1],
            data_receita=row[2],
            nf=row[3],
            cliente=row[4],
            valor_servico=row[5],
            valor_material=row[6],
            imposto=row[7],
            icms=row[8],
            valor_liquido=row[9],
            id_receita=row[0]
        )

    def atualizar(self, receita: Receita):
        self.execute(
            """
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
            """,
            (
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
            ),
            commit=True
        )

    def excluir(self, id_receita: int):
        result = self.execute(
            "DELETE FROM receitas WHERE id_receita = %s",
            (id_receita,),
            commit=True
        )
        return result is not None
