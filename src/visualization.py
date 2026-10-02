# ============================================================
# IPL 2027 PREDICTION - VISUALIZATION SYSTEM
# Historical Data : 2008-2026
# Prediction Year : 2027
# ============================================================

import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

PROCESSED_DIR = os.path.join(
    DATA_DIR,
    "processed"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

CHART_DIR = os.path.join(
    OUTPUT_DIR,
    "charts"
)

PREDICTION_DIR = os.path.join(
    OUTPUT_DIR,
    "predictions"
)

REPORT_DIR = os.path.join(
    OUTPUT_DIR,
    "reports"
)

os.makedirs(
    CHART_DIR,
    exist_ok=True
)

os.makedirs(
    PREDICTION_DIR,
    exist_ok=True
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


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
    "Sunrisers Hyderabad"
]


# ============================================================
# TEAM ALIASES
# ============================================================

ALIASES = {
    "Royal Challengers Bangalore":
        "Royal Challengers Bengaluru",

    "Royal Challengers Bengaluru":
        "Royal Challengers Bengaluru",

    "Delhi Daredevils":
        "Delhi Capitals",

    "Delhi Capitals":
        "Delhi Capitals",

    "Kings XI Punjab":
        "Punjab Kings",

    "Punjab Kings":
        "Punjab Kings"
}


def normalize_team(name):

    if pd.isna(name):
        return name

    name = str(name).strip()

    return ALIASES.get(
        name,
        name
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_csv(path):

    if not os.path.exists(path):

        print(
            f"[SKIPPED] File not found: {path}"
        )

        return pd.DataFrame()

    try:

        df = pd.read_csv(path)

        df.columns = [
            str(c).strip()
            for c in df.columns
        ]

        return df

    except Exception as e:

        print(
            f"[ERROR] Could not load {path}: {e}"
        )

        return pd.DataFrame()


def find_column(df, names):

    for name in names:

        if name in df.columns:
            return name

    return None


def save_chart(filename):

    path = os.path.join(
        CHART_DIR,
        filename
    )

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"[CREATED] {filename}"
    )


def safe_numeric(
    df,
    column,
    default=0
):

    if column is None:

        return pd.Series(
            default,
            index=df.index,
            dtype=float
        )

    return pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(default)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("IPL VISUALIZATION SYSTEM")
print("=" * 70)

print("Historical data : 2008-2026")
print("Prediction year : 2027")

print("=" * 70)


# ============================================================
# 1. IPL 2027 PREDICTION CHART
# ============================================================

print(
    "\n1. Creating IPL 2027 prediction chart..."
)


prediction_file = os.path.join(
    PREDICTION_DIR,
    "ipl_2027_final_prediction.csv"
)

prediction_df = load_csv(
    prediction_file
)


if prediction_df.empty:

    # fallback
    prediction_file = os.path.join(
        OUTPUT_DIR,
        "predictions",
        "ipl_2027_prediction_input.csv"
    )

    prediction_df = load_csv(
        prediction_file
    )


if not prediction_df.empty:

    team_col = find_column(
        prediction_df,
        [
            "team",
            "team_name"
        ]
    )

    score_col = find_column(
        prediction_df,
        [
            "final_prediction_score",
            "prediction_score",
            "score"
        ]
    )

    probability_col = find_column(
        prediction_df,
        [
            "model_probability",
            "prediction_probability",
            "probability"
        ]
    )

    if team_col and score_col:

        plot_df = prediction_df.copy()

        plot_df["score"] = safe_numeric(
            plot_df,
            score_col
        )

        plot_df = plot_df.sort_values(
            "score",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df[team_col],
            plot_df["score"]
        )

        plt.xlabel(
            "Prediction Score"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "IPL 2027 Team Prediction Score"
        )

        save_chart(
            "ipl_2027_prediction.png"
        )


# ============================================================
# 2. IPL TITLE HISTORY
# ============================================================

print(
    "\n2. Creating IPL title history chart..."
)


title_file = os.path.join(
    REPORT_DIR,
    "ipl_champions_2008_2026.csv"
)

title_df = load_csv(
    title_file
)


if not title_df.empty:

    team_col = find_column(
        title_df,
        [
            "team",
            "winner",
            "champion"
        ]
    )

    if team_col:

        title_counts = (
            title_df[team_col]
            .apply(normalize_team)
            .value_counts()
            .sort_values()
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            title_counts.index,
            title_counts.values
        )

        plt.xlabel(
            "Number of IPL Titles"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "IPL Title History (2008-2026)"
        )

        save_chart(
            "ipl_titles_2008_2026.png"
        )


# ============================================================
# 3. HISTORICAL TEAM WINS
# ============================================================

print(
    "\n3. Creating historical wins chart..."
)


team_file = os.path.join(
    PROCESSED_DIR,
    "team_overall_analysis.csv"
)

team_df = load_csv(
    team_file
)


if not team_df.empty:

    team_col = find_column(
        team_df,
        [
            "team",
            "team_name"
        ]
    )

    wins_col = find_column(
        team_df,
        [
            "wins",
            "historical_wins",
            "total_wins"
        ]
    )

    if team_col and wins_col:

        plot_df = team_df.copy()

        plot_df["wins_value"] = safe_numeric(
            plot_df,
            wins_col
        )

        plot_df["team_clean"] = (
            plot_df[team_col]
            .apply(normalize_team)
        )

        plot_df = plot_df.sort_values(
            "wins_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df["team_clean"],
            plot_df["wins_value"]
        )

        plt.xlabel(
            "Historical Wins"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "Historical IPL Team Wins"
        )

        save_chart(
            "historical_team_wins.png"
        )


# ============================================================
# 4. HISTORICAL WINS VS TITLES
# ============================================================

print(
    "\n4. Creating wins vs titles chart..."
)


if not team_df.empty:

    team_col = find_column(
        team_df,
        [
            "team",
            "team_name"
        ]
    )

    wins_col = find_column(
        team_df,
        [
            "wins",
            "historical_wins",
            "total_wins"
        ]
    )

    titles_col = find_column(
        team_df,
        [
            "historical_titles",
            "titles",
            "championships"
        ]
    )

    if (
        team_col
        and wins_col
        and titles_col
    ):

        plt.figure(
            figsize=(11, 7)
        )

        x = safe_numeric(
            team_df,
            wins_col
        )

        y = safe_numeric(
            team_df,
            titles_col
        )

        plt.scatter(
            x,
            y,
            s=100
        )

        for i in range(
            len(team_df)
        ):

            plt.annotate(
                str(
                    team_df.iloc[i][team_col]
                ),
                (
                    x.iloc[i],
                    y.iloc[i]
                ),
                fontsize=8
            )

        plt.xlabel(
            "Historical Wins"
        )

        plt.ylabel(
            "IPL Titles"
        )

        plt.title(
            "Historical Wins vs IPL Titles"
        )

        save_chart(
            "historical_wins_vs_titles.png"
        )


# ============================================================
# 5. 2026 TEAM WINS
# ============================================================

print(
    "\n5. Creating 2026 wins chart..."
)


current_file = os.path.join(
    PROCESSED_DIR,
    "current_team_analysis_2026.csv"
)

current_df = load_csv(
    current_file
)


if not current_df.empty:

    team_col = find_column(
        current_df,
        [
            "team",
            "team_name"
        ]
    )

    wins_col = find_column(
        current_df,
        [
            "wins",
            "wins_2026"
        ]
    )

    if team_col and wins_col:

        plot_df = current_df.copy()

        plot_df["wins_value"] = safe_numeric(
            plot_df,
            wins_col
        )

        plot_df["team_clean"] = (
            plot_df[team_col]
            .apply(normalize_team)
        )

        plot_df = plot_df.sort_values(
            "wins_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df["team_clean"],
            plot_df["wins_value"]
        )

        plt.xlabel(
            "Wins in 2026"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "IPL 2026 Team Wins"
        )

        save_chart(
            "team_wins_2026.png"
        )


# ============================================================
# 6. 2027 TEAM STRENGTH
# ============================================================

print(
    "\n6. Creating team strength chart..."
)


strength_file = os.path.join(
    PROCESSED_DIR,
    "team_strength_features_2027.csv"
)

strength_df = load_csv(
    strength_file
)


if not strength_df.empty:

    team_col = find_column(
        strength_df,
        [
            "team",
            "team_name"
        ]
    )

    strength_col = find_column(
        strength_df,
        [
            "team_strength",
            "strength_score",
            "composite_strength",
            "overall_strength",
            "strength"
        ]
    )

    if team_col and strength_col:

        plot_df = strength_df.copy()

        plot_df["strength_value"] = safe_numeric(
            plot_df,
            strength_col
        )

        plot_df["team_clean"] = (
            plot_df[team_col]
            .apply(normalize_team)
        )

        plot_df = plot_df.sort_values(
            "strength_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df["team_clean"],
            plot_df["strength_value"]
        )

        plt.xlabel(
            "Team Strength"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "IPL 2027 Team Strength"
        )

        save_chart(
            "team_strength_2027.png"
        )


# ============================================================
# 7. TOP 10 BATSMEN
# ============================================================

print(
    "\n7. Creating top batsmen chart..."
)


batting_file = os.path.join(
    PROCESSED_DIR,
    "player_batting_analysis.csv"
)

batting_df = load_csv(
    batting_file
)


if not batting_df.empty:

    player_col = find_column(
        batting_df,
        [
            "player",
            "batter",
            "batsman",
            "batsman_name"
        ]
    )

    runs_col = find_column(
        batting_df,
        [
            "runs",
            "total_runs"
        ]
    )

    if player_col and runs_col:

        plot_df = batting_df.copy()

        plot_df["runs_value"] = safe_numeric(
            plot_df,
            runs_col
        )

        plot_df = plot_df.sort_values(
            "runs_value",
            ascending=False
        ).head(10)

        plot_df = plot_df.sort_values(
            "runs_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df[player_col],
            plot_df["runs_value"]
        )

        plt.xlabel(
            "Runs"
        )

        plt.ylabel(
            "Player"
        )

        plt.title(
            "Top 10 IPL Batsmen - Career Runs"
        )

        save_chart(
            "top_10_batsmen.png"
        )


# ============================================================
# 8. TOP 10 BOWLERS
# ============================================================

print(
    "\n8. Creating top bowlers chart..."
)


bowling_file = os.path.join(
    PROCESSED_DIR,
    "player_bowling_analysis.csv"
)

bowling_df = load_csv(
    bowling_file
)


if not bowling_df.empty:

    player_col = find_column(
        bowling_df,
        [
            "player",
            "bowler",
            "bowler_name"
        ]
    )

    wickets_col = find_column(
        bowling_df,
        [
            "wickets",
            "total_wickets"
        ]
    )

    if player_col and wickets_col:

        plot_df = bowling_df.copy()

        plot_df["wickets_value"] = safe_numeric(
            plot_df,
            wickets_col
        )

        plot_df = plot_df.sort_values(
            "wickets_value",
            ascending=False
        ).head(10)

        plot_df = plot_df.sort_values(
            "wickets_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df[player_col],
            plot_df["wickets_value"]
        )

        plt.xlabel(
            "Wickets"
        )

        plt.ylabel(
            "Player"
        )

        plt.title(
            "Top 10 IPL Bowlers - Career Wickets"
        )

        save_chart(
            "top_10_bowlers.png"
        )


# ============================================================
# 9. SEASON-WISE MATCHES
# ============================================================

print(
    "\n9. Creating season-wise matches chart..."
)


season_file = os.path.join(
    PROCESSED_DIR,
    "season_match_summary.csv"
)

season_df = load_csv(
    season_file
)


if not season_df.empty:

    season_col = find_column(
        season_df,
        [
            "season",
            "year"
        ]
    )

    matches_col = find_column(
        season_df,
        [
            "matches",
            "match_count",
            "total_matches"
        ]
    )

    if season_col and matches_col:

        plot_df = season_df.copy()

        plot_df["season_value"] = pd.to_numeric(
            plot_df[season_col],
            errors="coerce"
        )

        plot_df["matches_value"] = safe_numeric(
            plot_df,
            matches_col
        )

        plot_df = plot_df.sort_values(
            "season_value"
        )

        plt.figure(
            figsize=(12, 6)
        )

        plt.plot(
            plot_df["season_value"],
            plot_df["matches_value"],
            marker="o"
        )

        plt.xlabel(
            "IPL Season"
        )

        plt.ylabel(
            "Number of Matches"
        )

        plt.title(
            "IPL Matches by Season (2008-2026)"
        )

        plt.xticks(
            plot_df["season_value"],
            rotation=45
        )

        save_chart(
            "ipl_matches_yearly_trend.png"
        )


# ============================================================
# 10. RECENT FORM 2024-2026
# ============================================================

print(
    "\n10. Creating recent form chart..."
)


recent_file = os.path.join(
    PROCESSED_DIR,
    "team_recent_form_2024_2026.csv"
)

recent_df = load_csv(
    recent_file
)


if not recent_df.empty:

    team_col = find_column(
        recent_df,
        [
            "team",
            "team_name"
        ]
    )

    recent_col = find_column(
        recent_df,
        [
            "weighted_recent_form",
            "recent_form",
            "recent_win_percentage",
            "win_percentage"
        ]
    )

    if team_col and recent_col:

        plot_df = recent_df.copy()

        plot_df["recent_value"] = safe_numeric(
            plot_df,
            recent_col
        )

        plot_df["team_clean"] = (
            plot_df[team_col]
            .apply(normalize_team)
        )

        plot_df = plot_df.sort_values(
            "recent_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df["team_clean"],
            plot_df["recent_value"]
        )

        plt.xlabel(
            "Recent Form (%)"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "IPL Team Recent Form (2024-2026)"
        )

        save_chart(
            "team_recent_form_2024_2026.png"
        )


# ============================================================
# 11. PREDICTION SCORE CHART
# ============================================================

print(
    "\n11. Creating prediction score chart..."
)


if not prediction_df.empty:

    team_col = find_column(
        prediction_df,
        [
            "team",
            "team_name"
        ]
    )

    score_col = find_column(
        prediction_df,
        [
            "final_prediction_score",
            "prediction_score",
            "score"
        ]
    )

    if team_col and score_col:

        plot_df = prediction_df.copy()

        plot_df["score_value"] = safe_numeric(
            plot_df,
            score_col
        )

        plot_df = plot_df.sort_values(
            "score_value",
            ascending=True
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.barh(
            plot_df[team_col],
            plot_df["score_value"]
        )

        plt.xlabel(
            "Final Prediction Score"
        )

        plt.ylabel(
            "Team"
        )

        plt.title(
            "IPL 2027 Final Prediction Score"
        )

        save_chart(
            "ipl_2027_prediction_score.png"
        )


# ============================================================
# 12. HISTORICAL WINS VS 2027 PREDICTION
# ============================================================

print(
    "\n12. Creating historical wins vs 2027 prediction chart..."
)


if (
    not team_df.empty
    and not prediction_df.empty
):

    team_col_1 = find_column(
        team_df,
        [
            "team",
            "team_name"
        ]
    )

    wins_col = find_column(
        team_df,
        [
            "wins",
            "historical_wins",
            "total_wins"
        ]
    )

    team_col_2 = find_column(
        prediction_df,
        [
            "team",
            "team_name"
        ]
    )

    score_col = find_column(
        prediction_df,
        [
            "final_prediction_score",
            "prediction_score",
            "score"
        ]
    )

    if (
        team_col_1
        and wins_col
        and team_col_2
        and score_col
    ):

        left = team_df[
            [team_col_1, wins_col]
        ].copy()

        left.columns = [
            "team",
            "historical_wins"
        ]

        right = prediction_df[
            [team_col_2, score_col]
        ].copy()

        right.columns = [
            "team",
            "prediction_score"
        ]

        left["team"] = (
            left["team"]
            .apply(normalize_team)
        )

        right["team"] = (
            right["team"]
            .apply(normalize_team)
        )

        merged = pd.merge(
            left,
            right,
            on="team",
            how="inner"
        )

        merged["historical_wins"] = safe_numeric(
            merged,
            "historical_wins"
        )

        merged["prediction_score"] = safe_numeric(
            merged,
            "prediction_score"
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.scatter(
            merged["historical_wins"],
            merged["prediction_score"],
            s=100
        )

        for _, row in merged.iterrows():

            plt.annotate(
                row["team"],
                (
                    row["historical_wins"],
                    row["prediction_score"]
                ),
                fontsize=8
            )

        plt.xlabel(
            "Historical Wins"
        )

        plt.ylabel(
            "IPL 2027 Prediction Score"
        )

        plt.title(
            "Historical Wins vs IPL 2027 Prediction"
        )

        save_chart(
            "historical_wins_vs_2027_prediction.png"
        )


# ============================================================
# 13. 2026 WINS VS 2027 PREDICTION
# ============================================================

print(
    "\n13. Creating 2026 wins vs 2027 prediction chart..."
)


if (
    not current_df.empty
    and not prediction_df.empty
):

    team_col_1 = find_column(
        current_df,
        [
            "team",
            "team_name"
        ]
    )

    wins_col = find_column(
        current_df,
        [
            "wins",
            "wins_2026"
        ]
    )

    team_col_2 = find_column(
        prediction_df,
        [
            "team",
            "team_name"
        ]
    )

    score_col = find_column(
        prediction_df,
        [
            "final_prediction_score",
            "prediction_score",
            "score"
        ]
    )

    if (
        team_col_1
        and wins_col
        and team_col_2
        and score_col
    ):

        left = current_df[
            [team_col_1, wins_col]
        ].copy()

        left.columns = [
            "team",
            "wins_2026"
        ]

        right = prediction_df[
            [team_col_2, score_col]
        ].copy()

        right.columns = [
            "team",
            "prediction_score"
        ]

        left["team"] = (
            left["team"]
            .apply(normalize_team)
        )

        right["team"] = (
            right["team"]
            .apply(normalize_team)
        )

        merged = pd.merge(
            left,
            right,
            on="team",
            how="inner"
        )

        merged["wins_2026"] = safe_numeric(
            merged,
            "wins_2026"
        )

        merged["prediction_score"] = safe_numeric(
            merged,
            "prediction_score"
        )

        plt.figure(
            figsize=(11, 7)
        )

        plt.scatter(
            merged["wins_2026"],
            merged["prediction_score"],
            s=100
        )

        for _, row in merged.iterrows():

            plt.annotate(
                row["team"],
                (
                    row["wins_2026"],
                    row["prediction_score"]
                ),
                fontsize=8
            )

        plt.xlabel(
            "2026 Wins"
        )

        plt.ylabel(
            "IPL 2027 Prediction Score"
        )

        plt.title(
            "2026 Performance vs IPL 2027 Prediction"
        )

        save_chart(
            "2026_wins_vs_2027_prediction.png"
        )


# ============================================================
# 14. IPL 2027 MATCH-UP HEATMAP
# ============================================================

print(
    "\n14. Creating IPL 2027 match-up heatmap..."
)


matrix_file = os.path.join(
    PREDICTION_DIR,
    "ipl_2027_matchup_matrix.csv"
)

matrix_df = load_csv(
    matrix_file
)


if not matrix_df.empty:

    # First column is normally the team/index column
    first_col = matrix_df.columns[0]

    matrix_df = matrix_df.set_index(
        first_col
    )

    matrix_df.index = [
        normalize_team(x)
        for x in matrix_df.index
    ]

    matrix_df.columns = [
        normalize_team(x)
        for x in matrix_df.columns
    ]

    # Keep only current teams
    valid_rows = [
        x for x in CURRENT_TEAMS
        if x in matrix_df.index
    ]

    valid_cols = [
        x for x in CURRENT_TEAMS
        if x in matrix_df.columns
    ]

    if valid_rows and valid_cols:

        matrix_plot = matrix_df.loc[
            valid_rows,
            valid_cols
        ].apply(
            pd.to_numeric,
            errors="coerce"
        )

        plt.figure(
            figsize=(14, 10)
        )

        image = plt.imshow(
            matrix_plot.values,
            aspect="auto"
        )

        plt.colorbar(
            image,
            label="Prediction %"
        )

        plt.xticks(
            range(len(matrix_plot.columns)),
            matrix_plot.columns,
            rotation=75,
            fontsize=8
        )

        plt.yticks(
            range(len(matrix_plot.index)),
            matrix_plot.index,
            fontsize=8
        )

        plt.title(
            "IPL 2027 Team Match-Up Prediction Matrix"
        )

        plt.xlabel(
            "Opponent Team"
        )

        plt.ylabel(
            "Team"
        )

        # Add values
        for i in range(
            len(matrix_plot.index)
        ):

            for j in range(
                len(matrix_plot.columns)
            ):

                value = matrix_plot.iloc[
                    i,
                    j
                ]

                if pd.notna(value):

                    plt.text(
                        j,
                        i,
                        f"{value:.0f}",
                        ha="center",
                        va="center",
                        fontsize=7
                    )

        save_chart(
            "ipl_2027_matchup_heatmap.png"
        )


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n")
print("=" * 70)
print("VISUALIZATION COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    f"Charts saved in:\n{CHART_DIR}"
)

print(
    "\nIPL visualization process completed successfully."
)

print("=" * 70)