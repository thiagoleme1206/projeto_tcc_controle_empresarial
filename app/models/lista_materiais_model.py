class ListaMateriais:
    def __init__(self, id_lista, os_referencia, responsavel, observacao, data_criacao):
        self.id_lista = id_lista
        self.os_referencia = os_referencia
        self.responsavel = responsavel
        self.observacao = observacao
        self.data_criacao = data_criacao

class ItemListaMateriais:
    def __init__(self, id, id_lista, produto_id, nome_produto, quantidade, unidade, preco_unitario, observacao):
        self.id = id
        self.id_lista = id_lista
        self.produto_id = produto_id
        self.nome_produto = nome_produto
        self.quantidade = quantidade
        self.unidade = unidade
        self.preco_unitario = preco_unitario
        self.observacao = observacao