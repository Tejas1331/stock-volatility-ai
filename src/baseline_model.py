import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_recall_curve, auc
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


def train_baseline(train_df, val_df, features, target):
    # ----------------------------
    # Prepare data
    # ----------------------------
    X_train = train_df[features]
    y_train = train_df[target]

    X_val = val_df[features]
    y_val = val_df[target]

    # ----------------------------
    # Model pipeline
    # ----------------------------
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    # ----------------------------
    # Probabilities (NOT labels)
    # ----------------------------
    val_probs = pipeline.predict_proba(X_val)[:, 1]

    # ----------------------------
    # Precision–Recall analysis
    # ----------------------------
    precision, recall, thresholds = precision_recall_curve(y_val, val_probs)
    pr_auc = auc(recall, precision)

    print("\n===== PRECISION–RECALL ANALYSIS =====")
    print(f"PR-AUC: {pr_auc:.4f}")

    threshold_df = pd.DataFrame({
        "threshold": thresholds,
        "precision": precision[:-1],
        "recall": recall[:-1]
    })

    # Sort by recall (descending)
    threshold_df = threshold_df.sort_values("recall", ascending=False)

    print("\nTop threshold candidates (high recall first):")
    print(threshold_df.head(10))

    # ----------------------------
    # Choose a business-aware threshold
    # ----------------------------
    chosen_threshold = 0.25   # reasonable starting point
    val_preds = (val_probs >= chosen_threshold).astype(int)

    print(f"\n===== CLASSIFICATION REPORT @ THRESHOLD {chosen_threshold} =====")
    print(classification_report(y_val, val_preds, digits=4))

    return pipeline, pr_auc


if __name__ == "__main__":
    from split_and_checks import time_based_split
    from regime_features import add_regime_features

    # ----------------------------
    # Load persisted dataset
    # ----------------------------
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

    model, pr_auc = train_baseline(
        train_df,
        val_df,
        FEATURES,
        TARGET
    )
