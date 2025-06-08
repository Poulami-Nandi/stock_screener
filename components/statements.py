import streamlit as st
import pandas as pd

def render_statements(stock_data):
    st.subheader("📄 Financial Statements")

    # Income Statement
    income = stock_data.get("income_statement", {})
    if income:
        st.markdown("#### Income Statement")
        df_income = pd.DataFrame(income).T.sort_index(ascending=False)
        df_income.columns = [col.replace("_", " ").title() for col in df_income.columns]
        st.dataframe(df_income.style.format("{:,.0f}"), use_container_width=True)
    else:
        st.info("No income statement data available.")

    # Add similar sections for Balance Sheet and Cash Flow if available in data
