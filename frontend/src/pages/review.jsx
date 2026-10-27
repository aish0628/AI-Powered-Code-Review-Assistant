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

const SEV_BADGE = { high: "badge high", medium: "badge medium", low: "badge low" };

export default function Review() {
  const [code, setCode] = useState(SAMPLE);
  const [report, setReport] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function run() {
    setErr(""); setLoading(true); setReport(null);
    try {
      const data = await api.review(code, "input.py");
      setReport(data);
    } catch (e) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  }

  const nHigh = report ? report.functions.filter(f => f.level === "HIGH").length : 0;
  const nFindings = report ? report.functions.reduce((a, f) => a + f.findings.length, 0) : 0;

  return (
    <div className="main">
      <h2>Review code</h2>
      <div className="card">
        <textarea rows={14} value={code} onChange={e => setCode(e.target.value)} />
        <div style={{ display: "flex", gap: 10 }}>
          <button className="primary" style={{ width: 180 }} onClick={run} disabled={loading}>
            {loading ? "Reviewing..." : "Review code"}
          </button>
          <button className="primary" style={{ width: 160, background: "#2a2f3a" }}
                  onClick={() => setCode(SAMPLE)}>Load sample</button>
        </div>
        {err && <div className="error-msg" style={{ marginTop: 10 }}>{err}</div>}
      </div>

      {report && (
        <>
          <div className="metrics-row">
            <div className="metric"><div className="num">{report.functions.length}</div><div className="label">Functions analyzed</div></div>
            <div className="metric"><div className="num">{nHigh}</div><div className="label">High priority</div></div>
            <div className="metric"><div className="num">{nFindings}</div><div className="label">Total findings</div></div>
          </div>

          {report.functions.map((it, i) => (
            <div key={i} className={"func-card " + it.level}>
              <div className="title">{it.function}()  —  priority {it.priority}</div>
              <div className="meta">
                line {it.line} · ML risk {it.ml_risk ?? "n/a"} · rule score {it.rule_score} · {it.level}
              </div>
              {it.findings.length === 0 && <div className="finding">No rule violations.</div>}
              {it.findings.map((f, j) => (
                <div key={j} className="finding">
                  <span className={SEV_BADGE[f.severity]}>{f.severity}</span>
                  line {f.line} — <b>{f.rule}</b>: {f.message}
                </div>
              ))}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
