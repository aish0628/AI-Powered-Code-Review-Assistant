import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Dashboard({ setPage }) {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.history().then(setRows).catch(e => setErr(e.message));
  }, []);

  const totalHigh = rows.reduce((a, r) => a + r.n_high, 0);
  const totalFunctions = rows.reduce((a, r) => a + r.n_functions, 0);
  const avgScore = rows.length
    ? Math.round(rows.reduce((a, r) => a + Math.max(0, 100 - r.n_high * 15), 0) / rows.length)
    : 0;

  return (
    <div className="main">
      <div className="eyebrow">AI CODE INTELLIGENCE</div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2 className="page-title">Analyze. Improve. Ship better code.</h2>
          <p className="page-sub">Review your code, catch issues early, and track quality over time.</p>
        </div>
        <button className="primary" style={{ width: 170 }} onClick={() => setPage("Review")}>+ New Code Review</button>
      </div>
      {err && <div className="error-msg">{err}</div>}

      <div className="stat-row">
        <div className="stat-card"><div className="stitle">Total Reviews</div><div className="snum">{rows.length}</div></div>
        <div className="stat-card high"><div className="stitle">High-Priority Found</div><div className="snum">{totalHigh}</div></div>
        <div className="stat-card"><div className="stitle">Functions Analyzed</div><div className="snum">{totalFunctions}</div></div>
        <div className="stat-card"><div className="stitle">Avg. Quality Score</div><div className="snum">{avgScore}/100</div></div>
      </div>

      <div className="card">
        <h3>Recent Reviews</h3>
        {rows.length === 0 ? (
          <p style={{ fontFamily: "system-ui, sans-serif", color: "var(--muted)" }}>No reviews yet — run one from New Code Review.</p>
        ) : (
          <table>
            <thead><tr><th>File</th><th>Date</th><th>Functions</th><th>High</th><th>Status</th></tr></thead>
            <tbody>
              {rows.slice(0, 8).map(r => (
                <tr key={r.id}>
                  <td>{r.file_name}</td>
                  <td>{r.created_at}</td>
                  <td>{r.n_functions}</td>
                  <td>{r.n_high}</td>
                  <td><span className="status-dot" />Completed</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
