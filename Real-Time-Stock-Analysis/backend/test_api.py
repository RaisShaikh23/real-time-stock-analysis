import pytest
from fastapi.testclient import TestClient

from backend.api import app


client = TestClient(app)


# ============================================================
# HEALTH CHECK
# ============================================================

def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert "message" in data


# ============================================================
# STOCK DATA
# ============================================================

def test_get_stock_data():

    response = client.get("/stocks/AAPL/data")

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "AAPL"
    assert data["rows"] > 0
    assert isinstance(data["data"], list)

    assert len(data["data"]) > 0

    first_row = data["data"][0]

    assert "symbol" in first_row
    assert "date" in first_row
    assert "open" in first_row
    assert "high" in first_row
    assert "low" in first_row
    assert "close" in first_row
    assert "volume" in first_row


# ============================================================
# MODEL RESULTS
# ============================================================

def test_get_models():

    response = client.get(
        "/models",
        params={"symbol": "AAPL"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "AAPL"
    assert data["rows"] > 0
    assert isinstance(data["models"], list)

    first_model = data["models"][0]

    assert "model" in first_model
    assert "horizon" in first_model
    assert "mae" in first_model
    assert "mse" in first_model
    assert "rmse" in first_model
    assert "r2" in first_model


# ============================================================
# PREDICTIONS
# ============================================================

def test_get_predictions():

    response = client.get(
        "/prediction",
        params={"symbol": "AAPL"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "AAPL"
    assert data["rows"] > 0
    assert isinstance(data["predictions"], list)

    first_prediction = data["predictions"][0]

    assert "symbol" in first_prediction
    assert "forecast_date" in first_prediction
    assert "horizon" in first_prediction
    assert "model" in first_prediction
    assert "predicted_price" in first_prediction


# ============================================================
# METRICS
# ============================================================

def test_get_metrics():

    response = client.get(
        "/metrics",
        params={"symbol": "AAPL"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "AAPL"
    assert data["rows"] > 0
    assert isinstance(data["metrics"], list)

    first_metric = data["metrics"][0]

    assert "model" in first_metric
    assert "horizon" in first_metric
    assert "mae" in first_metric
    assert "mse" in first_metric
    assert "rmse" in first_metric
    assert "r2" in first_metric


# ============================================================
# INVALID STOCK SYMBOL
# ============================================================

def test_invalid_stock_symbol():

    response = client.get(
        "/stocks/INVALID_SYMBOL/data"
    )

    assert response.status_code == 404


# ============================================================
# CASE INSENSITIVITY
# ============================================================

def test_stock_symbol_case_insensitive():

    response = client.get(
        "/stocks/aapl/data"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["symbol"] == "AAPL"