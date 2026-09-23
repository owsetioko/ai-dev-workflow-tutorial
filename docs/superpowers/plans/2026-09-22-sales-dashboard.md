# Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the ShopSmart Streamlit dashboard (KPIs, monthly trend, category and region breakdowns) from `data/sales-data.csv`, ready for the user to deploy to Streamlit Community Cloud.

**Architecture:** `data.py` holds plain pandas functions for loading and calculating, with no Streamlit code, and is covered by pytest. `app.py` is the Streamlit page: it calls `data.py` and draws Plotly charts. Each milestone adds one or two data functions (test-first) and then the matching section of the page.

**Tech Stack:** Python 3.11+, Streamlit, pandas, Plotly Express, pytest.

**Spec:** `docs/superpowers/specs/2026-09-22-sales-dashboard-design.md`

**Numbering:** Plan steps are numbered **Plan Step 1–10**. Milestones on the board are **TASK-1 to TASK-5**. Each plan step says which milestone it belongs to. The small checkboxes inside a plan step are its actions (a, b, c …).

## Global Constraints

- Work on the current branch `feature/sales-dashboard`. Do not create a git worktree.
- Dependencies go in a virtual environment in `venv/` and are listed in `requirements.txt`. Don't use uv, conda or poetry.
- `data.py` never imports Streamlit.
- Keep the code simple and readable: plain functions, short files, a comment wherever the reason isn't obvious.
- Every commit message starts with its milestone ID, e.g. `TASK-2: Add KPI calculations`.
- Stay out of scope: nothing from PRD Phase 2 (filters, date ranges, authentication, export, database, drill-down).
- Deployment (Plan Step 10) is done **by the user**, from `main` after merging. Whoever executes the plan stops before it.

**Small additions to the spec** (they keep the spec's intent and make it testable):
- `DATA_PATH` in `data.py` is built from the file's own location, so the app works from any folder (see Review Focus 1).
- `format_currency(value)` lives in `data.py` so the `$116,500` formatting can be tested.
- `pytest.ini` sets `pythonpath = .` so tests in `tests/` can `import data`.
- `.gitignore` needs no change: it already ignores `venv/` and `__pycache__/`.

## Review Focus

1. **Starting the app from another folder** (e.g. `streamlit run ~/…/app.py`). A plain relative path like `"data/sales-data.csv"` would then show the "missing file" error even though the file exists. Covered by `DATA_PATH` being absolute, with a test in Plan Step 1.
2. **Months drawn out of order.** If months were grouped as text or sorted wrongly, the trend line would zig-zag. Covered by a test in Plan Step 5 that months run from 2024-01 to 2024-12 in increasing order.
3. **Largest bar at the bottom.** Plotly draws horizontal bars from the bottom up, so data sorted highest-first ends up upside-down. Covered by `categoryorder="total ascending"` in Plan Step 8, plus an explicit visual check there.
4. **Currency rounding and separators** (`$116,500`, not `116500.21` or `$116500`). Covered by the `format_currency` test in Plan Step 3.
5. **Counting order lines instead of orders.** If an order ever had two lines, counting rows would overcount. Covered by the duplicate-ID test in Plan Step 3.

---

### Plan Step 1: Environment and CSV loading (TASK-1)

**Files:**
- Create: `requirements.txt`, `pytest.ini`, `data.py`, `tests/test_data.py`

**Interfaces:**
- Produces: `DATA_PATH: pathlib.Path` (absolute path to `data/sales-data.csv`) and `load_sales(path=DATA_PATH) -> pandas.DataFrame`, with `date` as datetime64. It raises `FileNotFoundError` if the file is missing.

- [ ] **a. Create `requirements.txt`**

```
streamlit
pandas
plotly
pytest
```

- [ ] **b. Create the virtual environment and install**

Run:
```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```
Expected: ends with `Successfully installed …` including streamlit, pandas, plotly and pytest.
If the install fails on Python 3.14 (usually while building `pyarrow`), install Python 3.12 or 3.13 from python.org, delete `venv/`, and recreate it with `python3.12 -m venv venv`.

- [ ] **c. Create `pytest.ini`**

```ini
[pytest]
pythonpath = .
testpaths = tests
```

- [ ] **d. Write the failing tests in `tests/test_data.py`**

```python
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
```

- [ ] **e. Run the tests and confirm they fail**

Run: `venv/bin/python -m pytest -v`
Expected: collection error `ModuleNotFoundError: No module named 'data'` (the module doesn't exist yet).

- [ ] **f. Create `data.py`**

```python
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
```

- [ ] **g. Run the tests and confirm they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `4 passed`.

- [ ] **h. Commit**

```bash
git add requirements.txt pytest.ini data.py tests/test_data.py
git commit -m "TASK-1: Add environment and CSV loading with tests"
```

---

### Plan Step 2: Dashboard page with title and missing-file error (TASK-1)

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: `DATA_PATH`, `load_sales` from Plan Step 1.
- Produces: `app.py` with a `df` DataFrame available below the error check. Later plan steps append sections to the end of the file and extend the `from data import …` line.

- [ ] **a. Create `app.py`**

```python
"""ShopSmart Sales Dashboard.

Run with:  streamlit run app.py
This file holds the page layout and charts; the calculations live in data.py.
"""
import streamlit as st

from data import DATA_PATH, load_sales

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")


@st.cache_data
def get_sales():
    """Load the CSV once and reuse it each time the page reruns."""
    return load_sales(DATA_PATH)


st.title("ShopSmart Sales Dashboard")

try:
    df = get_sales()
except FileNotFoundError:
    st.error(
        "Could not find the sales data file. "
        "Expected it at data/sales-data.csv in the project folder."
    )
    st.stop()  # Show only the message above; render nothing else.

start = df["date"].min().strftime("%b %d, %Y")
end = df["date"].max().strftime("%b %d, %Y")
st.caption(f"Sales data from {start} to {end}")
```

- [ ] **b. Check that the page renders without errors**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', len(at.exception))
print('title:', at.title[0].value)
print('caption:', at.caption[0].value)
"
```
Expected:
```
exceptions: 0
title: ShopSmart Sales Dashboard
caption: Sales data from Jan 03, 2024 to Dec 31, 2024
```

- [ ] **c. Check the missing-file message**

Temporarily move the CSV away, run the page, then put the CSV back. The `;` makes sure the file is restored even if the check fails.

Run:
```bash
mv data/sales-data.csv data/sales-data.csv.bak; venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', len(at.exception))
print('error:', at.error[0].value)
print('captions:', len(at.caption))
"; mv data/sales-data.csv.bak data/sales-data.csv
```
Expected:
```
exceptions: 0
error: Could not find the sales data file. Expected it at data/sales-data.csv in the project folder.
captions: 0
```
Then confirm the CSV is back: `ls data/` shows `sales-data.csv`.

- [ ] **d. Look at it in the browser**

Stop any old server first, then start the app:
```bash
pkill -f "streamlit run app.py"; venv/bin/streamlit run app.py
```
Open http://localhost:8501. Expected: the title and date-range caption, nothing else. Stop the server with `Ctrl+C`.

- [ ] **e. Commit**

```bash
git add app.py
git commit -m "TASK-1: Add dashboard page with title and missing-file error"
```

---

### Plan Step 3: KPI calculations (TASK-2)

**Files:**
- Modify: `data.py` (append functions)
- Modify: `tests/test_data.py` (extend import, append tests)

**Interfaces:**
- Consumes: `load_sales` from Plan Step 1.
- Produces: `total_sales(df) -> float`, `total_orders(df) -> int`, `format_currency(value: float) -> str` (e.g. `"$116,500"`).

- [ ] **a. Write the failing tests**

In `tests/test_data.py`, change the import line to:
```python
from data import DATA_PATH, format_currency, load_sales, total_orders, total_sales
```
Append:
```python
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
```

- [ ] **b. Run the tests and confirm they fail**

Run: `venv/bin/python -m pytest -v`
Expected: collection error `ImportError: cannot import name 'format_currency' from 'data'`.

- [ ] **c. Append to `data.py`**

```python
def total_sales(df):
    """Total revenue across all transactions."""
    return float(df["total_amount"].sum())


def total_orders(df):
    """Number of distinct orders (an order with several lines counts once)."""
    return int(df["order_id"].nunique())


def format_currency(value):
    """Format dollars with separators and no cents, e.g. $116,500."""
    return f"${value:,.0f}"
```

- [ ] **d. Run the tests and confirm they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `8 passed`.

- [ ] **e. Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-2: Add KPI calculations and currency formatting"
```

---

### Plan Step 4: KPI cards on the page (TASK-2)

**Files:**
- Modify: `app.py` (extend import, append section)

**Interfaces:**
- Consumes: `total_sales`, `total_orders`, `format_currency` from Plan Step 3.

- [ ] **a. Update `app.py`**

Change the import line to:
```python
from data import DATA_PATH, format_currency, load_sales, total_orders, total_sales
```
Append to the end of the file:
```python

# --- KPI cards ---
kpi_sales, kpi_orders = st.columns(2)
kpi_sales.metric("Total Sales", format_currency(total_sales(df)))
kpi_orders.metric("Total Orders", f"{total_orders(df):,}")
```

- [ ] **b. Check the metrics**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', len(at.exception))
for m in at.metric: print(m.label, '=', m.value)
"
```
Expected:
```
exceptions: 0
Total Sales = $116,500
Total Orders = 482
```

- [ ] **c. Look at it in the browser**

Run: `pkill -f "streamlit run app.py"; venv/bin/streamlit run app.py`
Expected at http://localhost:8501: two KPI cards side by side under the caption. Stop with `Ctrl+C`.

- [ ] **d. Commit**

```bash
git add app.py
git commit -m "TASK-2: Show Total Sales and Total Orders KPI cards"
```

---

### Plan Step 5: Monthly sales calculation (TASK-3)

**Files:**
- Modify: `data.py`, `tests/test_data.py`

**Interfaces:**
- Produces: `monthly_sales(df) -> DataFrame` with columns `month` (datetime64, first day of each month) and `sales` (float), one row per month, oldest first.

- [ ] **a. Write the failing test**

In `tests/test_data.py`, change the import line to:
```python
from data import (
    DATA_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    total_orders,
    total_sales,
)
```
Append:
```python
def test_monthly_sales_has_twelve_months_in_order(sales):
    monthly = monthly_sales(sales)
    assert list(monthly.columns) == ["month", "sales"]
    assert len(monthly) == 12
    assert monthly["month"].iloc[0] == pd.Timestamp("2024-01-01")
    assert monthly["month"].iloc[-1] == pd.Timestamp("2024-12-01")
    # Months must run forwards, or the trend line would zig-zag.
    assert monthly["month"].is_monotonic_increasing
    assert monthly["sales"].sum() == pytest.approx(116500.21)
```

- [ ] **b. Run the tests and confirm they fail**

Run: `venv/bin/python -m pytest -v`
Expected: collection error `ImportError: cannot import name 'monthly_sales' from 'data'`.

- [ ] **c. Append to `data.py`**

```python
def monthly_sales(df):
    """Total sales for each calendar month, oldest month first.

    Each month is labelled by its first day (e.g. 2024-01-01), which Plotly
    draws as a proper date axis.
    """
    months = df["date"].dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby(months)["total_amount"].sum().reset_index()
    monthly.columns = ["month", "sales"]
    return monthly
```

- [ ] **d. Run the tests and confirm they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `9 passed`.

- [ ] **e. Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-3: Add monthly sales calculation"
```

---

### Plan Step 6: Sales trend chart (TASK-3)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `monthly_sales` from Plan Step 5.

- [ ] **a. Update `app.py`**

Add below `import streamlit as st`:
```python
import plotly.express as px
```
so the top of the file reads:
```python
import plotly.express as px
import streamlit as st
```
Change the `from data import …` line to:
```python
from data import (
    DATA_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    total_orders,
    total_sales,
)
```
Append to the end of the file:
```python

# --- Sales trend ---
trend_fig = px.line(
    monthly_sales(df),
    x="month",
    y="sales",
    markers=True,
    title="Monthly Sales Trend",
    labels={"month": "Month", "sales": "Sales ($)"},
)
# Hover shows the month name and the exact amount, e.g. "March 2024  $9,876.54".
trend_fig.update_traces(hovertemplate="%{x|%B %Y}<br>$%{y:,.2f}<extra></extra>")
st.plotly_chart(trend_fig)
```

- [ ] **b. Check the page still runs cleanly**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', len(at.exception))
"
```
Expected: `exceptions: 0`

- [ ] **c. Look at it in the browser**

Run: `pkill -f "streamlit run app.py"; venv/bin/streamlit run app.py`
Expected at http://localhost:8501: a full-width line chart titled "Monthly Sales Trend" with 12 points from Jan to Dec 2024. Hovering a point shows the month and a dollar value with cents. Stop with `Ctrl+C`.

- [ ] **d. Commit**

```bash
git add app.py
git commit -m "TASK-3: Add monthly sales trend chart"
```

---

### Plan Step 7: Category and region totals (TASK-4)

**Files:**
- Modify: `data.py`, `tests/test_data.py`

**Interfaces:**
- Produces: `sales_by(df, column: str) -> DataFrame` with columns `<column>` and `sales`, sorted highest sales first, index 0..n-1. Called with `"category"` and `"region"`.

- [ ] **a. Write the failing tests**

In `tests/test_data.py`, change the import line to:
```python
from data import (
    DATA_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    sales_by,
    total_orders,
    total_sales,
)
```
Append:
```python
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
```

- [ ] **b. Run the tests and confirm they fail**

Run: `venv/bin/python -m pytest -v`
Expected: collection error `ImportError: cannot import name 'sales_by' from 'data'`.

- [ ] **c. Append to `data.py`**

```python
def sales_by(df, column):
    """Total sales for each value of `column` (e.g. "category"), highest first."""
    totals = df.groupby(column)["total_amount"].sum().reset_index()
    totals.columns = [column, "sales"]
    return totals.sort_values("sales", ascending=False).reset_index(drop=True)
```

- [ ] **d. Run the tests and confirm they pass**

Run: `venv/bin/python -m pytest -v`
Expected: `11 passed`.

- [ ] **e. Commit**

```bash
git add data.py tests/test_data.py
git commit -m "TASK-4: Add sales totals by category and region"
```

---

### Plan Step 8: Category and region bar charts (TASK-4)

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_by` from Plan Step 7.

- [ ] **a. Update `app.py`**

Change the `from data import …` line to:
```python
from data import (
    DATA_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    sales_by,
    total_orders,
    total_sales,
)
```
Add this function directly below `get_sales()` (above `st.title(...)`):
```python


def bar_chart(totals, column, title):
    """Horizontal bar chart of sales per `column`, largest bar at the top."""
    fig = px.bar(
        totals,
        x="sales",
        y=column,
        orientation="h",
        title=title,
        labels={"sales": "Sales ($)", column: column.title()},
    )
    # Plotly stacks horizontal bars from the bottom up; ordering by ascending
    # total puts the smallest at the bottom and the largest at the top.
    fig.update_yaxes(categoryorder="total ascending")
    fig.update_traces(hovertemplate="%{y}<br>$%{x:,.2f}<extra></extra>")
    return fig
```
Append to the end of the file:
```python

# --- Breakdowns ---
left, right = st.columns(2)
left.plotly_chart(bar_chart(sales_by(df, "category"), "category", "Sales by Category"))
right.plotly_chart(bar_chart(sales_by(df, "region"), "region", "Sales by Region"))
```

- [ ] **b. Check the page still runs cleanly**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', len(at.exception))
"
```
Expected: `exceptions: 0`

- [ ] **c. Look at it in the browser**

Run: `pkill -f "streamlit run app.py"; venv/bin/streamlit run app.py`
Expected at http://localhost:8501, below the trend chart, two charts side by side:
- **Sales by Category**, top to bottom: Electronics, Wearables, Audio, Smart Home, Accessories.
- **Sales by Region**, top to bottom: North, West, East, South.
- Hovering a bar shows its name and a dollar value with cents.

If the largest bar is at the **bottom**, the `categoryorder` line is missing or wrong. Stop with `Ctrl+C`.

- [ ] **d. Commit**

```bash
git add app.py
git commit -m "TASK-4: Add sales by category and region bar charts"
```

---

### Plan Step 9: Final test run and local check (TASK-5)

**Files:** none expected. If a check fails, fix the file it points to.

- [ ] **a. Run the full test suite**

Run: `venv/bin/python -m pytest -v`
Expected: `11 passed`, no failures, no warnings summary.

- [ ] **b. Run the whole page once more**

Run:
```bash
venv/bin/python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('app.py').run()
print('exceptions:', len(at.exception))
print('errors:', len(at.error))
for m in at.metric: print(m.label, '=', m.value)
"
```
Expected:
```
exceptions: 0
errors: 0
Total Sales = $116,500
Total Orders = 482
```

- [ ] **c. Final browser check against the PRD**

Run: `pkill -f "streamlit run app.py"; venv/bin/streamlit run app.py`
At http://localhost:8501 confirm, top to bottom: title and caption; the KPI cards `$116,500` and `482`; the monthly trend (12 points); category and region bars sorted largest at the top. The terminal running Streamlit shows no errors or warnings, and the page loads within about 5 seconds. Stop with `Ctrl+C`.

- [ ] **d. Commit only if fixes were needed**

Run `git status --short`. If files changed, commit them:
```bash
git add <changed files>
git commit -m "TASK-5: Fix issues found in final check"
```
If nothing changed, there's nothing to commit.

- [ ] **e. Stop here and hand off to the user for Plan Step 10.**

---

### Plan Step 10: Deploy to Streamlit Community Cloud (TASK-5) — USER'S STEP

**The executor does not perform this step.** The user deploys from `main` after merging.

- [ ] **a. Push the branch:** `git push -u origin feature/sales-dashboard`
- [ ] **b. Merge into `main`:** open a pull request on GitHub for `feature/sales-dashboard` and merge it, then pull `main` locally.
- [ ] **c. Create the app:** go to https://share.streamlit.io, sign in with GitHub, click **Create app**, and choose "Deploy a public app from GitHub".
- [ ] **d. Fill in the form:** repository `owsetioko/ai-dev-workflow-tutorial`, branch `main`, main file path `app.py`. Under **Advanced settings**, pick Python 3.12 or newer. Click **Deploy**.
- [ ] **e. Verify:** when the build finishes, the public URL shows the same values as the local app: `$116,500`, `482`, 12 months, Electronics and North at the top of their charts.
- [ ] **f. Record it:** move TASK-5 to Done in `TASKS.md` and note the public URL.
