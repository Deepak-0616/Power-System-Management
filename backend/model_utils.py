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
    return np.array([data[i:i + TIMESTEPS] for i in range(len(data) - TIMESTEPS)])

def generate_predicted_dataset(uploaded_files, output_path):
    dfs = [pd.read_csv(f) for f in uploaded_files]
    data = pd.concat(dfs, ignore_index=True)

    REQUIRED_COLUMNS = ["voltage", "current", "frequency", "power"]
    data = data[REQUIRED_COLUMNS]

    scaled = scaler.transform(data.values)

    X = make_sequences(scaled)
    reconstructed = model.predict(X)

    predicted_scaled = reconstructed.mean(axis=1)

    # ✅ CONVERT BACK TO REAL UNITS
    predicted_real = scaler.inverse_transform(predicted_scaled)

    df = pd.DataFrame(predicted_real, columns=REQUIRED_COLUMNS)
    df.to_csv(output_path, index=False)


def validate_actual_vs_predicted(actual_csv, predicted_csv):
    actual = pd.read_csv(actual_csv)
    predicted = pd.read_csv(predicted_csv)

    min_len = min(len(actual), len(predicted))
    actual = actual.iloc[:min_len]
    predicted = predicted.iloc[:min_len]

    actual_s = scaler.transform(actual.values)
    predicted_s = scaler.transform(predicted.values)

    deviation = np.mean(np.abs(actual_s - predicted_s))

    # ✅ RETURN PURE PYTHON TYPES
    return float(deviation), bool(deviation > THRESHOLD)
