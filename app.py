import streamlit as st
import requests
import pandas as pd

# Load API key from Streamlit secrets
API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"

# Metric categories
VALUATION_METRICS = [
    "PERatio", "PEGRatio", "PriceToBookRatio", "PriceToSalesRatioTTM", "EVToRevenue", "EVToEBITDA"
]
EARNINGS_METRICS = [
    "EPS", "EBITDA", "ProfitMargin", "OperatingMarginTTM"
]
GROWTH_METRICS = [
    "QuarterlyEarningsGrowthYOY", "QuarterlyRevenueGrowthYOY", "ReturnOnAssetsTTM", "ReturnOnEquityTTM"
]
BOOK_DIVIDEND_METRICS = [
    "BookValue", "SharesOutstanding", "DividendPerShare", "DividendYield"
]

# Fetch Alpha Vantage overview data
@st.cache_data(show_spinner=False)
def fetch_company_overview(symbol):
    params = {
        "function": "OVERVIEW",
        "symbol": symbol.upper(),
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data if "Symbol" in data else None
    return None

# Streamlit UI
st.set_page_config(page_title="Stock Valuation Dashboard", layout="wide")
st.title("📊 Stock Valuation Dashboard")

symbol = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, IBM):", "")

if symbol:
    data = fetch_company_overview(symbol)
    if data:
        st.success(f"Company Overview for **{symbol.upper()}**")

        # Render tables as static and responsive
        def display_table(title, metric_list):
            st.subheader(title)
            df = pd.DataFrame({
                "Metric": metric_list,
                "Value": [data.get(metric, "N/A") for metric in metric_list]
            }).set_index("Metric")
            st.table(df)

        display_table("💰 Valuation Multiples", VALUATION_METRICS)
        display_table("📈 Earnings & Profitability", EARNINGS_METRICS)
        display_table("📊 Growth Metrics", GROWTH_METRICS)
        display_table("📚 Book & Dividends", BOOK_DIVIDEND_METRICS)

    else:
        st.error("No data found for that ticker. Please try another.")

