import streamlit as st
from pathlib import Path
import pandas as pd
import hashlib
import json
import re

# ================================================================
# IPL INTELLIGENCE & IPL 2027 PREDICTION DASHBOARD
# Robust version: project-relative paths + safe session state
# ================================================================

st.set_page_config(
    page_title="IPL Intelligence | 2027 Prediction",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# PROJECT PATHS
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

# If this app.py is inside a dashboard/ folder, the project root is one level up.
if (BASE_DIR / "data").exists() or (BASE_DIR / "outputs").exists():
    PROJECT_DIR = BASE_DIR
elif (BASE_DIR.parent / "data").exists() or (BASE_DIR.parent / "outputs").exists():
    PROJECT_DIR = BASE_DIR.parent
else:
    PROJECT_DIR = BASE_DIR

SEARCH_DIRS = [
    PROJECT_DIR / "data" / "processed",
    PROJECT_DIR / "outputs" / "predictions",
    PROJECT_DIR / "outputs" / "reports",
    PROJECT_DIR / "outputs" / "charts",
    PROJECT_DIR / "data",
    PROJECT_DIR,
]
CHART_DIR = PROJECT_DIR / "outputs" / "charts"
USERS_FILE = PROJECT_DIR / "users.json"

CURRENT_TEAMS = [
    "Chennai Super Kings",
    "Delhi Capitals",
    "Gujarat Titans",
    "Kolkata Knight Riders",
    "Lucknow Super Giants",
    "Mumbai Indians",
    "Punjab Kings",
    "Rajasthan Royals",
    "Royal Challengers Bengaluru",
    "Sunrisers Hyderabad",
]

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
    <style>
    .hero {
        padding: 24px 28px;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,.25);
        margin-bottom: 20px;
    }
    .hero h1 { margin: 0; font-size: 38px; }
    .hero p { margin: 7px 0 0 0; opacity: .8; font-size: 16px; }
    .section { font-size: 25px; font-weight: 750; margin-top: 12px; }
    .muted { opacity: .72; font-size: 13px; }
    .login-box { max-width: 560px; margin: 40px auto; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# SAFE SESSION STATE
# -----------------------------
DEFAULT_STATE = {
    "logged_in": False,
    "username": "",
    "role": "user",
}
for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -----------------------------
# FILE HELPERS
# -----------------------------
def norm(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


@st.cache_data(show_spinner=False)
def discover_csv_files():
    files = []
    seen = set()
    for folder in SEARCH_DIRS:
        try:
            if not folder.exists():
                continue
            for f in folder.rglob("*.csv"):
                key = str(f.resolve()).lower()
                if key not in seen:
                    seen.add(key)
                    files.append(f)
        except Exception:
            pass
    return files


def find_csv(*names):
    files = discover_csv_files()
    # exact
    for name in names:
        target = str(name).lower()
        for f in files:
            if f.name.lower() == target:
                return f
    # normalized
    targets = {norm(x) for x in names}
    for f in files:
        if norm(f.name) in targets:
            return f
    # partial, only when reasonably specific
    for name in names:
        target = norm(Path(name).stem)
        if len(target) < 5:
            continue
        for f in files:
            current = norm(f.stem)
            if target in current or current in target:
                return f
    return None


@st.cache_data(show_spinner=False)
def read_csv(path):
    try:
        df = pd.read_csv(path)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(axis=0, how="all").dropna(axis=1, how="all")
    except Exception:
        return pd.DataFrame()


def load_csv(*names):
    path = find_csv(*names)
    if path is None:
        return pd.DataFrame(), None
    return read_csv(str(path)), path


def show_df(df, height=430):
    if df is None or df.empty:
        st.info("No data available for this section.")
        return
    st.dataframe(df, use_container_width=True, height=height)


def numeric_column(df, keywords):
    for col in df.columns:
        c = str(col).lower().replace(" ", "_")
        if any(k in c for k in keywords):
            return col
    return None

# -----------------------------
# AUTHENTICATION
# -----------------------------
ADMIN_USER = "admin"
ADMIN_PASS = "IPL@2027Admin"


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users():
    admin = {ADMIN_USER: {"password": hash_password(ADMIN_PASS), "role": "admin"}}
    try:
        if USERS_FILE.exists():
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
            if not isinstance(users, dict):
                users = {}
            users.setdefault(ADMIN_USER, admin[ADMIN_USER])
            return users
    except Exception:
        pass
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(admin, f, indent=2)
    except Exception:
        pass
    return admin


def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False


def login_screen():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero"><h1>🏏 IPL Intelligence</h1>'
        '<p>IPL Analytics & IPL 2027 Prediction System</p></div>',
        unsafe_allow_html=True,
    )
    login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

    with login_tab:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
        if submit:
            users = load_users()
            if username in users and users[username].get("password") == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = users[username].get("role", "user")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with register_tab:
        with st.form("register_form", clear_on_submit=True):
            username = st.text_input("Create username")
            password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submit = st.form_submit_button("Create Account", use_container_width=True)
        if submit:
            username = username.strip()
            if len(username) < 3:
                st.error("Username must contain at least 3 characters.")
            elif len(password) < 6:
                st.error("Password must contain at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                users = load_users()
                if username in users:
                    st.error("Username already exists.")
                else:
                    users[username] = {"password": hash_password(password), "role": "user"}
                    if save_users(users):
                        st.success("Account created. Please use the Login tab.")
                    else:
                        st.error("Could not save the account.")
    st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.logged_in:
    login_screen()
    st.stop()

# -----------------------------
# LOAD DATA
# -----------------------------
season_df, season_path = load_csv("season_match_summary.csv", "team_season_analysis.csv")
team_overall_df, team_overall_path = load_csv("team_overall_analysis.csv")
team_recent_df, team_recent_path = load_csv("team_recent_form_2024_2026.csv", "team_recent_form.csv")
current_2026_df, current_2026_path = load_csv("current_team_analysis_2026.csv")
team_strength_df, team_strength_path = load_csv("team_strength_features_2027.csv", "current_team_features_2026.csv")
batting_df, batting_path = load_csv("player_batting_analysis.csv")
bowling_df, bowling_path = load_csv("player_bowling_analysis.csv")
player_recent_df, player_recent_path = load_csv("player_recent_form.csv")
player_2026_df, player_2026_path = load_csv("player_2026_form.csv")
pom_df, pom_path = load_csv("player_of_match_counts.csv")
champions_df, champions_path = load_csv("ipl_champions_2008_2026.csv")
runners_df, runners_path = load_csv("ipl_runners_up_2008_2026.csv")
prediction_df, prediction_path = load_csv("ipl_2027_final_prediction.csv", "ipl_2027_prediction_summary.csv")
matchup_df, matchup_path = load_csv("ipl_2027_matchup_predictions.csv", "ipl_2027_matchup_report.csv")
matchup_matrix_df, matchup_matrix_path = load_csv("ipl_2027_matchup_matrix.csv")
comparison_df, comparison_path = load_csv("team_comparison_2027.csv", "team_comparison_2027_report.csv", "team_overall_analysis.csv")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🏏 IPL Intelligence")
st.sidebar.caption(f"User: {st.session_state.username}")
st.sidebar.caption(f"Role: {st.session_state.role.upper()}")

menu = st.sidebar.radio(
    "Dashboard",
    [
        "🏠 Overview",
        "📊 Historical Analysis",
        "🏏 Team Analytics",
        "👤 Player Analytics",
        "⚔️ Team Comparison",
        "🔥 Match-up Prediction",
        "🔮 IPL 2027 Prediction",
        "📈 Visualizations",
    ],
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "user"
    st.rerun()

# -----------------------------
# OVERVIEW
# -----------------------------
if menu == "🏠 Overview":
    st.markdown(
        '<div class="hero"><h1>🏏 IPL Intelligence & IPL 2027 Prediction</h1>'
        '<p>Historical IPL analytics from 2008–2026 with team, player, match-up and 2027 prediction modules.</p></div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Seasons Analysed", "19")
    c2.metric("Matches Analysed", "1,243")
    c3.metric("Current Teams", "10")
    c4.metric("Prediction Season", "2027")

    st.markdown('<div class="section">📌 Project Modules</div>', unsafe_allow_html=True)
    module_df = pd.DataFrame({
        "Module": [
            "IPL Historical Analysis",
            "Team Analytics",
            "Player Analytics",
            "Team Comparison",
            "Team Match-up",
            "IPL 2027 Prediction",
            "Visualizations",
            "Login / Registration",
        ],
        "Status": ["Ready"] * 8,
    })
    show_df(module_df, 350)

    st.markdown('<div class="section">📂 Data Status</div>', unsafe_allow_html=True)
    status_rows = []
    checks = {
        "Historical Season Data": season_path,
        "Team Analysis": team_overall_path,
        "Player Batting": batting_path,
        "Player Bowling": bowling_path,
        "2027 Prediction": prediction_path,
        "Match-up": matchup_path,
    }
    for name, path in checks.items():
        status_rows.append({"Module": name, "Status": "✅ Loaded" if path else "⚠️ Not found"})
    show_df(pd.DataFrame(status_rows), 300)

# -----------------------------
# HISTORICAL
# -----------------------------
elif menu == "📊 Historical Analysis":
    st.title("📊 IPL Historical Analysis — 2008 to 2026")
    t1, t2, t3, t4 = st.tabs(["Season Analysis", "🏆 Champions", "🥈 Runners-up", "Team Performance"])

    with t1:
        show_df(season_df)
    with t2:
        show_df(champions_df)
        if not champions_df.empty:
            col = next((c for c in champions_df.columns if "champion" in str(c).lower()), None)
            if col:
                counts = champions_df[col].value_counts().rename_axis("Team").reset_index(name="Titles")
                st.subheader("Championship Count")
                show_df(counts, 300)
    with t3:
        show_df(runners_df)
    with t4:
        show_df(team_overall_df)

# -----------------------------
# TEAM ANALYTICS
# -----------------------------
elif menu == "🏏 Team Analytics":
    st.title("🏏 Team Analytics")
    t1, t2, t3, t4 = st.tabs(["2026 Performance", "Recent Form", "2027 Strength", "Historical"])
    with t1:
        show_df(current_2026_df)
    with t2:
        show_df(team_recent_df)
    with t3:
        show_df(team_strength_df)
    with t4:
        show_df(team_overall_df)

# -----------------------------
# PLAYER ANALYTICS
# -----------------------------
elif menu == "👤 Player Analytics":
    st.title("👤 Player Analytics")
    t1, t2, t3, t4, t5 = st.tabs(["🏏 Batting", "🎯 Bowling", "📈 Recent Form", "⭐ 2026 Form", "🏅 Player of Match"])
    with t1:
        show_df(batting_df, 550)
    with t2:
        show_df(bowling_df, 550)
    with t3:
        show_df(player_recent_df, 500)
    with t4:
        show_df(player_2026_df, 500)
    with t5:
        show_df(pom_df, 450)

# -----------------------------
# TEAM COMPARISON
# -----------------------------
elif menu == "⚔️ Team Comparison":
    st.title("⚔️ Current IPL Team Comparison")
    if comparison_df.empty:
        st.info("Team comparison data is not available.")
    else:
        show_df(comparison_df, 550)

# -----------------------------
# MATCH-UP
# -----------------------------
elif menu == "🔥 Match-up Prediction":
    st.title("🔥 IPL Team Match-up Analysis")
    st.info("This module uses recent head-to-head results and team-strength features. It is an analytical comparison, not a guarantee of a future result.")
    if not matchup_matrix_df.empty:
        st.subheader("10 × 10 Match-up Matrix")
        show_df(matchup_matrix_df, 600)
    st.subheader("Pair-wise Match-up Results")
    show_df(matchup_df, 600)

# -----------------------------
# PREDICTION
# -----------------------------
elif menu == "🔮 IPL 2027 Prediction":
    st.title("🔮 IPL 2027 Prediction")
    st.info("The displayed probability is a relative analytical output among the 10 current IPL teams. It is not a guaranteed real-world probability.")

    if prediction_df.empty:
        st.warning("IPL 2027 prediction data is not available.")
    else:
        show_df(prediction_df, 600)

        team_col = next((c for c in prediction_df.columns if "team" in str(c).lower()), None)
        prob_col = next((c for c in prediction_df.columns if "prob" in str(c).lower()), None)
        score_col = next((c for c in prediction_df.columns if "score" in str(c).lower()), None)

        if team_col and prob_col:
            chart = prediction_df.copy()
            chart[prob_col] = pd.to_numeric(chart[prob_col], errors="coerce")
            chart = chart.dropna(subset=[prob_col]).sort_values(prob_col, ascending=False)
            if not chart.empty:
                st.subheader("📊 2027 Analytical Probability")
                st.bar_chart(chart.set_index(team_col)[prob_col])

        if team_col and score_col:
            chart = prediction_df.copy()
            chart[score_col] = pd.to_numeric(chart[score_col], errors="coerce")
            chart = chart.dropna(subset=[score_col]).sort_values(score_col, ascending=False)
            if not chart.empty:
                st.subheader("💪 2027 Prediction Score")
                st.bar_chart(chart.set_index(team_col)[score_col])

        st.subheader("📌 Prediction Factors")
        factors = pd.DataFrame({
            "Factor": [
                "Historical performance",
                "Recent form 2024–2026",
                "2026 performance",
                "Team strength",
                "Batting strength",
                "Bowling strength",
                "Consistency",
                "Historical titles",
            ],
            "Included": ["Yes"] * 8,
        })
        show_df(factors, 330)

# -----------------------------
# VISUALIZATIONS
# -----------------------------
elif menu == "📈 Visualizations":
    st.title("📈 IPL Visualizations")
    charts = []
    try:
        if CHART_DIR.exists():
            charts = sorted(CHART_DIR.glob("*.png"))
    except Exception:
        charts = []

    if not charts:
        st.info("No PNG charts were found in outputs/charts.")
    else:
        st.success(f"{len(charts)} charts loaded successfully.")
        for chart in charts:
            st.subheader(chart.stem.replace("_", " ").title())
            st.image(str(chart), use_container_width=True)

# -----------------------------
# ADMIN INFO
# -----------------------------
if st.session_state.role == "admin":
    with st.sidebar.expander("👑 Admin"):
        st.success("Admin access enabled")
        st.caption("Full dashboard access")

st.markdown("---")
st.caption("IPL Intelligence & IPL 2027 Prediction System | IPL 2008–2026 Analytics")