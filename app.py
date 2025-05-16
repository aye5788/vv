import streamlit as st
import requests
import pandas as pd

# Load API key from Streamlit secrets
API_KEY = st.secrets["ALPHA_VANTAGE_API_KEY"]
BASE_URL = "https://www.alphavantage.co/query"

# Friendly metric display names
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

VALUATION_METRICS = ["PERatio", "PEGRatio", "PriceToBookRatio", "PriceToSalesRatioTTM", "EVToRevenue", "EVToEBITDA"]
EARNINGS_METRICS = ["EPS", "EBITDA", "ProfitMargin", "OperatingMarginTTM"]
GROWTH_METRICS = ["QuarterlyEarningsGrowthYOY", "QuarterlyRevenueGrowthYOY", "ReturnOnAssetsTTM", "ReturnOnEquityTTM"]
BOOK_DIVIDEND_METRICS = ["BookValue", "SharesOutstanding", "DividendPerShare", "DividendYield"]

# ------------------------- Helper Functions -------------------------

@st.cache_data(show_spinner=False)
def fetch_company_overview(symbol):
    response = requests.get(BASE_URL, params={
        "function": "OVERVIEW",
        "symbol": symbol.upper(),
        "apikey": API_KEY
    })
    data = response.json()
    return data if "Symbol" in data else None

@st.cache_data(show_spinner=False)
def fetch_cash_flow(symbol):
    response = requests.get(BASE_URL, params={
        "function": "CASH_FLOW",
        "symbol": symbol.upper(),
        "apikey": API_KEY
    })
    return response.json() if "annualReports" in response.json() else None

def display_table(title, metric_list, data):
    st.subheader(title)
    rows = []
    for metric in metric_list:
        raw_value = data.get(metric, "N/A")
        try:
            if raw_value.replace(".", "", 1).isdigit() and len(raw_value) > 9:
                formatted_value = f"{int(float(raw_value)):,}"
            else:
                formatted_value = raw_value
        except:
            formatted_value = raw_value

        label = FRIENDLY_LABELS.get(metric, metric)
        rows.append(f"<tr><td style='text-align:left'><b>{label}</b></td><td style='text-align:right'>{formatted_value}</td></tr>")

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

# ------------------------- DCF Calculation -------------------------

def calculate_dcf(fcf_values, shares_outstanding, discount_rate=0.10, terminal_growth=0.025, years=5):
    if len(fcf_values) < 2 or shares_outstanding == 0:
        return "N/A"

    # Sort FCFs by oldest to newest
    fcf_values = fcf_values[::-1]
    fcf_cagr = ((fcf_values[-1] / fcf_values[0]) ** (1 / (len(fcf_values)-1))) - 1 if fcf_values[0] > 0 else 0.10
    last_fcf = fcf_values[-1]

    future_fcfs = [last_fcf * ((1 + fcf_cagr) ** t) / ((1 + discount_rate) ** t) for t in range(1, years + 1)]
    terminal_value = (future_fcfs[-1] * (1 + terminal_growth)) / (discount_rate - terminal_growth)
    terminal_discounted = terminal_value / ((1 + discount_rate) ** years)

    firm_value = sum(future_fcfs) + terminal_discounted
    fair_value_per_share = firm_value / shares_outstanding
    return round(fair_value_per_share, 2)

# ------------------------- Streamlit Layout -------------------------

st.set_page_config(page_title="Stock Valuation Dashboard", layout="wide")
st.title("📊 Stock Valuation Dashboard")

symbol = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, IBM):", "")

if symbol:
    overview = fetch_company_overview(symbol)
    cashflow = fetch_cash_flow(symbol)

    if overview:
        st.success(f"Company Overview for **{symbol.upper()}**")

        display_table("💰 Valuation Multiples", VALUATION_METRICS, overview)
        display_table("📈 Earnings & Profitability", EARNINGS_METRICS, overview)
        display_table("📊 Growth Metrics", GROWTH_METRICS, overview)
        display_table("📚 Book & Dividends", BOOK_DIVIDEND_METRICS, overview)

        # EV / Revenue
        try:
            ev = float(overview.get("EnterpriseValue", "0"))
            revenue = float(overview.get("RevenueTTM", "0"))
            if revenue > 0:
                ev_to_rev = round(ev / revenue, 2)
                st.metric(label="🔹 EV / Revenue", value=ev_to_rev)
        except:
            pass

        # DCF
        st.subheader("📉 Discounted Cash Flow (DCF) Valuation")

        try:
            annual_reports = cashflow["annualReports"]
            fcfs = []
            for report in annual_reports[:5]:
                op_cf = float(report["operatingCashflow"])
                capex = float(report["capitalExpenditures"])
                fcfs.append(op_cf - capex)

            shares = float(overview.get("SharesOutstanding", "0"))
            dcf_value = calculate_dcf(fcfs, shares)
            st.metric(label="📈 DCF Estimated Fair Value (per share)", value=dcf_value)
        except:
            st.warning("DCF could not be computed due to missing or invalid cash flow data.")
    else:
        st.error("No data found for that ticker. Please try another.")

