from fastapi import APIRouter, HTTPException

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