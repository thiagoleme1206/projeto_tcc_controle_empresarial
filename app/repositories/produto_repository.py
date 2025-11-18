from app.models.produto_model import Produto
from app.repositories.base_repository import BaseRepository

class ProdutoRepository(BaseRepository):

    def listar_todos(self):
        rows = self.execute(
            """
            SELECT id, nome, descricao, quantidade, unidade,
                   preco_unitario, estoque_minimo, criado_em
            FROM produtos
            """,
            fetchall=True
        )
        return [Produto(*row) for row in rows]

    def buscar_por_id(self, id):
        row = self.execute(
            """
            SELECT id, nome, descricao, quantidade, unidade,
                   preco_unitario, estoque_minimo, criado_em
            FROM produtos
            WHERE id = %s
            """,
            (id,),
            fetchone=True
        )
        return Produto(*row) if row else None

    def inserir(self, produto):
        self.execute(
            """
            INSERT INTO produtos (nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                produto.nome,
                produto.descricao,
                produto.quantidade,
                produto.unidade,
                produto.preco_unitario,
                produto.estoque_minimo
            ),
            commit=True
        )

    def atualizar(self, produto):
        self.execute(
            """
            UPDATE produtos
            SET nome = %s, descricao = %s, quantidade = %s, unidade = %s,
                preco_unitario = %s, estoque_minimo = %s
            WHERE id = %s
            """,
            (
                produto.nome,
                produto.descricao,
                produto.quantidade,
                produto.unidade,
                produto.preco_unitario,
                produto.estoque_minimo,
                produto.id
            ),
            commit=True
        )

    def deletar(self, id):
        self.execute(
            "DELETE FROM produtos WHERE id = %s",
            (id,),
            commit=True
        )

    def atualizar_quantidade(self, produto_id, nova_qtde):
        self.execute(
            """
            UPDATE produtos
            SET quantidade = %s
            WHERE id = %s
            """,
            (nova_qtde, produto_id),
            commit=True
        )
