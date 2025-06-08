import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from yahooquery import Ticker as YQ_Ticker

TIMEFRAMES = {
    "1D": ("1d", "5m"),
    "5D": ("5d", "15m"),
    "1M": ("1mo", "1d"),
    "6M": ("6mo", "1d"),
    "1Yr": ("1y", "1d"),
    "3Yr": ("3y", "1d"),
    "5Yr": ("5y", "1d"),
    "10Yr": ("10y", "1wk"),
    "Max": ("max", "1mo")
}

def render_combined_chart(ticker):
    st.subheader("📈 Stock Overview Chart")

    chart_mode = st.radio("Select Chart Mode", ["Price", "PE Ratio"], horizontal=True)
    selected_range = st.radio("Duration", list(TIMEFRAMES.keys()), horizontal=True, index=4)
    period, interval = TIMEFRAMES[selected_range]

    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    if hist.empty:
        st.warning("No historical data available.")
        return

    hist.reset_index(inplace=True)
    hist.rename(columns={"Datetime": "Date"}, inplace=True)
    hist["SMA_50"] = hist["Close"].rolling(window=50).mean()
    hist["SMA_200"] = hist["Close"].rolling(window=200).mean()

    fig = go.Figure()

    if chart_mode == "Price":
        show_sma50 = st.checkbox("Show 50 DMA", value=False)
        show_sma200 = st.checkbox("Show 200 DMA", value=False)
        show_volume = st.checkbox("Show Volume", value=True)

        fig.add_trace(go.Scatter(x=hist["Date"], y=hist["Close"], name="Price", line=dict(color="blue", width=2)))

        if show_sma50:
            fig.add_trace(go.Scatter(x=hist["Date"], y=hist["SMA_50"], name="50 DMA", line=dict(color="orange", dash="dot")))

        if show_sma200:
            fig.add_trace(go.Scatter(x=hist["Date"], y=hist["SMA_200"], name="200 DMA", line=dict(color="gray", dash="dash")))

        if show_volume:
            fig.add_trace(go.Bar(
                x=hist["Date"], y=hist["Volume"], name="Volume",
                yaxis="y2", marker_color="rgba(173,216,230,0.4)", opacity=0.6
            ))

        fig.update_layout(
            yaxis=dict(title="Price"),
            yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False)
        )

    elif chart_mode == "PE Ratio":
        st.markdown("Toggle indicators:")
        col1, col2, col3 = st.columns(3)
        show_eps = col1.checkbox("TTM EPS", value=True)
        show_pe = col2.checkbox("PE", value=True)
        show_median = col3.checkbox("Median PE", value=True)

        df = hist.copy()

        try:
            yq_stock = YQ_Ticker(ticker)
            income_stmt_raw = yq_stock.income_statement(frequency='q')

            if isinstance(income_stmt_raw, dict) and ticker in income_stmt_raw:
                income_stmt = pd.DataFrame(income_stmt_raw[ticker])
            else:
                income_stmt = income_stmt_raw

            # Safely select available EPS column
            eps_column = None
            for col in ['epsBasic', 'epsDiluted']:
                if col in income_stmt.columns:
                    eps_column = col
                    break

            if eps_column is None:
                raise ValueError("EPS data (basic or diluted) not found in income statement.")

            eps_df = income_stmt[['asOfDate', eps_column]].dropna()
            eps_df.columns = ['Date', 'EPS']
            eps_df["Date"] = pd.to_datetime(eps_df["Date"])
            eps_df = eps_df.sort_values("Date")
            eps_df["TTM_EPS"] = eps_df["EPS"].rolling(window=4).sum()

            df = pd.merge_asof(df.sort_values("Date"), eps_df[['Date', 'TTM_EPS']], on="Date", direction="backward")
            df["PE"] = df["Close"] / df["TTM_EPS"]

        except Exception as e:
            st.error(f"Failed to load EPS data: {e}")
            return

        if show_eps:
            fig.add_trace(go.Bar(
                x=df["Date"],
                y=df["TTM_EPS"],
                name="TTM EPS",
                yaxis="y1",
                marker_color="rgba(135, 206, 250, 0.6)"
            ))

        if show_pe:
            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["PE"],
                name="PE",
                yaxis="y2",
                line=dict(color="blue", width=2)
            ))

        if show_median:
            median_pe = np.median(df["PE"].dropna())
            fig.add_trace(go.Scatter(
                x=[df["Date"].min(), df["Date"].max()],
                y=[median_pe, median_pe],
                name=f"Median PE = {median_pe:.1f}",
                yaxis="y2",
                mode="lines",
                line=dict(color="gray", dash="dot")
            ))

        fig.update_layout(
            yaxis=dict(title="TTM EPS"),
            yaxis2=dict(title="PE", overlaying="y", side="right", showgrid=False)
        )

    # === X-axis configuration ===
    xaxis_config = dict(title="Date", showgrid=False, rangeslider_visible=False, showticklabels=True)

    if interval == "1d" and period in ["1mo", "6mo", "1y", "3y", "5y"]:
        xaxis_config["rangebreaks"] = [
            dict(bounds=["sat", "mon"]),
            dict(values=pd.date_range(start=hist["Date"].min(), end=hist["Date"].max(), freq="B").difference(hist["Date"]))
        ]

    if period in ["1d", "5d"] and interval in ["5m", "15m"]:
        xaxis_config["rangebreaks"] = [
            dict(bounds=["sat", "mon"]),
            dict(bounds=["16:00", "09:30"], pattern="hour")
        ]

    if period == "1d":
        xaxis_config["tickformat"] = "%H:%M"
        xaxis_config["dtick"] = 1800000
    elif period == "5d":
        xaxis_config["tickformat"] = "%m-%d %H:%M"
        xaxis_config["dtick"] = 3600000

    fig.update_layout(
        xaxis=xaxis_config,
        title=f"{ticker} – {'Price' if chart_mode == 'Price' else 'PE Ratio'} Chart",
        legend=dict(orientation="h", yanchor="top", y=-0.25),
        height=500,
        margin=dict(t=40, b=60)
    )

    st.plotly_chart(fig, use_container_width=True)
