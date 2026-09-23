# Sales Dashboard Design

**Date:** 2026-09-22
**Source requirements:** `prd/ecommerce-analytics.md`
**Milestones:** `TASKS.md` (TASK-1 to TASK-5)
**Branch:** `feature/sales-dashboard`

## Goal

A single-page Streamlit dashboard for ShopSmart that shows Total Sales, Total Orders, a monthly sales trend, and sales by category and by region. Everything is read from `data/sales-data.csv`. The page must look professional enough for an executive meeting and be deployable to Streamlit Community Cloud.

## Constraints

- Work on the current branch `feature/sales-dashboard`; no git worktree.
- Dependencies live in a Python virtual environment in `venv/` and are listed in `requirements.txt` (the file Streamlit Community Cloud reads).
- Code stays simple and readable: plain functions, short files, comments where the reason isn't obvious.
- Stack: Python 3.11+, Streamlit, pandas, Plotly, pytest.
- Out of scope: everything in PRD Phase 2 (filters, date ranges, authentication, export, database, drill-down).

## Files

```
requirements.txt      streamlit, pandas, plotly, pytest
.gitignore            adds venv/ (and Python cache files)
data/sales-data.csv   existing data, unchanged
data.py               pure pandas: loading and calculations (no Streamlit)
app.py                Streamlit page: layout and Plotly charts
tests/test_data.py    pytest tests for data.py
```

`data.py` never imports Streamlit, so its functions can be tested without starting the app.

## Data functions (`data.py`)

| Function | Returns | Notes |
|---|---|---|
| `load_sales(path)` | DataFrame | Reads the CSV and parses `date` as a date. Raises `FileNotFoundError` if the file is missing. |
| `total_sales(df)` | float | Sum of `total_amount`. |
| `total_orders(df)` | int | Number of unique `order_id` values. |
| `monthly_sales(df)` | DataFrame with columns `month`, `sales` | One row per calendar month, in date order. |
| `sales_by(df, column)` | DataFrame with columns `column`, `sales` | Sum of `total_amount` for each value of `column` (`"category"` or `"region"`), sorted highest to lowest. |

## Data flow

1. `app.py` calls `load_sales("data/sales-data.csv")`, wrapped in a function marked `@st.cache_data` so the CSV is read only once.
2. `app.py` passes the DataFrame to the calculation functions.
3. Each function returns a number (for a KPI) or a small table (for a chart), and `app.py` renders it.

## Page layout (`app.py`)

Wide page layout, top to bottom:

1. **Title** "ShopSmart Sales Dashboard" with a caption giving the data's date range.
2. **KPI row:** two `st.metric` cards side by side.
   - Total Sales formatted as currency with no cents, e.g. `$116,500`.
   - Total Orders formatted with thousands separators, e.g. `482`.
3. **Sales trend:** full-width Plotly line chart of monthly sales. X-axis "Month", y-axis "Sales ($)". Hover shows the exact value.
4. **Breakdowns:** two columns side by side.
   - "Sales by Category": horizontal Plotly bar chart, largest bar at the top.
   - "Sales by Region": horizontal Plotly bar chart, largest bar at the top.
   - Hover shows exact values on both.

Every chart has a title and axis labels. Plotly's default styling is used; there is no custom theme.

## Error handling

- **Missing CSV:** `app.py` catches `FileNotFoundError` from `load_sales`, shows `st.error` with a message naming the expected path `data/sales-data.csv`, then calls `st.stop()`. Nothing else renders and no stack trace appears.
- There is no other validation. The data file is fixed and known, and the PRD's Phase 1 doesn't ask for handling malformed data.

## Testing

`tests/test_data.py` runs with `pytest` against the real CSV. The expected values below were calculated from `data/sales-data.csv`:

| Test | Expected |
|---|---|
| `total_orders` | 482 |
| `total_sales` | 116,500.21 (to the cent) |
| `monthly_sales` | 12 rows from 2024-01 to 2024-12, summing to the same total as `total_sales` |
| `sales_by(df, "category")` | 5 rows; Electronics first (42,683.67), Accessories last (11,162.64) |
| `sales_by(df, "region")` | 4 rows in the order North, West, East, South |
| `load_sales` with a missing path | raises `FileNotFoundError` |

Each data function is built test-first: write the test, watch it fail, then write the function. Layout and charts are checked by eye with `streamlit run app.py`.

## Milestone mapping

| Milestone | Work |
|---|---|
| TASK-1: Project setup and data loading | `venv/`, `requirements.txt`, `.gitignore`, `load_sales()` and its tests, `app.py` with the title, caption and missing-file error |
| TASK-2: KPI scorecards | `total_sales()`, `total_orders()`, their tests, KPI row |
| TASK-3: Sales trend chart | `monthly_sales()`, its test, trend chart |
| TASK-4: Category and region breakdowns | `sales_by()`, its tests, both bar charts |
| TASK-5: Test and deploy | Full test run, then a final check of the local app for errors and warnings. Deployment to Streamlit Community Cloud is done by the user from `main` after merging; the plan ends with step-by-step instructions and stops there. |

Each milestone ends with a commit whose message includes its TASK ID, as the Definition of Done in `TASKS.md` requires.

## Risks

- **Python 3.14 on this machine is very new.** If Streamlit, pandas or Plotly fails to install into `venv/`, recreate the venv with Python 3.12 or 3.13. Both meet the PRD's "Python 3.11+".
