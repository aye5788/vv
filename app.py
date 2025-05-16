import streamlit as st
import requests
import pandas as pd

# Load API key securely from Streamlit secrets
API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"

# Define metrics to display
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

# Function to fetch Alpha Vantage company overview
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

# Streamlit App Layout
st.set_page_config(page_title="Stock Valuation Dashboard", layout="wide")
st.title("📊 Stock Valuation Dashboard")

symbol = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, IBM):", "")

if symbol:
    data = fetch_company_overview(symbol)

    if data:
        st.success(f"Company Overview for **{symbol.upper()}**")

        st.subheader("💰 Valuation Multiples")
        st.dataframe(
            pd.DataFrame({
                "Metric": VALUATION_METRICS,
                "Value": [data.get(metric, "N/A") for metric in VALUATION_METRICS]
            }).set_index("Metric")
        )

        st.subheader("📈 Earnings & Profitability")
        st.dataframe(
            pd.DataFrame({
                "Metric": EARNINGS_METRICS,
                "Value": [data.get(metric, "N/A") for metric in EARNINGS_METRICS]
            }).set_index("Metric")
        )

        st.subheader("📊 Growth Metrics")
        st.dataframe(
            pd.DataFrame({
                "Metric": GROWTH_METRICS,
                "Value": [data.get(metric, "N/A") for metric in GROWTH_METRICS]
            }).set_index("Metric")
        )

        st.subheader("📚 Book & Dividends")
        st.dataframe(
            pd.DataFrame({
                "Metric": BOOK_DIVIDEND_METRICS,
                "Value": [data.get(metric, "N/A") for metric in BOOK_DIVIDEND_METRICS]
            }).set_index("Metric")
        )

    else:
        st.error("No data found for that ticker. Please try another.")
