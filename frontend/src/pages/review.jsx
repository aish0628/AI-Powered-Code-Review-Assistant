import React, { useState } from "react";
import { api } from "../api.js";

const SAMPLE = `def get_user(db, name):
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    password = "admin123"
    result = db.execute(query)
    for i in range(len(result)):
        for j in range(len(result)):
            if result[i] == result[j] and i != j:
                print("dup")
    try:
        return result[0]
    except:
        pass
`;

const TABS = ["All", "High", "Medium", "Low"];
const BADGE = { high: "badge high", medium: "badge medium", low: "badge low" };

export default function Review() {
  const [code, setCode] = useState(SAMPLE);
  const [report, setReport] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState("All");

  async function run() {
    setErr(""); setLoading(true); setReport(null);
    try { setReport(await api.review(code, "input.py")); }
    catch (e) { setErr(e.message); }
    finally { setLoading(false); }
  }

  const allFindings = report
    ? report.functions.flatMap(f => f.findings.map(fi => ({ ...fi, fn: f.function })))
    : [];
  const shown = tab === "All" ? allFindings : allFindings.filter(f => f.severity === tab.toLowerCase());
  const nHigh = allFindings.filter(f => f.severity === "high").length;
  const nMed = allFindings.filter(f => f.severity === "medium").length;
  const nLow = allFindings.filter(f => f.severity === "low").length;
  const score = report ? Math.max(0, 100 - nHigh * 15 - nMed * 7 - nLow * 2) : null;

  return (
    <div className="main">
      <div className="eyebrow">NEW CODE REVIEW</div>
      <h2 className="page-title">Analyze your code</h2>
      <p className="page-sub">Paste a Python function or file to get an AI-assisted review.</p>

      <div className="card">
        <textarea rows={12} value={code} onChange={e => setCode(e.target.value)} />
        <div style={{ display: "flex", gap: 10 }}>
          <button className="primary" style={{ width: 180 }} onClick={run} disabled={loading}>
            {loading ? "Reviewing..." : "Review code"}
          </button>
          <button className="primary" style={{ width: 160, background: "var(--border)", color: "var(--text)" }}
                  onClick={() => setCode(SAMPLE)}>Load sample</button>
        </div>
        {err && <div className="error-msg" style={{ marginTop: 10 }}>{err}</div>}
      </div>

      {report && (
        <>
          <div className="eyebrow" style={{ marginTop: 6 }}>REVIEW COMPLETE</div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: 18 }}>
            <h2 className="page-title" style={{ margin: 0 }}>Code Review Results</h2>
            <div className="score-wrap">
              <div className="score-ring"><div className="score-num">{score}</div></div>
              <div style={{ fontFamily: "system-ui, sans-serif", fontSize: 12, color: "var(--muted)" }}>
                Overall Score<br /><b style={{ color: "var(--text)" }}>{score}/100</b>
              </div>
            </div>
          </div>

          <div className="stat-row">
            <div className="stat-card high"><div className="stitle">Critical Issues</div><div className="snum">{nHigh}</div></div>
            <div className="stat-card medium"><div className="stitle">Warnings</div><div className="snum">{nMed}</div></div>
            <div className="stat-card"><div className="stitle">Suggestions</div><div className="snum">{nLow}</div></div>
            <div className="stat-card"><div className="stitle">Functions Analyzed</div><div className="snum">{report.functions.length}</div></div>
          </div>

          <div className="review-split">
            <div className="code-pane">{code}</div>
            <div className="issues-pane">
              <div className="issue-tabs">
                {TABS.map(t => (
                  <span key={t} className={tab === t ? "active" : ""} onClick={() => setTab(t)}>{t}</span>
                ))}
              </div>
              <div className="issues-list">
                {shown.length === 0 && <p style={{ fontFamily: "system-ui, sans-serif", color: "var(--muted)", fontSize: 13 }}>No findings in this category.</p>}
                {shown.map((f, i) => (
                  <div key={i} className="issue-card">
                    <div className="ihead">
                      <div>
                        <div className="ititle">{f.rule.replace(/-/g, " ")}</div>
                        <div className="imeta">{f.fn}() · Line {f.line}</div>
                      </div>
                      <span className={BADGE[f.severity]}>{f.severity}</span>
                    </div>
                    <div className="ibody">{f.message}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
