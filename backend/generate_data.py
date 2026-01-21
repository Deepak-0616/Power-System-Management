import numpy as np
import pandas as pd
import os

np.random.seed(0)

OUT = "../data/uploaded"
os.makedirs(OUT, exist_ok=True)

def generate(month):
    n = 24 * 30
    voltage = 230 + np.random.normal(0, 2, n)
    current = 10 + np.random.normal(0, 0.5, n)
    frequency = 50 + np.random.normal(0, 0.03, n)
    power = voltage * current + np.random.normal(0, 5, n)

    df = pd.DataFrame({
        "voltage": voltage,
        "current": current,
        "frequency": frequency,
        "power": power
    })

    df.to_csv(f"{OUT}/{month}.csv", index=False)
    print(f"Generated {month}.csv")

generate("2022_01")
generate("2022_02")
generate("2022_03")
