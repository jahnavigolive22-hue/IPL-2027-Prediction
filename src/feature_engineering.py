from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs" / "predictions"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CURRENT IPL TEAMS - 2027
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
        "Punjab Kings",

    "Pune Warriors":
        "Pune Warriors India",

    "Pune Warriors India":
        "Pune Warriors India",

    "Rising Pune Supergiant":
        "Rising Pune Supergiants",

    "Rising Pune Supergiants":
        "Rising Pune Supergiants",
}


def normalize_team(team):

    if pd.isna(team):
        return ""

    team = str(team).strip()

    return TEAM_ALIASES.get(team, team)


# ============================================================
# SAFE NUMBER
# ============================================================

def to_number(value):

    try:
        return float(value)
    except:
        return 0.0


# ============================================================
# WIN PERCENTAGE
# ============================================================

def win_percentage(wins, losses):

    total = wins + losses

    if total <= 0:
        return 0.0

    return (wins / total) * 100


# ============================================================
# LOAD TEAM SEASON DATA
# ============================================================

def load_team_season_data():

    file_path = (
        PROCESSED_DIR
        / "team_season_analysis.csv"
    )

    if not file_path.exists():

        raise FileNotFoundError(
            "\nteam_season_analysis.csv not found.\n"
            "First run:\n"
            "python src\\team_analysis.py"
        )

    df = pd.read_csv(file_path)

    print(
        f"Team-season records loaded: {len(df)}"
    )

    return df


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(df):

    df = df.copy()

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "team",
        "season",
        "matches",
        "wins",
        "losses",
    ]

    for column in required_columns:

        if column not in df.columns:

            if column == "team":
                raise ValueError(
                    "Column 'team' missing from team_season_analysis.csv"
                )

            if column == "season":
                raise ValueError(
                    "Column 'season' missing from team_season_analysis.csv"
                )

            df[column] = 0

    # --------------------------------------------------------
    # Optional columns
    # --------------------------------------------------------

    optional_columns = [
        "no_results_or_ties",
        "win_percentage",
        "runs_scored",
        "runs_conceded",
        "run_difference",
        "champion",
        "runner_up",
    ]

    for column in optional_columns:

        if column not in df.columns:
            df[column] = 0

    # --------------------------------------------------------
    # Team names
    # --------------------------------------------------------

    df["team"] = (
        df["team"]
        .apply(normalize_team)
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "season",
        "matches",
        "wins",
        "losses",
        "no_results_or_ties",
        "win_percentage",
        "runs_scored",
        "runs_conceded",
        "run_difference",
        "champion",
        "runner_up",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

    df["season"] = (
        df["season"]
        .astype(int)
    )

    # --------------------------------------------------------
    # Recalculate win percentage
    # --------------------------------------------------------

    df["win_percentage"] = np.where(
        (df["wins"] + df["losses"]) > 0,

        (
            df["wins"]
            /
            (
                df["wins"]
                + df["losses"]
            )
        ) * 100,

        0
    )

    # --------------------------------------------------------
    # Recalculate run difference
    # --------------------------------------------------------

    df["run_difference"] = (
        df["runs_scored"]
        -
        df["runs_conceded"]
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        ["team", "season"]
    ).reset_index(drop=True)

    return df


# ============================================================
# CREATE HISTORICAL TRAINING FEATURES
# ============================================================

def create_historical_features(df):

    records = []

    print()
    print("=" * 70)
    print("CREATING HISTORICAL FEATURES")
    print("=" * 70)

    for team in sorted(
        df["team"].unique()
    ):

        team_df = (
            df[df["team"] == team]
            .sort_values("season")
            .reset_index(drop=True)
        )

        for index, row in team_df.iterrows():

            current_season = int(
                row["season"]
            )

            # ------------------------------------------------
            # VERY IMPORTANT:
            # Only previous seasons.
            # Current season result is NOT used as feature.
            # ------------------------------------------------

            previous = team_df[
                team_df["season"]
                < current_season
            ]

            # ------------------------------------------------
            # Historical
            # ------------------------------------------------

            matches_before = (
                previous["matches"].sum()
            )

            wins_before = (
                previous["wins"].sum()
            )

            losses_before = (
                previous["losses"].sum()
            )

            historical_win_pct = win_percentage(
                wins_before,
                losses_before
            )

            run_difference_before = (
                previous["run_difference"].sum()
            )

            titles_before = (
                previous["champion"].sum()
            )

            runner_ups_before = (
                previous["runner_up"].sum()
            )

            # ------------------------------------------------
            # Last season
            # ------------------------------------------------

            if len(previous) >= 1:

                last = previous.iloc[-1]

                last_win_pct = to_number(
                    last["win_percentage"]
                )

                last_wins = to_number(
                    last["wins"]
                )

                last_losses = to_number(
                    last["losses"]
                )

                last_run_difference = to_number(
                    last["run_difference"]
                )

            else:

                last_win_pct = 0
                last_wins = 0
                last_losses = 0
                last_run_difference = 0

            # ------------------------------------------------
            # Last 3 seasons
            # ------------------------------------------------

            last3 = previous.tail(3)

            last3_wins = (
                last3["wins"].sum()
            )

            last3_losses = (
                last3["losses"].sum()
            )

            last3_win_pct = win_percentage(
                last3_wins,
                last3_losses
            )

            last3_run_difference = (
                last3["run_difference"].sum()
            )

            # ------------------------------------------------
            # Last 5 seasons
            # ------------------------------------------------

            last5 = previous.tail(5)

            last5_wins = (
                last5["wins"].sum()
            )

            last5_losses = (
                last5["losses"].sum()
            )

            last5_win_pct = win_percentage(
                last5_wins,
                last5_losses
            )

            # ------------------------------------------------
            # Consistency
            # ------------------------------------------------

            if len(previous) >= 2:

                standard_deviation = (
                    previous[
                        "win_percentage"
                    ].std()
                )

                if pd.isna(
                    standard_deviation
                ):
                    standard_deviation = 0

            else:

                standard_deviation = 0

            consistency_score = max(
                0,
                100 - standard_deviation
            )

            # ------------------------------------------------
            # Current season target
            # ------------------------------------------------

            champion_target = int(
                row["champion"]
            )

            runner_up_target = int(
                row["runner_up"]
            )

            # ------------------------------------------------
            # Record
            # ------------------------------------------------

            records.append({

                "season":
                    current_season,

                "team":
                    team,

                "seasons_before":
                    len(previous),

                "matches_before":
                    matches_before,

                "wins_before":
                    wins_before,

                "losses_before":
                    losses_before,

                "historical_win_percentage":
                    round(
                        historical_win_pct,
                        4
                    ),

                "historical_run_difference":
                    run_difference_before,

                "titles_before":
                    titles_before,

                "runner_ups_before":
                    runner_ups_before,

                "last_season_win_percentage":
                    last_win_pct,

                "last_season_wins":
                    last_wins,

                "last_season_losses":
                    last_losses,

                "last_season_run_difference":
                    last_run_difference,

                "last_3_win_percentage":
                    last3_win_pct,

                "last_3_wins":
                    last3_wins,

                "last_3_losses":
                    last3_losses,

                "last_3_run_difference":
                    last3_run_difference,

                "last_5_win_percentage":
                    last5_win_pct,

                "last_5_wins":
                    last5_wins,

                "last_5_losses":
                    last5_losses,

                "consistency_score":
                    consistency_score,

                # Target
                "champion":
                    champion_target,

                "runner_up":
                    runner_up_target,
            })

    result = pd.DataFrame(records)

    return result


# ============================================================
# CREATE 2024-2026 RECENT FORM
# ============================================================

def create_recent_form(df):

    rows = []

    for team in CURRENT_TEAMS:

        team_df = df[
            df["team"] == team
        ]

        row = {
            "team": team
        }

        percentages = []

        for season in [2024, 2025, 2026]:

            season_df = team_df[
                team_df["season"]
                == season
            ]

            if len(season_df) > 0:

                wins = (
                    season_df[
                        "wins"
                    ].sum()
                )

                losses = (
                    season_df[
                        "losses"
                    ].sum()
                )

                percentage = win_percentage(
                    wins,
                    losses
                )

            else:

                percentage = 0

            row[
                f"win_percentage_{season}"
            ] = round(
                percentage,
                4
            )

            percentages.append(
                percentage
            )

        # ----------------------------------------------------
        # More weight to latest season
        # ----------------------------------------------------

        row[
            "weighted_recent_form"
        ] = round(
            (
                percentages[0] * 0.20
                +
                percentages[1] * 0.30
                +
                percentages[2] * 0.50
            ),
            4
        )

        rows.append(row)

    return pd.DataFrame(rows)


# ============================================================
# CREATE 2026 FEATURES
# ============================================================

def create_2026_features(df):

    rows = []

    for team in CURRENT_TEAMS:

        team_df = df[
            (df["team"] == team)
            &
            (df["season"] == 2026)
        ]

        if len(team_df) > 0:

            row = team_df.iloc[0]

            matches = to_number(
                row["matches"]
            )

            wins = to_number(
                row["wins"]
            )

            losses = to_number(
                row["losses"]
            )

            win_pct = win_percentage(
                wins,
                losses
            )

            run_difference = to_number(
                row["run_difference"]
            )

        else:

            matches = 0
            wins = 0
            losses = 0
            win_pct = 0
            run_difference = 0

        rows.append({

            "team": team,

            "matches_2026":
                matches,

            "wins_2026":
                wins,

            "losses_2026":
                losses,

            "win_percentage_2026":
                round(
                    win_pct,
                    4
                ),

            "run_difference_2026":
                run_difference,
        })

    return pd.DataFrame(rows)


# ============================================================
# CREATE 2027 TEAM STRENGTH
# ============================================================

def create_2027_strength(
    df,
    recent_df,
    current_df
):

    rows = []

    for team in CURRENT_TEAMS:

        history = df[
            df["team"] == team
        ]

        # ----------------------------------------------------
        # Historical
        # ----------------------------------------------------

        historical_wins = (
            history["wins"].sum()
        )

        historical_losses = (
            history["losses"].sum()
        )

        historical_strength = (
            win_percentage(
                historical_wins,
                historical_losses
            )
        )

        # ----------------------------------------------------
        # Recent
        # ----------------------------------------------------

        recent_row = recent_df[
            recent_df["team"] == team
        ]

        if len(recent_row) > 0:

            recent_strength = to_number(
                recent_row.iloc[0][
                    "weighted_recent_form"
                ]
            )

        else:

            recent_strength = 0

        # ----------------------------------------------------
        # Latest
        # ----------------------------------------------------

        latest_row = current_df[
            current_df["team"] == team
        ]

        if len(latest_row) > 0:

            latest_strength = to_number(
                latest_row.iloc[0][
                    "win_percentage_2026"
                ]
            )

        else:

            latest_strength = 0

        # ----------------------------------------------------
        # Consistency
        # ----------------------------------------------------

        if len(history) >= 2:

            consistency_std = (
                history[
                    "win_percentage"
                ].std()
            )

            if pd.isna(
                consistency_std
            ):
                consistency_std = 0

        else:

            consistency_std = 0

        consistency_strength = max(
            0,
            100 - consistency_std
        )

        # ----------------------------------------------------
        # Run strength
        # ----------------------------------------------------

        if len(history) > 0:

            run_values = (
                history[
                    "run_difference"
                ]
            )

            mean_run = (
                run_values.mean()
            )

            run_strength = (
                50
                +
                (
                    mean_run / 100
                )
            )

            run_strength = max(
                0,
                min(
                    100,
                    run_strength
                )
            )

        else:

            run_strength = 0

        # ----------------------------------------------------
        # Final composite
        # ----------------------------------------------------

        team_strength_score = (
            historical_strength * 0.20
            +
            recent_strength * 0.30
            +
            latest_strength * 0.30
            +
            consistency_strength * 0.10
            +
            run_strength * 0.10
        )

        rows.append({

            "team": team,

            "historical_strength":
                round(
                    historical_strength,
                    4
                ),

            "recent_strength":
                round(
                    recent_strength,
                    4
                ),

            "latest_strength":
                round(
                    latest_strength,
                    4
                ),

            "consistency_strength":
                round(
                    consistency_strength,
                    4
                ),

            "run_strength":
                round(
                    run_strength,
                    4
                ),

            "team_strength_score":
                round(
                    team_strength_score,
                    4
                ),
        })

    return pd.DataFrame(rows)


# ============================================================
# CREATE 2027 PREDICTION INPUT
# ============================================================

def create_2027_prediction_input(
    df,
    recent_df,
    current_df,
    strength_df
):

    rows = []

    for team in CURRENT_TEAMS:

        history = df[
            df["team"] == team
        ].sort_values(
            "season"
        )

        # ----------------------------------------------------
        # Overall history
        # ----------------------------------------------------

        wins = (
            history["wins"].sum()
        )

        losses = (
            history["losses"].sum()
        )

        matches = (
            history["matches"].sum()
        )

        historical_win_pct = (
            win_percentage(
                wins,
                losses
            )
        )

        historical_run_difference = (
            history[
                "run_difference"
            ].sum()
        )

        titles = (
            history[
                "champion"
            ].sum()
        )

        runner_ups = (
            history[
                "runner_up"
            ].sum()
        )

        # ----------------------------------------------------
        # Last 3
        # ----------------------------------------------------

        last3 = history.tail(3)

        last3_win_pct = win_percentage(
            last3["wins"].sum(),
            last3["losses"].sum()
        )

        # ----------------------------------------------------
        # Last 5
        # ----------------------------------------------------

        last5 = history.tail(5)

        last5_win_pct = win_percentage(
            last5["wins"].sum(),
            last5["losses"].sum()
        )

        # ----------------------------------------------------
        # Recent
        # ----------------------------------------------------

        recent_row = recent_df[
            recent_df["team"] == team
        ]

        if len(recent_row) > 0:

            recent = recent_row.iloc[0]

            win_2024 = to_number(
                recent[
                    "win_percentage_2024"
                ]
            )

            win_2025 = to_number(
                recent[
                    "win_percentage_2025"
                ]
            )

            win_2026 = to_number(
                recent[
                    "win_percentage_2026"
                ]
            )

            weighted_recent = to_number(
                recent[
                    "weighted_recent_form"
                ]
            )

        else:

            win_2024 = 0
            win_2025 = 0
            win_2026 = 0
            weighted_recent = 0

        # ----------------------------------------------------
        # 2026
        # ----------------------------------------------------

        current_row = current_df[
            current_df["team"] == team
        ]

        if len(current_row) > 0:

            current = current_row.iloc[0]

            matches_2026 = to_number(
                current[
                    "matches_2026"
                ]
            )

            wins_2026 = to_number(
                current[
                    "wins_2026"
                ]
            )

            losses_2026 = to_number(
                current[
                    "losses_2026"
                ]
            )

            run_difference_2026 = to_number(
                current[
                    "run_difference_2026"
                ]
            )

        else:

            matches_2026 = 0
            wins_2026 = 0
            losses_2026 = 0
            run_difference_2026 = 0

        # ----------------------------------------------------
        # Strength
        # ----------------------------------------------------

        strength_row = strength_df[
            strength_df["team"] == team
        ]

        if len(strength_row) > 0:

            strength = strength_row.iloc[0]

            historical_strength = to_number(
                strength[
                    "historical_strength"
                ]
            )

            recent_strength = to_number(
                strength[
                    "recent_strength"
                ]
            )

            latest_strength = to_number(
                strength[
                    "latest_strength"
                ]
            )

            consistency_strength = to_number(
                strength[
                    "consistency_strength"
                ]
            )

            run_strength = to_number(
                strength[
                    "run_strength"
                ]
            )

            team_strength_score = to_number(
                strength[
                    "team_strength_score"
                ]
            )

        else:

            historical_strength = 0
            recent_strength = 0
            latest_strength = 0
            consistency_strength = 0
            run_strength = 0
            team_strength_score = 0

        # ----------------------------------------------------
        # Final row
        # ----------------------------------------------------

        rows.append({

            "prediction_season":
                2027,

            "team":
                team,

            "matches_2008_2026":
                matches,

            "wins_2008_2026":
                wins,

            "losses_2008_2026":
                losses,

            "historical_win_percentage":
                round(
                    historical_win_pct,
                    4
                ),

            "historical_run_difference":
                historical_run_difference,

            "titles_before_2027":
                titles,

            "runner_ups_before_2027":
                runner_ups,

            "last_3_win_percentage":
                round(
                    last3_win_pct,
                    4
                ),

            "last_5_win_percentage":
                round(
                    last5_win_pct,
                    4
                ),

            "win_percentage_2024":
                win_2024,

            "win_percentage_2025":
                win_2025,

            "win_percentage_2026":
                win_2026,

            "weighted_recent_form":
                weighted_recent,

            "matches_2026":
                matches_2026,

            "wins_2026":
                wins_2026,

            "losses_2026":
                losses_2026,

            "run_difference_2026":
                run_difference_2026,

            "historical_strength":
                historical_strength,

            "recent_strength":
                recent_strength,

            "latest_strength":
                latest_strength,

            "consistency_strength":
                consistency_strength,

            "run_strength":
                run_strength,

            "team_strength_score":
                team_strength_score,

            "current_team":
                1,
        })

    return pd.DataFrame(rows)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("IPL FEATURE ENGINEERING - FINAL")
    print("=" * 70)

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_team_season_data()

    # --------------------------------------------------------
    # CLEAN
    # --------------------------------------------------------

    df = clean_data(df)

    print(
        f"Clean records: {len(df)}"
    )

    print(
        f"Seasons: {df['season'].min()} - {df['season'].max()}"
    )

    # --------------------------------------------------------
    # HISTORICAL FEATURES
    # --------------------------------------------------------

    historical_features = (
        create_historical_features(df)
    )

    # --------------------------------------------------------
    # RECENT FORM
    # --------------------------------------------------------

    recent_df = create_recent_form(df)

    # --------------------------------------------------------
    # 2026 FEATURES
    # --------------------------------------------------------

    current_df = create_2026_features(df)

    # --------------------------------------------------------
    # 2027 STRENGTH
    # --------------------------------------------------------

    strength_df = create_2027_strength(
        df,
        recent_df,
        current_df
    )

    # --------------------------------------------------------
    # 2027 INPUT
    # --------------------------------------------------------

    prediction_df = (
        create_2027_prediction_input(
            df,
            recent_df,
            current_df,
            strength_df
        )
    )

    # ========================================================
    # SAVE
    # ========================================================

    historical_path = (
        PROCESSED_DIR
        / "team_season_features.csv"
    )

    recent_path = (
        PROCESSED_DIR
        / "team_recent_form_2024_2026.csv"
    )

    current_path = (
        PROCESSED_DIR
        / "current_team_features_2026.csv"
    )

    strength_path = (
        PROCESSED_DIR
        / "team_strength_features_2027.csv"
    )

    prediction_path = (
        OUTPUT_DIR
        / "ipl_2027_prediction_input.csv"
    )

    historical_features.to_csv(
        historical_path,
        index=False
    )

    recent_df.to_csv(
        recent_path,
        index=False
    )

    current_df.to_csv(
        current_path,
        index=False
    )

    strength_df.to_csv(
        strength_path,
        index=False
    )

    prediction_df.to_csv(
        prediction_path,
        index=False
    )

    # ========================================================
    # VALIDATION
    # ========================================================

    print()
    print("=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(
        "Historical feature records:",
        len(historical_features)
    )

    print(
        "2027 prediction records:",
        len(prediction_df)
    )

    print(
        "2027 teams:",
        prediction_df["team"].nunique()
    )

    missing = [
        team
        for team in CURRENT_TEAMS
        if team not in
        prediction_df["team"].tolist()
    ]

    if len(missing) == 0:

        print(
            "Current 10 IPL teams: PASS"
        )

    else:

        print(
            "Missing teams:",
            missing
        )

    duplicates = (
        prediction_df[
            "team"
        ]
        .duplicated()
        .sum()
    )

    print(
        "Duplicate teams:",
        duplicates
    )

    wrong_year = (
        prediction_df[
            "prediction_season"
        ]
        != 2027
    ).sum()

    print(
        "Wrong prediction year:",
        wrong_year
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print()
    print("=" * 70)
    print("IPL 2027 FEATURE SUMMARY")
    print("=" * 70)

    display_columns = [
        "team",
        "historical_win_percentage",
        "last_3_win_percentage",
        "win_percentage_2024",
        "win_percentage_2025",
        "win_percentage_2026",
        "weighted_recent_form",
        "team_strength_score",
    ]

    print(
        prediction_df[
            display_columns
        ]
        .sort_values(
            "team_strength_score",
            ascending=False
        )
        .to_string(index=False)
    )

    # ========================================================
    # FILES
    # ========================================================

    print()
    print("=" * 70)
    print("FILES CREATED")
    print("=" * 70)

    print(historical_path)
    print(recent_path)
    print(current_path)
    print(strength_path)
    print(prediction_path)

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 70)
    print("STEP 5 COMPLETED SUCCESSFULLY")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()