import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@patch("services.data_service.fetch_ohlcv")
def test_post_backtest_run(mock_fetch):
    # Mock de dados
    import pandas as pd
    mock_fetch.return_value = pd.DataFrame({
        "date": pd.date_range("2025-01-01", "2025-01-10"),
        "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 1000
    })

    payload = {
        "ticker": "AAPL",
        "start_date": "2025-01-01",
        "end_date": "2025-01-10",
        "strategy_type": "SMA_Cross"
    }

    response = client.post("/backtests/run", json=payload)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["status"] == "PENDING"
