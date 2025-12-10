# ============================================================
# 📊 LSTM Stock Price Prediction App (Streamlit)
# Réalisé par: El jeddaoui imadeddine  (EMSI 2025/2026)
# Reference: Keras Docs, Towards Data Science
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ------------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------------
st.set_page_config(page_title="📈 LSTM Stock Predictor", layout="wide")
st.title("📊 Stock Price Prediction using LSTM (Keras + yFinance)")
st.markdown("### Réalisé par: imadeddine el jeddaoui(EMSI 2025/2026)")

# ------------------------------------------------------------
# Sidebar Configuration
# ------------------------------------------------------------
st.sidebar.header("⚙️ Configuration")

stock_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, MSFT):", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))
epochs = st.sidebar.slider("Number of Epochs", 10, 100, 25)
batch_size = st.sidebar.slider("Batch Size", 16, 128, 32)
time_steps = st.sidebar.slider("Time Steps (look-back window)", 30, 120, 60)

# ------------------------------------------------------------
# Step 1: Download Stock Data
# ------------------------------------------------------------
st.subheader(f"📥 Downloading Data for {stock_symbol}")

try:
    data = yf.download(stock_symbol, start=start_date, end=end_date)
    if data.empty:
        st.error("No data found. Please check the symbol or date range.")
        st.stop()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    st.stop()

st.dataframe(data.tail())

# ------------------------------------------------------------
# Step 2: Data Preparation
# ------------------------------------------------------------
dataset = data[['Close']].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

training_data_len = int(len(dataset) * 0.8)

# Training set
train_data = scaled_data[:training_data_len]
X_train, y_train = [], []
for i in range(time_steps, len(train_data)):
    X_train.append(train_data[i - time_steps:i, 0])
    y_train.append(train_data[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# ------------------------------------------------------------
# Step 3: Build LSTM Model
# ------------------------------------------------------------
st.subheader("🧠 Building and Training the Model...")

model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(units=50, return_sequences=True),
    Dropout(0.2),
    LSTM(units=50),
    Dropout(0.2),
    Dense(units=1)
])
model.compile(optimizer='adam', loss='mean_squared_error')

with st.spinner("Training in progress... ⏳"):
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)

st.success("✅ Model trained successfully!")

# ------------------------------------------------------------
# Step 4: Testing and Prediction
# ------------------------------------------------------------
test_data = scaled_data[training_data_len - time_steps:]
X_test, y_test = [], dataset[training_data_len:]
for i in range(time_steps, len(test_data)):
    X_test.append(test_data[i - time_steps:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

predicted_prices = model.predict(X_test)
predicted_prices = scaler.inverse_transform(predicted_prices)

# Evaluation Metrics
rmse = np.sqrt(mean_squared_error(y_test, predicted_prices))
mae = mean_absolute_error(y_test, predicted_prices)

st.metric(label="RMSE (Root Mean Squared Error)", value=f"{rmse:.2f}")
st.metric(label="MAE (Mean Absolute Error)", value=f"{mae:.2f}")

# ------------------------------------------------------------
# Step 5: Visualization
# ------------------------------------------------------------
st.subheader("📉 Real vs Predicted Stock Prices")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(y_test, color='black', label='Real Price')
ax.plot(predicted_prices, color='green', label='Predicted Price (LSTM)')
ax.set_title(f'{stock_symbol} Stock Price Prediction')
ax.set_xlabel('Time')
ax.set_ylabel('Price (USD)')
ax.legend()
st.pyplot(fig)

# ------------------------------------------------------------
# Step 6: Predict Next Day
# ------------------------------------------------------------
st.subheader("🔮 Next Day Price Prediction")

last_60_days = scaled_data[-time_steps:]
last_60_days = np.reshape(last_60_days, (1, time_steps, 1))
next_day_scaled = model.predict(last_60_days)
next_day_price = scaler.inverse_transform(next_day_scaled)

st.write(f"📈 **Predicted next day closing price for {stock_symbol}: ${next_day_price[0][0]:.2f}**")

# ------------------------------------------------------------
# Step 7: Save the Model
# ------------------------------------------------------------
if st.button("💾 Save Model"):
    model.save(f"{stock_symbol}_lstm_model.h5")
    st.success(f"Model saved as `{stock_symbol}_lstm_model.h5`")

st.markdown("---")
st.caption("Réalisé par Mehdi | EMSI 2023/2024 | Based on Keras + yFinance")


# # ============================================================
# # FASTAPI: Stock Price Prediction API (LSTM + yfinance)
# # Author: Mehdi (EMSI 2023/2024)
# # ============================================================

# from fastapi import FastAPI
# from pydantic import BaseModel
# import numpy as np
# import pandas as pd
# import yfinance as yf
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dropout, Dense
# from datetime import datetime, timedelta
# import uvicorn

# # ============================================================
# # 1️⃣ FastAPI Setup
# # ============================================================
# app = FastAPI(
#     title="AI Stock Prediction API",
#     description="Predict next-day stock prices using LSTM and Yahoo Finance data.",
#     version="1.0.0"
# )

# # ============================================================
# # 2️⃣ Request Model
# # ============================================================
# class StockRequest(BaseModel):
#     symbol: str
#     period: str = "6M"  # Default 6 months


# # ============================================================
# # 3️⃣ Helper: LSTM Training Function
# # ============================================================
# def train_lstm_model(df):
#     if df.empty or len(df) < 60:
#         return np.nan

#     data = df[['Close']].values
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     scaled_data = scaler.fit_transform(data)

#     X_train, y_train = [], []
#     for i in range(60, len(scaled_data)):
#         X_train.append(scaled_data[i - 60:i, 0])
#         y_train.append(scaled_data[i, 0])

#     X_train, y_train = np.array(X_train), np.array(y_train)
#     X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

#     model = Sequential([
#         LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
#         Dropout(0.2),
#         LSTM(50),
#         Dropout(0.2),
#         Dense(1)
#     ])
#     model.compile(optimizer='adam', loss='mean_squared_error')
#     model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=0)

#     last_60_days = scaled_data[-60:]
#     last_60_days = np.reshape(last_60_days, (1, 60, 1))
#     pred_scaled = model.predict(last_60_days)
#     pred_price = scaler.inverse_transform(pred_scaled)

#     return float(pred_price[0][0])


# # ============================================================
# # 4️⃣ Endpoint: Predict
# # ============================================================
# @app.post("/predict")
# def predict_stock(data: StockRequest):
#     now = datetime.now()
#     periods = {
#         '1D': now - timedelta(days=1),
#         '5D': now - timedelta(days=5),
#         '1M': now - timedelta(days=30),
#         '6M': now - timedelta(days=180),
#         '1Y': now - timedelta(days=365),
#         '5Y': now - timedelta(days=5 * 365),
#         'All': '2010-01-01'
#     }

#     start_date = periods.get(data.period.upper(), now - timedelta(days=180))
#     df = yf.download(data.symbol, start=start_date, end=now, progress=False)

#     if df.empty:
#         return {"error": "No data found for this stock or period."}

#     predicted_price = train_lstm_model(df)

#     return {
#         "symbol": data.symbol.upper(),
#         "period": data.period,
#         "predicted_price": predicted_price,
#         "last_close": float(df['Close'][-1]),
#         "start_date": str(start_date),
#         "end_date": str(now.strftime('%Y-%m-%d')),
#         "data_points": len(df)
#     }


# # ============================================================
# # 5️⃣ Run App
# # ============================================================
# if __name__ == "__main__":
#     uvicorn.run("app_fastapi:app", host="0.0.0.0", port=8000, reload=True)
