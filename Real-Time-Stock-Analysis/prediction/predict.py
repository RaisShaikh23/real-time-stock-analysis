import os
import numpy as np
import pandas as pd

from models_store.model_persistence import load_model
from models.xgboost_model import prepare_xgboost_data


DATA_PATH = "data/processed/AAPL_features.csv"
SELECTION_PATH = "reports/evaluation/final_model_selection.csv"
OUTPUT_PATH = "reports/predictions/AAPL_predictions.csv"
MODEL_DIRECTORY = "models_store"


def load_stock_data():
    """Load feature-engineered stock data."""

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Feature dataset not found: {DATA_PATH}"
        )

    return pd.read_csv(
        DATA_PATH,
        index_col=0,
        parse_dates=True
    )


def load_model_selection():
    """Load the selected model for each horizon."""

    if not os.path.exists(SELECTION_PATH):
        raise FileNotFoundError(
            f"Model selection file not found: {SELECTION_PATH}"
        )

    selection = pd.read_csv(SELECTION_PATH)

    required_columns = [
        "Horizon",
        "Selected_Model"
    ]

    missing = [
        column
        for column in required_columns
        if column not in selection.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    return selection


def get_future_business_dates(last_date, horizon):
    """Generate approximate future business dates."""

    return pd.bdate_range(
        start=last_date + pd.Timedelta(days=1),
        periods=horizon
    )


def get_saved_model_name(model_name, horizon):
    """Build the saved model filename."""

    return f"AAPL_{model_name}_{horizon}day"


def forecast_with_saved_model(
    data,
    model,
    model_name,
    horizon
):
    """Generate a forecast using a loaded model."""

    if model_name == "XGBoost":

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

    elif model_name == "SARIMA":

        forecast = model.forecast(
            steps=horizon
        )

        return np.asarray(
            forecast,
            dtype=float
        )

    elif model_name == "Prophet":

        future_dates = get_future_business_dates(
            data.index[-1],
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
            f"Unsupported model: {model_name}"
        )


def generate_predictions():

    print("=" * 60)
    print("GENERATING PREDICTIONS USING SAVED MODELS")
    print("=" * 60)

    data = load_stock_data()
    selection = load_model_selection()

    print("\nDataset shape:")
    print(data.shape)

    last_date = data.index[-1]
    last_close = float(
        data["Close"].iloc[-1]
    )

    print(
        f"\nLatest available date: {last_date}"
    )

    print(
        f"Latest Close: {last_close:.4f}"
    )

    results = []

    for _, row in selection.iterrows():

        horizon_text = str(row["Horizon"])
        horizon = int(
            horizon_text.replace("-Day", "")
        )

        model_name = str(
            row["Selected_Model"]
        )

        saved_model_name = get_saved_model_name(
            model_name,
            horizon
        )

        print(
            f"\nLoading {saved_model_name}..."
        )

        model = load_model(
            saved_model_name,
            directory=MODEL_DIRECTORY
        )

        forecast = forecast_with_saved_model(
            data=data,
            model=model,
            model_name=model_name,
            horizon=horizon
        )

        if model_name == "XGBoost":
            predicted_price = float(
                forecast[0]
            )
        else:
            predicted_price = float(
                forecast[horizon - 1]
            )

        future_dates = get_future_business_dates(
            last_date,
            horizon
        )

        forecast_date = future_dates[
            horizon - 1
        ]

        results.append({
            "Symbol": "AAPL",
            "Forecast_Generated": pd.Timestamp.now(),
            "Last_Known_Date": last_date,
            "Last_Known_Close": last_close,
            "Forecast_Date": forecast_date,
            "Horizon": horizon,
            "Model": model_name,
            "Predicted_Price": predicted_price,
            "Actual_Price": np.nan,
            "Absolute_Error": np.nan,
            "Error_Percentage": np.nan,
        })

        print(
            f"Forecast: {predicted_price:.4f}"
        )

    results = pd.DataFrame(results)

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n" + "=" * 60)
    print("FINAL PREDICTIONS")
    print("=" * 60)

    print(
        results[
            [
                "Symbol",
                "Forecast_Date",
                "Horizon",
                "Model",
                "Predicted_Price",
                "Actual_Price",
                "Absolute_Error",
                "Error_Percentage",
            ]
        ].to_string(index=False)
    )

    print("\nPredictions saved to:")
    print(OUTPUT_PATH)

    return results


if __name__ == "__main__":
    generate_predictions()