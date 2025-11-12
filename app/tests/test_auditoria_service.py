
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date
from app.services.auditoria_service import AuditoriaService

@pytest.fixture
def mock_conn():
    return MagicMock()

@pytest.fixture
def service(mock_conn, monkeypatch):
    monkeypatch.setattr("app.services.auditoria_service.DatabaseConnection", lambda: MagicMock(get_connection=lambda: mock_conn))
    return AuditoriaService()

def test_registrar_acao(service, mock_conn):
    cursor = MagicMock()
    mock_conn.cursor.return_value = cursor

    service.registrar_acao("admin", "INSERT", "usuarios", "criação de novo usuário")
    cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

def test_consultar_por_usuario(service, mock_conn):
    cursor = MagicMock()
    mock_conn.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        ("admin", "INSERT", "usuarios", "criação de novo usuário", datetime.now())
    ]

    resultado = service.consultar_por_usuario("admin")
    assert resultado
    cursor.execute.assert_called_once()
    cursor.fetchall.assert_called_once()

def test_consultar_por_data(service, mock_conn):
    cursor = MagicMock()
    mock_conn.cursor.return_value = cursor
    cursor.fetchall.return_value = [
        ("admin", "DELETE", "projetos", "exclusão de projeto", datetime.now())
    ]

    resultado = service.consultar_por_data(date.today())
    assert resultado
    cursor.execute.assert_called_once()
    cursor.fetchall.assert_called_once()
