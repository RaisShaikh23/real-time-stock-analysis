import os
import pandas as pd

from prediction.predict import generate_predictions
from database.schema import create_tables
from database.repository import insert_predictions


DATA_PATH = "data/processed/AAPL_features.csv"
PREDICTIONS_PATH = "reports/predictions/AAPL_predictions.csv"


def refresh_predictions(symbol="AAPL"):
    symbol = symbol.upper()

    if symbol != "AAPL":
        raise ValueError("Currently only AAPL is supported.")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Feature dataset not found: {DATA_PATH}"
        )

    # Make sure database tables exist
    create_tables()

    # Generate fresh predictions using saved models
    generate_predictions()

    # Check prediction file
    if not os.path.exists(PREDICTIONS_PATH):
        raise FileNotFoundError(
            f"Prediction file not found: {PREDICTIONS_PATH}"
        )

    # Load generated predictions
    predictions = pd.read_csv(PREDICTIONS_PATH)

    # Insert predictions into SQLite
    insert_predictions(predictions)

    # Convert DataFrame to JSON-safe records.
    # NaN -> None, which becomes JSON null.
    records = predictions.to_dict(orient="records")

    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    return {
        "symbol": symbol,
        "prediction_rows": len(records),
        "predictions": records
    }