"""
IPL TEAM COMPARISON
IPL 2008-2026 Historical + Recent + 2026 + 2027 Strength Comparison

Output:
    data/processed/team_comparison_2027.csv
    outputs/reports/team_comparison_2027_report.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CURRENT IPL TEAMS
# ============================================================

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


# ============================================================
# TEAM NAME NORMALIZATION
# ============================================================

TEAM_ALIASES = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Royal Challengers Bengaluru": "Royal Challengers Bengaluru",

    "Delhi Daredevils": "Delhi Capitals",
    "Delhi Capitals": "Delhi Capitals",

    "Kings XI Punjab": "Punjab Kings",
    "Punjab Kings": "Punjab Kings",

    "Rising Pune Supergiants": "Rising Pune Supergiants",
    "Rising Pune Supergiant": "Rising Pune Supergiants",

    "Pune Warriors": "Pune Warriors India",
    "Pune Warriors India": "Pune Warriors India",

    "Chennai Super Kings": "Chennai Super Kings",
    "Gujarat Titans": "Gujarat Titans",
    "Kolkata Knight Riders": "Kolkata Knight Riders",
    "Lucknow Super Giants": "Lucknow Super Giants",
    "Mumbai Indians": "Mumbai Indians",
    "Rajasthan Royals": "Rajasthan Royals",
    "Sunrisers Hyderabad": "Sunrisers Hyderabad",
}


def normalize_team(team):
    if pd.isna(team):
        return team

    team = str(team).strip()

    return TEAM_ALIASES.get(team, team)


# ============================================================
# SAFE NUMERIC
# ============================================================

def numeric(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


# ============================================================
# LOAD FILE
# ============================================================

def load_csv(filename):
    path = PROCESSED_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


# ============================================================
# HISTORICAL TEAM ANALYSIS
# ============================================================

def prepare_team_data():

    df = load_csv("team_season_analysis.csv")

    if df.empty:
        df = load_csv("team_overall_analysis.csv")

    if df.empty:
        raise FileNotFoundError(
            "Team analysis CSV files were not found."
        )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    # Normalize team column
    team_column = None

    for col in ["team", "Team", "TEAM"]:
        if col in df.columns:
            team_column = col
            break

    if team_column is None:
        raise ValueError(
            "Team column not found in team analysis data."
        )

    df["team"] = df[team_column].apply(normalize_team)

    # Season
    season_column = None

    for col in ["season", "Season", "year", "Year"]:
        if col in df.columns:
            season_column = col
            break

    if season_column:
        df["season"] = pd.to_numeric(
            df[season_column],
            errors="coerce"
        )

    # Wins
    win_column = None

    for col in ["wins", "Wins", "win"]:
        if col in df.columns:
            win_column = col
            break

    if win_column:
        df["wins"] = numeric(df[win_column])
    else:
        df["wins"] = 0

    # Matches
    match_column = None

    for col in [
        "matches",
        "Matches",
        "matches_played",
        "Matches_Played"
    ]:
        if col in df.columns:
            match_column = col
            break

    if match_column:
        df["matches"] = numeric(
            df[match_column]
        )
    else:
        df["matches"] = 0

    # Win %
    if "win_percentage" in df.columns:
        df["win_percentage"] = numeric(
            df["win_percentage"]
        )

    elif "win_pct" in df.columns:
        df["win_percentage"] = numeric(
            df["win_pct"]
        )

    else:
        df["win_percentage"] = np.where(
            df["matches"] > 0,
            df["wins"] / df["matches"] * 100,
            0
        )

    return df


# ============================================================
# TEAM COMPARISON
# ============================================================

def build_comparison():

    df = prepare_team_data()

    # Only current 10 teams
    current = df[
        df["team"].isin(CURRENT_TEAMS)
    ].copy()

    if current.empty:
        raise ValueError(
            "No current IPL team records found."
        )

    # --------------------------------------------------------
    # HISTORICAL
    # --------------------------------------------------------

    historical = (
        current
        .groupby("team", as_index=False)
        .agg(
            historical_matches=("matches", "sum"),
            historical_wins=("wins", "sum"),
            historical_win_percentage=(
                "win_percentage",
                "mean"
            ),
        )
    )

    # --------------------------------------------------------
    # RECENT 2024-2026
    # --------------------------------------------------------

    recent = current[
        current["season"].between(
            2024,
            2026
        )
    ].copy()

    if not recent.empty:

        recent_summary = (
            recent
            .groupby("team", as_index=False)
            .agg(
                recent_matches=("matches", "sum"),
                recent_wins=("wins", "sum"),
                recent_win_percentage=(
                    "win_percentage",
                    "mean"
                ),
            )
        )

    else:

        recent_summary = pd.DataFrame(
            columns=[
                "team",
                "recent_matches",
                "recent_wins",
                "recent_win_percentage",
            ]
        )

    # --------------------------------------------------------
    # 2026
    # --------------------------------------------------------

    latest = current[
        current["season"] == 2026
    ].copy()

    if not latest.empty:

        latest_summary = (
            latest
            .groupby("team", as_index=False)
            .agg(
                matches_2026=("matches", "sum"),
                wins_2026=("wins", "sum"),
                win_percentage_2026=(
                    "win_percentage",
                    "mean"
                ),
            )
        )

    else:

        latest_summary = pd.DataFrame(
            columns=[
                "team",
                "matches_2026",
                "wins_2026",
                "win_percentage_2026",
            ]
        )

    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    result = historical.merge(
        recent_summary,
        on="team",
        how="left"
    )

    result = result.merge(
        latest_summary,
        on="team",
        how="left"
    )

    # --------------------------------------------------------
    # FILL MISSING
    # --------------------------------------------------------

    numeric_columns = [
        "historical_matches",
        "historical_wins",
        "historical_win_percentage",
        "recent_matches",
        "recent_wins",
        "recent_win_percentage",
        "matches_2026",
        "wins_2026",
        "win_percentage_2026",
    ]

    for col in numeric_columns:

        if col in result.columns:
            result[col] = numeric(
                result[col]
            )

    # --------------------------------------------------------
    # COMPARISON INDEX
    # --------------------------------------------------------

    result["historical_component"] = (
        result["historical_win_percentage"]
        * 0.30
    )

    result["recent_component"] = (
        result["recent_win_percentage"]
        * 0.40
    )

    result["latest_component"] = (
        result["win_percentage_2026"]
        * 0.30
    )

    result["comparison_index"] = (
        result["historical_component"]
        + result["recent_component"]
        + result["latest_component"]
    )

    # --------------------------------------------------------
    # RANK FOR DISPLAY
    # --------------------------------------------------------

    result = result.sort_values(
        "comparison_index",
        ascending=False
    ).reset_index(drop=True)

    result["comparison_position"] = (
        result.index + 1
    )

    # --------------------------------------------------------
    # ROUND
    # --------------------------------------------------------

    percentage_columns = [
        "historical_win_percentage",
        "recent_win_percentage",
        "win_percentage_2026",
        "comparison_index",
    ]

    for col in percentage_columns:

        if col in result.columns:
            result[col] = result[col].round(2)

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    processed_output = (
        PROCESSED_DIR /
        "team_comparison_2027.csv"
    )

    report_output = (
        OUTPUT_DIR /
        "team_comparison_2027_report.csv"
    )

    result.to_csv(
        processed_output,
        index=False
    )

    result.to_csv(
        report_output,
        index=False
    )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("IPL TEAM COMPARISON - 2027")
    print("=" * 70)

    try:

        result = build_comparison()

        print()
        print(
            f"Current IPL teams analysed: "
            f"{len(result)}"
        )

        print()
        print(
            "Team comparison:"
        )

        display_columns = [
            "comparison_position",
            "team",
            "historical_wins",
            "historical_win_percentage",
            "recent_wins",
            "recent_win_percentage",
            "wins_2026",
            "win_percentage_2026",
            "comparison_index",
        ]

        print(
            result[display_columns].to_string(
                index=False
            )
        )

        print()
        print(
            "Files created:"
        )

        print(
            "data/processed/"
            "team_comparison_2027.csv"
        )

        print(
            "outputs/reports/"
            "team_comparison_2027_report.csv"
        )

        print()
        print(
            "TEAM COMPARISON COMPLETED SUCCESSFULLY"
        )

    except Exception as error:

        print()
        print(
            "[ERROR]",
            str(error)
        )


if __name__ == "__main__":
    main()