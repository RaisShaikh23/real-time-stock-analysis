import os
import numpy as np
import pandas as pd

from models_store.model_persistence import load_model
from models.xgboost_model import prepare_xgboost_data


DATA_PATH = "data/processed/AAPL_features.csv"
MODEL_DIRECTORY = "models_store"


SELECTED_MODELS = {
    1: "AAPL_SARIMA_1day",
    3: "AAPL_SARIMA_3day",
    10: "AAPL_XGBoost_10day",
    15: "AAPL_Prophet_15day",
}


def load_stock_data():
    """Load the latest feature-engineered stock data."""

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Feature dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True
    )

    return data


def get_future_business_dates(last_date, horizon):
    """
    Generate future business dates for a forecast horizon.

    Note:
    This uses business days as an approximation to trading days.
    """

    return pd.bdate_range(
        start=last_date + pd.Timedelta(days=1),
        periods=horizon
    )


def forecast_with_saved_model(data, horizon, model_name):
    """
    Generate a forecast using a previously saved model.
    """

    model = load_model(
        model_name,
        directory=MODEL_DIRECTORY
    )

    if model_name.startswith("AAPL_XGBoost"):

        X, _ = prepare_xgboost_data(
            data,
            horizon=horizon
        )

        latest_features = X.iloc[[-1]]

        prediction = model.predict(
            latest_features
        )

        return np.asarray(
            prediction,
            dtype=float
        )

    elif model_name.startswith("AAPL_SARIMA"):

        forecast = model.forecast(
            steps=horizon
        )

        return np.asarray(
            forecast,
            dtype=float
        )

    elif model_name.startswith("AAPL_Prophet"):

        last_date = data.index[-1]

        future_dates = get_future_business_dates(
            last_date,
            horizon
        )

        future = pd.DataFrame({
            "ds": future_dates
        })

        forecast = model.predict(future)

        return np.asarray(
            forecast["yhat"],
            dtype=float
        )

    else:
        raise ValueError(
            f"Unsupported saved model: {model_name}"
        )


def generate_saved_model_predictions():

    print("=" * 60)
    print("SAVED MODEL PREDICTION")
    print("=" * 60)

    data = load_stock_data()

    print("\nDataset shape:")
    print(data.shape)

    last_date = data.index[-1]
    last_close = float(data["Close"].iloc[-1])

    print(f"\nLatest available date: {last_date}")
    print(f"Latest Close: {last_close:.4f}")

    results = []

    for horizon, model_name in SELECTED_MODELS.items():

        print(
            f"\nLoading {model_name}..."
        )

        forecast = forecast_with_saved_model(
            data=data,
            horizon=horizon,
            model_name=model_name
        )

        # XGBoost returns one direct prediction.
        # SARIMA and Prophet return a forecast path.
        if model_name.startswith("AAPL_XGBoost"):
            predicted_price = float(forecast[0])
        else:
            predicted_price = float(
                forecast[horizon - 1]
            )

        future_dates = get_future_business_dates(
            last_date,
            horizon
        )

        forecast_date = future_dates[horizon - 1]

        results.append({
            "Symbol": "AAPL",
            "Forecast_Generated": pd.Timestamp.now(),
            "Last_Known_Date": last_date,
            "Last_Known_Close": last_close,
            "Forecast_Date": forecast_date,
            "Horizon": horizon,
            "Model": model_name.replace(
                "AAPL_", ""
            ),
            "Predicted_Price": predicted_price,
            "Actual_Price": np.nan,
            "Absolute_Error": np.nan,
            "Error_Percentage": np.nan,
        })

        print(
            f"Forecast: {predicted_price:.4f}"
        )

    results = pd.DataFrame(results)

    print("\n" + "=" * 60)
    print("FINAL SAVED-MODEL PREDICTIONS")
    print("=" * 60)

    print(
        results[
            [
                "Forecast_Date",
                "Horizon",
                "Model",
                "Predicted_Price",
            ]
        ].to_string(index=False)
    )

    return results


if __name__ == "__main__":
    generate_saved_model_predictions()