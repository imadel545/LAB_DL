# ============================================================
# LSTM Stock Price Prediction using yfinance
# Réalisé par: El jeddaoui imadeddine (EMSI 2025/2026)
# Reference: Towards Data Science, Keras Documentation
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense

# ------------------------------------------------------------
# Step 1: Download stock data using yfinance
# ------------------------------------------------------------
stock_symbol = "AAPL"  # Example: Apple Inc. (You can change this to TSLA, MSFT, etc.)
start_date = "2018-01-01"
end_date = "2024-12-31"

print(f"Downloading data for {stock_symbol}...")
data = yf.download(stock_symbol, start=start_date, end=end_date)
print(data.head())

# ------------------------------------------------------------
# Step 2: Prepare training data
# ------------------------------------------------------------
# We'll use the "Close" price
dataset = data[['Close']].values

# Normalize data (important for LSTM)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset)

# Create sequences (60 previous days -> 1 next day)
X_train = []
y_train = []
time_steps = 60

for i in range(time_steps, len(scaled_data)):
    X_train.append(scaled_data[i - time_steps:i, 0])
    y_train.append(scaled_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# ------------------------------------------------------------
# Step 3: Build the LSTM model
# ------------------------------------------------------------
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))  # Output layer

model.compile(optimizer='adam', loss='mean_squared_error')
model.summary()

# ------------------------------------------------------------
# Step 4: Train the model
# ------------------------------------------------------------
print("Training model...")
model.fit(X_train, y_train, epochs=25, batch_size=32, verbose=1)

# ------------------------------------------------------------
# Step 5: Prepare test data and make predictions
# ------------------------------------------------------------
# Split data into training and testing (80/20)
training_data_len = int(len(dataset) * 0.8)
test_data = dataset[training_data_len - time_steps:, :]

# Prepare test sequences
inputs = scaler.transform(test_data)
X_test = []
for i in range(time_steps, len(inputs)):
    X_test.append(inputs[i - time_steps:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Predict
predicted_prices = model.predict(X_test)
predicted_prices = scaler.inverse_transform(predicted_prices)

# ------------------------------------------------------------
# Step 6: Visualization
# ------------------------------------------------------------
real_prices = dataset[training_data_len:, :]

plt.figure(figsize=(12, 6))
plt.plot(real_prices, color='black', label=f'Real {stock_symbol} Price')
plt.plot(predicted_prices, color='green', label=f'Predicted {stock_symbol} Price (LSTM)')
plt.title(f'{stock_symbol} Stock Price Prediction using LSTM')
plt.xlabel('Time')
plt.ylabel('Stock Price (USD)')
plt.legend()
plt.show()

# ------------------------------------------------------------
# Step 7: Save the model
# ------------------------------------------------------------
model.save(f'{stock_symbol}_lstm_model.h5')
print(f"✅ Model saved as {stock_symbol}_lstm_model.h5")

# ------------------------------------------------------------
# Step 8 (Optional): Predict next day price
# ------------------------------------------------------------
last_60_days = scaled_data[-time_steps:]
last_60_days = np.reshape(last_60_days, (1, time_steps, 1))
next_day_scaled = model.predict(last_60_days)
next_day_price = scaler.inverse_transform(next_day_scaled)

print(f"\n📈 Predicted next day {stock_symbol} closing price: ${next_day_price[0][0]:.2f}")

# # ============================================================
# # Stock Price Prediction Dashboard with LSTM + yfinance
# # Designed like Yahoo Finance chart
# # Author: Mehdi (EMSI 2023/2024)
# # ============================================================

# import numpy as np
# import pandas as pd
# import yfinance as yf
# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import LSTM, Dropout, Dense
# from datetime import datetime, timedelta
# import plotly.graph_objects as go
# from dash import Dash, dcc, html, Input, Output

# # ============================================================
# # 1️⃣ Create the LSTM model function
# # ============================================================
# def train_lstm_model(df):
#     data = df[['Close']].values
#     scaler = MinMaxScaler(feature_range=(0, 1))
#     scaled_data = scaler.fit_transform(data)

#     X_train, y_train = [], []
#     for i in range(60, len(scaled_data)):
#         X_train.append(scaled_data[i-60:i, 0])
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
#     return pred_price[0][0]

# # ============================================================
# # 2️⃣ Create the Dash app
# # ============================================================
# app = Dash(__name__)
# app.title = "Stock Dashboard (LSTM)"

# # Layout
# app.layout = html.Div(style={'backgroundColor': '#0d1117', 'color': 'white', 'fontFamily': 'Arial'}, children=[
#     html.H2("📈 AI Stock Price Prediction Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),

#     # Dropdown for stock selection
#     html.Div([
#         html.Label("Select Stock Symbol:", style={'fontWeight': 'bold'}),
#         dcc.Dropdown(
#             id='stock-symbol',
#             options=[
#                 {'label': 'Apple (AAPL)', 'value': 'AAPL'},
#                 {'label': 'Tesla (TSLA)', 'value': 'TSLA'},
#                 {'label': 'Microsoft (MSFT)', 'value': 'MSFT'},
#                 {'label': 'Amazon (AMZN)', 'value': 'AMZN'},
#             ],
#             value='AAPL',
#             clearable=False,
#             style={'width': '300px', 'color': 'black'}
#         )
#     ], style={'textAlign': 'center', 'marginBottom': '20px'}),

#     # Period selector (like Yahoo Finance)
#     html.Div([
#         html.Button(period, id=period, n_clicks=0,
#                     style={'margin': '3px', 'backgroundColor': '#161b22', 'color': 'white', 'border': '1px solid #30363d', 'padding': '6px 12px'})
#         for period in ['1D', '5D', '1M', '6M', '1Y', '5Y', 'All']
#     ], style={'textAlign': 'center', 'marginBottom': '10px'}),

#     # Graph
#     dcc.Graph(id='stock-chart', style={'height': '500px'}),

#     # Info section
#     html.Div(id='stock-info', style={'textAlign': 'center', 'marginTop': '30px', 'fontSize': '16px'})
# ])

# # ============================================================
# # 3️⃣ Callbacks
# # ============================================================
# @app.callback(
#     Output('stock-chart', 'figure'),
#     Output('stock-info', 'children'),
#     [Input('stock-symbol', 'value')] +
#     [Input(period, 'n_clicks') for period in ['1D', '5D', '1M', '6M', '1Y', '5Y', 'All']]
# )
# def update_chart(symbol, *args):
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         period = '6M'
#     else:
#         period = ctx.triggered[0]['prop_id'].split('.')[0]

#     now = datetime.now()
#     periods = {
#         '1D': now - timedelta(days=1),
#         '5D': now - timedelta(days=5),
#         '1M': now - timedelta(days=30),
#         '6M': now - timedelta(days=180),
#         '1Y': now - timedelta(days=365),
#         '5Y': now - timedelta(days=5*365),
#         'All': '2010-01-01'
#     }

#     start_date = periods[period]
#     df = yf.download(symbol, start=start_date, end=now)
#     predicted_price = train_lstm_model(df)

#     # Plotly chart
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price', line=dict(color='cyan')))
#     fig.add_hline(y=predicted_price, line_dash="dot", line_color='green',
#                   annotation_text=f'Predicted Next Close: ${predicted_price:.2f}',
#                   annotation_position="top right")
#     fig.update_layout(
#         template='plotly_dark',
#         paper_bgcolor='#0d1117',
#         plot_bgcolor='#0d1117',
#         font=dict(color='white'),
#         margin=dict(l=20, r=20, t=50, b=20),
#         xaxis_title="Date",
#         yaxis_title="Price (USD)",
#     )

#     # Stock info
#     info = yf.Ticker(symbol).info
#     info_text = html.Div([
#         html.P(f"📅 Range: {start_date} → {now.strftime('%Y-%m-%d')}"),
#         html.P(f"💰 Previous Close: {info.get('previousClose')}  |  Open: {info.get('open')}"),
#         html.P(f"📊 Market Cap: {info.get('marketCap')}  |  Volume: {info.get('volume')}"),
#         html.P(f"📈 52-Week Range: {info.get('fiftyTwoWeekLow')} – {info.get('fiftyTwoWeekHigh')}"),
#         html.P(f"💹 PE Ratio (TTM): {info.get('trailingPE')}  |  EPS (TTM): {info.get('trailingEps')}"),
#         html.P(f"📆 Next Earnings Date: {info.get('earningsDate')}")
#     ])

#     return fig, info_text

# # ============================================================
# # Run app
# # ============================================================
# if __name__ == '__main__':
#     app.run_server(debug=True)
