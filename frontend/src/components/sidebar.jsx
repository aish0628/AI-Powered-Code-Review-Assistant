import React from "react";

const ITEMS = [
  { key: "Dashboard", icon: "▦" },
  { key: "Review", icon: "✎", label: "New Code Review" },
  { key: "History", icon: "↺", label: "Review History" },
  { key: "Settings", icon: "⚙" },
];

export default function Sidebar({ page, setPage, username, displayName, onLogout }) {
  const initials = (displayName || username || "?").slice(0, 2).toUpperCase();
  return (
    <div className="sidebar">
      <div className="brand">
        <div className="mark">CR</div>
        <div className="name">CodeReview <span className="ai">AI</span></div>
      </div>
      {ITEMS.map(it => (
        <div key={it.key}
             className={"nav-item" + (page === it.key ? " active" : "")}
             onClick={() => setPage(it.key)}>
          <span className="ic">{it.icon}</span>
          <span>{it.label || it.key}</span>
        </div>
      ))}
      <div className="sidebar-foot">
        <div className="profile-row">
          <div className="avatar">{initials}</div>
          <div>
            <div className="pname">{displayName || username}</div>
            <div className="prole">Student Developer</div>
          </div>
        </div>
        <button className="logout" onClick={onLogout}>Logout</button>
      </div>
    </div>
  );
}
