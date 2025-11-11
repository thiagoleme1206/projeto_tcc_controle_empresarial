from app.database.db_connection import DatabaseConnection
from app.models.lista_materiais_model import ListaMateriais, ItemListaMateriais

class ListaMateriaisRepository:
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()

    def criar_lista(self, lista):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO lista_materiais (os_referencia, responsavel, observacao)
            VALUES (%s, %s, %s) RETURNING id_lista
        """, (lista.os_referencia, lista.responsavel, lista.observacao))
        id_lista = cursor.fetchone()[0]
        self.conn.commit()
        return id_lista

    def adicionar_item(self, item):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO itens_lista_materiais (
                id_lista, produto_id, nome_produto, quantidade, unidade, preco_unitario, observacao
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            item.id_lista,
            item.produto_id,
            item.nome_produto,
            item.quantidade,
            item.unidade,
            item.preco_unitario,
            item.observacao
        ))
        self.conn.commit()

    def listar_listas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id_lista, os_referencia, responsavel, observacao, data_criacao
            FROM lista_materiais
            ORDER BY data_criacao DESC
        """)
        rows = cursor.fetchall()
        return [ListaMateriais(*row) for row in rows]

    def buscar_itens_por_lista(self, id_lista):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, id_lista, produto_id, nome_produto, quantidade, unidade, preco_unitario, observacao
            FROM itens_lista_materiais
            WHERE id_lista = %s
        """, (id_lista,))
        rows = cursor.fetchall()
        return [ItemListaMateriais(*row) for row in rows]

    def excluir_itens_por_lista(self, id_lista):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM itens_lista_materiais WHERE id_lista = %s", (id_lista,))
        self.conn.commit()

    def excluir_lista(self, id_lista):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM lista_materiais WHERE id_lista = %s", (id_lista,))
        self.conn.commit()

    # ✅ NOVOS MÉTODOS

    def atualizar_quantidade(self, id_item, nova_qtde):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE itens_lista_materiais
            SET quantidade = %s
            WHERE id = %s
        """, (nova_qtde, id_item))
        self.conn.commit()

    def atualizar_preco(self, id_item, novo_preco):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE itens_lista_materiais
            SET preco_unitario = %s
            WHERE id = %s
        """, (novo_preco, id_item))
        self.conn.commit()

    def remover_item(self, id_item):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM itens_lista_materiais WHERE id = %s", (id_item,))
        self.conn.commit()

    def buscar_item_na_lista(self, id_lista, produto_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, id_lista, produto_id, nome_produto, quantidade, unidade, preco_unitario, observacao
            FROM itens_lista_materiais
            WHERE id_lista = %s AND produto_id = %s
        """, (id_lista, produto_id))
        row = cursor.fetchone()
        return ItemListaMateriais(*row) if row else None
    
    def atualizar_observacao(self, id_item, nova_obs):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE itens_lista_materiais
            SET observacao = %s
            WHERE id = %s
        """, (nova_obs, id_item))
        self.conn.commit()