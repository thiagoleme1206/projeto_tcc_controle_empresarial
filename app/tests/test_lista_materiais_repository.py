import pytest
from unittest.mock import MagicMock
from app.models.lista_materiais_model import ListaMateriais, ItemListaMateriais
from app.repositories.lista_materiais_repository import ListaMateriaisRepository

@pytest.fixture
def mock_conexao(monkeypatch):
    """Mocka a conexão e cursor do banco"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Substitui DatabaseConnection no módulo do repositório
    from app.repositories import lista_materiais_repository as repo_module
    monkeypatch.setattr(
        repo_module,
        "DatabaseConnection",
        lambda: type("FakeConn", (), {"get_connection": lambda self: mock_conn})()
    )

    return mock_conn, mock_cursor

@pytest.fixture
def repo(mock_conexao):
    """Cria instância do repositório com mock aplicado"""
    return ListaMateriaisRepository()


# ==== TESTES ====
def test_criar_lista(repo, mock_conexao):
    """ Deve executar INSERT ao criar uma lista"""
    _, cursor = mock_conexao
    cursor.fetchone.return_value = [1]

    lista = ListaMateriais(None, "OS123", "João", "obs", None)
    id_gerado = repo.criar_lista(lista)

    assert id_gerado == 1
    cursor.execute.assert_called_once()
    assert "insert into lista_materiais" in cursor.execute.call_args[0][0].lower()
    repo.conn.commit.assert_called_once()


def test_adicionar_item(repo, mock_conexao):
    """ Deve inserir um item na lista"""
    _, cursor = mock_conexao

    item = ItemListaMateriais(None, 1, 2, "Produto X", 10, "un", 5.5, "obs item")
    repo.adicionar_item(item)

    cursor.execute.assert_called_once()
    query, params = cursor.execute.call_args[0]
    assert "insert into itens_lista_materiais" in query.lower()
    assert params[0] == 1
    assert params[2] == "Produto X"
    repo.conn.commit.assert_called_once()


def test_listar_listas(repo, mock_conexao):
    """ Deve retornar lista de objetos ListaMateriais"""
    _, cursor = mock_conexao
    cursor.fetchall.return_value = [
        (1, "OS01", "Ana", "teste", "2025-11-11"),
        (2, "OS02", "Carlos", "obs", "2025-11-11")
    ]

    listas = repo.listar_listas()

    assert len(listas) == 2
    assert listas[0].os_referencia == "OS01"
    cursor.execute.assert_called_once()


def test_buscar_itens_por_lista(repo, mock_conexao):
    """ Deve retornar itens da lista"""
    _, cursor = mock_conexao
    cursor.fetchall.return_value = [
        (1, 1, 10, "Produto A", 2, "un", 5.0, "obs"),
        (2, 1, 11, "Produto B", 4, "cx", 8.0, "ok"),
    ]

    itens = repo.buscar_itens_por_lista(1)

    assert len(itens) == 2
    assert itens[1].nome_produto == "Produto B"
    cursor.execute.assert_called_once()


def test_atualizar_quantidade(repo, mock_conexao):
    """ Deve executar UPDATE de quantidade"""
    _, cursor = mock_conexao
    repo.atualizar_quantidade(1, 50)
    cursor.execute.assert_called_once()
    query, params = cursor.execute.call_args[0]
    assert "update itens_lista_materiais" in query.lower()
    assert params == (50, 1)
    repo.conn.commit.assert_called_once()


def test_remover_item(repo, mock_conexao):
    """ Deve deletar item por ID"""
    _, cursor = mock_conexao
    repo.remover_item(3)
    cursor.execute.assert_called_once()
    query, params = cursor.execute.call_args[0]
    assert "delete from itens_lista_materiais" in query.lower()
    assert params == (3,)
    repo.conn.commit.assert_called_once()
