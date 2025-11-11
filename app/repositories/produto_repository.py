from app.database.db_connection import DatabaseConnection
from app.models.produto_model import Produto
from app.models.lista_materiais_model import ItemListaMateriais

class ProdutoRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def listar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo, criado_em FROM produtos")
        rows = cursor.fetchall()
        return [Produto(*row) for row in rows]

    def buscar_por_id(self, id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo, criado_em FROM produtos WHERE id = %s", (id,))
        row = cursor.fetchone()
        return Produto(*row) if row else None

    def inserir(self, produto):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (produto.nome, produto.descricao, produto.quantidade, produto.unidade, produto.preco_unitario, produto.estoque_minimo))
        self.conn.commit()

    def atualizar(self, produto):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE produtos
            SET nome = %s, descricao = %s, quantidade = %s, unidade = %s, preco_unitario = %s, estoque_minimo = %s
            WHERE id = %s
        """, (produto.nome, produto.descricao, produto.quantidade, produto.unidade, produto.preco_unitario, produto.estoque_minimo, produto.id))
        self.conn.commit()

    def deletar(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
        self.conn.commit()

    def atualizar_quantidade(self, produto_id, nova_qtde):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE produtos
            SET quantidade = %s
            WHERE id = %s
        """, (nova_qtde, produto_id))
        self.conn.commit()