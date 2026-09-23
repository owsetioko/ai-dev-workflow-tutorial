"""Tests for data.py, run against the real sales CSV."""
import pandas as pd
import pytest

from data import DATA_PATH, load_sales


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
