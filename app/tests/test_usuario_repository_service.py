
import pytest
from unittest.mock import MagicMock, patch
from app.services.usuario_service import UsuarioService
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario_model import Usuario

# Testes de Service
@patch("app.services.usuario_service.DatabaseConnection")
def test_criar_usuario(mock_db):
    mock_conn = MagicMock()
    mock_db.return_value.get_connection.return_value = mock_conn
    service = UsuarioService()
    service.criar_usuario("João", "joao123", "senha123", "vendedor")
    cursor = mock_conn.cursor.return_value
    cursor.execute.assert_called()
    mock_conn.commit.assert_called()

@patch("app.services.usuario_service.DatabaseConnection")
def test_alterar_usuario_nome(mock_db):
    mock_conn = MagicMock()
    mock_db.return_value.get_connection.return_value = mock_conn
    service = UsuarioService()
    service.alterar_usuario("joao123", nome="João da Silva")
    cursor = mock_conn.cursor.return_value
    cursor.execute.assert_called()
    mock_conn.commit.assert_called()

@patch("app.services.usuario_service.DatabaseConnection")
def test_ativar_inativar_usuario(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [(1,), None]  # Simula usuário existente e inexistente
    mock_db.return_value.get_connection.return_value = mock_conn

    service = UsuarioService()
    service.ativar_inativar_usuario("joao123", True)
    mock_conn.commit.assert_called()

    with pytest.raises(ValueError):
        service.ativar_inativar_usuario("nao_existe", True)

@patch("app.services.usuario_service.DatabaseConnection")
def test_excluir_usuario(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)
    mock_db.return_value.get_connection.return_value = mock_conn

    service = UsuarioService()
    service.excluir_usuario("joao123")
    mock_conn.commit.assert_called()

@patch("app.services.usuario_service.DatabaseConnection")
def test_consultar_usuarios(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, "João", "joao123", "hash", "vendedor", True)]
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value.get_connection.return_value = mock_conn

    service = UsuarioService()
    usuarios = service.consultar_usuarios(ativo=True)
    assert len(usuarios) == 1

# Teste de Repository
@patch("app.repositories.usuario_repository.DatabaseConnection")
def test_usuario_repository_buscar_por_login(mock_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1, "João", "joao123", "hash", "vendedor", True)
    mock_conn.cursor.return_value = mock_cursor
    mock_db.return_value.get_connection.return_value = mock_conn

    repo = UsuarioRepository()
    usuario = repo.buscar_por_login("joao123")
    assert usuario.login == "joao123"
