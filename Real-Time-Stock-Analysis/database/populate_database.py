import os
import pandas as pd

from database.schema import create_tables
from database.repository import (
    insert_market_data,
    insert_model_results,
    insert_predictions,
)


MARKET_DATA_PATH = "data/processed/AAPL.csv"
MODEL_RESULTS_PATH = "reports/evaluation/backtest_results.csv"
PREDICTIONS_PATH = "reports/predictions/AAPL_predictions.csv"


def main():

    print("=" * 60)
    print("POPULATING SQLITE DATABASE")
    print("=" * 60)

    # --------------------------------------------------------
    # Create tables
    # --------------------------------------------------------

    create_tables()

    # --------------------------------------------------------
    # Market data
    # --------------------------------------------------------

    if not os.path.exists(MARKET_DATA_PATH):
        raise FileNotFoundError(
            f"Market data not found: {MARKET_DATA_PATH}"
        )

    market_data = pd.read_csv(
        MARKET_DATA_PATH,
        index_col=0,
        parse_dates=True
    )

    insert_market_data(
        market_data,
        symbol="AAPL"
    )

    print(
        f"\nMarket data inserted: "
        f"{len(market_data)} rows"
    )

    # --------------------------------------------------------
    # Model results
    # --------------------------------------------------------

    if not os.path.exists(MODEL_RESULTS_PATH):
        raise FileNotFoundError(
            f"Model results not found: "
            f"{MODEL_RESULTS_PATH}"
        )

    model_results = pd.read_csv(
        MODEL_RESULTS_PATH
    )

    insert_model_results(
        model_results
    )

    print(
        f"Model results inserted: "
        f"{len(model_results)} rows"
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    if not os.path.exists(PREDICTIONS_PATH):
        raise FileNotFoundError(
            f"Predictions not found: "
            f"{PREDICTIONS_PATH}"
        )

    predictions = pd.read_csv(
        PREDICTIONS_PATH
    )

    insert_predictions(
        predictions
    )

    print(
        f"Predictions inserted: "
        f"{len(predictions)} rows"
    )

    print("\n" + "=" * 60)
    print("DATABASE POPULATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()