import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Mapping of display labels to yfinance parameters
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

def render_price_chart(ticker):
    st.subheader("📈 Price, Volume & Moving Averages")

    selected_range = st.radio(
        "Select Duration",
        list(TIMEFRAMES.keys()),
        horizontal=True,
        index=4  # Default to "1Yr"
    )

    period, interval = TIMEFRAMES[selected_range]

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            st.warning("No data available for this selection.")
            return

        df.reset_index(inplace=True)
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["SMA_200"] = df["Close"].rolling(window=200).mean()

        x_axis = df["Datetime"] if "Datetime" in df.columns else df["Date"]

        fig = go.Figure()

        # Main price line
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=df["Close"],
            name="Price",
            line=dict(color="blue", width=2)
        ))

        # SMA 50 (hidden by default)
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=df["SMA_50"],
            name="50 DMA",
            visible="legendonly",
            line=dict(color="orange", dash="dot")
        ))

        # SMA 200 (hidden by default)
        fig.add_trace(go.Scatter(
            x=x_axis,
            y=df["SMA_200"],
            name="200 DMA",
            visible="legendonly",
            line=dict(color="gray", dash="dash")
        ))

        # Volume bars on secondary y-axis
        fig.add_trace(go.Bar(
            x=x_axis,
            y=df["Volume"],
            name="Volume",
            yaxis="y2",
            marker_color="rgba(173,216,230,0.4)",
            opacity=0.6
        ))

        # Configure x-axis
        xaxis_config = dict(
            title="Time",
            showgrid=False,
            rangeslider_visible=False,
            showticklabels=True
        )

        # === Handle gaps ===
        if interval == "1d" and period in ["1mo", "6mo", "1y", "3y", "5y"]:
            xaxis_config["rangebreaks"] = [
                dict(bounds=["sat", "mon"]),
                dict(values=pd.date_range(start=x_axis.min(), end=x_axis.max(), freq="B").difference(x_axis))
            ]

        if period == "5d" and interval == "15m":
            xaxis_config["rangebreaks"] = [
                dict(bounds=["sat", "mon"]),
                dict(bounds=["16:00", "09:30"], pattern="hour")  # Skip non-trading hours
            ]

        # Reduce tick clutter for intraday views
        if period == "1d":
            xaxis_config["tickformat"] = "%H:%M"
            xaxis_config["dtick"] = 1800000  # 30 min
        elif period == "5d":
            xaxis_config["tickformat"] = "%m-%d %H:%M"
            xaxis_config["dtick"] = 3600000  # 1 hour

        # Final layout
        fig.update_layout(
            title=f"{ticker} - Price, Volume & MA ({selected_range})",
            xaxis=xaxis_config,
            yaxis=dict(title="Price"),
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.25,
                xanchor="left",
                x=0
            ),
            height=500,
            margin=dict(t=40, b=60)
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Chart error: {e}")
