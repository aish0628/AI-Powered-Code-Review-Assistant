"""Per-user settings: display name, theme, and review weighting. Stored in settings.json."""
import json, os

FILE = "settings.json"
DEFAULTS = {"display_name": "", "theme": "Dark", "ml_weight": 0.5}

def _load():
    if os.path.exists(FILE):
        with open(FILE) as f:
            return json.load(f)
    return {}

def _save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_settings(username):
    data = _load()
    s = dict(DEFAULTS)
    s.update(data.get(username, {}))
    return s

def save_settings(username, **kwargs):
    data = _load()
    s = dict(DEFAULTS)
    s.update(data.get(username, {}))
    s.update(kwargs)
    data[username] = s
    _save(data)
    return s