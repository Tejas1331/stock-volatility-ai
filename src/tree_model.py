from lightgbm import LGBMClassifier

FEATURES = [
    "log_return",
    "vol_past",
    "Volume",
    "vol_percentile",
    "vol_compression",
    "trend_strength"
]

TARGET = "vol_expansion"


def train_lightgbm_model(df):
    """
    Trains a LightGBM model on full historical data.
    Assumes data has already passed sanity checks.
    """

    X = df[FEATURES]
    y = df[TARGET]

    model = LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=-1,
        num_leaves=31,
        min_child_samples=50,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary",
        class_weight="balanced",
        random_state=42
    )

    model.fit(X, y)

    return model
