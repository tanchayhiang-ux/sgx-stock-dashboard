import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="My SGX Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# ----------------------------------
# AUTO REFRESH
# ----------------------------------
st.markdown(
    """
    <meta http-equiv="refresh" content="30">
    """,
    unsafe_allow_html=True
)

# ----------------------------------
# STOCK LIST
# ----------------------------------
STOCKS = {
    "D05.SI": "DBS Group",
    "O39.SI": "OCBC Bank",
    "U11.SI": "UOB",
    "BN4.SI": "Keppel Ltd",
    "9CI.SI": "CapitaLand Investment",
    "C38U.SI": "CapitaLand Integrated Commercial Trust",
    "G07.SI": "Great Eastern Holdings",
    "U10.SI": "UOB Kay Hian",
    "Z74.SI": "Singtel"
}

st.title("📈 My Favourite SGX Stocks")

st.caption(
    f"Last Updated: {datetime.now().strftime('%d %b %Y %H:%M:%S')}"
)

# ----------------------------------
# GET STOCK DATA
# ----------------------------------
data = []

for symbol, company in STOCKS.items():

    try:
        stock = yf.Ticker(symbol)

        info = stock.info

        current_price = info.get("currentPrice")

        previous_close = info.get("previousClose")

        if current_price and previous_close:
            change = current_price - previous_close
            pct_change = (change / previous_close) * 100
        else:
            change = 0
            pct_change = 0

        market_cap = info.get("marketCap", 0)

        pe_ratio = info.get("trailingPE", "N/A")

        dividend_yield = info.get("dividendYield")

        if dividend_yield:
            dividend_yield = round(dividend_yield * 100, 2)

        high52 = info.get("fiftyTwoWeekHigh", "N/A")

        low52 = info.get("fiftyTwoWeekLow", "N/A")

        data.append(
            {
                "Name": company,
                "Symbol": symbol,
                "Price": current_price,
                "Change": round(change, 3),
                "% Change": round(pct_change, 2),
                "PE": pe_ratio,
                "Dividend Yield %": dividend_yield,
                "52W High": high52,
                "52W Low": low52,
                "Market Cap": market_cap
            }
        )

    except:
        pass

df = pd.DataFrame(data)

# ----------------------------------
# DASHBOARD TABLE
# ----------------------------------
st.subheader("Stock Overview")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# ----------------------------------
# STOCK CHART
# ----------------------------------
st.subheader("Price Chart")

selected = st.selectbox(
    "Choose a stock",
    list(STOCKS.keys()),
    format_func=lambda x: f"{STOCKS[x]} ({x})"
)

ticker = yf.Ticker(selected)

hist = ticker.history(period="1y")

if not hist.empty:

    st.line_chart(
        hist["Close"],
        use_container_width=True
    )

# ----------------------------------
# PORTFOLIO CALCULATOR
# ----------------------------------
st.subheader("Portfolio Calculator")

portfolio_value = 0

for symbol, company in STOCKS.items():

    qty = st.number_input(
        f"{company} Shares",
        min_value=0,
        value=0,
        step=100,
        key=symbol
    )

    try:
        price = yf.Ticker(symbol).info.get("currentPrice", 0)

        portfolio_value += qty * price

    except:
        pass

st.metric(
    "Estimated Portfolio Value (SGD)",
    f"${portfolio_value:,.2f}"
)

# ----------------------------------
# TOP GAINERS
# ----------------------------------
st.subheader("Best Performer Today")

if not df.empty:

    top = df.sort_values(
        "% Change",
        ascending=False
    ).iloc[0]

    st.success(
        f"{top['Name']} "
        f"({top['Symbol']}) "
        f"{top['% Change']}%"
    )

# ----------------------------------
# DOWNLOAD CSV
# ----------------------------------
csv = df.to_csv(index=False)

st.download_button(
    "Download Stock Data",
    csv,
    file_name="sgx_stocks.csv",
    mime="text/csv"
)
