import os
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "lstm_autoencoder.keras")
SCALER_PATH = os.path.join(BASE, "model", "scaler.save")
THRESHOLD_PATH = os.path.join(BASE, "model", "threshold.txt")

model = load_model(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
THRESHOLD = float(open(THRESHOLD_PATH).read())

TIMESTEPS = 24

def make_sequences(data):
    return np.array([data[i:i+TIMESTEPS] for i in range(len(data)-TIMESTEPS)])

def generate_predicted_dataset(uploaded_files, output_path):
    dfs = [pd.read_csv(f) for f in uploaded_files]
    data = pd.concat(dfs).values
    scaled = scaler.fit_transform(data)

    X = make_sequences(scaled)
    reconstructed = model.predict(X)

    predicted = reconstructed.mean(axis=1)
    pd.DataFrame(predicted).to_csv(output_path, index=False)

def validate_actual_vs_predicted(actual_csv, predicted_csv):
    actual = pd.read_csv(actual_csv).values
    predicted = pd.read_csv(predicted_csv).values

    length = min(len(actual), len(predicted))
    error = np.mean(np.abs(actual[:length] - predicted[:length]))

    return error, error > THRESHOLD
