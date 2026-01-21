import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, RepeatVector, TimeDistributed

DATA_DIR = "../data/uploaded"
MODEL_DIR = "model"
TIMESTEPS = 24

os.makedirs(MODEL_DIR, exist_ok=True)

files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)]
dfs = [pd.read_csv(f) for f in files]
data = pd.concat(dfs).values

scaler = MinMaxScaler()
scaled = scaler.fit_transform(data)
joblib.dump(scaler, f"{MODEL_DIR}/scaler.save")

def seq(data):
    return np.array([data[i:i+TIMESTEPS] for i in range(len(data)-TIMESTEPS)])

X = seq(scaled)

inp = Input(shape=(TIMESTEPS, X.shape[2]))
x = LSTM(64)(inp)
x = Dense(32, activation="relu")(x)
x = RepeatVector(TIMESTEPS)(x)
x = LSTM(64, return_sequences=True)(x)
out = TimeDistributed(Dense(X.shape[2]))(x)

model = Model(inp, out)
model.compile(optimizer="adam", loss="mse")
model.fit(X, X, epochs=25, batch_size=32)

model.save(f"{MODEL_DIR}/lstm_autoencoder.keras")

recon = model.predict(X)
errors = np.mean(np.abs(recon - X), axis=(1,2))
threshold = np.percentile(errors, 99)

with open(f"{MODEL_DIR}/threshold.txt", "w") as f:
    f.write(str(threshold))

print("Training complete")
