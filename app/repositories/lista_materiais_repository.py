from app.models.lista_materiais_model import ListaMateriais, ItemListaMateriais
from app.repositories.base_repository import BaseRepository

class ListaMateriaisRepository(BaseRepository):

    def criar_lista(self, lista):
        row = self.execute("""
            INSERT INTO lista_materiais (os_referencia, responsavel, observacao)
            VALUES (%s, %s, %s)
            RETURNING id_lista
        """,
        (lista.os_referencia, lista.responsavel, lista.observacao),
        fetchone=True,
        commit=True)

        return row[0]

    def adicionar_item(self, item):
        self.execute("""
            INSERT INTO itens_lista_materiais (
                id_lista, produto_id, nome_produto, quantidade, unidade, preco_unitario, observacao
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            item.id_lista,
            item.produto_id,
            item.nome_produto,
            item.quantidade,
            item.unidade,
            item.preco_unitario,
            item.observacao
        ),
        commit=True)

    def listar_listas(self):
        rows = self.execute("""
            SELECT id_lista, os_referencia, responsavel, observacao, data_criacao
            FROM lista_materiais
            ORDER BY data_criacao DESC
        """,
        fetchall=True)

        return [ListaMateriais(*row) for row in rows]

    def buscar_itens_por_lista(self, id_lista):
        rows = self.execute("""
            SELECT id, id_lista, produto_id, nome_produto, quantidade, unidade,
                   preco_unitario, observacao
            FROM itens_lista_materiais
            WHERE id_lista = %s
        """,
        (id_lista,),
        fetchall=True)

        return [ItemListaMateriais(*row) for row in rows]

    def excluir_itens_por_lista(self, id_lista):
        self.execute(
            "DELETE FROM itens_lista_materiais WHERE id_lista = %s",
            (id_lista,),
            commit=True
        )

    def excluir_lista(self, id_lista):
        self.execute(
            "DELETE FROM lista_materiais WHERE id_lista = %s",
            (id_lista,),
            commit=True
        )

    # -----------------------------
    # MÉTODOS DE ATUALIZAÇÃO
    # -----------------------------

    def atualizar_quantidade(self, id_item, nova_qtde):
        self.execute("""
            UPDATE itens_lista_materiais
            SET quantidade = %s
            WHERE id = %s
        """,
        (nova_qtde, id_item),
        commit=True)

    def atualizar_preco(self, id_item, novo_preco):
        self.execute("""
            UPDATE itens_lista_materiais
            SET preco_unitario = %s
            WHERE id = %s
        """,
        (novo_preco, id_item),
        commit=True)

    def atualizar_observacao(self, id_item, nova_obs):
        self.execute("""
            UPDATE itens_lista_materiais
            SET observacao = %s
            WHERE id = %s
        """,
        (nova_obs, id_item),
        commit=True)

    # -----------------------------
    # BUSCAS ESPECÍFICAS
    # -----------------------------

    def buscar_item_na_lista(self, id_lista, produto_id):
        row = self.execute("""
            SELECT id, id_lista, produto_id, nome_produto, quantidade,
                   unidade, preco_unitario, observacao
            FROM itens_lista_materiais
            WHERE id_lista = %s AND produto_id = %s
        """,
        (id_lista, produto_id),
        fetchone=True)

        return ItemListaMateriais(*row) if row else None

    def remover_item(self, id_item):
        self.execute(
            "DELETE FROM itens_lista_materiais WHERE id = %s RETURNING id",
            (id_item,),
            fetchone=True,
            commit=True
        )
