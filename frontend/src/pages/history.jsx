import React, { useEffect, useState } from "react";
import { api } from "../api.js";

const SEV_BADGE = { high: "badge high", medium: "badge medium", low: "badge low" };

export default function History() {
  const [rows, setRows] = useState([]);
  const [open, setOpen] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => { load(); }, []);

  async function load() {
    try { setRows(await api.history()); }
    catch (e) { setErr(e.message); }
  }

  async function openOne(id) {
    try { setOpen(await api.historyOne(id)); }
    catch (e) { setErr(e.message); }
  }

  return (
    <div className="main">
      <h2>History</h2>
      {err && <div className="error-msg">{err}</div>}
      <div className="card">
        {rows.length === 0 ? (
          <p>No reviews yet. Run one from the Review page.</p>
        ) : (
          <table>
            <thead><tr><th>#</th><th>Date</th><th>File</th><th>Functions</th><th>High</th><th></th></tr></thead>
            <tbody>
              {rows.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td><td>{r.created_at}</td><td>{r.file_name}</td>
                  <td>{r.n_functions}</td><td>{r.n_high}</td>
                  <td><button className="primary" style={{ width: "auto", padding: "4px 10px" }}
                              onClick={() => openOne(r.id)}>Open</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {open && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Review #{open.file} detail</h3>
          {open.functions.map((it, i) => (
            <div key={i} className={"func-card " + it.level}>
              <div className="title">{it.function}() — priority {it.priority}</div>
              {it.findings.map((f, j) => (
                <div key={j} className="finding">
                  <span className={SEV_BADGE[f.severity]}>{f.severity}</span>
                  line {f.line} — <b>{f.rule}</b>: {f.message}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}