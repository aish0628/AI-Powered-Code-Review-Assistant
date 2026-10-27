"""Step 6: Streamlit website — login/register + Review, History, Dashboard pages."""
import streamlit as st
import pandas as pd
from reviewer import review, load_model
from auth import register, login, change_password
from history_db import save_review, list_reviews, get_review
from settings_store import get_settings, save_settings

st.set_page_config(page_title="AI Code Review Assistant", page_icon="🔍", layout="wide")

SAMPLE = '''def get_user(db, name):
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    password = "admin123"
    result = db.execute(query)
    for i in range(len(result)):
        for j in range(len(result)):
            if result[i] == result[j] and i != j:
                print("dup")
    try:
        return result[0]
    except:
        pass
'''
LEVEL_ICON = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟢"}
SEV_ICON = {"high": "🔴", "medium": "🟠", "low": "🟡"}

if "user" not in st.session_state:
    st.session_state.user = None

@st.cache_resource
def get_model():
    return load_model("model.joblib")

# ---------- LOGIN / REGISTER ----------
def auth_screen():
    st.title("🔍 AI Code Review Assistant")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="li_u")
        p = st.text_input("Password", type="password", key="li_p")
        if st.button("Log in", type="primary"):
            ok, msg = login(u, p)
            if ok:
                st.session_state.user = u.strip()
                st.rerun()
            else:
                st.error(msg)
    with tab2:
        u = st.text_input("Choose a username", key="re_u")
        p = st.text_input("Choose a password", type="password", key="re_p")
        if st.button("Create account"):
            ok, msg = register(u, p)
            (st.success if ok else st.error)(msg)

# ---------- REVIEW PAGE ----------
def page_review(model, settings):
    st.header("Review code")
    col1, col2 = st.columns([3, 1])
    with col1:
        code = st.text_area("Paste Python code", value=SAMPLE, height=300)
    with col2:
        st.write(""); st.write("")
        run = st.button("Review code", type="primary", use_container_width=True)

    if run:
        if not code.strip():
            st.error("Paste some code first.")
            return
        try:
            report = review(code, "input.py", model, ml_weight=settings["ml_weight"])
        except SyntaxError as e:
            st.error(f"Syntax error in code: {e}")
            return
        save_review(st.session_state.user, report, "input.py")

        n = len(report["functions"])
        n_high = sum(f["level"] == "HIGH" for f in report["functions"])
        m1, m2, m3 = st.columns(3)
        m1.metric("Functions analyzed", n)
        m2.metric("High priority", n_high)
        m3.metric("Total findings", sum(len(f["findings"]) for f in report["functions"]))
        st.divider()
        for it in report["functions"]:
            icon = LEVEL_ICON[it["level"]]
            ml = "n/a" if it["ml_risk"] is None else f"{it['ml_risk']:.2f}"
            with st.expander(f"{icon} **{it['function']}()** — priority {it['priority']} "
                             f"(line {it['line']}, ML risk {ml}, rule score {it['rule_score']})",
                             expanded=(it["level"] == "HIGH")):
                if it["findings"]:
                    for f in it["findings"]:
                        st.markdown(f"{SEV_ICON[f['severity']]} **{f['rule']}** (line {f['line']}) — {f['message']}")
                else:
                    st.write("No rule violations in this function.")
        st.success("Saved to your history.")

# ---------- HISTORY PAGE ----------
def page_history():
    st.header("History")
    rows = list_reviews(st.session_state.user)
    if not rows:
        st.info("No reviews yet. Run one from the Review page.")
        return
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    ids = [r["id"] for r in rows]
    pick = st.selectbox("Open a past review", ids, format_func=lambda i: f"#{i}")
    if st.button("Open"):
        rep = get_review(pick, st.session_state.user)
        for it in rep["functions"]:
            icon = LEVEL_ICON[it["level"]]
            st.markdown(f"{icon} **{it['function']}()** — priority {it['priority']}")
            for f in it["findings"]:
                st.markdown(f"&nbsp;&nbsp;{SEV_ICON[f['severity']]} {f['rule']} (line {f['line']}): {f['message']}")

# ---------- DASHBOARD PAGE ----------
def page_dashboard():
    st.header("Dashboard")
    rows = list_reviews(st.session_state.user)
    if not rows:
        st.info("No data yet.")
        return
    df = pd.DataFrame(rows)
    c1, c2 = st.columns(2)
    c1.metric("Total reviews", len(df))
    c2.metric("Total HIGH-priority functions found", int(df["n_high"].sum()))
    st.bar_chart(df.set_index("created_at")[["n_functions", "n_high"]])

# ---------- SETTINGS PAGE ----------
def page_settings(settings):
    st.header("Settings")

    st.subheader("Profile")
    name = st.text_input("Display name", value=settings["display_name"])
    if st.button("Save profile"):
        save_settings(st.session_state.user, display_name=name)
        st.success("Profile updated.")
        st.rerun()

    st.divider()
    st.subheader("Appearance")
    theme = st.radio("Theme", ["Dark", "Light"], index=["Dark", "Light"].index(settings["theme"]), horizontal=True)
    if theme != settings["theme"]:
        save_settings(st.session_state.user, theme=theme)
        st.rerun()

    st.divider()
    st.subheader("Review preference")
    st.caption("How much the review priority trusts the ML model vs. the static rules.")
    w = st.slider("ML weight", 0.0, 1.0, float(settings["ml_weight"]), 0.05,
                  help="0 = rules only, 1 = ML only, 0.5 = equal balance")
    if st.button("Save review preference"):
        save_settings(st.session_state.user, ml_weight=w)
        st.success("Saved.")

    st.divider()
    st.subheader("Change password")
    old = st.text_input("Current password", type="password", key="cp_old")
    new = st.text_input("New password", type="password", key="cp_new")
    if st.button("Update password"):
        ok, msg = change_password(st.session_state.user, old, new)
        (st.success if ok else st.error)(msg)

# ---------- MAIN ----------
model = get_model()
if st.session_state.user is None:
    auth_screen()
else:
    settings = get_settings(st.session_state.user)
    if settings["theme"] == "Light":
        st.markdown("<style>body,.stApp{background:#fff;color:#111}</style>", unsafe_allow_html=True)

    who = settings["display_name"] or st.session_state.user
    st.sidebar.write(f"Logged in as **{who}**")
    if model is None:
        st.sidebar.warning("model.joblib not found — static rules only.")
    page = st.sidebar.radio("Go to", ["Review", "History", "Dashboard", "Settings"])
    if st.sidebar.button("Log out"):
        st.session_state.user = None
        st.rerun()

    if page == "Review":
        page_review(model, settings)
    elif page == "History":
        page_history()
    elif page == "Dashboard":
        page_dashboard()
    else:
        page_settings(settings)