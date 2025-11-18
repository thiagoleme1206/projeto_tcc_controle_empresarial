import pytest
from unittest.mock import MagicMock
from app.services.proposta_service import PropostaService
from app.models.proposta_model import Proposta

@pytest.fixture
def mock_repo(monkeypatch):
    """Mocka o repositório dentro do serviço"""
    mock_repo = MagicMock()
    from app.services import proposta_service as service_module
    monkeypatch.setattr(service_module, "PropostaRepository", lambda: mock_repo)
    return mock_repo


@pytest.fixture
def service(mock_repo):
    """Instancia o serviço com o repositório mockado"""
    return PropostaService()


def test_listar_propostas(service, mock_repo):
    """ Testa se listar_propostas() retorna o que o repositório devolver"""
    proposta = Proposta(1, "Projeto A", "Desc", 5000.0, "pendente", None)
    mock_repo.listar_todas.return_value = [proposta]

    resultado = service.listar_propostas()

    assert len(resultado) == 1
    assert resultado[0].titulo == "Projeto A"
    mock_repo.listar_todas.assert_called_once()


def test_cadastrar_proposta(service, mock_repo):
    """ Testa se cadastrar_proposta() cria objeto Proposta e envia ao repo"""
    service.cadastrar_proposta("Novo", "Descrição", 1000.0, "aprovada")

    assert mock_repo.inserir.called
    proposta_inserida = mock_repo.inserir.call_args[0][0]
    assert isinstance(proposta_inserida, Proposta)
    assert proposta_inserida.titulo == "Novo"
    assert proposta_inserida.valor == 1000.0
    assert proposta_inserida.status == "aprovada"


def test_atualizar_proposta(service, mock_repo):
    """ Testa se atualizar_proposta() cria objeto Proposta com ID e atualiza via repo"""
    service.atualizar_proposta(1, "Atualizada", "Nova desc", 2000.0, "pendente")

    assert mock_repo.atualizar.called
    proposta_atualizada = mock_repo.atualizar.call_args[0][0]
    assert proposta_atualizada.id == 1
    assert proposta_atualizada.titulo == "Atualizada"
    assert proposta_atualizada.valor == 2000.0


def test_deletar_proposta(service, mock_repo):
    """ Testa se deletar_proposta() chama o repo com o ID correto"""
    service.deletar_proposta(7)
    mock_repo.deletar.assert_called_once_with(7)


def test_cadastrar_proposta_com_valores_limite(service, mock_repo):
    """ Testa o cadastro com valores extremos (ex: valor zero)"""
    service.cadastrar_proposta("Zerada", "Sem valor", 0.0, "pendente")
    proposta = mock_repo.inserir.call_args[0][0]
    assert proposta.valor == 0.0
