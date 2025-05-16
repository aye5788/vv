import streamlit as st
import requests
import pandas as pd

# Securely load API key from Streamlit secrets
API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"

# Friendly metric names (alias map)
FRIENDLY_LABELS = {
    "PERatio": "P/E Ratio",
    "PEGRatio": "PEG Ratio",
    "PriceToBookRatio": "Price/Book",
    "PriceToSalesRatioTTM": "Price/Sales",
    "EVToRevenue": "EV/Revenue",
    "EVToEBITDA": "EV/EBITDA",
    "EPS": "Earnings Per Share",
    "EBITDA": "EBITDA",
    "ProfitMargin": "Profit Margin",
    "OperatingMarginTTM": "Operating Margin",
    "QuarterlyEarningsGrowthYOY": "Qtr Earnings Growth (YoY)",
    "QuarterlyRevenueGrowthYOY": "Qtr Revenue Growth (YoY)",
    "ReturnOnAssetsTTM": "Return on Assets",
    "ReturnOnEquityTTM": "Return on Equity",
    "BookValue": "Book Value",
    "SharesOutstanding": "Shares Outstanding",
    "DividendPerShare": "Dividend/Share",
    "DividendYield": "Dividend Yield"
}

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

# Fetch overview data from Alpha Vantage
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

# Function to render clean HTML-style tables
def display_table(title, metric_list, data):
    st.subheader(title)
    rows = []
    for metric in metric_list:
        raw_value = data.get(metric, "N/A")
        try:
            # Format large integers (like shares, EBITDA)
            if raw_value.replace(".", "", 1).isdigit() and len(raw_value) > 9:
                formatted_value = f"{int(float(raw_value)):,}"
            else:
                formatted_value = raw_value
        except:
            formatted_value = raw_value

        label = FRIENDLY_LABELS.get(metric, metric)
        rows.append(
            f"<tr><td style='text-align:left'><b>{label}</b></td><td style='text-align:right'>{formatted_value}</td></tr>"
        )

    html_table = f"""
    <table style='width:100%; border-spacing: 0 10px;'>
        <thead>
            <tr>
                <th style='text-align:left'>Metric</th>
                <th style='text-align:right'>Value</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """
    st.markdown(html_table, unsafe_allow_html=True)

# Page layout and UI
st.set_page_config(page_title="Stock Valuation Dashboard", layout="wide")
st.title("📊 Stock Valuation Dashboard")

symbol = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, IBM):", "")

if symbol:
    data = fetch_company_overview(symbol)
    if data:
        st.success(f"Company Overview for **{symbol.upper()}**")

        display_table("💰 Valuation Multiples", VALUATION_METRICS, data)
        display_table("📈 Earnings & Profitability", EARNINGS_METRICS, data)
        display_table("📊 Growth Metrics", GROWTH_METRICS, data)
        display_table("📚 Book & Dividends", BOOK_DIVIDEND_METRICS, data)
    else:
        st.error("No data found for that ticker. Please try another.")


