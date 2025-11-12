
import pytest
from unittest.mock import MagicMock
from app.services.relatorio_service import RelatorioService


@pytest.fixture
def mock_conexao(monkeypatch):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    from app.services import relatorio_service as service_module
    monkeypatch.setattr(
        service_module,
        "DatabaseConnection",
        lambda: type("FakeConn", (), {"get_connection": lambda self: mock_conn})()
    )
    return mock_conn, mock_cursor


@pytest.fixture
def repository(mock_conexao):
    return RelatorioService()


def test_buscar_projeto_por_os(repository, mock_conexao):
    _, cursor = mock_conexao
    cursor.fetchone.return_value = ("OS001", "Cliente Exemplo", "Rua Projetada", "Eng. Carlos")

    resultado = repository.buscar_projeto_por_os("OS001")
    assert resultado[0] == "OS001"
    cursor.execute.assert_called_once()
    assert "%s" in cursor.execute.call_args[0][0]


def test_buscar_dados_orcamento(repository, mock_conexao):
    _, cursor = mock_conexao
    cursor.fetchone.return_value = (10, 20, 30, 40, 50, 60, 70, 80, 90, 100)

    resultado = repository.buscar_dados_orcamento("OS001")
    assert isinstance(resultado, tuple)
    assert resultado[0] == 10


def test_buscar_dados_despesas(repository, mock_conexao):
    _, cursor = mock_conexao
    cursor.fetchone.return_value = (15, 25, 35, 45, 55, 65, 75, 85, 95, 105)

    resultado = repository.buscar_dados_despesas("OS001")
    assert resultado[1] == 25
    cursor.execute.assert_called_once()
