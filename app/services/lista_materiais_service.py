# app/services/lista_materiais_service.py

from app.repositories.lista_materiais_repository import ListaMateriaisRepository
from app.models.lista_materiais_model import ListaMateriais, ItemListaMateriais

class ListaMateriaisService:
    def __init__(self):
        self.repo = ListaMateriaisRepository()

    # --------------------------------
    # Helpers / Validadores
    # --------------------------------

    def _to_float(self, valor, default=0.0):
        try:
            return float(valor)
        except (ValueError, TypeError):
            return default

    def _to_int(self, valor, default=0):
        try:
            return int(valor)
        except (ValueError, TypeError):
            return default

    def _validate_required(self, os_referencia, responsavel):
        if not os_referencia or not str(os_referencia).strip():
            raise ValueError("❌ O número da OS é obrigatório.")
        if not responsavel or not responsavel.strip():
            raise ValueError("❌ O responsável é obrigatório.")

    # --------------------------------
    # Operações principais
    # --------------------------------

    def criar_lista(self, os_referencia, responsavel, observacao, itens):
        self._validate_required(os_referencia, responsavel)

        lista = ListaMateriais(
            id_lista=None,
            os_referencia=os_referencia,
            responsavel=responsavel.strip(),
            observacao=(observacao or "").strip(),
            data_criacao=None
        )

        id_lista = self.repo.criar_lista(lista)

        # Registrar itens
        for item in itens:
            item.id_lista = id_lista
            item.quantidade = self._to_float(item.quantidade)
            item.preco_unitario = self._to_float(item.preco_unitario)
            self.repo.adicionar_item(item)

        return id_lista

    def listar_listas(self):
        return self.repo.listar_listas()

    def buscar_itens(self, id_lista):
        return self.repo.buscar_itens_por_lista(id_lista)

    def excluir_lista(self, id_lista):
        # Exclui itens antes da lista (garante integridade dependendo do FK)
        self.repo.excluir_itens_por_lista(id_lista)
        return self.repo.excluir_lista(id_lista)

    # --------------------------------
    # Atualizações em itens
    # --------------------------------

    def atualizar_quantidade(self, id_item, nova_qtde):
        nova_qtde = self._to_float(nova_qtde)
        if nova_qtde < 0:
            raise ValueError("❌ A quantidade não pode ser negativa.")
        self.repo.atualizar_quantidade(id_item, nova_qtde)

    def atualizar_preco(self, id_item, novo_preco):
        novo_preco = self._to_float(novo_preco)
        if novo_preco < 0:
            raise ValueError("❌ O preço não pode ser negativo.")
        self.repo.atualizar_preco(id_item, novo_preco)

    def remover_item(self, id_item):
        return self.repo.remover_item(id_item)

    # --------------------------------
    # Adicionar item com validação
    # --------------------------------

    def adicionar_ou_atualizar_item(self, novo_item, estoque_disponivel):
        estoque_disponivel = self._to_float(estoque_disponivel)
        novo_item.quantidade = self._to_float(novo_item.quantidade)

        if estoque_disponivel <= 0:
            raise ValueError("❌ Estoque indisponível para esse produto.")

        item_existente = self.repo.buscar_item_na_lista(
            novo_item.id_lista,
            novo_item.produto_id
        )

        # Atualiza caso já exista
        if item_existente:
            nova_qtde = item_existente.quantidade + novo_item.quantidade

            if nova_qtde > estoque_disponivel:
                raise ValueError("❌ Quantidade excede o estoque disponível.")

            self.repo.atualizar_quantidade(item_existente.id, nova_qtde)
            return True

        # Adiciona novo item
        if novo_item.quantidade > estoque_disponivel:
            raise ValueError("❌ Quantidade excede o estoque disponível.")

        self.repo.adicionar_item(novo_item)
        return True
