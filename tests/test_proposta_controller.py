import pytest
from unittest.mock import MagicMock, patch, ANY
from app.controllers import proposta_controller

@pytest.fixture
def mock_usuario_vendedor():
    """Usuário com acesso total (grupo vendedor)"""
    return MagicMock(grupo="vendedor")


@pytest.fixture
def mock_usuario_engenheiro():
    """Usuário com acesso apenas para consulta"""
    return MagicMock(grupo="engenheiro")


@pytest.fixture
def setup_service(monkeypatch):
    """Mocka o PropostaService dentro do controller"""
    mock_service = MagicMock()
    monkeypatch.setattr(proposta_controller, "PropostaService", lambda: mock_service)
    return mock_service

# ==== TESTES ====
def test_listar_propostas_chamado_com_acesso_total(mock_usuario_vendedor, setup_service, monkeypatch):
    """Deve chamar listar_propostas() duas vezes por passar nos dois blocos if"""
    monkeypatch.setattr("builtins.input", lambda _: "1")

    with patch.object(proposta_controller, "listar_propostas") as mock_listar:
        proposta_controller.menu_propostas(mock_usuario_vendedor)
        assert mock_listar.call_count == 2
        assert all(call.args == (setup_service,) for call in mock_listar.call_args_list)


def test_cadastrar_proposta_chamado(mock_usuario_vendedor, setup_service, monkeypatch):
    """ Deve chamar cadastrar_proposta() quando usuário escolhe opção 2"""
    monkeypatch.setattr("builtins.input", lambda _: "2")

    with patch.object(proposta_controller, "cadastrar_proposta") as mock_cadastrar:
        proposta_controller.menu_propostas(mock_usuario_vendedor)
        mock_cadastrar.assert_called_once_with(setup_service)


def test_usuario_engenheiro_so_pode_listar(mock_usuario_engenheiro, setup_service, monkeypatch):
    """ Usuário com acesso limitado deve poder apenas listar propostas"""
    monkeypatch.setattr("builtins.input", lambda _: "1")

    with patch.object(proposta_controller, "listar_propostas") as mock_listar:
        proposta_controller.menu_propostas(mock_usuario_engenheiro)
        mock_listar.assert_called_once_with(setup_service)


def test_opcao_invalida_nao_chama_nada(mock_usuario_vendedor, setup_service, monkeypatch):
    """ Opção inválida não deve acionar nenhuma função do menu"""
    monkeypatch.setattr("builtins.input", lambda _: "99")

    with patch.object(proposta_controller, "listar_propostas") as listar, \
         patch.object(proposta_controller, "cadastrar_proposta") as cadastrar, \
         patch.object(proposta_controller, "atualizar_proposta") as atualizar, \
         patch.object(proposta_controller, "excluir_proposta") as excluir:
        
        proposta_controller.menu_propostas(mock_usuario_vendedor)

        listar.assert_not_called()
        cadastrar.assert_not_called()
        atualizar.assert_not_called()
        excluir.assert_not_called()


def test_voltar_sem_erro(mock_usuario_vendedor, setup_service, monkeypatch):
    """ Deve simplesmente retornar se a opção for 0"""
    monkeypatch.setattr("builtins.input", lambda _: "0")

    with patch("builtins.print") as mock_print:
        proposta_controller.menu_propostas(mock_usuario_vendedor)
        mock_print.assert_any_call("\n=== Módulo de Propostas ===")
