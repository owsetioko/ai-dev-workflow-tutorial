"""Tests for data.py, run against the real sales CSV."""
import pandas as pd
import pytest

from data import DATA_PATH, format_currency, load_sales, total_orders, total_sales


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
