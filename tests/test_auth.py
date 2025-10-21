import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
from app.main import app

client = TestClient(app)

def test_logout():
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["detail"] == "Вы успешно вышли из системы"

