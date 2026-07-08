import pandas as pd
import numpy as np

# Generate a small mock dataset for testing
n_rows = 5000
dates = pd.date_range(start="2023-01-01", periods=n_rows, freq="1min")
lps = np.zeros(n_rows)
# Add some fake failures well spaced out so the sliding window captures both 0s and 1s
lps[1000] = 1 
lps[2500] = 1
lps[4000] = 1

data = {
    "Unnamed: 0": range(n_rows),
    "timestamp": dates,
    "LPS": lps,
    "sensor_1": np.random.normal(0, 1, n_rows),
    "sensor_2": np.random.normal(5, 2, n_rows),
}

df = pd.DataFrame(data)
df.to_csv("data/raw/metropt-3.csv", index=False)
print("Mock dataset updated!")
