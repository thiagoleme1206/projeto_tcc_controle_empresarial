import pytest
from unittest.mock import MagicMock
from app.services.estoque_service import EstoqueService
from app.models.produto_model import Produto

@pytest.fixture
def mock_repo():
    """Cria um repositório mockado"""
    repo = MagicMock()
    return repo

@pytest.fixture
def estoque_service(mock_repo, monkeypatch):
    """Substitui o ProdutoRepository dentro do EstoqueService por um mock"""
    from app.services import estoque_service as estoque_service_module
    monkeypatch.setattr(estoque_service_module, "ProdutoRepository", lambda: mock_repo)
    return EstoqueService()

def test_listar_produtos(estoque_service, mock_repo):
    # Se o serviço retorna a lista corretamente
    produto = Produto(1, "Caneta", "Caneta azul", 100, "un", 2.5, 10)
    mock_repo.listar_todos.return_value = [produto]

    resultado = estoque_service.listar_produtos()

    assert len(resultado) == 1
    assert resultado[0].nome == "Caneta"
    mock_repo.listar_todos.assert_called_once()

def test_cadastrar_produto(estoque_service, mock_repo):
    # Se repo.inserir() é chamado corretamente
    estoque_service.cadastrar_produto("Lápis", "Lápis HB", 200, "un", 1.5, 20)

    assert mock_repo.inserir.called
    args = mock_repo.inserir.call_args[0]
    produto_inserido = args[0]
    assert produto_inserido.nome == "Lápis"
    assert produto_inserido.quantidade == 200

def test_atualizar_produto(estoque_service, mock_repo):
    # Se repo.atualizar() é chamado com os dados certos
    estoque_service.atualizar_produto(1, "Borracha", "Borracha branca", 50, "un", 0.75, 5)

    assert mock_repo.atualizar.called
    args = mock_repo.atualizar.call_args[0]
    produto_atualizado = args[0]
    assert produto_atualizado.id == 1
    assert produto_atualizado.nome == "Borracha"

def test_deletar_produto(estoque_service, mock_repo):
    # Se repo.deletar() é chamado com o ID correto
    estoque_service.deletar_produto(5)

    mock_repo.deletar.assert_called_once_with(5)

def test_cadastrar_produto_valores_extremos(estoque_service, mock_repo):
    # Testa valores atípicos, como preço muito alto e quantidade zero
    estoque_service.cadastrar_produto("Super Produto", "Descrição", 0, "kg", 99999.99, 0)

    assert mock_repo.inserir.called
