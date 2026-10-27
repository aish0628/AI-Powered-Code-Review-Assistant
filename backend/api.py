"""Flask REST API for the AI Code Review Assistant (used by the React frontend)."""
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS

from auth import register, login, change_password, make_token, verify_token
from reviewer import review, load_model
from history_db import save_review, list_reviews, get_review
from settings_store import get_settings, save_settings

app = Flask(__name__)
CORS(app)  # allow the React dev server (different port) to call this API
MODEL = load_model("model.joblib")

def auth_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        header = request.headers.get("Authorization", "")
        token = header.split(" ", 1)[1] if header.startswith("Bearer ") else None
        username = verify_token(token) if token else None
        if not username:
            return jsonify({"error": "Not authenticated"}), 401
        request.username = username
        return fn(*a, **kw)
    return wrapper

# ---------- Auth ----------
@app.post("/api/register")
def api_register():
    d = request.get_json(force=True)
    ok, msg = register(d.get("username", ""), d.get("password", ""))
    return jsonify({"ok": ok, "message": msg}), (200 if ok else 400)

@app.post("/api/login")
def api_login():
    d = request.get_json(force=True)
    ok, msg = login(d.get("username", ""), d.get("password", ""))
    if not ok:
        return jsonify({"ok": False, "message": msg}), 401
    token = make_token(d["username"].strip())
    return jsonify({"ok": True, "token": token, "username": d["username"].strip()})

@app.post("/api/change-password")
@auth_required
def api_change_password():
    d = request.get_json(force=True)
    ok, msg = change_password(request.username, d.get("old_password", ""), d.get("new_password", ""))
    return jsonify({"ok": ok, "message": msg}), (200 if ok else 400)

# ---------- Review ----------
@app.post("/api/review")
@auth_required
def api_review():
    d = request.get_json(force=True)
    code = d.get("code", "")
    settings = get_settings(request.username)
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    try:
        report = review(code, d.get("file_name", "input.py"), MODEL, ml_weight=settings["ml_weight"])
    except SyntaxError as e:
        return jsonify({"error": f"Syntax error: {e}"}), 400
    save_review(request.username, report, d.get("file_name", "input.py"))
    return jsonify(report)

# ---------- History ----------
@app.get("/api/history")
@auth_required
def api_history():
    return jsonify(list_reviews(request.username))

@app.get("/api/history/<int:review_id>")
@auth_required
def api_history_one(review_id):
    rep = get_review(review_id, request.username)
    if rep is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(rep)

# ---------- Settings ----------
@app.get("/api/settings")
@auth_required
def api_get_settings():
    return jsonify(get_settings(request.username))

@app.post("/api/settings")
@auth_required
def api_save_settings():
    d = request.get_json(force=True)
    allowed = {k: d[k] for k in ("display_name", "theme", "ml_weight") if k in d}
    return jsonify(save_settings(request.username, **allowed))

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "model_loaded": MODEL is not None})

if __name__ == "__main__":
    app.run(debug=True, port=5000)