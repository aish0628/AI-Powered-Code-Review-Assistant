"""User accounts: register / login, stored locally in users.json (hashed passwords).
Also issues/verifies JWT tokens so the React frontend can stay logged in."""
import json, os, hashlib, hmac, secrets, datetime
import jwt

USERS_FILE = "users.json"
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me")
JWT_ALGO = "HS256"
JWT_EXPIRY_HOURS = 24

def make_token(username):
    payload = {"sub": username,
              "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def verify_token(token):
    """Returns username, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload["sub"]
    except jwt.PyJWTError:
        return None

def _load():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def _save(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()

def register(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    users = _load()
    if username in users:
        return False, "Username already exists."
    salt = secrets.token_hex(16)
    users[username] = {"salt": salt, "hash": _hash(password, salt)}
    _save(users)
    return True, "Account created. You can log in now."

def login(username, password):
    users = _load()
    u = users.get(username.strip())
    if not u:
        return False, "No such user."
    if hmac.compare_digest(_hash(password, u["salt"]), u["hash"]):
        return True, "Logged in."
    return False, "Wrong password."

def change_password(username, old_password, new_password):
    ok, msg = login(username, old_password)
    if not ok:
        return False, "Current password is incorrect."
    if len(new_password) < 4:
        return False, "New password must be at least 4 characters."
    users = _load()
    salt = secrets.token_hex(16)
    users[username]["salt"] = salt
    users[username]["hash"] = _hash(new_password, salt)
    _save(users)
    return True, "Password updated."