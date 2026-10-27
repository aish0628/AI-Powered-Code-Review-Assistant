// Thin wrapper around the Flask API. Base URL is proxied by Vite ("/api" -> localhost:5000).
const BASE = "/api";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || data.error || "Request failed");
  return data;
}

export const api = {
  register: (username, password) =>
    fetch(`${BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then(handle),

  login: (username, password) =>
    fetch(`${BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    }).then(handle),

  changePassword: (old_password, new_password) =>
    fetch(`${BASE}/change-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ old_password, new_password }),
    }).then(handle),

  review: (code, file_name = "input.py") =>
    fetch(`${BASE}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ code, file_name }),
    }).then(handle),

  history: () => fetch(`${BASE}/history`, { headers: authHeaders() }).then(handle),

  historyOne: (id) => fetch(`${BASE}/history/${id}`, { headers: authHeaders() }).then(handle),

  getSettings: () => fetch(`${BASE}/settings`, { headers: authHeaders() }).then(handle),

  saveSettings: (settings) =>
    fetch(`${BASE}/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(settings),
    }).then(handle),
};
