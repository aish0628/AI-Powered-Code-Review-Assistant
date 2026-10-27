"""Step 5: Fuse static findings + ML risk score into a ranked review."""
import argparse, json, os
import joblib
import pandas as pd
from static_analyzer import analyze
from feature_extractor import extract_features, FEATURE_NAMES

SEV_W = {"high": 1.0, "medium": 0.5, "low": 0.15}
W_ML, W_RULES = 0.5, 0.5   # fusion weights (tune in evaluation step)

def load_model(path):
    if path and os.path.exists(path):
        return joblib.load(path)["model"]
    return None

def rule_score(findings):
    """0..1 score from findings: worst finding + small bonus per extra."""
    if not findings:
        return 0.0
    ws = sorted((SEV_W[f.severity] for f in findings), reverse=True)
    return min(1.0, ws[0] + 0.1 * sum(ws[1:]))

def level(score):
    return "HIGH" if score >= 0.6 else "MEDIUM" if score >= 0.3 else "LOW"

def review(source, file_name="<input>", model=None, ml_weight=None):
    """ml_weight: 0..1 override for how much the fused priority trusts the ML score
    vs the static rules (defaults to W_ML)."""
    w_ml = W_ML if ml_weight is None else ml_weight
    w_rules = 1 - w_ml
    findings, _ = analyze(source)
    rows = extract_features(source, file_name)
    items = []
    for r in rows:
        mine = [f for f in findings if f.function == r["function"]]
        ml = None
        if model is not None:
            ml = float(model.predict_proba(pd.DataFrame([[r[n] for n in FEATURE_NAMES]], columns=FEATURE_NAMES))[0][1])
        rs = rule_score(mine)
        priority = rs if ml is None else w_ml * ml + w_rules * rs
        items.append({
            "function": r["function"], "line": r["line"],
            "ml_risk": None if ml is None else round(ml, 2),
            "rule_score": round(rs, 2), "priority": round(priority, 2),
            "level": level(priority),
            "findings": [{"line": f.line, "severity": f.severity,
                          "rule": f.rule, "message": f.message} for f in mine],
        })
    items.sort(key=lambda x: -x["priority"])
    module_level = [{"line": f.line, "severity": f.severity, "rule": f.rule,
                     "message": f.message} for f in findings if not f.function]
    return {"file": file_name, "functions": items, "module_findings": module_level}

def to_text(rep):
    out = [f"CODE REVIEW: {rep['file']}", "=" * 50]
    for it in rep["functions"]:
        ml = "n/a" if it["ml_risk"] is None else f"{it['ml_risk']:.2f}"
        out.append(f"\n[{it['level']}] {it['function']}()  (line {it['line']})"
                   f"  priority={it['priority']}  ML-risk={ml}  rules={it['rule_score']}")
        for f in it["findings"]:
            out.append(f"   - line {f['line']} [{f['severity'].upper()}] {f['rule']}: {f['message']}")
        if not it["findings"]:
            out.append("   - no rule violations")
    for f in rep["module_findings"]:
        out.append(f"\n[module] line {f['line']} [{f['severity'].upper()}] {f['rule']}: {f['message']}")
    return "\n".join(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--model", default="model.joblib")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = review(open(a.file, encoding="utf-8").read(), a.file, load_model(a.model))
    print(json.dumps(rep, indent=2) if a.json else to_text(rep))
    if load_model(a.model) is None:
        print("\n(note: no trained model found, showing static rules only)")