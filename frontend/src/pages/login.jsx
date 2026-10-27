import React, { useState } from "react";
import { api } from "../api.js";

export default function Login({ onLoggedIn }) {
  const [tab, setTab] = useState("login");

  const [lu, setLu] = useState(""); const [lp, setLp] = useState("");
  const [loginErr, setLoginErr] = useState("");

  const [ru, setRu] = useState(""); const [rp, setRp] = useState("");
  const [regMsg, setRegMsg] = useState(""); const [regOk, setRegOk] = useState(false);

  async function doLogin(e) {
    e.preventDefault();
    setLoginErr("");
    try {
      const data = await api.login(lu, lp);
      localStorage.setItem("token", data.token);
      localStorage.setItem("username", data.username);
      onLoggedIn(data.username);
    } catch (err) {
      setLoginErr(err.message);
    }
  }

  async function doRegister(e) {
    e.preventDefault();
    setRegMsg(""); setRegOk(false);
    try {
      const data = await api.register(ru, rp);
      setRegOk(data.ok);
      setRegMsg(data.message);
      if (data.ok) { setTab("login"); setLu(ru); }
    } catch (err) {
      setRegMsg(err.message);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>🔍 AI Code Review Assistant</h1>
        <p className="sub">Static rules + ML, fused into one ranked review.</p>
        <div className="tabs">
          <button className={tab === "login" ? "active" : ""} onClick={() => setTab("login")}>Login</button>
          <button className={tab === "register" ? "active" : ""} onClick={() => setTab("register")}>Register</button>
        </div>

        {tab === "login" ? (
          <form onSubmit={doLogin}>
            <input placeholder="Username" value={lu} onChange={e => setLu(e.target.value)} />
            <input placeholder="Password" type="password" value={lp} onChange={e => setLp(e.target.value)} />
            {loginErr && <div className="error-msg">{loginErr}</div>}
            <button className="primary" type="submit">Log in</button>
          </form>
        ) : (
          <form onSubmit={doRegister}>
            <input placeholder="Choose a username" value={ru} onChange={e => setRu(e.target.value)} />
            <input placeholder="Choose a password" type="password" value={rp} onChange={e => setRp(e.target.value)} />
            {regMsg && <div className={regOk ? "success-msg" : "error-msg"}>{regMsg}</div>}
            <button className="primary" type="submit">Create account</button>
          </form>
        )}
      </div>
    </div>
  );
}