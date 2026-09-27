"""
End-to-end prediction pipeline.

Pipeline flow:

1. Evaluate pending predictions
2. Generate fresh predictions using saved models
"""

from prediction.evaluate_predictions import evaluate_predictions
from prediction.predict import generate_predictions


def run_pipeline(symbol="AAPL"):
    """
    Run the complete prediction pipeline.

    Parameters
    ----------
    symbol : str
        Stock symbol to process.

    Returns
    -------
    dict
        Pipeline execution summary.
    """

    print("=" * 60)
    print("RUNNING END-TO-END PREDICTION PIPELINE")
    print("=" * 60)

    print("\n[1/2] Evaluating pending predictions...")

    evaluation_result = evaluate_predictions(
        symbol=symbol
    )

    print("\n[2/2] Generating new predictions...")

    prediction_result = generate_predictions()

    print("\n" + "=" * 60)
    print("PREDICTION PIPELINE COMPLETED")
    print("=" * 60)

    return {
        "symbol": symbol,
        "evaluation": evaluation_result,
        "predictions": prediction_result,
    }


if __name__ == "__main__":
    run_pipeline()