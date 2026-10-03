"""
End-to-end market data update pipeline.

Flow:

1. Fetch latest market data
2. Update raw dataset
3. Validate and preprocess data
4. Generate features and targets
"""

from data.update_data import update_stock_data
from data.preprocess_data import main as preprocess_main
from features.run_features import main as features_main


def update_market_pipeline(symbol="AAPL"):
    """
    Run the complete market-data update pipeline.

    Parameters
    ----------
    symbol : str
        Stock ticker symbol.

    Returns
    -------
    dict
        Summary of the update process.
    """

    symbol = symbol.strip().upper()

    if not symbol:
        raise ValueError(
            "Stock symbol cannot be empty."
        )

    if symbol != "AAPL":
        raise ValueError(
            "Currently only AAPL is supported."
        )

    print("=" * 60)
    print("RUNNING MARKET DATA UPDATE PIPELINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Update raw market data
    # ---------------------------------------------------------

    print("\n[1/3] Updating raw market data...")

    raw_data = update_stock_data(
        symbol=symbol
    )

    # ---------------------------------------------------------
    # 2. Preprocess data
    # ---------------------------------------------------------

    print("\n[2/3] Preprocessing market data...")

    preprocess_main()

    # ---------------------------------------------------------
    # 3. Feature engineering
    # ---------------------------------------------------------

    print("\n[3/3] Running feature engineering...")

    features_main()

    print("\n" + "=" * 60)
    print("MARKET DATA UPDATE PIPELINE COMPLETED")
    print("=" * 60)

    return {
        "symbol": symbol,
        "raw_rows": len(raw_data),
        "status": "success",
    }


if __name__ == "__main__":
    update_market_pipeline()