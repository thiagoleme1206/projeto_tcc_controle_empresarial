import pytest
from unittest.mock import MagicMock
from app.models.produto_model import Produto
from app.repositories.produto_repository import ProdutoRepository

@pytest.fixture
def mock_conexao(monkeypatch):
    # Cria mocks para a conexão e cursor
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock da DatabaseConnection
    from app.repositories import produto_repository as repo_module
    monkeypatch.setattr(
        repo_module,
        "DatabaseConnection",
        lambda: type("FakeDB", (), {"get_connection": lambda self: mock_conn})()
    )

    return mock_conn, mock_cursor

@pytest.fixture
def repo(mock_conexao):
    return ProdutoRepository()

def test_inserir_chama_execute_com_dados(repo, mock_conexao):
    #Testa se o método `inserir()` do repositório chama `execute()` corretamente
    # com os dados esperados para inserir um produto.
    _, mock_cursor = mock_conexao
    produto = Produto(None, "Caneta", "Azul", 100, "un", 2.5, 10)
    
    repo.inserir(produto)

    assert mock_cursor.execute.called
    assert mock_cursor.execute.call_args[0][0].strip().lower().startswith("insert into produtos")
    assert mock_cursor.execute.call_args[0][1] == ("Caneta", "Azul", 100, "un", 2.5, 10)
    assert repo.conn.commit.called

def test_deletar_chama_execute_com_id(repo, mock_conexao):
    #Testa se o método `deletar()` executa uma query DELETE corretamente
    # passando o ID correto e chamando `conn.commit()`.
    _, mock_cursor = mock_conexao

    repo.deletar(7)

    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args[0]
    assert "delete from produtos" in query.lower()
    assert params == (7,)
    assert repo.conn.commit.called

def test_buscar_por_id_executa_com_id(repo, mock_conexao):
    # Testa se o método `buscar_por_id()` executa a query corretamente com o ID
    # e converte o resultado em um objeto `Produto`.
    _, mock_cursor = mock_conexao

    mock_cursor.fetchone.return_value = (1, "Caneta", "Azul", 100, "un", 2.5, 10, None)

    produto = repo.buscar_por_id(1)

    mock_cursor.execute.assert_called_once()
    assert produto.nome == "Caneta"
    assert produto.quantidade == 100

def test_atualizar_produto_executa_com_id(repo, mock_conexao):
    # Testa se o método `atualizar()` chama `cursor.execute()` com uma query UPDATE
    # e garante que o ID do produto é passado corretamente como último parâmetro.
    _, mock_cursor = mock_conexao
    produto = Produto(1, "Caneta Azul", "Caneta Bic", 200, "un", 3.0, 5)

    repo.atualizar(produto)

    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args[0]
    assert "update produtos" in query.lower()
    assert params[-1] == 1
    assert repo.conn.commit.called

def test_listar_todos_retorna_lista(repo, mock_conexao):
    # Testa se o método `listar_todos()` interpreta corretamente os dados vindos do banco
    # e retorna uma lista de objetos `Produto`.
    _, mock_cursor = mock_conexao

    mock_cursor.fetchall.return_value = [
        (1, "Lápis", "HB", 10, "un", 1.0, 2, None),
        (2, "Caneta", "Azul", 20, "un", 2.0, 5, None),
    ]

    produtos = repo.listar_todos()

    assert len(produtos) == 2
    assert produtos[0].nome == "Lápis"
    assert produtos[1].nome == "Caneta"
