import pandas as pd

from database.repository import (
    get_pending_predictions,
    get_market_data,
    update_prediction_evaluation,
)


def evaluate_predictions(symbol="AAPL"):

    print("=" * 60)
    print("PREDICTION EVALUATION")
    print("=" * 60)

    predictions = get_pending_predictions(symbol)
    market_data = get_market_data(symbol)

    print(f"\nPending predictions: {len(predictions)}")
    print(f"Market records available: {len(market_data)}")

    if predictions.empty:
        print("\nNo pending predictions.")
        return []

    results = []

    # Make sure dates are comparable
    market_data["date"] = pd.to_datetime(
        market_data["date"]
    ).dt.strftime("%Y-%m-%d")

    for _, prediction in predictions.iterrows():

        forecast_date = pd.to_datetime(
            prediction["forecast_date"]
        ).strftime("%Y-%m-%d")

        horizon = int(prediction["horizon"])
        model = prediction["model"]
        predicted_price = float(
            prediction["predicted_price"]
        )

        print(
            f"\n{forecast_date} | "
            f"{horizon}-Day | "
            f"{model}"
        )

        actual_rows = market_data[
            market_data["date"] == forecast_date
        ]

        if actual_rows.empty:

            print("Actual price: NOT AVAILABLE")

            results.append({
                "forecast_date": forecast_date,
                "horizon": horizon,
                "model": model,
                "predicted_price": predicted_price,
                "actual_price": None,
                "absolute_error": None,
                "error_percentage": None,
                "status": "Pending",
            })

            continue

        actual_price = float(
            actual_rows.iloc[0]["close"]
        )

        absolute_error = abs(
            predicted_price - actual_price
        )

        error_percentage = (
            absolute_error / actual_price
        ) * 100

        updated_rows = update_prediction_evaluation(
            symbol=symbol,
            forecast_date=forecast_date,
            horizon=horizon,
            model=model,
            actual_price=actual_price,
            absolute_error=absolute_error,
            error_percentage=error_percentage,
        )

        print(
            f"Actual price: {actual_price:.4f}"
        )

        print(
            f"Absolute error: "
            f"{absolute_error:.4f}"
        )

        print(
            f"Error percentage: "
            f"{error_percentage:.4f}%"
        )

        print(
            f"Database rows updated: "
            f"{updated_rows}"
        )

        results.append({
            "forecast_date": forecast_date,
            "horizon": horizon,
            "model": model,
            "predicted_price": predicted_price,
            "actual_price": actual_price,
            "absolute_error": absolute_error,
            "error_percentage": error_percentage,
            "status": "Evaluated",
        })

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)

    evaluated = sum(
        1 for result in results
        if result["status"] == "Evaluated"
    )

    pending = sum(
        1 for result in results
        if result["status"] == "Pending"
    )

    print(f"\nTotal predictions: {len(results)}")
    print(f"Predictions updated: {evaluated}")
    print(f"Predictions pending: {pending}")

    return results

if __name__ == "__main__":
    evaluate_predictions("AAPL")