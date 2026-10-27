import React, { useState } from "react";
import Login from "./pages/Login.jsx";
import Review from "./pages/Review.jsx";
import History from "./pages/History.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Settings from "./pages/Settings.jsx";
import Sidebar from "./components/Sidebar.jsx";

export default function App() {
  const [username, setUsername] = useState(localStorage.getItem("username") || null);
  const [page, setPage] = useState("Review");

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setUsername(null);
  }

  if (!username) {
    return <Login onLoggedIn={(u) => setUsername(u)} />;
  }

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} username={username} onLogout={handleLogout} />
      {page === "Review" && <Review />}
      {page === "History" && <History />}
      {page === "Dashboard" && <Dashboard />}
      {page === "Settings" && <Settings />}
    </div>
  );
}