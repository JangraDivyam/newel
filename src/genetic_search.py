import random
import numpy as np

from src.feature_engineering import create_window_features
from src.model import train_random_forest


# ⭐ Search space
WINDOW_SIZES = [360, 540, 720]
STRIDES = [60, 120]
N_ESTIMATORS = [100, 200]
MAX_DEPTHS = [10, None]
FEATURE_RATIO = [0.5, 0.7, 1.0]


def generate_individual():
    return {
        "window_size": random.choice(WINDOW_SIZES),
        "stride": random.choice(STRIDES),
        "n_estimators": random.choice(N_ESTIMATORS),
        "max_depth": random.choice(MAX_DEPTHS),
        "feature_ratio": random.choice(FEATURE_RATIO),
    }


def mutate(ind):
    ind["window_size"] = random.choice(WINDOW_SIZES)
    ind["stride"] = random.choice(STRIDES)
    return ind


def fitness(ind, df):

    # create features
    feature_df = create_window_features(
        df,
        window_size=ind["window_size"],
        stride=ind["stride"]
    )

    split = int(0.8 * len(feature_df))

    train = feature_df.iloc[:split]
    test = feature_df.iloc[split:]

    X_train = train.drop(columns=["target"])
    y_train = train["target"]

    X_test = test.drop(columns=["target"])
    y_test = test["target"]

    # select subset of features according to individual's feature_ratio
    cols = X_train.columns.tolist()
    k = int(len(cols) * ind.get("feature_ratio", 1.0))
    if k < 1:
        k = 1
    selected = random.sample(cols, k)

    X_train = X_train[selected]
    X_test = X_test[selected]

    # train model
    model = train_random_forest(X_train, y_train)

    y_pred = model.predict(X_test)

    # fitness = recall for failure class
    recall = np.sum((y_test == 1) & (y_pred == 1)) / max(1, np.sum(y_test == 1))

    return recall