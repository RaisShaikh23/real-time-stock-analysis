import os
import pandas as pd

from prediction.pipeline import main as run_pipeline
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

    # ============================================================
    # 1. Make sure database tables exist
    # ============================================================

    create_tables()

    # ============================================================
    # 2. Run complete prediction pipeline
    #
    #    This performs:
    #    - Evaluation of pending predictions
    #    - Generation of new predictions
    # ============================================================

    run_pipeline()

    # ============================================================
    # 3. Check prediction file
    # ============================================================

    if not os.path.exists(PREDICTIONS_PATH):
        raise FileNotFoundError(
            f"Prediction file not found: {PREDICTIONS_PATH}"
        )

    # ============================================================
    # 4. Load generated predictions
    # ============================================================

    predictions = pd.read_csv(
        PREDICTIONS_PATH
    )

    # ============================================================
    # 5. Insert new predictions into SQLite
    # ============================================================

    insert_predictions(predictions)

    # ============================================================
    # 6. Convert DataFrame to JSON-safe records
    #    NaN -> None -> JSON null
    # ============================================================

    records = predictions.to_dict(
        orient="records"
    )

    for record in records:
        for key, value in record.items():

            if pd.isna(value):
                record[key] = None

    # ============================================================
    # 7. Return API response
    # ============================================================

    return {
        "symbol": symbol,
        "prediction_rows": len(records),
        "predictions": records
    }