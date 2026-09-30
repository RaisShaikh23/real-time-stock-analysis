from pathlib import Path

import pandas as pd

from config.config import RAW_DATA_DIR
from data.fetch_data import fetch_stock_data


def update_stock_data(symbol="AAPL"):
    """
    Fetch the latest market data and merge it
    with the existing raw dataset.
    """

    symbol = symbol.strip().upper()

    if not symbol:
        raise ValueError("Stock symbol cannot be empty.")

    raw_path = RAW_DATA_DIR / f"{symbol}.csv"

    print("=" * 60)
    print("UPDATING MARKET DATA")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Fetch latest data
    # ---------------------------------------------------------

    print(f"\nFetching latest data for {symbol}...")

    new_data = fetch_stock_data(
        symbol=symbol,
        period="5d",
        interval="1d",
    )

    print(f"New rows downloaded: {len(new_data)}")

    # ---------------------------------------------------------
    # 2. Load existing raw data
    # ---------------------------------------------------------

    if raw_path.exists():

        print(f"Existing dataset found: {raw_path}")

        existing_data = pd.read_csv(
            raw_path,
            index_col="Date",
            parse_dates=True,
        )

        print(f"Existing rows: {len(existing_data)}")

    else:

        print("No existing dataset found.")

        existing_data = pd.DataFrame()

    # ---------------------------------------------------------
    # 3. Combine old + new data
    # ---------------------------------------------------------

    if not existing_data.empty:

        combined_data = pd.concat(
            [
                existing_data,
                new_data,
            ]
        )

    else:

        combined_data = new_data.copy()

    # ---------------------------------------------------------
    # 4. Remove duplicate dates
    # ---------------------------------------------------------

    combined_data = combined_data[
        ~combined_data.index.duplicated(
            keep="last"
        )
    ]

    # ---------------------------------------------------------
    # 5. Sort chronologically
    # ---------------------------------------------------------

    combined_data = combined_data.sort_index()

    # ---------------------------------------------------------
    # 6. Save updated raw dataset
    # ---------------------------------------------------------

    combined_data.to_csv(raw_path)

    print("\nUpdated dataset:")
    print(f"Total rows: {len(combined_data)}")
    print(f"First date: {combined_data.index.min()}")
    print(f"Latest date: {combined_data.index.max()}")

    print(f"\nSaved updated data to:")
    print(raw_path)

    print("\n" + "=" * 60)
    print("MARKET DATA UPDATE COMPLETED")
    print("=" * 60)

    return combined_data


if __name__ == "__main__":

    try:

        update_stock_data("AAPL")

    except Exception as error:

        print(f"Error: {error}")