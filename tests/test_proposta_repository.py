import pytest
from unittest.mock import MagicMock
from app.models.proposta_model import Proposta
from app.repositories.proposta_repository import PropostaRepository

@pytest.fixture
def mock_conexao(monkeypatch):
    """Mocka a conexão e o cursor do banco"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Substitui DatabaseConnection
    from app.repositories import proposta_repository as repo_module
    monkeypatch.setattr(
        repo_module,
        "DatabaseConnection",
        lambda: type("FakeDB", (), {"get_connection": lambda self: mock_conn})()
    )

    return mock_conn, mock_cursor


@pytest.fixture
def repo(mock_conexao):
    return PropostaRepository()


# ==== TESTES ====

def test_inserir_chama_execute_com_dados(repo, mock_conexao):
    """ Testa se inserir() chama execute com os dados da proposta"""
    _, mock_cursor = mock_conexao
    proposta = Proposta(None, "Nova", "Descrição", 1500.0, "pendente", None)

    repo.inserir(proposta)

    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args[0]
    assert "insert into propostas" in query.lower()
    assert params == ("Nova", "Descrição", 1500.0, "pendente")
    repo.conn.commit.assert_called_once()


def test_deletar_chama_execute_com_id(repo, mock_conexao):
    """ Testa se deletar() executa com o ID correto"""
    _, mock_cursor = mock_conexao

    repo.deletar(5)

    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args[0]
    assert "delete from propostas" in query.lower()
    assert params == (5,)
    repo.conn.commit.assert_called_once()


def test_buscar_por_id_retorna_proposta(repo, mock_conexao):
    """ Testa se buscar_por_id() retorna um objeto Proposta"""
    _, mock_cursor = mock_conexao
    mock_cursor.fetchone.return_value = (1, "Título", "Desc", 999.0, "aprovada", None)

    proposta = repo.buscar_por_id(1)

    assert isinstance(proposta, Proposta)
    assert proposta.id == 1
    assert proposta.status == "aprovada"
    mock_cursor.execute.assert_called_once()


def test_listar_todas_retorna_lista(repo, mock_conexao):
    """ Testa se listar_todas() retorna uma lista de propostas"""
    _, mock_cursor = mock_conexao
    mock_cursor.fetchall.return_value = [
        (1, "A", "Desc A", 100.0, "pendente", None),
        (2, "B", "Desc B", 200.0, "aprovada", None)
    ]

    propostas = repo.listar_todas()

    assert len(propostas) == 2
    assert propostas[0].titulo == "A"
    assert propostas[1].status == "aprovada"


def test_atualizar_chama_execute_com_id(repo, mock_conexao):
    """ Testa se atualizar() executa UPDATE com ID correto"""
    _, mock_cursor = mock_conexao
    proposta = Proposta(1, "Atualizada", "Nova desc", 1234.5, "aprovada", None)

    repo.atualizar(proposta)

    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args[0]
    assert "update propostas" in query.lower()
    assert params[-1] == 1  # ID
    repo.conn.commit.assert_called_once()
