"""One-time training script. Run from the backend/ directory: python ml/train.py"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo

ML_DIR = Path(__file__).parent
CSV_PATH = ML_DIR / "dataset.csv"
MODEL_PATH = ML_DIR / "model.pkl"
FEATURES_PATH = ML_DIR / "feature_columns.json"
DEFAULTS_PATH = ML_DIR / "feature_defaults.json"


def load_or_fetch_dataset() -> pd.DataFrame:
    if CSV_PATH.exists():
        print(f"Loading existing dataset from {CSV_PATH}")
        return pd.read_csv(CSV_PATH)

    print("Downloading dataset from UCI ML Repository (id=327)...")
    phishing = fetch_ucirepo(id=327)
    df = phishing.data.features.copy()
    df["result"] = phishing.data.targets
    df.to_csv(CSV_PATH, index=False)
    print(f"Saved {len(df)} rows to {CSV_PATH}")
    return df


def main():
    df = load_or_fetch_dataset()
    print(f"Dataset shape: {df.shape}")

    # Binary target: 1 = phishing (-1 in UCI), 0 = legitimate (1 in UCI)
    df["target"] = (df["result"] == -1).astype(int)
    print(f"Phishing: {df['target'].sum()}  Legitimate: {(df['target'] == 0).sum()}")

    # Train on all 30 UCI feature columns for maximum accuracy.
    # At inference, the 9 URL-extractable features are mapped explicitly;
    # the remaining 21 columns are filled with their training-set mean so the
    # model sees "average URL" behaviour rather than a forced legitimate default.
    feature_cols = [c for c in df.columns if c not in ("result", "target")]
    X = df[feature_cols]
    y = df["target"]

    # Save per-column means before splitting (whole-dataset mean = neutral default)
    col_means = {col: round(float(X[col].mean()), 6) for col in feature_cols}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"Train: {len(X_train)}  Test: {len(X_test)}  Features: {len(feature_cols)}")

    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    train_acc = clf.score(X_train, y_train)
    test_acc = clf.score(X_test, y_test)
    print(f"\nTraining accuracy: {train_acc:.4f}")
    print(f"Test accuracy:     {test_acc:.4f}")

    y_pred = clf.predict(X_test)
    print("\nClassification report:")
    print(classification_report(y_test, y_pred, target_names=["legitimate", "phishing"]))

    if test_acc < 0.90:
        print("WARNING: test accuracy below 90% — check feature mapping", file=sys.stderr)

    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    with open(FEATURES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)
    print(f"Feature columns saved to {FEATURES_PATH}")

    with open(DEFAULTS_PATH, "w") as f:
        json.dump(col_means, f, indent=2)
    print(f"Feature defaults (column means) saved to {DEFAULTS_PATH}")


if __name__ == "__main__":
    main()
