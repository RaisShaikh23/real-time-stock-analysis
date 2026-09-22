from database.repository import (
    get_market_data,
    get_model_results,
    get_predictions
)


def main():

    print("=" * 60)
    print("DATABASE VERIFICATION")
    print("=" * 60)

    # Market data
    market_data = get_market_data("AAPL")

    print("\n1. MARKET DATA")
    print(f"Rows: {len(market_data)}")
    print(market_data.head())

    # Model results
    model_results = get_model_results("AAPL")

    print("\n2. MODEL RESULTS")
    print(f"Rows: {len(model_results)}")
    print(model_results)

    # Predictions
    predictions = get_predictions("AAPL")

    print("\n3. PREDICTIONS")
    print(f"Rows: {len(predictions)}")
    print(predictions)

    print("\n" + "=" * 60)
    print("DATABASE VERIFICATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()