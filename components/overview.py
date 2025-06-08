import streamlit as st

def render_overview(stock_data):
    st.header(stock_data["name"])
    st.subheader(f"{stock_data['exchange']} | {stock_data['sector']}")
    st.markdown(f"**Business Description:** {stock_data['description']}")
