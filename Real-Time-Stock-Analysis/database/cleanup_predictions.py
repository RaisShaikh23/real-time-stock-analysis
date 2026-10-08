import sqlite3

DATABASE_PATH = "database/stock_analysis.db"


def cleanup_predictions():

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    print("=" * 60)
    print("CLEANING DUPLICATE PREDICTIONS")
    print("=" * 60)

    cursor.execute(
        """
        DELETE FROM predictions
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM predictions
            GROUP BY
                symbol,
                forecast_date,
                horizon,
                model
        )
        """
    )

    deleted = cursor.rowcount

    connection.commit()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM predictions
        """
    )

    remaining = cursor.fetchone()[0]

    connection.close()

    print(f"Duplicate rows removed: {deleted}")
    print(f"Remaining prediction rows: {remaining}")

    print("=" * 60)
    print("CLEANUP COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    cleanup_predictions()