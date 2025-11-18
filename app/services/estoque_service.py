# app/services/estoque_service.py

from app.repositories.produto_repository import ProdutoRepository
from app.models.produto_model import Produto

class EstoqueService:
    def __init__(self):
        self.repo = ProdutoRepository()

    # ----------------------------
    # Validadores / Helpers
    # ----------------------------

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

    def _validate_required(self, nome, unidade):
        if not nome or not nome.strip():
            raise ValueError("❌ O nome do produto é obrigatório.")
        if not unidade or not unidade.strip():
            raise ValueError("❌ A unidade do produto é obrigatória.")

    # ----------------------------
    # Operações de Estoque
    # ----------------------------

    def listar_produtos(self):
        return self.repo.listar_todos()

    def cadastrar_produto(self, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo):
        # Validar campos obrigatórios
        self._validate_required(nome, unidade)

        produto = Produto(
            id=None,
            nome=nome.strip(),
            descricao=(descricao or "").strip(),
            quantidade=self._to_float(quantidade),
            unidade=unidade.strip(),
            preco_unitario=self._to_float(preco_unitario),
            estoque_minimo=self._to_float(estoque_minimo),
        )

        return self.repo.inserir(produto)

    def atualizar_produto(self, id, nome, descricao, quantidade, unidade, preco_unitario, estoque_minimo):
        # Validar campos obrigatórios
        self._validate_required(nome, unidade)

        produto = Produto(
            id=id,
            nome=nome.strip(),
            descricao=(descricao or "").strip(),
            quantidade=self._to_float(quantidade),
            unidade=unidade.strip(),
            preco_unitario=self._to_float(preco_unitario),
            estoque_minimo=self._to_float(estoque_minimo),
        )

        return self.repo.atualizar(produto)

    def deletar_produto(self, id):
        return self.repo.deletar(id)
