from app.repositories.lista_materiais_repository import ListaMateriaisRepository
from app.models.lista_materiais_model import ListaMateriais, ItemListaMateriais

class ListaMateriaisService:
    def __init__(self):
        self.repo = ListaMateriaisRepository()

    def criar_lista(self, os_referencia, responsavel, observacao, itens):
        lista = ListaMateriais(None, os_referencia, responsavel, observacao, None)
        id_lista = self.repo.criar_lista(lista)
        for item in itens:
            item.id_lista = id_lista
            self.repo.adicionar_item(item)
        return id_lista

    def listar_listas(self):
        return self.repo.listar_listas()

    def buscar_itens(self, id_lista):
        return self.repo.buscar_itens_por_lista(id_lista)

    def excluir_lista(self, id_lista):
        self.repo.excluir_lista(id_lista)

    # Métodos para alterar itens
    def atualizar_quantidade(self, id_item, nova_qtde):
        self.repo.atualizar_quantidade(id_item, nova_qtde)

    def atualizar_preco(self, id_item, novo_preco):
        self.repo.atualizar_preco(id_item, novo_preco)

    def remover_item(self, id_item):
        self.repo.remover_item(id_item)

    def adicionar_ou_atualizar_item(self, novo_item, estoque_disponivel):
        item_existente = self.repo.buscar_item_na_lista(novo_item.id_lista, novo_item.produto_id)

        if item_existente:
            nova_qtde = item_existente.quantidade + novo_item.quantidade
            if nova_qtde > estoque_disponivel:
                print("❌ Quantidade excede o estoque disponível.")
                return False
            self.repo.atualizar_quantidade(item_existente.id, nova_qtde)
            return True
        else:
            if novo_item.quantidade > estoque_disponivel:
                print("❌ Quantidade excede o estoque disponível.")
                return False
            self.repo.adicionar_item(novo_item)
            return True            