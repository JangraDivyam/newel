import numpy as np
import pandas as pd


# STEP-2 FUNCTION (LABELING)
def create_early_failure_labels(df, horizon_steps=720):

    df = df.copy()

    # detect failure start
    df["failure_event"] = (df["LPS"].diff() == 1).astype(int)

    # create target
    df["target"] = 0

    failure_indices = df.index[df["failure_event"] == 1].tolist()

    for idx in failure_indices:
        start = max(0, idx - horizon_steps)
        df.loc[start:idx, "target"] = 1

    return df


# STEP-3 FUNCTION (WINDOW FEATURES)
def create_window_features(df, window_size=360, stride=60):

    feature_rows = []

    sensor_cols = df.columns.drop(
        ["timestamp", "LPS", "failure_event", "target"]
    )

    for start in range(0, len(df) - window_size, stride):

        end = start + window_size
        window = df.iloc[start:end]

        feature_dict = {}

        for col in sensor_cols:

            values = window[col].values

            # feature_dict[f"{col}_mean"] = np.mean(values)
            # feature_dict[f"{col}_std"] = np.std(values)
            # feature_dict[f"{col}_min"] = np.min(values)
            # feature_dict[f"{col}_max"] = np.max(values)
            # feature_dict[f"{col}_last"] = values[-1]
            # feature_dict[f"{col}_trend"] = values[-1] - values[0]

            feature_dict[f"{col}_mean"] = np.mean(values)
            feature_dict[f"{col}_std"] = np.std(values)
            feature_dict[f"{col}_min"] = np.min(values)
            feature_dict[f"{col}_max"] = np.max(values)
            feature_dict[f"{col}_last"] = values[-1]

            # ⭐ NEW FEATURES
            feature_dict[f"{col}_range"] = np.max(values) - np.min(values)
            feature_dict[f"{col}_trend"] = values[-1] - values[0]
            feature_dict[f"{col}_abs_change"] = np.mean(np.abs(np.diff(values)))
            feature_dict[f"{col}_variance"] = np.var(values)

        # feature_dict["target"] = window["target"].iloc[-1]
        if window["target"].sum() > 0:
            feature_dict["target"] = 1
        else:
            feature_dict["target"] = 0

        feature_rows.append(feature_dict)

    feature_df = pd.DataFrame(feature_rows)

    return feature_df