"""ShopSmart Sales Dashboard.

Run with:  streamlit run app.py
This file holds the page layout and charts; the calculations live in data.py.
"""
import streamlit as st

from data import DATA_PATH, format_currency, load_sales, total_orders, total_sales

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

# --- KPI cards ---
kpi_sales, kpi_orders = st.columns(2)
kpi_sales.metric("Total Sales", format_currency(total_sales(df)))
kpi_orders.metric("Total Orders", f"{total_orders(df):,}")
