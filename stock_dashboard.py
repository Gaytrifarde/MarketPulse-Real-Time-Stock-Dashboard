import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="MarketPulse – Real-Time Stock Dashboard",
    layout="wide"
)

# ---------------- CUSTOM THEME ----------------

st.markdown("""
<style>

/* Background */

.stApp{
background: linear-gradient(
135deg,
#e0f2fe,
#dbeafe,
#ede9fe
);
}

/* Text */

html,body,p,span,label{
color:#0f172a !important;
}

/* Headings */

h1{
color:#0f172a !important;
font-size:42px !important;
font-weight:900 !important;
text-align:center;
}

h2,h3{
color:#0f172a !important;
font-weight:bold !important;
}

/* Sidebar */

[data-testid="stSidebar"]{
background-color:white;
}

/* Sidebar text */

[data-testid="stSidebar"] *{
color:black !important;
}

/* Search input */

[data-testid="stSidebar"] input{
background-color:#f8fafc !important;
color:black !important;
border-radius:10px;
border:1px solid #cbd5e1;
}

/* KPI cards */

[data-testid="metric-container"]{

background:rgba(255,255,255,0.75);

padding:15px;

border-radius:15px;

box-shadow:0px 4px 12px rgba(0,0,0,.1);

}

/* Tables */

[data-testid="stDataFrame"]{

background:white;
border-radius:10px;

}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------

st.markdown(
"<h1>📊 MarketPulse – Real-Time Stock Dashboard</h1>",
unsafe_allow_html=True
)

st.markdown(
"<h3 style='text-align:center'>Live Top Gainers | Top Losers | Volume Leaders</h3>",
unsafe_allow_html=True
)

st.markdown("---")

# ---------------- SIDEBAR ----------------

st.sidebar.header("Dashboard Controls")

search = st.sidebar.text_input("🔍 Search Stock")

stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "BHARTIARTL.NS",
    "SBIN.NS",
    "ITC.NS",
    "LT.NS",
    "TATAMOTORS.NS",
    "HINDUNILVR.NS",
    "AXISBANK.NS",
    "WIPRO.NS",
    "MARUTI.NS",
    "HCLTECH.NS",
    "SUNPHARMA.NS",
    "NTPC.NS",
    "POWERGRID.NS",
    "TITAN.NS"
]

# ---------------- FETCH DATA ----------------

@st.cache_data(ttl=60)
def fetch_data(stock_list):

    result = []

    try:

        raw = yf.download(
            stock_list,
            period="5d",
            interval="1d",
            group_by="ticker",
            progress=False,
            auto_adjust=False
        )

        for stock in stock_list:

            try:

                if stock not in raw:
                    continue

                df = raw[stock].dropna()

                if len(df) < 2:
                    continue

                current = float(df["Close"].iloc[-1])
                previous = float(df["Close"].iloc[-2])
                volume = int(df["Volume"].iloc[-1])

                change = ((current - previous) / previous) * 100

                result.append({

                    "Stock": stock.replace(".NS", ""),
                    "Price": round(current, 2),
                    "Change %": round(change, 2),
                    "Volume": volume

                })

            except Exception as e:
                print(f"Error in {stock}: {e}")
                continue

    except Exception as e:
        st.error(f"Data download failed: {e}")

    return pd.DataFrame(
        result,
        columns=["Stock", "Price", "Change %", "Volume"]
    )

# ---------------- LOAD DATA ----------------

market_df = fetch_data(stocks)

# Safety check

if market_df.empty:
    st.error("No market data available right now.")
    st.stop()

# ---------------- SEARCH FILTER ----------------

if search:

    market_df = market_df[
        market_df["Stock"]
        .str.contains(search.upper(), na=False)
    ]

# ---------------- KPI CARDS ----------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "📌 Tracked Stocks",
    len(market_df)
)

c2.metric(
    "📈 Gainers",
    len(market_df[market_df["Change %"] > 0])
)

c3.metric(
    "📉 Losers",
    len(market_df[market_df["Change %"] < 0])
)

c4.metric(
    "📊 Total Volume",
    f"{market_df['Volume'].sum():,}"
)

st.markdown("---")

# ---------------- TABLES ----------------

left, right = st.columns(2)

gainers = market_df.sort_values(
    "Change %",
    ascending=False
).head(5)

losers = market_df.sort_values(
    "Change %",
    ascending=True
).head(5)

volume = market_df.sort_values(
    "Volume",
    ascending=False
).head(5)

with left:

    st.subheader("📈 TOP GAINERS")

    st.dataframe(
        gainers.style.background_gradient(
            subset=["Change %"],
            cmap="Greens"
        ),
        use_container_width=True
    )

    st.subheader("📉 TOP LOSERS")

    st.dataframe(
        losers.style.background_gradient(
            subset=["Change %"],
            cmap="Reds"
        ),
        use_container_width=True
    )

with right:

    st.subheader("📊 VOLUME LEADERS")

    st.dataframe(
        volume.style.background_gradient(
            subset=["Volume"],
            cmap="Blues"
        ),
        use_container_width=True
    )

# ---------------- CHARTS ----------------

st.markdown("---")

st.subheader("📊 VOLUME COMPARISON")

fig1 = px.bar(
    volume,
    x="Stock",
    y="Volume",
    color="Volume",
    color_continuous_scale="Blues",
    text_auto=True
)

fig1.update_layout(
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ---------------- MARKET OVERVIEW ----------------

st.markdown("---")

st.subheader("📈 MARKET OVERVIEW")

market_df["Status"] = market_df[
    "Change %"
].apply(
    lambda x: "Gainer" if x > 0 else "Loser"
)

fig2 = px.scatter(
    market_df,
    x="Change %",
    y="Price",
    size="Volume",
    color="Status",
    hover_name="Stock",
    text="Stock",
    size_max=60
)

fig2.update_layout(
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ---------------- FOOTER ----------------

st.markdown("---")

st.markdown(
"""
<div style='text-align:center;
padding:15px;
font-size:18px;
font-weight:bold;
color:#334155;'>

🚀 Powered by Streamlit + Plotly + Yahoo Finance

</div>
""",
unsafe_allow_html=True
)
