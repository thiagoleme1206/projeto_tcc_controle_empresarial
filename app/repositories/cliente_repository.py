from app.models.clientes_model import Cliente
from app.repositories.base_repository import BaseRepository

class ClienteRepository(BaseRepository):

    def listar_todos(self):
        rows = self.execute(
            "SELECT id_cliente, cpf_cnpj, nome FROM clientes ORDER BY id_cliente",
            fetchall=True
        )
        return [Cliente(*row) for row in rows]

    def buscar_por_id(self, id_cliente):
        row = self.execute(
            "SELECT id_cliente, cpf_cnpj, nome FROM clientes WHERE id_cliente = %s",
            (id_cliente,),
            fetchone=True
        )
        return Cliente(*row) if row else None

    def criar_cliente(self, cpf_cnpj, nome):
        row = self.execute(
            """
            INSERT INTO clientes (cpf_cnpj, nome)
            VALUES (%s, %s)
            RETURNING id_cliente
            """,
            (cpf_cnpj, nome),
            fetchone=True,
            commit=True
        )
        return row[0]

    def atualizar_cliente(self, id_cliente, cpf_cnpj, nome):
        result = self.execute(
            """
            UPDATE clientes
            SET cpf_cnpj = %s, nome = %s
            WHERE id_cliente = %s
            RETURNING id_cliente
            """,
            (cpf_cnpj, nome, id_cliente),
            fetchone=True,
            commit=True
        )
        return result is not None

    def excluir_cliente(self, id_cliente):
        result = self.execute(
            "DELETE FROM clientes WHERE id_cliente = %s RETURNING id_cliente",
            (id_cliente,),
            fetchone=True,
            commit=True
        )
        return result is not None
