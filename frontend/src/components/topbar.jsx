import React from "react";

export default function Topbar({ title, initials }) {
  return (
    <div className="topbar">
      <h1>{title}</h1>
      <div className="right">
        <input className="search" placeholder="Search reviews, files..." readOnly />
        <span style={{ cursor: "pointer", color: "var(--muted)" }}>🔔</span>
        <span style={{ cursor: "pointer", color: "var(--muted)" }}>☀</span>
        <div className="avatar">{initials}</div>
      </div>
    </div>
  );
}
