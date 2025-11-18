import pytest
from app.services.lista_materiais_service import ListaMateriaisService
from app.models.lista_materiais_model import ListaMateriais, ItemListaMateriais
from unittest.mock import MagicMock

@pytest.fixture
def service():
    service = ListaMateriaisService()
    service.repo = MagicMock()
    return service

def test_criar_lista(service):
    item = ItemListaMateriais(None, None, 1, "Produto A", 10, "un", 5.0, "obs")
    service.repo.criar_lista.return_value = 1
    id_gerado = service.criar_lista("OS123", "João", "obs lista", [item])
    assert id_gerado == 1
    assert item.id_lista == 1
    service.repo.adicionar_item.assert_called_once_with(item)

def test_listar_listas(service):
    service.listar_listas()
    service.repo.listar_listas.assert_called_once()

def test_excluir_lista(service):
    service.excluir_lista(2)
    service.repo.excluir_lista.assert_called_once_with(2)

def test_atualizar_quantidade(service):
    service.atualizar_quantidade(10, 50)
    service.repo.atualizar_quantidade.assert_called_once_with(10, 50)

def test_adicionar_ou_atualizar_item_novo(service):
    item = ItemListaMateriais(None, 1, 1, "Produto A", 5, "un", 10.0, "")
    service.repo.buscar_item_na_lista.return_value = None
    sucesso = service.adicionar_ou_atualizar_item(item, estoque_disponivel=10)
    assert sucesso is True
    service.repo.adicionar_item.assert_called_once_with(item)
