import os
import pandas as pd

from models.sarima_model import fit_sarima
from models.xgboost_model import fit_xgboost
from models.prophet_model import fit_prophet
from models_store.model_persistence import save_model


DATA_PATH = "data/processed/AAPL_features.csv"
SELECTION_PATH = "reports/evaluation/final_model_selection.csv"
MODEL_DIRECTORY = "models_store"


def load_data():
    """Load feature-engineered stock data."""

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


def load_model_selection():
    """Load the selected model for each forecast horizon."""

    if not os.path.exists(SELECTION_PATH):
        raise FileNotFoundError(
            f"Model selection file not found: {SELECTION_PATH}"
        )

    selection = pd.read_csv(SELECTION_PATH)

    required_columns = [
        "Horizon",
        "Selected_Model"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in selection.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in model selection file: "
            f"{missing_columns}"
        )

    return selection


def train_selected_model(data, model_name, horizon):
    """
    Train one selected model for a specific horizon.
    """

    if model_name == "SARIMA":

        model = fit_sarima(
            data,
            target_column="Close",
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 5)
        )

    elif model_name == "XGBoost":

        model = fit_xgboost(
            data,
            horizon=horizon
        )

    elif model_name == "Prophet":

        model = fit_prophet(
            data,
            target_column="Close"
        )

    else:
        raise ValueError(
            f"Unsupported model: {model_name}"
        )

    return model


def main():

    print("=" * 60)
    print("TRAINING AND SAVING FINAL MODELS")
    print("=" * 60)

    # Load data
    data = load_data()

    print("\nDataset shape:")
    print(data.shape)

    # Load selected models
    selection = load_model_selection()

    print("\nSelected models:")

    for _, row in selection.iterrows():
        horizon = int(row["Horizon"].replace("-Day", ""))
        model_name = row["Selected_Model"]

        print(
            f"{horizon}-Day -> {model_name}"
        )

    print("\nTraining models...\n")

    for _, row in selection.iterrows():

        horizon = int(row["Horizon"].replace("-Day", ""))
        model_name = row["Selected_Model"]

        print(
            f"Training {model_name} for "
            f"{horizon}-Day horizon..."
        )

        model = train_selected_model(
            data=data,
            model_name=model_name,
            horizon=horizon
        )

        model_filename = (
            f"AAPL_{model_name}_{horizon}day"
        )

        saved_path = save_model(
            model=model,
            model_name=model_filename,
            directory=MODEL_DIRECTORY
        )

        print(
            f"Saved: {saved_path}\n"
        )

    print("=" * 60)
    print("ALL FINAL MODELS SAVED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()