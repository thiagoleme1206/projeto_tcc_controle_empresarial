from app.repositories.produto_repository import ProdutoRepository
from app.models.produto_model import Produto

class EstoqueService:
    def __init__(self):
        self.repo = ProdutoRepository()

    def listar_produtos(self):
        return self.repo.listar_todos()

    def cadastrar_produto(self, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo):
        produto = Produto(None, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo)
        self.repo.inserir(produto)

    def atualizar_produto(self, id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo):
        produto = Produto(id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo)
        self.repo.atualizar(produto)

    def deletar_produto(self, id):
        self.repo.deletar(id)
