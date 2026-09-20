from database.database import get_connection


def create_tables():
    """
    Create all database tables required by the project.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # --------------------------------------------------
        # MARKET DATA
        # --------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                UNIQUE(symbol, date)
            )
            """
        )

        # --------------------------------------------------
        # MODEL RESULTS
        # --------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS model_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                model TEXT NOT NULL,
                horizon INTEGER NOT NULL,
                mae REAL,
                mse REAL,
                rmse REAL,
                r2 REAL,
                test_windows INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, model, horizon)
            )
            """
        )

        # --------------------------------------------------
        # PREDICTIONS
        # --------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                forecast_generated TEXT,
                last_known_date TEXT,
                last_known_close REAL,
                forecast_date TEXT NOT NULL,
                horizon INTEGER NOT NULL,
                model TEXT NOT NULL,
                predicted_price REAL NOT NULL,
                actual_price REAL,
                absolute_error REAL,
                error_percentage REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()

    print("=" * 60)
    print("DATABASE SCHEMA")
    print("=" * 60)
    print("\nDatabase tables created successfully.")
    print("\nTables:")
    print("1. market_data")
    print("2. model_results")
    print("3. predictions")