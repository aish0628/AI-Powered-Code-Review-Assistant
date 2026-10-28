import React, { useState, useEffect } from "react";
import Login from "./pages/Login.jsx";
import Review from "./pages/Review.jsx";
import History from "./pages/History.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Settings from "./pages/Settings.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Topbar from "./components/Topbar.jsx";
import { api } from "./api.js";

const TITLES = { Dashboard: "Dashboard", Review: "New Code Review", History: "Review History", Settings: "Settings" };

export default function App() {
  const [username, setUsername] = useState(localStorage.getItem("username") || null);
  const [displayName, setDisplayName] = useState("");
  const [page, setPage] = useState("Dashboard");

  useEffect(() => {
    if (username) api.getSettings().then(s => setDisplayName(s.display_name)).catch(() => {});
  }, [username]);

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setUsername(null);
  }

  if (!username) {
    return <Login onLoggedIn={(u) => setUsername(u)} />;
  }

  const initials = (displayName || username).slice(0, 2).toUpperCase();

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} username={username} displayName={displayName} onLogout={handleLogout} />
      <div className="content-col">
        <Topbar title={TITLES[page]} initials={initials} />
        {page === "Dashboard" && <Dashboard setPage={setPage} />}
        {page === "Review" && <Review />}
        {page === "History" && <History />}
        {page === "Settings" && <Settings onProfileChange={setDisplayName} />}
      </div>
    </div>
  );
}
