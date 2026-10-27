"""Step 2: Turn each function into a numeric feature vector for ML."""
import csv, sys
from static_analyzer import analyze

FEATURE_NAMES = [
    "loc", "complexity", "max_nesting", "n_params", "has_docstring",
    "n_returns", "n_calls", "complexity_per_loc",
    "n_high", "n_medium", "n_low",
]

def extract_features(source: str, file_name: str = "<input>"):
    """Returns a list of rows: one dict per function (identity + features)."""
    findings, metrics = analyze(source)
    rows = []
    for m in metrics:
        mine = [f for f in findings if f.function == m.name]
        row = {
            "file": file_name, "function": m.name, "line": m.line,
            "loc": m.loc,
            "complexity": m.complexity,
            "max_nesting": m.max_nesting,
            "n_params": m.n_params,
            "has_docstring": int(m.has_docstring),
            "n_returns": m.n_returns,
            "n_calls": m.n_calls,
            "complexity_per_loc": round(m.complexity / max(m.loc, 1), 3),
            "n_high": sum(f.severity == "high" for f in mine),
            "n_medium": sum(f.severity == "medium" for f in mine),
            "n_low": sum(f.severity == "low" for f in mine),
        }
        rows.append(row)
    return rows

def to_matrix(rows):
    """Rows -> list of number lists in FEATURE_NAMES order (for scikit-learn)."""
    return [[r[name] for name in FEATURE_NAMES] for r in rows]

def files_to_csv(paths, out_csv):
    all_rows = []
    for p in paths:
        try:
            all_rows += extract_features(open(p, encoding="utf-8").read(), p)
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"skip {p}: {e}")
    if not all_rows:
        print("no functions found"); return
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader(); w.writerows(all_rows)
    print(f"{len(all_rows)} functions -> {out_csv}")

if __name__ == "__main__":
    # usage: python feature_extractor.py out.csv file1.py file2.py ...
    files_to_csv(sys.argv[2:], sys.argv[1])