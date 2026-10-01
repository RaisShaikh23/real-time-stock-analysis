"""
Verify SQLite database contents.

Checks:
1. Market data
2. Model evaluation results
3. Predictions
"""

from database.database import fetch_all, fetch_one


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def verify_market_data():
    print_section("MARKET DATA")

    row = fetch_one(
        """
        SELECT
            COUNT(*) AS total_rows,
            MIN(date) AS first_date,
            MAX(date) AS latest_date
        FROM market_data
        WHERE symbol = ?
        """,
        ("AAPL",)
    )

    print(f"Rows: {row['total_rows']}")
    print(f"First date: {row['first_date']}")
    print(f"Latest date: {row['latest_date']}")


def verify_model_results():
    print_section("MODEL RESULTS")

    row = fetch_one(
        """
        SELECT COUNT(*) AS total_rows
        FROM model_results
        """
    )

    print(f"Rows: {row['total_rows']}")

    print("\nModel results by horizon:")

    rows = fetch_all(
        """
        SELECT
            horizon,
            COUNT(*) AS count
        FROM model_results
        GROUP BY horizon
        ORDER BY horizon
        """
    )

    for row in rows:
        print(
            f"  {row['horizon']}-Day: "
            f"{row['count']} record(s)"
        )


def verify_predictions():
    print_section("PREDICTIONS")

    row = fetch_one(
        """
        SELECT COUNT(*) AS total_rows
        FROM predictions
        """
    )

    print(f"Rows: {row['total_rows']}")

    print("\nPrediction records:")

    rows = fetch_all(
        """
        SELECT
            symbol,
            forecast_date,
            horizon,
            model,
            predicted_price,
            actual_price
        FROM predictions
        ORDER BY forecast_date
        """
    )

    for row in rows:
        print(
            f"  {row['symbol']} | "
            f"{row['forecast_date']} | "
            f"{row['horizon']}-Day | "
            f"{row['model']} | "
            f"Predicted: {row['predicted_price']} | "
            f"Actual: {row['actual_price']}"
        )


def main():

    print("=" * 60)
    print("SQLITE DATABASE VERIFICATION")
    print("=" * 60)

    verify_market_data()
    verify_model_results()
    verify_predictions()

    print("\n" + "=" * 60)
    print("DATABASE VERIFICATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()