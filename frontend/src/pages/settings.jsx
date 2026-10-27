import React, { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [name, setName] = useState("");
  const [weight, setWeight] = useState(0.5);
  const [msg, setMsg] = useState("");

  const [oldPw, setOldPw] = useState(""); const [newPw, setNewPw] = useState("");
  const [pwMsg, setPwMsg] = useState("");

  useEffect(() => {
    api.getSettings().then(s => {
      setSettings(s); setName(s.display_name); setWeight(s.ml_weight);
    });
  }, []);

  async function saveProfile() {
    const s = await api.saveSettings({ display_name: name });
    setSettings(s); setMsg("Profile updated.");
  }

  async function saveWeight(w) {
    setWeight(w);
    const s = await api.saveSettings({ ml_weight: w });
    setSettings(s);
  }

  async function updatePassword() {
    setPwMsg("");
    try {
      const r = await api.changePassword(oldPw, newPw);
      setPwMsg(r.message);
    } catch (e) { setPwMsg(e.message); }
  }

  if (!settings) return <div className="main"><h2>Settings</h2><p>Loading...</p></div>;

  return (
    <div className="main">
      <h2>Settings</h2>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Profile</h3>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="Display name" />
        <button className="primary" style={{ width: 160 }} onClick={saveProfile}>Save profile</button>
        {msg && <div className="success-msg" style={{ marginTop: 10 }}>{msg}</div>}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Review preference</h3>
        <p style={{ color: "var(--muted)", fontSize: 13 }}>
          How much the review priority trusts the ML model vs. static rules.
        </p>
        <div className="slider-row">
          <span>Rules</span>
          <input type="range" min="0" max="1" step="0.05" value={weight}
                 onChange={e => saveWeight(parseFloat(e.target.value))} />
          <span>ML</span>
        </div>
        <div style={{ color: "var(--muted)", fontSize: 12 }}>Current: {weight}</div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Change password</h3>
        <input type="password" placeholder="Current password" value={oldPw} onChange={e => setOldPw(e.target.value)} />
        <input type="password" placeholder="New password" value={newPw} onChange={e => setNewPw(e.target.value)} />
        <button className="primary" style={{ width: 180 }} onClick={updatePassword}>Update password</button>
        {pwMsg && <div className="error-msg" style={{ marginTop: 10 }}>{pwMsg}</div>}
      </div>
    </div>
  );
}
