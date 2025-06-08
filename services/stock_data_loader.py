import json
import yfinance as yf

def get_mock_data(ticker):
    try:
        with open("data/mock_stock_data.json") as f:
            data = json.load(f)
        return data.get(ticker.upper(), None)
    except Exception as e:
        return None

def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)

        info = stock.info

        data = {
            "name": info.get("longName", ticker),
            "exchange": info.get("exchange", "N/A"),
            "sector": info.get("sector", "N/A"),
            "description": info.get("longBusinessSummary", "Description not available."),
            "financials": {
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "eps": info.get("trailingEps", "N/A"),
                "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else "N/A",
            },
            "price_data": get_price_history(stock),
            "income_statement": {}  # Placeholder – yfinance doesn't expose IS/BS easily
        }
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


def get_price_history(stock):
    try:
        df = stock.history(period="1mo")
        df.reset_index(inplace=True)
        return [{"date": row["Date"].strftime("%Y-%m-%d"), "close": row["Close"]} for _, row in df.iterrows()]
    except:
        return []
