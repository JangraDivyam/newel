import pandas as pd
import os

from src.feature_engineering import (
    create_early_failure_labels,
    create_window_features
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "raw", "metropt-3.csv")

# STEP 1 — load
df = pd.read_csv(file_path)

df = df.drop(columns=["Unnamed: 0"])
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

print("Raw shape:", df.shape)

# STEP 2 — labeling
df = create_early_failure_labels(df)

print("Failure events:", df["failure_event"].sum())
print("Target counts:\n", df["target"].value_counts())

# STEP 3 — windowing
feature_df = create_window_features(df)

print("Feature dataset shape:", feature_df.shape)
print("Window target counts:\n", feature_df["target"].value_counts())
print(feature_df.head())

from src.model import train_random_forest, evaluate_model

# ----------------------------
# STEP 4 — Train/Test Split
# ----------------------------

split_index = int(0.8 * len(feature_df))

train_df = feature_df.iloc[:split_index]
test_df = feature_df.iloc[split_index:]

X_train = train_df.drop(columns=["target"])
y_train = train_df["target"]

X_test = test_df.drop(columns=["target"])
y_test = test_df["target"]

print("\nTrain size:", X_train.shape)
print("Test size:", X_test.shape)

# ----------------------------
# Train Model
# ----------------------------

model = train_random_forest(X_train, y_train)

# ----------------------------
# Evaluate
# ----------------------------

evaluate_model(model, X_test, y_test)

import joblib
joblib.dump(model, "random_forest_model.pkl")
print("Model saved to random_forest_model.pkl")

from src.genetic_search import generate_individual, mutate, fitness

print("\n--- Running Genetic Search ---")

population = [generate_individual() for _ in range(5)]

for gen in range(3):
    print(f"\nGeneration {gen+1}")

    scores = []

    for ind in population:
        score = fitness(ind, df)
        print(ind, "-> Recall:", score)
        scores.append((score, ind))

    scores.sort(reverse=True, key=lambda x: x[0])

    # keep best 2
    population = [scores[0][1], scores[1][1]]

    # mutate
    while len(population) < 5:
        new_ind = mutate(scores[0][1].copy())
        population.append(new_ind)

best = scores[0]
print("\nBest config:", best)