"""Tests for data.py, run against the real sales CSV."""
import pandas as pd
import pytest

from data import (
    DATA_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    sales_by,
    total_orders,
    total_sales,
)


@pytest.fixture
def sales():
    return load_sales()


def test_data_path_is_absolute_and_exists():
    # An absolute path means the app finds the CSV from any folder.
    assert DATA_PATH.is_absolute()
    assert DATA_PATH.exists()


def test_load_sales_reads_every_row(sales):
    assert len(sales) == 482


def test_load_sales_parses_dates(sales):
    assert pd.api.types.is_datetime64_any_dtype(sales["date"])


def test_load_sales_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales(tmp_path / "missing.csv")


def test_total_sales(sales):
    assert total_sales(sales) == pytest.approx(116500.21)


def test_total_orders(sales):
    assert total_orders(sales) == 482


def test_total_orders_counts_each_order_once():
    # Two lines belonging to the same order still count as one order.
    df = pd.DataFrame({"order_id": ["ORD-1", "ORD-1", "ORD-2"]})
    assert total_orders(df) == 2


def test_format_currency_rounds_and_adds_separators():
    assert format_currency(116500.21) == "$116,500"
    assert format_currency(1234567.89) == "$1,234,568"


def test_monthly_sales_has_twelve_months_in_order(sales):
    monthly = monthly_sales(sales)
    assert list(monthly.columns) == ["month", "sales"]
    assert len(monthly) == 12
    assert monthly["month"].iloc[0] == pd.Timestamp("2024-01-01")
    assert monthly["month"].iloc[-1] == pd.Timestamp("2024-12-01")
    # Months must run forwards, or the trend line would zig-zag.
    assert monthly["month"].is_monotonic_increasing
    assert monthly["sales"].sum() == pytest.approx(116500.21)


def test_sales_by_category_sorted_highest_first(sales):
    by_category = sales_by(sales, "category")
    assert list(by_category.columns) == ["category", "sales"]
    assert len(by_category) == 5
    assert by_category["category"].iloc[0] == "Electronics"
    assert by_category["sales"].iloc[0] == pytest.approx(42683.67)
    assert by_category["category"].iloc[-1] == "Accessories"
    assert by_category["sales"].iloc[-1] == pytest.approx(11162.64)
    assert by_category["sales"].is_monotonic_decreasing


def test_sales_by_region_sorted_highest_first(sales):
    by_region = sales_by(sales, "region")
    assert list(by_region["region"]) == ["North", "West", "East", "South"]
