import os
import pandas as pd

from data.update_pipeline import update_market_pipeline
from prediction.evaluate_predictions import evaluate_predictions
from prediction.predict import generate_predictions

from database.schema import create_tables
from database.repository import insert_market_data, insert_predictions


DATA_PATH = "data/processed/AAPL.csv"
PREDICTIONS_PATH = "reports/predictions/AAPL_predictions.csv"


def refresh_predictions(symbol="AAPL"):
    symbol = symbol.strip().upper()

    if symbol != "AAPL":
        raise ValueError("Currently only AAPL is supported.")

    print("=" * 60)
    print("STARTING FULL MARKET REFRESH")
    print("=" * 60)

    # ---------------------------------------------------------
    # STEP 1: Update market data, preprocessing, features
    # ---------------------------------------------------------
    print("\n[1/4] Updating market data pipeline...")

    update_result = update_market_pipeline(symbol)

    # ---------------------------------------------------------
    # STEP 2: Update SQLite market data
    # ---------------------------------------------------------
    print("\n[2/4] Updating database market data...")

    create_tables()

    market_data = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True
    )

    market_data = market_data.reset_index()

    insert_market_data(
        market_data,
        symbol=symbol
    )

    # ---------------------------------------------------------
    # STEP 3: Evaluate previous predictions
    # ---------------------------------------------------------
    print("\n[3/4] Evaluating previous predictions...")

    evaluation_result = evaluate_predictions(
        symbol=symbol
    )

    # ---------------------------------------------------------
    # STEP 4: Generate new predictions
    # ---------------------------------------------------------
    print("\n[4/4] Generating new predictions...")

    prediction_result = generate_predictions()

    if not os.path.exists(PREDICTIONS_PATH):
        raise FileNotFoundError(
            f"Prediction file not found: {PREDICTIONS_PATH}"
        )

    predictions = pd.read_csv(PREDICTIONS_PATH)

    insert_predictions(predictions)

    # Convert NaN values to None for JSON response
    records = predictions.to_dict(orient="records")

    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    print("\n" + "=" * 60)
    print("FULL MARKET REFRESH COMPLETED")
    print("=" * 60)

    return {
        "symbol": symbol,
        "update": update_result,
        "evaluation": evaluation_result,
        "prediction_rows": len(records),
        "predictions": records,
    }