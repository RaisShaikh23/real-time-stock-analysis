import sqlite3

import pytest

from database.repository import (
    get_market_data,
    get_model_results,
    get_predictions,
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

DATABASE_PATH = "database/stock_data.db"


# ============================================================
# MARKET DATA
# ============================================================

def test_get_market_data():

    result = get_market_data("AAPL")

    assert result is not None
    assert len(result) > 0

    first_row = result[0]

    assert first_row["symbol"] == "AAPL"
    assert "date" in first_row
    assert "open" in first_row
    assert "high" in first_row
    assert "low" in first_row
    assert "close" in first_row
    assert "volume" in first_row


# ============================================================
# MODEL RESULTS
# ============================================================

def test_get_model_results():

    result = get_model_results("AAPL")

    assert result is not None
    assert len(result) > 0

    first_row = result[0]

    assert first_row["symbol"] == "AAPL"
    assert "model" in first_row
    assert "horizon" in first_row
    assert "mae" in first_row
    assert "mse" in first_row
    assert "rmse" in first_row
    assert "r2" in first_row


# ============================================================
# PREDICTIONS
# ============================================================

def test_get_predictions():

    result = get_predictions("AAPL")

    assert result is not None
    assert len(result) > 0

    first_row = result[0]

    assert first_row["symbol"] == "AAPL"
    assert "forecast_date" in first_row
    assert "horizon" in first_row
    assert "model" in first_row
    assert "predicted_price" in first_row


# ============================================================
# INVALID SYMBOL
# ============================================================

def test_invalid_symbol_returns_empty():

    result = get_market_data("INVALID_SYMBOL")

    assert result == []


# ============================================================
# DATABASE TABLES
# ============================================================

def test_database_tables_exist():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """
    )

    tables = {row[0] for row in cursor.fetchall()}

    connection.close()

    assert "market_data" in tables
    assert "model_results" in tables
    assert "predictions" in tables