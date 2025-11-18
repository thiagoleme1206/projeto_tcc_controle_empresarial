from app.models.proposta_model import Proposta
from app.repositories.base_repository import BaseRepository

class PropostaRepository(BaseRepository):

    def listar_todas(self):
        rows = self.execute(
            "SELECT id, titulo, descricao, valor, status, criado_em FROM propostas",
            fetchall=True
        )
        return [Proposta(*row) for row in rows]

    def buscar_por_id(self, id_proposta):
        row = self.execute(
            "SELECT id, titulo, descricao, valor, status, criado_em FROM propostas WHERE id = %s",
            (id_proposta,),
            fetchone=True
        )
        return Proposta(*row) if row else None

    def inserir(self, proposta: Proposta):
        self.execute(
            """
            INSERT INTO propostas (titulo, descricao, valor, status)
            VALUES (%s, %s, %s, %s)
            """,
            (proposta.titulo, proposta.descricao, proposta.valor, proposta.status),
            commit=True
        )

    def atualizar(self, proposta: Proposta):
        self.execute(
            """
            UPDATE propostas
            SET titulo = %s, descricao = %s, valor = %s, status = %s
            WHERE id = %s
            """,
            (proposta.titulo, proposta.descricao, proposta.valor, proposta.status, proposta.id),
            commit=True
        )

    def deletar(self, id_proposta):
        self.execute(
            "DELETE FROM propostas WHERE id = %s",
            (id_proposta,),
            commit=True
        )
