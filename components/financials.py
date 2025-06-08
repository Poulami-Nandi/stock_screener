import streamlit as st

def render_financials(stock_data):
    st.subheader("📊 Key Financial Ratios")

    financials = stock_data.get("financials", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Market Cap", financials.get("market_cap", "N/A"))
        st.metric("EPS (TTM)", financials.get("eps", "N/A"))

    with col2:
        st.metric("P/E Ratio", financials.get("pe_ratio", "N/A"))
        st.metric("Dividend Yield", f"{financials.get('dividend_yield', 0)}%")

    # Add more metrics as your mock or live data supports
