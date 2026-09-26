import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Real-Time Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# API FUNCTIONS
# ============================================================

def get_stock_data(symbol):

    response = requests.get(
        f"{API_URL}/stocks/{symbol}/data",
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return pd.DataFrame(result["data"])


def get_model_results(symbol):

    response = requests.get(
        f"{API_URL}/models",
        params={"symbol": symbol},
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return pd.DataFrame(result["models"])


def get_predictions(symbol):

    response = requests.get(
        f"{API_URL}/prediction",
        params={"symbol": symbol},
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return pd.DataFrame(result["predictions"])


def refresh_predictions(symbol):

    response = requests.post(
        f"{API_URL}/refresh",
        params={"symbol": symbol},
        timeout=300
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📈 Real-Time Stock Analysis & Prediction Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Market analysis • Machine learning • Multi-horizon forecasting • Model evaluation'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Dashboard Controls")

symbol = st.sidebar.text_input(
    "Stock Symbol",
    value="AAPL"
).upper().strip()

st.sidebar.markdown("---")

st.sidebar.caption("Prediction Controls")

refresh_button = st.sidebar.button(
    "🔄 Refresh Predictions",
    use_container_width=True
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Backend API:\n"
    "http://127.0.0.1:8000"
)


# ============================================================
# REFRESH
# ============================================================

if refresh_button:

    with st.spinner("Generating predictions using saved models..."):

        try:

            refresh_predictions(symbol)

            st.success(
                f"Predictions refreshed successfully for {symbol}."
            )

            st.rerun()

        except requests.exceptions.RequestException as error:

            st.error(
                f"API request failed: {error}"
            )

        except Exception as error:

            st.error(
                f"Refresh failed: {error}"
            )


# ============================================================
# LOAD DATA
# ============================================================

try:

    stock_data = get_stock_data(symbol)
    model_data = get_model_results(symbol)
    prediction_data = get_predictions(symbol)

except requests.exceptions.ConnectionError:

    st.error(
        "❌ Cannot connect to FastAPI.\n\n"
        "Start the backend with:\n\n"
        "`uvicorn backend.api:app --reload`"
    )

    st.stop()

except requests.exceptions.HTTPError as error:

    st.error(
        f"FastAPI returned an error: {error}"
    )

    st.stop()

except Exception as error:

    st.error(
        f"Unexpected error: {error}"
    )

    st.stop()


# ============================================================
# PREPARE STOCK DATA
# ============================================================

stock_data["date"] = pd.to_datetime(
    stock_data["date"]
)

stock_data = stock_data.sort_values(
    "date"
).reset_index(drop=True)


stock_data["daily_return"] = (
    stock_data["close"].pct_change() * 100
)

stock_data["rolling_volatility_20"] = (
    stock_data["daily_return"]
    .rolling(20)
    .std()
)

stock_data["sma_20"] = (
    stock_data["close"]
    .rolling(20)
    .mean()
)

stock_data["sma_50"] = (
    stock_data["close"]
    .rolling(50)
    .mean()
)

stock_data["sma_200"] = (
    stock_data["close"]
    .rolling(200)
    .mean()
)

# ============================================================
# PREDICTION SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">🔮 Multi-Horizon Predictions</div>',
    unsafe_allow_html=True
)

if not prediction_data.empty and not stock_data.empty:

    latest_close = float(
        stock_data["close"].iloc[-1]
    )

    prediction_display = prediction_data.copy()

    prediction_display["predicted_price"] = pd.to_numeric(
        prediction_display["predicted_price"],
        errors="coerce"
    )

    prediction_display["horizon"] = pd.to_numeric(
        prediction_display["horizon"],
        errors="coerce"
    )

    prediction_display = prediction_display.dropna(
        subset=["predicted_price", "horizon"]
    )

    if not prediction_display.empty:

        # ----------------------------------------------------
        # Calculate price change
        # ----------------------------------------------------

        prediction_display["price_change"] = (
            prediction_display["predicted_price"]
            - latest_close
        )

        prediction_display["percentage_change"] = (
            prediction_display["price_change"]
            / latest_close
        ) * 100

        # ----------------------------------------------------
        # Prediction cards
        # ----------------------------------------------------

        horizons = [1, 3, 10, 15]

        available_predictions = (
            prediction_display[
                prediction_display["horizon"].isin(horizons)
            ]
            .sort_values("horizon")
        )

        columns = st.columns(4)

        for column, (_, row) in zip(
            columns,
            available_predictions.iterrows()
        ):

            horizon = int(row["horizon"])
            model = row["model"]
            predicted_price = float(
                row["predicted_price"]
            )
            price_change = float(
                row["price_change"]
            )
            percentage_change = float(
                row["percentage_change"]
            )

            with column:

                st.metric(
                    label=f"{horizon}-Day • {model}",
                    value=f"${predicted_price:.2f}",
                    delta=(
                        f"{price_change:+.2f} "
                        f"({percentage_change:+.2f}%)"
                    )
                )

        st.caption(
            f"Latest available close: ${latest_close:.2f}"
        )

    else:

        st.info(
            "No valid prediction values are available."
        )

else:

    st.info(
        "Prediction data is not available."
    )

# ============================================================
# SELECTED MODEL BY HORIZON
# ============================================================

st.markdown(
    '<div class="section-title">🤖 Selected Model by Forecast Horizon</div>',
    unsafe_allow_html=True
)

if not prediction_data.empty:

    model_selection_display = prediction_data[
        ["horizon", "model"]
    ].copy()

    model_selection_display = (
        model_selection_display
        .drop_duplicates()
        .sort_values("horizon")
    )

    model_selection_display["horizon"] = (
        model_selection_display["horizon"]
        .astype(int)
        .astype(str)
        + "-Day"
    )

    model_selection_display.columns = [
        "Forecast Horizon",
        "Selected Model"
    ]

    st.dataframe(
        model_selection_display,
        use_container_width=True,
        hide_index=True
    )
# ============================================================
# FORECAST PRICE VISUALIZATION
# ============================================================

st.subheader("📈 Forecast Price by Horizon")

if not prediction_display.empty:

    forecast_chart = prediction_display.copy()

    forecast_chart["forecast_label"] = (
        forecast_chart["horizon"]
        .astype(int)
        .astype(str)
        + "-Day"
    )

    fig_forecast = go.Figure()

    fig_forecast.add_trace(
        go.Scatter(
            x=forecast_chart["forecast_label"],
            y=forecast_chart["predicted_price"],
            mode="lines+markers",
            name="Predicted Price"
        )
    )

    fig_forecast.add_hline(
        y=latest_close,
        line_dash="dash",
        annotation_text="Latest Close"
    )

    fig_forecast.update_layout(
        title="Current Price vs Multi-Horizon Forecast",
        xaxis_title="Forecast Horizon",
        yaxis_title="Price",
        height=450
    )

    st.plotly_chart(
        fig_forecast,
        use_container_width=True
    )
# ============================================================
# MARKET OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">📊 Market Overview</div>',
    unsafe_allow_html=True
)

latest = stock_data.iloc[-1]

if len(stock_data) > 1:

    previous_close = stock_data.iloc[-2]["close"]

else:

    previous_close = latest["close"]


price_change = (
    latest["close"] - previous_close
)

price_change_percentage = (
    price_change / previous_close * 100
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Latest Price",
        f"${latest['close']:.2f}",
        f"{price_change_percentage:+.2f}%"
    )


with col2:

    st.metric(
        "Open",
        f"${latest['open']:.2f}"
    )


with col3:

    st.metric(
        "Day High",
        f"${latest['high']:.2f}"
    )


with col4:

    st.metric(
        "Day Low",
        f"${latest['low']:.2f}"
    )


with col5:

    st.metric(
        "Volume",
        f"{latest['volume']:,.0f}"
    )


st.caption(
    f"Symbol: {symbol} | "
    f"Latest available date: "
    f"{latest['date'].strftime('%Y-%m-%d')}"
)


# ============================================================
# PRICE + MOVING AVERAGES
# ============================================================

st.markdown(
    '<div class="section-title">📈 Price Analysis</div>',
    unsafe_allow_html=True
)


fig_price = go.Figure()

fig_price.add_trace(
    go.Scatter(
        x=stock_data["date"],
        y=stock_data["close"],
        mode="lines",
        name="Close"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=stock_data["date"],
        y=stock_data["sma_20"],
        mode="lines",
        name="SMA 20"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=stock_data["date"],
        y=stock_data["sma_50"],
        mode="lines",
        name="SMA 50"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=stock_data["date"],
        y=stock_data["sma_200"],
        mode="lines",
        name="SMA 200"
    )
)

fig_price.update_layout(
    title=f"{symbol} Close Price and Moving Averages",
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified",
    height=500
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)


# ============================================================
# CANDLESTICK CHART
# ============================================================

st.subheader("🕯️ OHLC Price Chart")

fig_candle = go.Figure(
    data=[
        go.Candlestick(
            x=stock_data["date"],
            open=stock_data["open"],
            high=stock_data["high"],
            low=stock_data["low"],
            close=stock_data["close"],
            name=symbol
        )
    ]
)

fig_candle.update_layout(
    title=f"{symbol} OHLC",
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False,
    height=500
)

st.plotly_chart(
    fig_candle,
    use_container_width=True
)


# ============================================================
# VOLUME
# ============================================================

st.subheader("📊 Trading Volume")

fig_volume = px.bar(
    stock_data,
    x="date",
    y="volume",
    title=f"{symbol} Trading Volume"
)

fig_volume.update_layout(
    xaxis_title="Date",
    yaxis_title="Volume",
    height=400
)

st.plotly_chart(
    fig_volume,
    use_container_width=True
)


# ============================================================
# AUTOMATED EDA
# ============================================================

st.markdown(
    '<div class="section-title">🔍 Automated EDA</div>',
    unsafe_allow_html=True
)


eda_col1, eda_col2 = st.columns(2)


# ------------------------------------------------------------
# Daily Returns
# ------------------------------------------------------------

with eda_col1:

    st.subheader("Daily Returns")

    fig_returns = px.line(
        stock_data,
        x="date",
        y="daily_return",
        title="Daily Percentage Returns"
    )

    fig_returns.update_layout(
        xaxis_title="Date",
        yaxis_title="Return (%)",
        height=400
    )

    st.plotly_chart(
        fig_returns,
        use_container_width=True
    )


# ------------------------------------------------------------
# Rolling Volatility
# ------------------------------------------------------------

with eda_col2:

    st.subheader("20-Day Rolling Volatility")

    fig_volatility = px.line(
        stock_data,
        x="date",
        y="rolling_volatility_20",
        title="20-Day Rolling Volatility"
    )

    fig_volatility.update_layout(
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        height=400
    )

    st.plotly_chart(
        fig_volatility,
        use_container_width=True
    )


# ============================================================
# RETURN DISTRIBUTION
# ============================================================

st.subheader("📊 Daily Return Distribution")

return_values = stock_data[
    "daily_return"
].dropna()

fig_distribution = px.histogram(
    return_values,
    nbins=50,
    title="Distribution of Daily Returns"
)

fig_distribution.update_layout(
    xaxis_title="Daily Return (%)",
    yaxis_title="Frequency",
    height=400
)

st.plotly_chart(
    fig_distribution,
    use_container_width=True
)


# ============================================================
# CORRELATION MATRIX
# ============================================================

st.subheader("🔗 OHLCV Correlation")

correlation_data = stock_data[
    [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]
].corr()

fig_correlation = px.imshow(
    correlation_data,
    text_auto=".2f",
    aspect="auto",
    title="Correlation Matrix"
)

fig_correlation.update_layout(
    height=500
)

st.plotly_chart(
    fig_correlation,
    use_container_width=True
)


# ============================================================
# MODEL COMPARISON
# ============================================================

st.markdown(
    '<div class="section-title">🤖 Model Comparison</div>',
    unsafe_allow_html=True
)


if not model_data.empty:

    model_display = model_data.copy()

    model_display["horizon_label"] = (
        model_display["horizon"]
        .astype(int)
        .astype(str)
        + "-Day"
    )

    model_display = model_display.rename(
        columns={
            "model": "Model",
            "horizon": "Horizon",
            "mae": "MAE",
            "mse": "MSE",
            "rmse": "RMSE",
            "r2": "R²"
        }
    )


    # --------------------------------------------------------
    # Model Table
    # --------------------------------------------------------

    st.subheader("Evaluation Metrics")

    st.dataframe(
        model_display[
            [
                "Model",
                "Horizon",
                "MAE",
                "MSE",
                "RMSE",
                "R²"
            ]
        ].round(4),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # RMSE Comparison
    # --------------------------------------------------------

    st.subheader("RMSE Comparison")

    fig_rmse = px.bar(
        model_display,
        x="Horizon",
        y="RMSE",
        color="Model",
        barmode="group",
        title="RMSE by Forecast Horizon"
    )

    fig_rmse.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_rmse,
        use_container_width=True
    )


    # --------------------------------------------------------
    # MAE Comparison
    # --------------------------------------------------------

    st.subheader("MAE Comparison")

    fig_mae = px.bar(
        model_display,
        x="Horizon",
        y="MAE",
        color="Model",
        barmode="group",
        title="MAE by Forecast Horizon"
    )

    fig_mae.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_mae,
        use_container_width=True
    )


    # --------------------------------------------------------
    # R² Comparison
    # --------------------------------------------------------

    st.subheader("R² Comparison")

    fig_r2 = px.bar(
        model_display,
        x="Horizon",
        y="R²",
        color="Model",
        barmode="group",
        title="R² by Forecast Horizon"
    )

    fig_r2.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_r2,
        use_container_width=True
    )


else:

    st.info(
        "No model evaluation results available."
    )


# ============================================================
# FORECAST SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">🔮 Forecast Summary</div>',
    unsafe_allow_html=True
)


if not prediction_data.empty:

    prediction_data["forecast_date"] = pd.to_datetime(
        prediction_data["forecast_date"]
    )

    prediction_data = prediction_data.sort_values(
        "horizon"
    )


    # --------------------------------------------------------
    # Forecast Cards
    # --------------------------------------------------------

    forecast_columns = st.columns(
        min(4, len(prediction_data))
    )


    for index, (_, row) in enumerate(
        prediction_data.iterrows()
    ):

        with forecast_columns[index]:

            st.metric(
                f"{int(row['horizon'])}-Day Forecast",
                f"${row['predicted_price']:.2f}"
            )

            st.caption(
                f"Model: {row['model']}"
            )

            st.caption(
                f"Date: "
                f"{row['forecast_date'].strftime('%Y-%m-%d')}"
            )


    # --------------------------------------------------------
    # Forecast Table
    # --------------------------------------------------------

    st.subheader(
        "Multi-Horizon Forecast Table"
    )

    forecast_table = prediction_data.copy()

    forecast_table["Forecast Date"] = (
        forecast_table["forecast_date"]
        .dt.strftime("%Y-%m-%d")
    )

    forecast_table["Horizon"] = (
        forecast_table["horizon"]
        .astype(int)
        .astype(str)
        + "-Day"
    )

    forecast_table = forecast_table.rename(
        columns={
            "model": "Model",
            "predicted_price": "Predicted Price",
            "actual_price": "Actual Price",
            "absolute_error": "Absolute Error",
            "error_percentage": "Error %"
        }
    )

    st.dataframe(
        forecast_table[
            [
                "Forecast Date",
                "Horizon",
                "Model",
                "Predicted Price",
                "Actual Price",
                "Absolute Error",
                "Error %"
            ]
        ].round(4),
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "No predictions available."
    )


# ============================================================
# ACTUAL VS PREDICTED
# ============================================================

st.markdown(
    '<div class="section-title">📈 Forecast Evaluation</div>',
    unsafe_allow_html=True
)


if not prediction_data.empty:

    prediction_data["actual_price"] = pd.to_numeric(
        prediction_data["actual_price"],
        errors="coerce"
    )

    evaluation_data = prediction_data.dropna(
        subset=["actual_price"]
    ).copy()


    if not evaluation_data.empty:

        evaluation_data = evaluation_data.sort_values(
            "forecast_date"
        )


        # ----------------------------------------------------
        # Actual vs Predicted
        # ----------------------------------------------------

        st.subheader(
            "Actual vs Predicted"
        )

        fig_actual = go.Figure()

        fig_actual.add_trace(
            go.Scatter(
                x=evaluation_data["forecast_date"],
                y=evaluation_data["actual_price"],
                mode="lines+markers",
                name="Actual"
            )
        )

        fig_actual.add_trace(
            go.Scatter(
                x=evaluation_data["forecast_date"],
                y=evaluation_data["predicted_price"],
                mode="lines+markers",
                name="Predicted"
            )
        )

        fig_actual.update_layout(
            title="Actual vs Predicted Price",
            xaxis_title="Forecast Date",
            yaxis_title="Price",
            hovermode="x unified",
            height=450
        )

        st.plotly_chart(
            fig_actual,
            use_container_width=True
        )


        # ----------------------------------------------------
        # Forecast Error
        # ----------------------------------------------------

        st.subheader(
            "Forecast Error"
        )

        error_data = evaluation_data.copy()

        error_data["error"] = (
            error_data["predicted_price"]
            - error_data["actual_price"]
        )

        fig_error = px.bar(
            error_data,
            x="forecast_date",
            y="error",
            color="horizon",
            title="Prediction Error"
        )

        fig_error.update_layout(
            xaxis_title="Forecast Date",
            yaxis_title="Prediction Error",
            height=400
        )

        st.plotly_chart(
            fig_error,
            use_container_width=True
        )


    else:

        st.info(
            "Actual prices are not available yet. "
            "Forecast error charts will appear when "
            "future predictions have corresponding actual prices."
        )


# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.markdown("---")

st.subheader("ℹ️ System Information")

info_col1, info_col2, info_col3 = st.columns(3)


with info_col1:

    st.metric(
        "Historical Records",
        f"{len(stock_data):,}"
    )


with info_col2:

    st.metric(
        "Models Evaluated",
        f"{len(model_data):,}"
    )


with info_col3:

    st.metric(
        "Forecast Horizons",
        f"{len(prediction_data):,}"
    )


st.caption(
    "Real-Time Stock Analysis & Prediction Dashboard | "
    "FastAPI + SQLite + ARIMA + SARIMA + Prophet + XGBoost"
)