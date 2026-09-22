from fastapi import APIRouter, HTTPException

from backend.service import refresh_predictions
from database.repository import (
    get_market_data,
    get_model_results,
    get_predictions
)


router = APIRouter()


@router.get("/stocks/{symbol}/data")
def get_stock_data(symbol: str):
    data = get_market_data(symbol.upper())

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No market data found for symbol: {symbol.upper()}"
        )

    return {
        "symbol": symbol.upper(),
        "rows": len(data),
        "data": data.to_dict(orient="records")
    }


@router.get("/models")
def get_models(symbol: str = "AAPL"):
    data = get_model_results(symbol.upper())

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No model results found for symbol: {symbol.upper()}"
        )

    return {
        "symbol": symbol.upper(),
        "rows": len(data),
        "models": data.to_dict(orient="records")
    }


@router.get("/prediction")
def get_prediction(symbol: str = "AAPL"):
    data = get_predictions(symbol.upper())

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No predictions found for symbol: {symbol.upper()}"
        )

    return {
        "symbol": symbol.upper(),
        "rows": len(data),
        "predictions": data.to_dict(orient="records")
    }

@router.get("/metrics")
def get_metrics(symbol: str = "AAPL"):
    data = get_model_results(symbol.upper())

    if data.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for symbol: {symbol.upper()}"
        )

    metrics = data[
        [
            "model",
            "horizon",
            "mae",
            "mse",
            "rmse",
            "r2"
        ]
    ]

    return {
        "symbol": symbol.upper(),
        "rows": len(metrics),
        "metrics": metrics.to_dict(orient="records")
    }

@router.post("/train")
def train_models(symbol: str = "AAPL"):
    symbol = symbol.upper()

    if symbol != "AAPL":
        raise HTTPException(
            status_code=400,
            detail="Currently only AAPL is supported."
        )

    try:
        from models_store.train_final_models import main as train_final_models

        train_final_models()

        return {
            "status": "success",
            "message": f"Models trained successfully for {symbol}."
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Model training failed: {str(error)}"
        )

@router.post("/refresh")
def refresh(symbol: str = "AAPL"):
    symbol = symbol.upper()

    if symbol != "AAPL":
        raise HTTPException(
            status_code=400,
            detail="Currently only AAPL is supported."
        )

    try:
        result = refresh_predictions(symbol)

        return {
            "status": "success",
            "message": f"Predictions refreshed successfully for {symbol}.",
            **result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Refresh failed: {str(error)}"
        )