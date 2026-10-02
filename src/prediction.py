import os
import numpy as np
import pandas as pd


# ============================================================
# IPL 2027 CHAMPION PREDICTION SYSTEM
# FINAL VERSION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "predictions",
    "ipl_2027_prediction_input.csv"
)

TEAM_SEASON_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "team_season_analysis.csv"
)

CURRENT_2026_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "current_team_analysis_2026.csv"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "predictions",
    "ipl_2027_final_prediction.csv"
)

SUMMARY_FILE = os.path.join(
    BASE_DIR,
    "outputs",
    "reports",
    "ipl_2027_prediction_summary.csv"
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
# IPL TITLE HISTORY - 2008 TO 2026
# ============================================================

TITLE_HISTORY = {

    "Mumbai Indians": 5,

    "Chennai Super Kings": 5,

    "Kolkata Knight Riders": 3,

    "Royal Challengers Bengaluru": 2,

    "Rajasthan Royals": 1,

    "Deccan Chargers": 1,

    "Sunrisers Hyderabad": 1,

    "Gujarat Titans": 1
}


# ============================================================
# IPL RUNNER-UP HISTORY
# ============================================================

RUNNER_UP_HISTORY = {

    "Chennai Super Kings": 5,

    "Royal Challengers Bengaluru": 3,

    "Gujarat Titans": 2,

    "Sunrisers Hyderabad": 2,

    "Punjab Kings": 1,

    "Rajasthan Royals": 1,

    "Kolkata Knight Riders": 1,

    "Delhi Capitals": 1
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:

        return pd.Series(
            50.0,
            index=series.index
        )

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    )


def find_column(
    dataframe,
    possible_names
):

    columns_lower = {
        str(column).lower().strip(): column
        for column in dataframe.columns
    }

    for name in possible_names:

        key = str(name).lower().strip()

        if key in columns_lower:

            return columns_lower[key]

    return None


def numeric_series(
    dataframe,
    column
):

    if column is None:

        return pd.Series(
            0.0,
            index=dataframe.index
        )

    return pd.to_numeric(
        dataframe[column],
        errors="coerce"
    ).fillna(0)


def safe_map(
    dataframe,
    column_name,
    mapping
):

    if column_name not in dataframe.columns:

        return pd.Series(
            0.0,
            index=dataframe.index
        )

    return (
        dataframe[column_name]
        .map(mapping)
        .fillna(0)
    )


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 75)
print("             IPL 2027 CHAMPION PREDICTION SYSTEM")
print("=" * 75)

print("Historical data : 2008-2026")
print("Prediction year  : 2027")

print("=" * 75)


# ============================================================
# LOAD PREDICTION INPUT
# ============================================================

if not os.path.exists(INPUT_FILE):

    raise FileNotFoundError(
        f"\nPrediction input not found:\n{INPUT_FILE}"
    )


df = pd.read_csv(INPUT_FILE)

print()
print(
    f"Prediction input loaded: {len(df)} records"
)


# ============================================================
# TEAM VALIDATION
# ============================================================

if "team" not in df.columns:

    raise ValueError(
        "Column 'team' not found."
    )


df["team"] = (
    df["team"]
    .astype(str)
    .str.strip()
)


found_teams = set(df["team"])

missing_teams = (
    set(CURRENT_TEAMS)
    - found_teams
)

extra_teams = (
    found_teams
    - set(CURRENT_TEAMS)
)


print()
print("=" * 75)
print("IPL 2027 PREDICTION DATA VALIDATION")
print("=" * 75)

print(
    f"Current IPL teams: {len(found_teams)}"
)


if missing_teams:

    print(
        "Missing teams:",
        missing_teams
    )

    raise ValueError(
        "Current team validation failed."
    )


if extra_teams:

    print(
        "Extra teams:",
        extra_teams
    )

    raise ValueError(
        "Extra team found."
    )


df = df[
    df["team"].isin(CURRENT_TEAMS)
].copy()


df = df.drop_duplicates(
    subset=["team"]
)


if len(df) != 10:

    raise ValueError(
        f"Expected 10 teams, found {len(df)}"
    )


print("Validation: PASSED")


# ============================================================
# HISTORICAL WINS FROM TEAM-SEASON ANALYSIS
# ============================================================

historical_wins = {}

historical_matches = {}

historical_losses = {}


if os.path.exists(TEAM_SEASON_FILE):

    season_df = pd.read_csv(
        TEAM_SEASON_FILE
    )

    season_team_col = find_column(
        season_df,
        [
            "team",
            "Team"
        ]
    )

    season_wins_col = find_column(
        season_df,
        [
            "wins",
            "Wins",
            "total_wins"
        ]
    )

    season_matches_col = find_column(
        season_df,
        [
            "matches",
            "Matches",
            "matches_played",
            "total_matches"
        ]
    )

    season_losses_col = find_column(
        season_df,
        [
            "losses",
            "Losses",
            "total_losses"
        ]
    )


    if season_team_col is not None:

        for team in CURRENT_TEAMS:

            team_rows = season_df[
                season_df[season_team_col]
                .astype(str)
                .str.strip()
                == team
            ]


            if season_wins_col is not None:

                historical_wins[team] = (
                    pd.to_numeric(
                        team_rows[season_wins_col],
                        errors="coerce"
                    )
                    .fillna(0)
                    .sum()
                )

            else:

                historical_wins[team] = 0


            if season_matches_col is not None:

                historical_matches[team] = (
                    pd.to_numeric(
                        team_rows[season_matches_col],
                        errors="coerce"
                    )
                    .fillna(0)
                    .sum()
                )

            else:

                historical_matches[team] = 0


            if season_losses_col is not None:

                historical_losses[team] = (
                    pd.to_numeric(
                        team_rows[season_losses_col],
                        errors="coerce"
                    )
                    .fillna(0)
                    .sum()
                )

            else:

                historical_losses[team] = 0


else:

    for team in CURRENT_TEAMS:

        historical_wins[team] = 0
        historical_matches[team] = 0
        historical_losses[team] = 0


# ============================================================
# 2026 WINS
# ============================================================

wins_2026 = {}

matches_2026 = {}

losses_2026 = {}

no_results_2026 = {}


if os.path.exists(CURRENT_2026_FILE):

    current_df = pd.read_csv(
        CURRENT_2026_FILE
    )

    current_team_col = find_column(
        current_df,
        [
            "team",
            "Team"
        ]
    )

    current_wins_col = find_column(
        current_df,
        [
            "wins_2026",
            "wins",
            "total_wins"
        ]
    )

    current_matches_col = find_column(
        current_df,
        [
            "matches_2026",
            "matches",
            "matches_played"
        ]
    )

    current_losses_col = find_column(
        current_df,
        [
            "losses_2026",
            "losses",
            "total_losses"
        ]
    )

    current_nr_col = find_column(
        current_df,
        [
            "no_results_2026",
            "no_results",
            "nr"
        ]
    )


    if current_team_col is not None:

        for team in CURRENT_TEAMS:

            rows = current_df[
                current_df[current_team_col]
                .astype(str)
                .str.strip()
                == team
            ]


            if len(rows) > 0:

                row = rows.iloc[0]


                if current_wins_col:

                    wins_2026[team] = float(
                        pd.to_numeric(
                            row[current_wins_col],
                            errors="coerce"
                        )
                        or 0
                    )

                else:

                    wins_2026[team] = 0


                if current_matches_col:

                    matches_2026[team] = float(
                        pd.to_numeric(
                            row[current_matches_col],
                            errors="coerce"
                        )
                        or 0
                    )

                else:

                    matches_2026[team] = 0


                if current_losses_col:

                    losses_2026[team] = float(
                        pd.to_numeric(
                            row[current_losses_col],
                            errors="coerce"
                        )
                        or 0
                    )

                else:

                    losses_2026[team] = 0


                if current_nr_col:

                    no_results_2026[team] = float(
                        pd.to_numeric(
                            row[current_nr_col],
                            errors="coerce"
                        )
                        or 0
                    )

                else:

                    no_results_2026[team] = 0

            else:

                wins_2026[team] = 0
                matches_2026[team] = 0
                losses_2026[team] = 0
                no_results_2026[team] = 0

else:

    for team in CURRENT_TEAMS:

        wins_2026[team] = 0
        matches_2026[team] = 0
        losses_2026[team] = 0
        no_results_2026[team] = 0


# ============================================================
# ADD WIN FEATURES TO DATAFRAME
# ============================================================

df["historical_wins"] = (
    df["team"]
    .map(historical_wins)
    .fillna(0)
)

df["historical_matches"] = (
    df["team"]
    .map(historical_matches)
    .fillna(0)
)

df["historical_losses"] = (
    df["team"]
    .map(historical_losses)
    .fillna(0)
)

df["wins_2026"] = (
    df["team"]
    .map(wins_2026)
    .fillna(0)
)

df["matches_2026"] = (
    df["team"]
    .map(matches_2026)
    .fillna(0)
)

df["losses_2026"] = (
    df["team"]
    .map(losses_2026)
    .fillna(0)
)

df["no_results_2026"] = (
    df["team"]
    .map(no_results_2026)
    .fillna(0)
)


# ============================================================
# CALCULATE WIN PERCENTAGES
# ============================================================

df["historical_win_pct_calculated"] = np.where(

    df["historical_matches"] > 0,

    (
        df["historical_wins"]
        / df["historical_matches"]
        * 100
    ),

    0
)


df["win_pct_2026_calculated"] = np.where(

    df["matches_2026"] > 0,

    (
        df["wins_2026"]
        / df["matches_2026"]
        * 100
    ),

    0
)


# ============================================================
# HISTORICAL TITLE FEATURES
# ============================================================

df["historical_titles"] = safe_map(
    df,
    "team",
    TITLE_HISTORY
)


df["runner_up_count"] = safe_map(
    df,
    "team",
    RUNNER_UP_HISTORY
)


df["title_strength"] = normalize(
    df["historical_titles"]
)


df["final_experience"] = normalize(
    df["runner_up_count"]
)


# ============================================================
# EXISTING FEATURE COLUMNS
# ============================================================

historical_feature_col = find_column(
    df,
    [
        "historical_win_percentage",
        "historical_win_pct",
        "historical_strength"
    ]
)


recent_feature_col = find_column(
    df,
    [
        "weighted_recent_form",
        "recent_win_percentage",
        "recent_win_pct",
        "recent_strength"
    ]
)


latest_feature_col = find_column(
    df,
    [
        "win_percentage_2026",
        "win_pct_2026",
        "latest_strength",
        "2026_win_percentage"
    ]
)


team_strength_col = find_column(
    df,
    [
        "team_strength_score",
        "team_strength",
        "strength_score"
    ]
)


batting_col = find_column(
    df,
    [
        "batting_strength",
        "batting_score",
        "run_strength"
    ]
)


bowling_col = find_column(
    df,
    [
        "bowling_strength",
        "bowling_score"
    ]
)


consistency_col = find_column(
    df,
    [
        "consistency_strength",
        "consistency_score",
        "consistency"
    ]
)


# ============================================================
# NORMALIZED COMPONENTS
# ============================================================

# Historical win percentage
if historical_feature_col is not None:

    historical_input = numeric_series(
        df,
        historical_feature_col
    )

else:

    historical_input = (
        df["historical_win_pct_calculated"]
    )


df["historical_component"] = normalize(
    historical_input
)


# Historical total wins
df["historical_wins_component"] = normalize(
    df["historical_wins"]
)


# 2026 wins
df["wins_2026_component"] = normalize(
    df["wins_2026"]
)


# 2026 win percentage
df["latest_wins_component"] = normalize(
    df["win_pct_2026_calculated"]
)


# Recent form
if recent_feature_col is not None:

    recent_input = numeric_series(
        df,
        recent_feature_col
    )

else:

    recent_input = (
        df["historical_component"]
    )


df["recent_component"] = normalize(
    recent_input
)


# Latest 2026 feature
if latest_feature_col is not None:

    latest_input = numeric_series(
        df,
        latest_feature_col
    )

else:

    latest_input = (
        df["win_pct_2026_calculated"]
    )


df["latest_component"] = normalize(
    latest_input
)


# Team strength
if team_strength_col is not None:

    df["team_strength_component"] = normalize(
        numeric_series(
            df,
            team_strength_col
        )
    )

else:

    df["team_strength_component"] = 50.0


# Batting
if batting_col is not None:

    df["batting_component"] = normalize(
        numeric_series(
            df,
            batting_col
        )
    )

else:

    df["batting_component"] = 50.0


# Bowling
if bowling_col is not None:

    df["bowling_component"] = normalize(
        numeric_series(
            df,
            bowling_col
        )
    )

else:

    df["bowling_component"] = 50.0


# Consistency
if consistency_col is not None:

    df["consistency_component"] = normalize(
        numeric_series(
            df,
            consistency_col
        )
    )

else:

    df["consistency_component"] = 50.0


# ============================================================
# 2024 + 2025 + 2026 FORM
# ============================================================

if "win_percentage_2024" in df.columns:

    form_2024_raw = numeric_series(
        df,
        "win_percentage_2024"
    )

    df["form_2024"] = normalize(
        form_2024_raw
    )

else:

    df["form_2024"] = 50.0


if "win_percentage_2025" in df.columns:

    form_2025_raw = numeric_series(
        df,
        "win_percentage_2025"
    )

    df["form_2025"] = normalize(
        form_2025_raw
    )

else:

    df["form_2025"] = 50.0


# Use calculated 2026 percentage
df["form_2026"] = normalize(
    df["win_pct_2026_calculated"]
)


# ============================================================
# RECENT 3 YEAR FORM
# ============================================================

df["recent_3_year_component"] = (

      df["form_2024"] * 0.25

    + df["form_2025"] * 0.35

    + df["form_2026"] * 0.40
)


# ============================================================
# WIN PERFORMANCE COMPONENT
# ============================================================

# Total historical wins + 2026 wins
# Gives actual match-winning performance a meaningful role.

df["win_performance_component"] = (

      df["historical_wins_component"] * 0.35

    + df["wins_2026_component"] * 0.25

    + df["latest_wins_component"] * 0.40
)


# ============================================================
# TITLE BONUS
# ============================================================

df["title_bonus"] = np.select(

    [
        df["historical_titles"] >= 5,

        df["historical_titles"] >= 3,

        df["historical_titles"] >= 2,

        df["historical_titles"] >= 1
    ],

    [
        5.0,
        3.5,
        2.5,
        1.5
    ],

    default=0.0
)


# ============================================================
# FINAL PREDICTION SCORE
# ============================================================

# ------------------------------------------------------------
# WEIGHTS
# ------------------------------------------------------------
#
# Historical win performance       15%
# Historical total wins             5%
# Recent 3-year form               15%
# 2026 performance                 15%
# Team strength                    15%
# Batting strength                 10%
# Bowling strength                 10%
# Consistency                       5%
# Title history                     5%
#
# Total = 100%
#
# Title history is included,
# but actual match performance has higher influence.
# ------------------------------------------------------------


df["final_prediction_score"] = (

      df["historical_component"] * 0.15

    + df["historical_wins_component"] * 0.05

    + df["recent_3_year_component"] * 0.15

    + df["win_performance_component"] * 0.15

    + df["latest_component"] * 0.10

    + df["team_strength_component"] * 0.15

    + df["batting_component"] * 0.10

    + df["bowling_component"] * 0.10

    + df["consistency_component"] * 0.05

    + df["title_strength"] * 0.05
)


# Add small transparent title bonus
df["final_prediction_score"] = (

    df["final_prediction_score"]

    + df["title_bonus"]
)


# ============================================================
# RELATIVE MODEL PROBABILITY
# ============================================================

# Temperature prevents one team from receiving
# an unrealistically extreme percentage.

temperature = 12.0

scores = (
    df["final_prediction_score"]
    .values
)

exp_scores = np.exp(
    (
        scores
        - scores.max()
    )
    / temperature
)

probabilities = (
    exp_scores
    / exp_scores.sum()
) * 100


df["model_probability"] = (
    probabilities
)


# ============================================================
# SORT / RANK
# ============================================================

df = df.sort_values(
    "final_prediction_score",
    ascending=False
).reset_index(
    drop=True
)


df["prediction_position"] = (
    df.index + 1
)


# ============================================================
# KEY FACTORS
# ============================================================

def key_factors(row):

    factors = {

        "Historical wins":
            row["historical_wins_component"],

        "Recent 3-year form":
            row["recent_3_year_component"],

        "2026 wins":
            row["wins_2026_component"],

        "2026 win percentage":
            row["latest_wins_component"],

        "Team strength":
            row["team_strength_component"],

        "Batting":
            row["batting_component"],

        "Bowling":
            row["bowling_component"],

        "Consistency":
            row["consistency_component"],

        "Title history":
            row["title_strength"]
    }


    sorted_factors = sorted(
        factors.items(),
        key=lambda item: item[1],
        reverse=True
    )


    return ", ".join(
        [
            item[0]
            for item in sorted_factors[:3]
        ]
    )


df["key_factors"] = df.apply(
    key_factors,
    axis=1
)


# ============================================================
# OUTPUT COLUMNS
# ============================================================

output_columns = [

    "prediction_position",

    "team",

    # Wins
    "historical_wins",
    "wins_2026",

    # Matches
    "historical_matches",
    "matches_2026",

    # Losses
    "historical_losses",
    "losses_2026",

    # Titles
    "historical_titles",
    "runner_up_count",

    # Prediction
    "final_prediction_score",
    "model_probability",

    # Components
    "historical_component",
    "historical_wins_component",
    "recent_3_year_component",
    "win_performance_component",
    "latest_component",
    "team_strength_component",
    "batting_component",
    "bowling_component",
    "consistency_component",
    "title_bonus",

    # Explanation
    "key_factors"
]


output = df[
    output_columns
].copy()


# ============================================================
# ROUND NUMBERS
# ============================================================

numeric_columns = [

    "final_prediction_score",

    "model_probability",

    "historical_component",

    "historical_wins_component",

    "recent_3_year_component",

    "win_performance_component",

    "latest_component",

    "team_strength_component",

    "batting_component",

    "bowling_component",

    "consistency_component",

    "title_bonus"
]


for column in numeric_columns:

    output[column] = (
        output[column]
        .round(2)
    )


# ============================================================
# SAVE FINAL PREDICTION
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

os.makedirs(
    os.path.dirname(SUMMARY_FILE),
    exist_ok=True
)


output.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY FILE
# ============================================================

summary = output[
    [
        "prediction_position",
        "team",
        "historical_wins",
        "wins_2026",
        "historical_titles",
        "final_prediction_score",
        "model_probability",
        "key_factors"
    ]
].copy()


summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# PRINT FINAL PREDICTION
# ============================================================

print()
print("=" * 75)
print("                  IPL 2027 FINAL PREDICTION")
print("=" * 75)

print()

display_columns = [

    "prediction_position",

    "team",

    "historical_wins",

    "wins_2026",

    "historical_titles",

    "final_prediction_score",

    "model_probability"
]


print(
    output[
        display_columns
    ].to_string(
        index=False
    )
)


# ============================================================
# WIN HISTORY CHECK
# ============================================================

print()
print("=" * 75)
print("                 TEAM WIN HISTORY CHECK")
print("=" * 75)

win_check = output[
    [
        "team",
        "historical_wins",
        "wins_2026",
        "historical_titles"
    ]
].sort_values(
    "historical_wins",
    ascending=False
)


print(
    win_check.to_string(
        index=False
    )
)


# ============================================================
# TITLE CHECK
# ============================================================

print()
print("=" * 75)
print("                 HISTORICAL IPL TITLE CHECK")
print("=" * 75)

title_check = output[
    [
        "team",
        "historical_titles"
    ]
].sort_values(
    "historical_titles",
    ascending=False
)


print(
    title_check.to_string(
        index=False
    )
)


# ============================================================
# CSK CHECK
# ============================================================

print()
print("=" * 75)
print("CSK VALIDATION")
print("=" * 75)

csk_row = output[
    output["team"]
    == "Chennai Super Kings"
]


if len(csk_row) > 0:

    csk = csk_row.iloc[0]

    print(
        "CSK historical wins :",
        int(csk["historical_wins"])
    )

    print(
        "CSK 2026 wins       :",
        int(csk["wins_2026"])
    )

    print(
        "CSK historical titles:",
        int(csk["historical_titles"])
    )

    print(
        "CSK prediction score:",
        csk["final_prediction_score"]
    )

    print(
        "CSK model probability:",
        csk["model_probability"]
    )


# ============================================================
# IMPORTANT NOTE
# ============================================================

print()
print("=" * 75)
print("                         IMPORTANT")
print("=" * 75)

print(
    "Model probability is a relative probability "
    "within the 10 current IPL teams."
)

print(
    "It is NOT a guaranteed IPL 2027 winning probability."
)

print(
    "Historical wins, recent form, 2026 performance, "
    "team strength, batting, bowling, consistency "
    "and title history are used."
)


# ============================================================
# FILES
# ============================================================

print()
print("=" * 75)
print("                       FILES CREATED")
print("=" * 75)

print(
    "1.",
    OUTPUT_FILE
)

print(
    "2.",
    SUMMARY_FILE
)


# ============================================================
# COMPLETED
# ============================================================

print()
print("=" * 75)
print("          IPL 2027 PREDICTION COMPLETED SUCCESSFULLY")
print("=" * 75)
print()