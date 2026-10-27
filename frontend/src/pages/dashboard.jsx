import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Dashboard() {
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.history().then(setRows).catch(e => setErr(e.message));
  }, []);

  const totalHigh = rows.reduce((a, r) => a + r.n_high, 0);
  const totalFunctions = rows.reduce((a, r) => a + r.n_functions, 0);
  const maxFn = Math.max(1, ...rows.map(r => r.n_functions));

  return (
    <div className="main">
      <h2>Dashboard</h2>
      {err && <div className="error-msg">{err}</div>}
      <div className="metrics-row">
        <div className="metric"><div className="num">{rows.length}</div><div className="label">Total reviews</div></div>
        <div className="metric"><div className="num">{totalFunctions}</div><div className="label">Functions analyzed</div></div>
        <div className="metric"><div className="num">{totalHigh}</div><div className="label">High-priority found</div></div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Functions analyzed per review</h3>
        {rows.length === 0 ? <p>No data yet.</p> : (
          <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 140 }}>
            {rows.slice().reverse().map(r => (
              <div key={r.id} title={`#${r.id}: ${r.n_functions} functions, ${r.n_high} high`}
                   style={{
                     width: 26,
                     height: `${(r.n_functions / maxFn) * 100}%`,
                     background: r.n_high > 0 ? "var(--high)" : "var(--accent)",
                     borderRadius: 4,
                   }} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
