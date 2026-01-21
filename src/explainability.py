import pandas as pd
import matplotlib.pyplot as plt

from lightgbm import LGBMClassifier


def plot_feature_importance(model, features):
    importance = model.feature_importances_

    imp_df = pd.DataFrame({
        "feature": features,
        "importance": importance
    }).sort_values("importance", ascending=False)

    print("\n===== GLOBAL FEATURE IMPORTANCE =====")
    print(imp_df)

    plt.figure(figsize=(8, 5))
    plt.barh(imp_df["feature"], imp_df["importance"])
    plt.gca().invert_yaxis()
    plt.title("LightGBM Feature Importance")
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.show()

    


if __name__ == "__main__":
    from split_and_checks import time_based_split
    from regime_features import add_regime_features

    # Load data
    df = pd.read_parquet("data/processed/reliance_labeled.parquet")
    df = add_regime_features(df)
    df = df.dropna()

    train_df, val_df, test_df = time_based_split(df)

    FEATURES = [
        "log_return",
        "vol_past",
        "Volume",
        "vol_percentile",
        "vol_compression",
        "trend_strength"
    ]

    TARGET = "vol_expansion"

    model = LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        class_weight="balanced",
        random_state=42
    )

    model.fit(train_df[FEATURES], train_df[TARGET])

    plot_feature_importance(model, FEATURES)
