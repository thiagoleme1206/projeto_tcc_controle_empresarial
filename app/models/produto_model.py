class Produto:
    def __init__(self, id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo, criado_em=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.quantidade = quantidade
        self.unidade = unidade
        self.preco_unitario = preco_unitario
        self.estoque_minimo = estoque_minimo
        self.criado_em = criado_em
