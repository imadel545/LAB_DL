# Lab: Stock price prediction
# Réalisé par: Your Name EMSI 2023/2024
# Réf: https://towardsdatascience.com/predicting-stock-prices-using-a-keras-lstm-model-4225457f0233

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# ===== TensorFlow (tf.keras) =====
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# --- Metal/MPS (Mac M1) : activer la croissance mémoire GPU ---
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    except Exception:
        pass

# ===== Chemins robustes =====
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Dataset"          # <-- respecte la casse "Dataset"
TRAIN_CSV = DATA_DIR / "train_dataset.csv"
TEST_CSV  = DATA_DIR / "test_dataset.csv"

assert TRAIN_CSV.exists(), f"Fichier introuvable: {TRAIN_CSV}"
assert TEST_CSV.exists(),  f"Fichier introuvable: {TEST_CSV}"

# ===== Step 1: Dataset =====
dataset_train = pd.read_csv(TRAIN_CSV)
training_set = dataset_train.iloc[:, 1:2].values  # colonne 'Open' (index 1)
print("Train head:\n", dataset_train.head())

# Normalisation [0,1]
sc = MinMaxScaler(feature_range=(0, 1))
training_set_scaled = sc.fit_transform(training_set)

# Fenêtrage (lookback=60)
lookback = 60
X_train, y_train = [], []
for i in range(lookback, len(training_set_scaled)):
    X_train.append(training_set_scaled[i - lookback:i, 0])
    y_train.append(training_set_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)

# Reshape LSTM: (batch, timesteps, features)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# ===== Step 2: Model =====
model = Sequential([
    LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
    Dropout(0.2),
    LSTM(units=50, return_sequences=True),
    Dropout(0.2),
    LSTM(units=50, return_sequences=True),
    Dropout(0.2),
    LSTM(units=50),
    Dropout(0.2),
    Dense(units=1)
])

model.compile(optimizer=Adam(), loss='mean_squared_error')

# ===== Step 3: Train =====
model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=1)

# ===== Step 4: Test =====
dataset_test = pd.read_csv(TEST_CSV)
real_stock_price = dataset_test.iloc[:, 1:2].values  # 'Open' (index 1)

# Concat train+test pour construire la fenêtre d'entrée du test
dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']), axis=0)
inputs = dataset_total[len(dataset_total) - len(dataset_test) - lookback:].values
inputs = inputs.reshape(-1, 1)
inputs = sc.transform(inputs)

X_test = []
for i in range(lookback, lookback + len(dataset_test)):
    X_test.append(inputs[i - lookback:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# ===== Prediction =====
predicted_stock_price = model.predict(X_test, verbose=0)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

# ===== Plot =====
plt.figure()
plt.plot(real_stock_price, color='black', label='Real Stock Price')
plt.plot(predicted_stock_price, color='green', label='Predicted Stock Price')
plt.title('Stock Price Prediction (LSTM)')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.tight_layout()
plt.show()

# ===== Save model =====
model_path = BASE_DIR / 'tata_model.h5'
model.save(model_path)
print(f"✅ Modèle sauvegardé: {model_path}")
