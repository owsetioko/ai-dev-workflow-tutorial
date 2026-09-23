"""Loading and calculations for the ShopSmart sales dashboard.

This module uses only pandas (no Streamlit), so every function here can be
tested with pytest without starting the app.
"""
from pathlib import Path

import pandas as pd

# Built from this file's location, so the CSV is found no matter which
# folder the app or the tests are started from.
DATA_PATH = Path(__file__).parent / "data" / "sales-data.csv"


def load_sales(path=DATA_PATH):
    """Read the sales CSV, with the date column parsed as dates.

    Raises FileNotFoundError if the file does not exist.
    """
    return pd.read_csv(path, parse_dates=["date"])


def total_sales(df):
    """Total revenue across all transactions."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order with several lines counts once)."""
    return int(df["order_id"].nunique())


def format_currency(value):
    """Format dollars with separators and no cents, e.g. $116,500."""
    return f"${value:,.0f}"
