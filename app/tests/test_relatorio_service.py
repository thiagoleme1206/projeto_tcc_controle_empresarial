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
def service(mock_conexao):
    return RelatorioService()


def test_buscar_projeto_por_os(service, mock_conexao):
    _, cursor = mock_conexao
    cursor.fetchone.return_value = ("OS123", "Cliente A", "Rua X", "Resp")

    projeto = service.buscar_projeto_por_os("OS123")
    assert projeto[0] == "OS123"
    cursor.execute.assert_called_once()
    assert "%s" in cursor.execute.call_args[0][0]


def test_buscar_dados_orcamento(service, mock_conexao):
    _, cursor = mock_conexao
    cursor.fetchone.return_value = (100, 50, 30, 20, 10, 60, 70, 80, 90, 100)

    dados = service.buscar_dados_orcamento("OS123")
    assert dados[0] == 100
    cursor.execute.assert_called_once()


def test_buscar_dados_despesas(service, mock_conexao):
    _, cursor = mock_conexao
    cursor.fetchone.return_value = (110, 55, 35, 25, 15, 65, 75, 85, 95, 105)

    dados = service.buscar_dados_despesas("OS123")
    assert dados[1] == 55
    cursor.execute.assert_called_once()


def test_criar_grafico_barras(service):
    orcamento = [100, 50, 30, 20, 10, 60, 70, 80, 90, 100]
    despesas = [110, 55, 35, 25, 15, 65, 75, 85, 95, 105]

    grafico = service.criar_grafico_barras(orcamento, despesas)
    assert grafico is not None
    assert hasattr(grafico, "add")


def test_criar_grafico_pizza_despesas(service):
    despesas = [110, 0, None, 25, 15, 65, 0, 85, None, 105]
    grafico = service.criar_grafico_pizza_despesas(despesas)
    assert grafico is not None
    assert hasattr(grafico, "add")
