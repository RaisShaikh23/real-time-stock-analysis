import pandas as pd

from database.database import (
    get_connection,
    execute_query,
    fetch_all,
    fetch_one
)


def insert_market_data(data, symbol):
    for _, row in data.iterrows():
        execute_query(
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
                symbol.upper(),
                row["Date"],
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
                row["Volume"]
            )
        )


def get_market_data(symbol="AAPL"):
    rows = fetch_all(
        """
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
        """,
        (symbol.upper(),)
    )

    return pd.DataFrame([dict(row) for row in rows])


def insert_model_results(data):
    for _, row in data.iterrows():
        execute_query(
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
                int(row["Horizon"]),
                row["MAE"],
                row["MSE"],
                row["RMSE"],
                row["R2"],
                row.get("Test_Windows")
            )
        )


def get_model_results(symbol="AAPL"):
    rows = fetch_all(
        """
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
        ORDER BY horizon, model
        """,
        (symbol.upper(),)
    )

    return pd.DataFrame([dict(row) for row in rows])


def insert_predictions(data):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        for _, row in data.iterrows():

            # Remove an existing prediction with the same
            # symbol + forecast date + horizon.
            cursor.execute(
                """
                DELETE FROM predictions
                WHERE symbol = ?
                  AND forecast_date = ?
                  AND horizon = ?
                """,
                (
                    row["Symbol"],
                    row["Forecast_Date"],
                    int(row["Horizon"])
                )
            )

            # Insert the latest prediction.
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
                    row["Forecast_Generated"],
                    row["Last_Known_Date"],
                    row["Last_Known_Close"],
                    row["Forecast_Date"],
                    int(row["Horizon"]),
                    row["Model"],
                    row["Predicted_Price"],
                    row["Actual_Price"],
                    row["Absolute_Error"],
                    row["Error_Percentage"]
                )
            )

        connection.commit()

    finally:
        connection.close()


def get_predictions(symbol="AAPL"):
    rows = fetch_all(
        """
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
        ORDER BY forecast_date, horizon
        """,
        (symbol.upper(),)
    )

    return pd.DataFrame([dict(row) for row in rows])