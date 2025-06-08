import streamlit as st
from services.stock_data_loader import get_mock_data
from services.stock_data_loader import get_stock_data
from components import overview, financials, charts, statements
from components.combined_chart import render_combined_chart

st.set_page_config(page_title="NYSE Stock Screener", layout="wide")
st.title("📈 NYSE Stock Screener")

ticker = st.text_input("Enter NYSE Ticker", value="AAPL").upper()

data = get_stock_data(ticker)
if data:
    overview.render_overview(data)
    financials.render_financials(data)
    #charts.render_price_chart(ticker)
    render_combined_chart(ticker)
    statements.render_statements(data)
else:
    st.warning("Ticker not found in mock data.")
