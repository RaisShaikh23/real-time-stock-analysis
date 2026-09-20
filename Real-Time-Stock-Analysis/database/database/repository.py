import pandas as pd

from database.database import get_connection


# ============================================================
# MARKET DATA
# ============================================================

def insert_market_data(data, symbol):
    """
    Insert OHLCV market data into the market_data table.

    Duplicate symbol/date combinations are ignored.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        for date, row in data.iterrows():

            cursor.execute(
                """
                INSERT OR IGNORE INTO market_data
                (
                    symbol,
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol,
                    pd.Timestamp(date).strftime("%Y-%m-%d"),
                    float(row["Open"]),
                    float(row["High"]),
                    float(row["Low"]),
                    float(row["Close"]),
                    float(row["Volume"]),
                )
            )

        connection.commit()

    finally:
        connection.close()


def get_market_data(symbol):
    """
    Retrieve all market data for a symbol.
    """

    connection = get_connection()

    try:
        query = """
            SELECT
                symbol,
                date,
                open,
                high,
                low,
                close,
                volume
            FROM market_data
            WHERE symbol = ?
            ORDER BY date
        """

        return pd.read_sql_query(
            query,
            connection,
            params=(symbol,)
        )

    finally:
        connection.close()


# ============================================================
# MODEL RESULTS
# ============================================================

def insert_model_results(data):
    """
    Insert model evaluation results into model_results.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        for _, row in data.iterrows():

            horizon_text = str(row["Horizon"])

            horizon = int(
                horizon_text.replace("-Day", "")
            )

            cursor.execute(
                """
                INSERT OR REPLACE INTO model_results
                (
                    symbol,
                    model,
                    horizon,
                    mae,
                    mse,
                    rmse,
                    r2,
                    test_windows
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "AAPL",
                    row["Model"],
                    horizon,
                    float(row["MAE"]),
                    float(row["MSE"]),
                    float(row["RMSE"]),
                    float(row["R2"]),
                    None,
                )
            )

        connection.commit()

    finally:
        connection.close()


def get_model_results(symbol="AAPL"):
    """
    Retrieve model evaluation results.
    """

    connection = get_connection()

    try:
        query = """
            SELECT
                symbol,
                model,
                horizon,
                mae,
                mse,
                rmse,
                r2,
                test_windows,
                created_at
            FROM model_results
            WHERE symbol = ?
            ORDER BY horizon, rmse
        """

        return pd.read_sql_query(
            query,
            connection,
            params=(symbol,)
        )

    finally:
        connection.close()


# ============================================================
# PREDICTIONS
# ============================================================

def insert_predictions(data):
    """
    Insert forecast predictions into the predictions table.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        for _, row in data.iterrows():

            cursor.execute(
                """
                INSERT INTO predictions
                (
                    symbol,
                    forecast_generated,
                    last_known_date,
                    last_known_close,
                    forecast_date,
                    horizon,
                    model,
                    predicted_price,
                    actual_price,
                    absolute_error,
                    error_percentage
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["Symbol"],
                    str(row["Forecast_Generated"]),
                    str(row["Last_Known_Date"]),
                    float(row["Last_Known_Close"]),
                    str(row["Forecast_Date"]),
                    int(row["Horizon"]),
                    row["Model"],
                    float(row["Predicted_Price"]),
                    (
                        None
                        if pd.isna(row["Actual_Price"])
                        else float(row["Actual_Price"])
                    ),
                    (
                        None
                        if pd.isna(row["Absolute_Error"])
                        else float(row["Absolute_Error"])
                    ),
                    (
                        None
                        if pd.isna(row["Error_Percentage"])
                        else float(row["Error_Percentage"])
                    ),
                )
            )

        connection.commit()

    finally:
        connection.close()


def get_predictions(symbol="AAPL"):
    """
    Retrieve predictions for a symbol.
    """

    connection = get_connection()

    try:
        query = """
            SELECT
                symbol,
                forecast_generated,
                last_known_date,
                last_known_close,
                forecast_date,
                horizon,
                model,
                predicted_price,
                actual_price,
                absolute_error,
                error_percentage,
                created_at
            FROM predictions
            WHERE symbol = ?
            ORDER BY forecast_date
        """

        return pd.read_sql_query(
            query,
            connection,
            params=(symbol,)
        )

    finally:
        connection.close()