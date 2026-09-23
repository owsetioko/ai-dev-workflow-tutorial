"""ShopSmart Sales Dashboard.

Run with:  streamlit run app.py
This file holds the page layout and charts; the calculations live in data.py.
"""
import plotly.express as px
import streamlit as st

from data import (
    DATA_PATH,
    format_currency,
    load_sales,
    monthly_sales,
    sales_by,
    total_orders,
    total_sales,
)

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")


@st.cache_data
def get_sales():
    """Load the CSV once and reuse it each time the page reruns."""
    return load_sales(DATA_PATH)


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

# --- KPI cards ---
kpi_sales, kpi_orders = st.columns(2)
kpi_sales.metric("Total Sales", format_currency(total_sales(df)))
kpi_orders.metric("Total Orders", f"{total_orders(df):,}")

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

# --- Breakdowns ---
left, right = st.columns(2)
left.plotly_chart(bar_chart(sales_by(df, "category"), "category", "Sales by Category"))
right.plotly_chart(bar_chart(sales_by(df, "region"), "region", "Sales by Region"))
