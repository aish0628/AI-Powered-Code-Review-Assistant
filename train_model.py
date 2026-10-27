"""Step 4: Train ML model to predict risky (buggy-looking) functions."""
import sys, glob
import pandas as pd, joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from feature_extractor import FEATURE_NAMES

def load(pattern):
    files = glob.glob(pattern)
    if not files:
        sys.exit(f"No files match {pattern}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    return df.drop_duplicates()

def main(pattern, model_out="model.joblib"):
    df = load(pattern)
    print(f"Rows: {len(df)} | buggy: {int(df.label.sum())} | clean: {int((1-df.label).sum())}")
    X, y = df[FEATURE_NAMES], df["label"]
    # Split by commit so before/after pairs never leak between train and test
    groups = df["commit"].astype(str) + df["file"].astype(str)
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42).split(X, y, groups))
    Xtr, Xte, ytr, yte = X.iloc[tr], X.iloc[te], y.iloc[tr], y.iloc[te]

    models = {
        "LogisticRegression (baseline)": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")),
        "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=8, class_weight="balanced", random_state=42),
    }
    best, best_auc = None, -1
    for name, m in models.items():
        m.fit(Xtr, ytr)
        prob = m.predict_proba(Xte)[:, 1]
        auc = roc_auc_score(yte, prob) if yte.nunique() > 1 else float("nan")
        print(f"\n=== {name} | ROC-AUC: {auc:.3f} ===")
        print(classification_report(yte, m.predict(Xte), target_names=["clean", "buggy"], zero_division=0))
        if auc > best_auc:
            best, best_auc, best_name = m, auc, name
    print(f"Best model: {best_name}")
    if hasattr(best, "feature_importances_"):
        imp = sorted(zip(FEATURE_NAMES, best.feature_importances_), key=lambda x: -x[1])
        print("Feature importance:")
        for n, v in imp:
            print(f"  {n:20s} {v:.3f}")
    joblib.dump({"model": best, "features": FEATURE_NAMES}, model_out)
    print(f"Saved -> {model_out}")

if __name__ == "__main__":
    # usage: python train_model.py "dataset*.csv" [model.joblib]
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "model.joblib")