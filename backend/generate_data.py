import numpy as np
import pandas as pd
import os

np.random.seed(42)

OUT_DIR = "data/testing"
os.makedirs(OUT_DIR, exist_ok=True)

HOURS = 24 * 30

def generate_normal(month):
    voltage = 230 + np.random.normal(0, 2, HOURS)
    current = 10 + np.random.normal(0, 0.5, HOURS)
    frequency = 50 + np.random.normal(0, 0.03, HOURS)
    power = voltage * current + np.random.normal(0, 5, HOURS)

    return pd.DataFrame({
        "voltage": voltage,
        "current": current,
        "frequency": frequency,
        "power": power
    })

def inject_fdi(df, attack_type="voltage_bias"):
    df = df.copy()

    if attack_type == "voltage_bias":
        df["voltage"] *= 1.08
        df["power"] *= 1.10

    elif attack_type == "power_injection":
        df["power"] += np.random.normal(200, 30, len(df))

    elif attack_type == "stealth_drift":
        drift = np.linspace(0, 0.07, len(df))
        df["voltage"] *= (1 + drift)
        df["power"] *= (1 + drift)

    return df

ATTACK_MONTHS = {
    "2025_04": "voltage_bias",
    "2025_06": "power_injection",
    "2025_09": "stealth_drift"
}

for m in range(1, 13):
    month = f"2025_{m:02d}"
    df = generate_normal(month)

    if month in ATTACK_MONTHS:
        df = inject_fdi(df, ATTACK_MONTHS[month])
        name = f"{month}_attack.csv"
        print(f"🚨 Generated ATTACK data: {name}")
    else:
        name = f"{month}.csv"
        print(f"✅ Generated normal data: {name}")

    df.to_csv(os.path.join(OUT_DIR, name), index=False)
