# ============================================================
# IPL TEAM MATCH-UP PREDICTOR
# IPL 2008-2026 HISTORY
# IPL 2027 MATCH-UP ANALYSIS
# ============================================================

from pathlib import Path
from itertools import combinations
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_PREDICTIONS = BASE_DIR / "outputs" / "predictions"
OUTPUT_REPORTS = BASE_DIR / "outputs" / "reports"

OUTPUT_PREDICTIONS.mkdir(parents=True, exist_ok=True)
OUTPUT_REPORTS.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

START_YEAR = 2008
END_YEAR = 2026
H2H_START_YEAR = 2024
H2H_END_YEAR = 2026
PREDICTION_YEAR = 2027


# ============================================================
# CURRENT IPL 10 TEAMS
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

def normalize_team(team):

    if pd.isna(team):
        return None

    value = str(team).strip().lower()

    # Remove unnecessary spaces
    value = " ".join(value.split())

    # --------------------------------------------------------
    # Chennai Super Kings
    # --------------------------------------------------------
    if (
        "chennai super kings" in value
        or value == "csk"
    ):
        return "Chennai Super Kings"

    # --------------------------------------------------------
    # Delhi Capitals
    # --------------------------------------------------------
    if (
        "delhi capitals" in value
        or "delhi daredevils" in value
        or value == "dc"
    ):
        return "Delhi Capitals"

    # --------------------------------------------------------
    # Gujarat Titans
    # --------------------------------------------------------
    if (
        "gujarat titans" in value
        or value == "gt"
    ):
        return "Gujarat Titans"

    # --------------------------------------------------------
    # Kolkata Knight Riders
    # --------------------------------------------------------
    if (
        "kolkata knight riders" in value
        or value == "kkr"
    ):
        return "Kolkata Knight Riders"

    # --------------------------------------------------------
    # Lucknow Super Giants
    # --------------------------------------------------------
    if (
        "lucknow super giants" in value
        or value == "lsg"
    ):
        return "Lucknow Super Giants"

    # --------------------------------------------------------
    # Mumbai Indians
    # --------------------------------------------------------
    if (
        "mumbai indians" in value
        or value == "mi"
    ):
        return "Mumbai Indians"

    # --------------------------------------------------------
    # Punjab Kings
    # --------------------------------------------------------
    if (
        "punjab kings" in value
        or "kings xi punjab" in value
        or value == "pbks"
    ):
        return "Punjab Kings"

    # --------------------------------------------------------
    # Rajasthan Royals
    # --------------------------------------------------------
    if (
        "rajasthan royals" in value
        or value == "rr"
    ):
        return "Rajasthan Royals"

    # --------------------------------------------------------
    # Royal Challengers Bengaluru
    # --------------------------------------------------------
    if (
        "royal challengers bengaluru" in value
        or "royal challengers bangalore" in value
        or value == "rcb"
    ):
        return "Royal Challengers Bengaluru"

    # --------------------------------------------------------
    # Sunrisers Hyderabad
    # --------------------------------------------------------
    if (
        "sunrisers hyderabad" in value
        or value == "srh"
    ):
        return "Sunrisers Hyderabad"

    return str(team).strip()


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

def normalize_columns(df):

    df = df.copy()

    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    rename_map = {}

    for col in df.columns:

        clean = col.replace("-", "_")

        if clean in ["team_1", "team1", "team_a"]:
            rename_map[col] = "team1"

        elif clean in ["team_2", "team2", "team_b"]:
            rename_map[col] = "team2"

        elif clean in ["winner", "winning_team", "match_winner"]:
            rename_map[col] = "winner"

        elif clean in ["season", "year"]:
            rename_map[col] = "season"

        elif clean in ["match_id", "id", "matchid"]:
            rename_map[col] = "match_id"

    df = df.rename(columns=rename_map)

    return df


# ============================================================
# FIND SEASON FROM FILE NAME
# ============================================================

def get_year_from_filename(filename):

    name = filename.lower()

    for year in range(START_YEAR, END_YEAR + 1):

        if str(year) in name:
            return year

    return None


# ============================================================
# LOAD IPL MATCH FILES
# ============================================================

def load_match_data():

    print("\n[1] Searching match CSV files...")

    all_data = []

    # --------------------------------------------------------
    # Search processed folder first
    # --------------------------------------------------------

    processed_files = sorted(
        PROCESSED_DIR.glob("ipl_matches_*.csv")
    )

    # --------------------------------------------------------
    # If not found, search raw folder
    # --------------------------------------------------------

    raw_files = sorted(
        RAW_DIR.glob("ipl_matches_*.csv")
    )

    files = processed_files + [
        f for f in raw_files
        if f not in processed_files
    ]

    # --------------------------------------------------------
    # Remove duplicates by filename
    # --------------------------------------------------------

    unique_files = {}

    for file in files:
        unique_files[file.name] = file

    files = sorted(unique_files.values())

    if not files:
        raise FileNotFoundError(
            "No yearly IPL match CSV files found."
        )

    print(
        f"[OK] Match files found: {len(files)}"
    )

    for file in files:

        year = get_year_from_filename(file.name)

        if year is None:
            continue

        try:

            df = pd.read_csv(file)

            df = normalize_columns(df)

            if "season" not in df.columns:
                df["season"] = year

            else:
                df["season"] = pd.to_numeric(
                    df["season"],
                    errors="coerce"
                )

                df["season"] = df["season"].fillna(year)

            required = [
                "team1",
                "team2",
                "winner"
            ]

            missing = [
                col
                for col in required
                if col not in df.columns
            ]

            if missing:

                print(
                    f"[WARNING] {file.name} missing columns: "
                    f"{missing}"
                )

                continue

            df["team1"] = df["team1"].apply(
                normalize_team
            )

            df["team2"] = df["team2"].apply(
                normalize_team
            )

            df["winner"] = df["winner"].apply(
                normalize_team
            )

            df["season"] = pd.to_numeric(
                df["season"],
                errors="coerce"
            )

            df = df[
                (df["season"] >= START_YEAR)
                & (df["season"] <= END_YEAR)
            ].copy()

            if "match_id" not in df.columns:

                df["match_id"] = (
                    df["season"].astype(str)
                    + "_"
                    + df.index.astype(str)
                )

            df["source_file"] = file.name

            all_data.append(df)

            print(
                f"[LOADED] {file.name} "
                f"-> {len(df)} matches"
            )

        except Exception as error:

            print(
                f"[WARNING] Could not load "
                f"{file.name}: {error}"
            )

    if not all_data:

        raise RuntimeError(
            "No IPL match data could be loaded."
        )

    matches = pd.concat(
        all_data,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Remove duplicate matches
    # --------------------------------------------------------

    matches = matches.drop_duplicates(
        subset=["match_id"]
    ).copy()

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    matches = matches[
        matches["team1"].notna()
        & matches["team2"].notna()
    ].copy()

    matches = matches[
        matches["team1"] != matches["team2"]
    ].copy()

    matches = matches.reset_index(drop=True)

    print(
        f"\n[OK] Total match records loaded: "
        f"{len(matches)}"
    )

    return matches


# ============================================================
# CALCULATE HEAD-TO-HEAD
# ============================================================

def calculate_h2h(matches):

    print(
        "\n[2] Calculating Head-to-Head records..."
    )

    recent = matches[
        (matches["season"] >= H2H_START_YEAR)
        & (matches["season"] <= H2H_END_YEAR)
    ].copy()

    # --------------------------------------------------------
    # ONLY CURRENT IPL TEAMS
    # --------------------------------------------------------

    recent = recent[
        recent["team1"].isin(CURRENT_TEAMS)
        & recent["team2"].isin(CURRENT_TEAMS)
    ].copy()

    print(
        f"Period: {H2H_START_YEAR}-{H2H_END_YEAR}"
    )

    print(
        f"[OK] Recent matches available: "
        f"{len(recent)}"
    )

    records = []

    # --------------------------------------------------------
    # All team combinations
    # --------------------------------------------------------

    for team_a, team_b in combinations(
        CURRENT_TEAMS,
        2
    ):

        team_a_wins = 0
        team_b_wins = 0
        total_matches = 0

        # ----------------------------------------------------
        # Team A vs Team B
        # ----------------------------------------------------

        mask_1 = (
            (recent["team1"] == team_a)
            & (recent["team2"] == team_b)
        )

        games_1 = recent[mask_1]

        # ----------------------------------------------------
        # Team B vs Team A
        # ----------------------------------------------------

        mask_2 = (
            (recent["team1"] == team_b)
            & (recent["team2"] == team_a)
        )

        games_2 = recent[mask_2]

        total_matches = (
            len(games_1)
            + len(games_2)
        )

        # ----------------------------------------------------
        # Count wins
        # ----------------------------------------------------

        if len(games_1) > 0:

            team_a_wins += (
                games_1["winner"]
                .eq(team_a)
                .sum()
            )

            team_b_wins += (
                games_1["winner"]
                .eq(team_b)
                .sum()
            )

        if len(games_2) > 0:

            team_a_wins += (
                games_2["winner"]
                .eq(team_a)
                .sum()
            )

            team_b_wins += (
                games_2["winner"]
                .eq(team_b)
                .sum()
            )

        # ----------------------------------------------------
        # Percentages
        # ----------------------------------------------------

        if total_matches > 0:

            team_a_pct = (
                team_a_wins
                / total_matches
                * 100
            )

            team_b_pct = (
                team_b_wins
                / total_matches
                * 100
            )

        else:

            team_a_pct = 50.0
            team_b_pct = 50.0

        # ----------------------------------------------------
        # Predicted side
        # ----------------------------------------------------

        if team_a_pct > team_b_pct:

            predicted_team = team_a

        elif team_b_pct > team_a_pct:

            predicted_team = team_b

        else:

            predicted_team = "Balanced"

        records.append({

            "team_a": team_a,

            "team_b": team_b,

            "matches_2024_2026": total_matches,

            "team_a_h2h_wins": int(team_a_wins),

            "team_b_h2h_wins": int(team_b_wins),

            "team_a_h2h_pct": round(
                team_a_pct,
                2
            ),

            "team_b_h2h_pct": round(
                team_b_pct,
                2
            ),

            "h2h_predicted_team":
                predicted_team
        })

    h2h = pd.DataFrame(records)

    return h2h


# ============================================================
# LOAD TEAM STRENGTH
# ============================================================

def load_team_strength():

    print(
        "\n[3] Loading 2027 team strength features..."
    )

    file = (
        PROCESSED_DIR
        / "team_strength_features_2027.csv"
    )

    if not file.exists():

        print(
            "[WARNING] Team strength file not found."
        )

        return pd.DataFrame({
            "team": CURRENT_TEAMS,
            "strength_score": [
                50.0
                for _ in CURRENT_TEAMS
            ]
        })

    df = pd.read_csv(file)

    df = normalize_columns(df)

    # --------------------------------------------------------
    # Detect team column
    # --------------------------------------------------------

    team_column = None

    for col in [
        "team",
        "team_name",
        "current_team"
    ]:

        if col in df.columns:

            team_column = col
            break

    if team_column is None:

        raise ValueError(
            "Team column not found in "
            "team_strength_features_2027.csv"
        )

    df["team"] = df[
        team_column
    ].apply(normalize_team)

    # --------------------------------------------------------
    # Find best available strength column
    # --------------------------------------------------------

    strength_candidates = [

        "composite_strength",

        "team_strength",

        "strength_score",

        "weighted_recent_win_pct",

        "recent_weighted_win_pct",

        "recent_form",

        "historical_win_pct"
    ]

    strength_column = None

    for col in strength_candidates:

        if col in df.columns:

            strength_column = col
            break

    # --------------------------------------------------------
    # If no strength column exists,
    # calculate from numeric columns
    # --------------------------------------------------------

    if strength_column is None:

        numeric_columns = df.select_dtypes(
            include=np.number
        ).columns.tolist()

        numeric_columns = [
            col
            for col in numeric_columns
            if col not in [
                "season",
                "year"
            ]
        ]

        if numeric_columns:

            df["strength_score"] = (
                df[numeric_columns]
                .mean(axis=1)
            )

        else:

            df["strength_score"] = 50.0

    else:

        df["strength_score"] = pd.to_numeric(
            df[strength_column],
            errors="coerce"
        )

    df["strength_score"] = (
        df["strength_score"]
        .fillna(
            df["strength_score"].median()
        )
    )

    # --------------------------------------------------------
    # Keep only current teams
    # --------------------------------------------------------

    df = df[
        df["team"].isin(CURRENT_TEAMS)
    ].copy()

    # --------------------------------------------------------
    # One row per team
    # --------------------------------------------------------

    df = (
        df.groupby("team", as_index=False)
        ["strength_score"]
        .mean()
    )

    # --------------------------------------------------------
    # Make sure all 10 teams exist
    # --------------------------------------------------------

    missing_teams = [
        team
        for team in CURRENT_TEAMS
        if team not in df["team"].values
    ]

    if missing_teams:

        fallback = (
            df["strength_score"].mean()
            if len(df) > 0
            else 50.0
        )

        missing_df = pd.DataFrame({

            "team": missing_teams,

            "strength_score": [
                fallback
                for _ in missing_teams
            ]
        })

        df = pd.concat(
            [df, missing_df],
            ignore_index=True
        )

    print(
        f"[OK] Team strength records: "
        f"{len(df)}"
    )

    return df


# ============================================================
# NORMALIZE STRENGTH TO 0-100
# ============================================================

def normalize_strength(df):

    df = df.copy()

    minimum = df["strength_score"].min()
    maximum = df["strength_score"].max()

    if maximum == minimum:

        df["strength_normalized"] = 50.0

    else:

        df["strength_normalized"] = (
            (
                df["strength_score"]
                - minimum
            )
            /
            (
                maximum
                - minimum
            )
            * 100
        )

    return df


# ============================================================
# CREATE MATCH-UP PREDICTIONS
# ============================================================

def create_matchup_predictions(
    h2h,
    strength
):

    print(
        "\n[4] Creating 2027 match-up predictions..."
    )

    strength = normalize_strength(
        strength
    )

    strength_map = dict(
        zip(
            strength["team"],
            strength["strength_normalized"]
        )
    )

    records = []

    # --------------------------------------------------------
    # All 45 combinations
    # --------------------------------------------------------

    for team_a, team_b in combinations(
        CURRENT_TEAMS,
        2
    ):

        # ----------------------------------------------------
        # Find H2H record
        # ----------------------------------------------------

        row = h2h[
            (h2h["team_a"] == team_a)
            & (h2h["team_b"] == team_b)
        ]

        if row.empty:

            row = h2h[
                (h2h["team_a"] == team_b)
                & (h2h["team_b"] == team_a)
            ]

            if not row.empty:

                h2h_a_pct = float(
                    row.iloc[0]["team_b_h2h_pct"]
                )

                h2h_b_pct = float(
                    row.iloc[0]["team_a_h2h_pct"]
                )

                matches = int(
                    row.iloc[0][
                        "matches_2024_2026"
                    ]
                )

                a_wins = int(
                    row.iloc[0][
                        "team_b_h2h_wins"
                    ]
                )

                b_wins = int(
                    row.iloc[0][
                        "team_a_h2h_wins"
                    ]
                )

            else:

                h2h_a_pct = 50.0
                h2h_b_pct = 50.0

                matches = 0
                a_wins = 0
                b_wins = 0

        else:

            h2h_a_pct = float(
                row.iloc[0]["team_a_h2h_pct"]
            )

            h2h_b_pct = float(
                row.iloc[0]["team_b_h2h_pct"]
            )

            matches = int(
                row.iloc[0][
                    "matches_2024_2026"
                ]
            )

            a_wins = int(
                row.iloc[0][
                    "team_a_h2h_wins"
                ]
            )

            b_wins = int(
                row.iloc[0][
                    "team_b_h2h_wins"
                ]
            )

        # ----------------------------------------------------
        # Team strength
        # ----------------------------------------------------

        strength_a = float(
            strength_map.get(
                team_a,
                50.0
            )
        )

        strength_b = float(
            strength_map.get(
                team_b,
                50.0
            )
        )

        # ----------------------------------------------------
        # Combined prediction
        #
        # H2H = 55%
        # Team strength = 45%
        # ----------------------------------------------------

        team_a_prediction = (
            h2h_a_pct * 0.55
            + strength_a * 0.45
        )

        team_b_prediction = (
            h2h_b_pct * 0.55
            + strength_b * 0.45
        )

        # ----------------------------------------------------
        # Convert to percentage
        # ----------------------------------------------------

        total = (
            team_a_prediction
            + team_b_prediction
        )

        if total > 0:

            team_a_final = (
                team_a_prediction
                / total
                * 100
            )

            team_b_final = (
                team_b_prediction
                / total
                * 100
            )

        else:

            team_a_final = 50.0
            team_b_final = 50.0

        # ----------------------------------------------------
        # Predicted team
        # ----------------------------------------------------

        if team_a_final > team_b_final:

            predicted_team = team_a

        elif team_b_final > team_a_final:

            predicted_team = team_b

        else:

            predicted_team = "Balanced"

        # ----------------------------------------------------
        # Confidence difference
        # ----------------------------------------------------

        confidence = abs(
            team_a_final
            - team_b_final
        )

        records.append({

            "team_a": team_a,

            "team_b": team_b,

            "matches_2024_2026":
                matches,

            "team_a_h2h_wins":
                a_wins,

            "team_b_h2h_wins":
                b_wins,

            "team_a_h2h_pct":
                round(
                    h2h_a_pct,
                    2
                ),

            "team_b_h2h_pct":
                round(
                    h2h_b_pct,
                    2
                ),

            "team_a_strength":
                round(
                    strength_a,
                    2
                ),

            "team_b_strength":
                round(
                    strength_b,
                    2
                ),

            "team_a_prediction_pct":
                round(
                    team_a_final,
                    2
                ),

            "team_b_prediction_pct":
                round(
                    team_b_final,
                    2
                ),

            "predicted_team":
                predicted_team,

            "prediction_confidence":
                round(
                    confidence,
                    2
                )
        })

    return pd.DataFrame(records)


# ============================================================
# CREATE 10 x 10 MATCH-UP MATRIX
# ============================================================

def create_matchup_matrix(predictions):

    print(
        "\n[5] Creating 10-team match-up matrix..."
    )

    matrix = pd.DataFrame(
        index=CURRENT_TEAMS,
        columns=CURRENT_TEAMS,
        dtype=float
    )

    # Same team
    for team in CURRENT_TEAMS:
        matrix.loc[team, team] = 50.0

    # --------------------------------------------------------
    # Fill matrix
    # --------------------------------------------------------

    for _, row in predictions.iterrows():

        team_a = row["team_a"]
        team_b = row["team_b"]

        a_pct = row[
            "team_a_prediction_pct"
        ]

        b_pct = row[
            "team_b_prediction_pct"
        ]

        matrix.loc[
            team_a,
            team_b
        ] = a_pct

        matrix.loc[
            team_b,
            team_a
        ] = b_pct

    matrix = matrix.round(2)

    return matrix


# ============================================================
# SAVE RESULTS
# ============================================================

def save_outputs(
    h2h,
    predictions,
    matrix
):

    print(
        "\n[6] Saving match-up reports..."
    )

    # --------------------------------------------------------
    # H2H processed file
    # --------------------------------------------------------

    h2h_file = (
        PROCESSED_DIR
        / "head_to_head_2024_2026.csv"
    )

    h2h.to_csv(
        h2h_file,
        index=False
    )

    # --------------------------------------------------------
    # Prediction file
    # --------------------------------------------------------

    prediction_file = (
        OUTPUT_PREDICTIONS
        / "ipl_2027_matchup_predictions.csv"
    )

    predictions.to_csv(
        prediction_file,
        index=False
    )

    # --------------------------------------------------------
    # Matrix
    # --------------------------------------------------------

    matrix_file = (
        OUTPUT_PREDICTIONS
        / "ipl_2027_matchup_matrix.csv"
    )

    matrix.to_csv(
        matrix_file
    )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    report_file = (
        OUTPUT_REPORTS
        / "ipl_2027_matchup_report.csv"
    )

    predictions.to_csv(
        report_file,
        index=False
    )

    print("\nFILES CREATED")

    print(
        f"1. {h2h_file}"
    )

    print(
        f"2. {prediction_file}"
    )

    print(
        f"3. {matrix_file}"
    )

    print(
        f"4. {report_file}"
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    predictions,
    matrix
):

    print(
        "\n"
        + "=" * 95
    )

    print(
        "IPL 2027 TEAM MATCH-UP PREDICTIONS"
    )

    print(
        "=" * 95
    )

    display_columns = [

        "team_a",

        "team_b",

        "matches_2024_2026",

        "team_a_h2h_wins",

        "team_b_h2h_wins",

        "team_a_prediction_pct",

        "team_b_prediction_pct",

        "predicted_team"
    ]

    print(
        predictions[
            display_columns
        ].to_string(index=False)
    )

    print(
        "\n"
        + "=" * 95
    )

    print(
        "IPL 2027 MATCH-UP MATRIX"
    )

    print(
        "=" * 95
    )

    print(
        matrix.to_string()
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print(
        "\n"
        + "=" * 65
    )

    print(
        "IPL TEAM MATCH-UP PREDICTOR"
    )

    print(
        "=" * 65
    )

    print(
        f"Historical data : "
        f"{START_YEAR}-{END_YEAR}"
    )

    print(
        f"H2H analysis    : "
        f"{H2H_START_YEAR}-{H2H_END_YEAR}"
    )

    print(
        f"Prediction year : "
        f"{PREDICTION_YEAR}"
    )

    print(
        "=" * 65
    )

    try:

        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------

        matches = load_match_data()

        # ----------------------------------------------------
        # STEP 2
        # ----------------------------------------------------

        h2h = calculate_h2h(
            matches
        )

        # ----------------------------------------------------
        # STEP 3
        # ----------------------------------------------------

        strength = load_team_strength()

        # ----------------------------------------------------
        # STEP 4
        # ----------------------------------------------------

        predictions = create_matchup_predictions(
            h2h,
            strength
        )

        # ----------------------------------------------------
        # STEP 5
        # ----------------------------------------------------

        matrix = create_matchup_matrix(
            predictions
        )

        # ----------------------------------------------------
        # STEP 6
        # ----------------------------------------------------

        save_outputs(
            h2h,
            predictions,
            matrix
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        display_results(
            predictions,
            matrix
        )

        print(
            "\n"
            + "=" * 65
        )

        print(
            "IPL MATCH-UP PREDICTION "
            "COMPLETED SUCCESSFULLY"
        )

        print(
            "=" * 65
        )

    except Exception as error:

        print(
            "\n[ERROR]"
        )

        print(
            str(error)
        )

        print(
            "\nPlease check the project data files."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()