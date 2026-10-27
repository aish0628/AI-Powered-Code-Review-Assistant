import React from "react";

const ITEMS = ["Review", "History", "Dashboard", "Settings"];

export default function Sidebar({ page, setPage, username, onLogout }) {
  return (
    <div className="sidebar">
      <div className="brand">🔍 Code Review AI</div>
      <div className="who">Logged in as <b>{username}</b></div>
      {ITEMS.map(item => (
        <div key={item}
             className={"nav-item" + (page === item ? " active" : "")}
             onClick={() => setPage(item)}>
          {item}
        </div>
      ))}
      <button className="logout" onClick={onLogout}>Log out</button>
    </div>
  );
}