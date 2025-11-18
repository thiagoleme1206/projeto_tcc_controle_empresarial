import pytest
from unittest.mock import MagicMock, patch, ANY
from app.controllers import estoque_controller

@pytest.fixture
def mock_usuario_estoquista():
    """Usuário com permissões completas de estoque"""
    return MagicMock(grupo="estoquista", login="user1")


@pytest.fixture
def mock_usuario_restrito():
    """Usuário sem permissões administrativas"""
    return MagicMock(grupo="vendedor", login="user2")


@pytest.fixture
def setup_services(monkeypatch):
    """Mocka os serviços usados no controller"""
    mock_service = MagicMock()
    mock_auditoria = MagicMock()
    monkeypatch.setattr(estoque_controller, "EstoqueService", lambda: mock_service)
    monkeypatch.setattr(estoque_controller, "AuditoriaService", lambda: mock_auditoria)
    return mock_service, mock_auditoria


def test_listar_produtos_chamado_para_estoquista(mock_usuario_estoquista, setup_services, monkeypatch):
    """ Deve chamar listar_produtos() ao escolher a opção 1"""
    mock_service, _ = setup_services
    monkeypatch.setattr("builtins.input", lambda _: "1")

    with patch.object(estoque_controller, "listar_produtos") as mock_listar:
        estoque_controller.menu_estoque(mock_usuario_estoquista)
        mock_listar.assert_called_once_with(mock_service, mock_usuario_estoquista, ANY)


def test_cadastrar_produto_chamado(mock_usuario_estoquista, setup_services, monkeypatch):
    """ Deve chamar cadastrar_produto() quando opção 2 é escolhida"""
    mock_service, mock_auditoria = setup_services
    monkeypatch.setattr("builtins.input", lambda _: "2")

    with patch.object(estoque_controller, "cadastrar_produto") as mock_cadastrar:
        estoque_controller.menu_estoque(mock_usuario_estoquista)
        mock_cadastrar.assert_called_once_with(mock_service, mock_usuario_estoquista, mock_auditoria)


def test_usuario_restrito_so_pode_listar(mock_usuario_restrito, setup_services, monkeypatch):
    """ Usuário sem permissão total deve ver apenas opção 1 e 0"""
    mock_service, _ = setup_services
    monkeypatch.setattr("builtins.input", lambda _: "1")

    with patch.object(estoque_controller, "listar_produtos") as mock_listar:
        estoque_controller.menu_estoque(mock_usuario_restrito)
        mock_listar.assert_called_once_with(mock_service)


def test_opcao_invalida_imprime_erro(mock_usuario_estoquista, setup_services, monkeypatch):
    """ Deve imprimir mensagem de erro se a opção for inválida"""
    monkeypatch.setattr("builtins.input", lambda _: "99")

    with patch("builtins.print") as mock_print:
        estoque_controller.menu_estoque(mock_usuario_estoquista)
        mock_print.assert_any_call("❌ Opção inválida.")


def test_voltar_ao_escolher_zero(mock_usuario_estoquista, setup_services, monkeypatch):
    """ Deve simplesmente retornar quando a opção for 0"""
    monkeypatch.setattr("builtins.input", lambda _: "0")

    with patch.object(estoque_controller, "listar_produtos") as mock_listar:
        estoque_controller.menu_estoque(mock_usuario_estoquista)
        mock_listar.assert_not_called()
