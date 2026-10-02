"""
IPL 2008-2026 Master Data Cleaning
----------------------------------
Reads yearly IPL match CSV files from data/raw/
and creates one clean master match dataset.

Input:
    data/raw/ipl_matches_2008.csv
    ...
    data/raw/ipl_matches_2026.csv

Output:
    data/processed/ipl_matches_clean_2008_2026.csv
"""

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# 1. PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. IPL TEAM NAME STANDARDIZATION
# ============================================================

TEAM_ALIASES = {
    # Royal Challengers
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Royal Challengers Bengaluru": "Royal Challengers Bengaluru",
    "RCB": "Royal Challengers Bengaluru",

    # Delhi
    "Delhi Daredevils": "Delhi Capitals",
    "Delhi Capitals": "Delhi Capitals",

    # Punjab
    "Kings XI Punjab": "Punjab Kings",
    "Punjab Kings": "Punjab Kings",

    # Rajasthan
    "Rajasthan Royals": "Rajasthan Royals",

    # Mumbai
    "Mumbai Indians": "Mumbai Indians",

    # Chennai
    "Chennai Super Kings": "Chennai Super Kings",

    # Kolkata
    "Kolkata Knight Riders": "Kolkata Knight Riders",

    # Hyderabad
    "Sunrisers Hyderabad": "Sunrisers Hyderabad",

    # Gujarat
    "Gujarat Titans": "Gujarat Titans",

    # Lucknow
    "Lucknow Super Giants": "Lucknow Super Giants",

    # Old teams - preserve historical identity
    "Deccan Chargers": "Deccan Chargers",
    "Pune Warriors India": "Pune Warriors India",
    "Pune Warriors": "Pune Warriors India",
    "Rising Pune Supergiants": "Rising Pune Supergiants",
    "Rising Pune Supergiant": "Rising Pune Supergiants",
    "Gujarat Lions": "Gujarat Lions",
    "Kochi Tuskers Kerala": "Kochi Tuskers Kerala",
}


# ============================================================
# 3. COLUMN STANDARDIZATION
# ============================================================

COLUMN_ALIASES = {
    "id": "match_id",
    "matchid": "match_id",
    "match_id": "match_id",

    "season": "season",
    "year": "season",

    "date": "date",
    "match_date": "date",

    "team1": "team1",
    "team_1": "team1",

    "team2": "team2",
    "team_2": "team2",

    "winner": "winner",
    "winning_team": "winner",

    "toss_winner": "toss_winner",
    "tosswinner": "toss_winner",

    "toss_decision": "toss_decision",
    "tossdecision": "toss_decision",

    "venue": "venue",

    "city": "city",

    "result": "result",

    "win_by_runs": "win_by_runs",
    "win_by_wickets": "win_by_wickets",

    "dl_applied": "dl_applied",

    "player_of_match": "player_of_match",
    "player_of_match_1": "player_of_match",
}


# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================

def clean_column_name(column):
    """
    Convert column names into a standard format.
    """
    column = str(column).strip().lower()

    replacements = {
        " ": "_",
        "-": "_",
        ".": "",
        "/": "_",
    }

    for old, new in replacements.items():
        column = column.replace(old, new)

    return column


def standardize_columns(df):
    """
    Standardize column names.
    """
    df = df.copy()

    df.columns = [
        clean_column_name(col)
        for col in df.columns
    ]

    rename_dict = {}

    for col in df.columns:
        if col in COLUMN_ALIASES:
            rename_dict[col] = COLUMN_ALIASES[col]

    df.rename(columns=rename_dict, inplace=True)

    return df


def clean_team_name(value):
    """
    Standardize IPL team names.
    """
    if pd.isna(value):
        return value

    value = str(value).strip()

    return TEAM_ALIASES.get(value, value)


def detect_season(df, expected_season):
    """
    Detect season from data.
    If season is missing, use the filename season.
    """

    if "season" not in df.columns:
        df["season"] = expected_season
        return df

    # Convert season to numeric where possible
    df["season"] = pd.to_numeric(
        df["season"],
        errors="coerce"
    )

    # Fill missing values from filename
    df["season"] = df["season"].fillna(expected_season)

    return df


def create_match_id(df, season):
    """
    Create a stable match ID only if the source
    does not already contain one.
    """

    if "match_id" not in df.columns:
        df["match_id"] = (
            str(season)
            + "_"
            + df.index.astype(str)
        )

    df["match_id"] = df["match_id"].astype(str).str.strip()

    return df


# ============================================================
# 5. LOAD YEARLY FILES
# ============================================================

all_matches = []

print("=" * 70)
print("IPL 2008-2026 DATA CLEANING STARTED")
print("=" * 70)

for season in range(2008, 2027):

    file_path = RAW_DIR / f"ipl_matches_{season}.csv"

    if not file_path.exists():

        print(
            f"[WARNING] Missing file: "
            f"ipl_matches_{season}.csv"
        )

        continue

    print(
        f"Reading {season}: "
        f"{file_path.name}"
    )

    try:

        df = pd.read_csv(file_path)

    except Exception as error:

        print(
            f"[ERROR] Could not read "
            f"{file_path.name}"
        )

        print(error)

        continue

    # Standardize columns
    df = standardize_columns(df)

    # Detect season
    df = detect_season(df, season)

    # Create match ID if required
    df = create_match_id(df, season)

    # Standardize team columns
    for column in [
        "team1",
        "team2",
        "winner",
        "toss_winner",
    ]:

        if column in df.columns:

            df[column] = (
                df[column]
                .apply(clean_team_name)
            )

    # Clean text columns
    for column in [
        "venue",
        "city",
        "result",
        "toss_decision",
        "player_of_match",
    ]:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # Date conversion
    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # Add source season for validation
    df["source_season"] = season

    all_matches.append(df)

    print(
        f"    Loaded matches: {len(df)}"
    )


# ============================================================
# 6. COMBINE ALL SEASONS
# ============================================================

if not all_matches:

    raise FileNotFoundError(
        "No IPL yearly CSV files were found "
        "inside data/raw/"
    )


matches = pd.concat(
    all_matches,
    ignore_index=True,
    sort=False
)


# ============================================================
# 7. KEEP IMPORTANT COLUMNS FIRST
# ============================================================

priority_columns = [
    "match_id",
    "season",
    "date",
    "team1",
    "team2",
    "winner",
    "toss_winner",
    "toss_decision",
    "venue",
    "city",
    "result",
    "win_by_runs",
    "win_by_wickets",
    "player_of_match",
]


existing_priority = [
    col
    for col in priority_columns
    if col in matches.columns
]

remaining_columns = [
    col
    for col in matches.columns
    if col not in existing_priority
]

matches = matches[
    existing_priority + remaining_columns
]


# ============================================================
# 8. REMOVE EXACT DUPLICATES
# ============================================================

before_duplicates = len(matches)

matches = matches.drop_duplicates()

after_duplicates = len(matches)

print()
print(
    f"Exact duplicate rows removed: "
    f"{before_duplicates - after_duplicates}"
)


# ============================================================
# 9. REMOVE DUPLICATE MATCH IDs
# ============================================================

before_match_duplicates = len(matches)

matches = (
    matches
    .sort_values(
        ["season", "match_id"]
    )
    .drop_duplicates(
        subset=["match_id"],
        keep="first"
    )
    .reset_index(drop=True)
)

after_match_duplicates = len(matches)

print(
    f"Duplicate match IDs removed: "
    f"{before_match_duplicates - after_match_duplicates}"
)


# ============================================================
# 10. VALIDATE SEASON RANGE
# ============================================================

matches["season"] = pd.to_numeric(
    matches["season"],
    errors="coerce"
)

invalid_seasons = matches[
    ~matches["season"].between(2008, 2026)
]

if len(invalid_seasons) > 0:

    print()
    print(
        "[WARNING] Invalid season records:"
    )

    print(
        invalid_seasons[
            ["match_id", "season"]
        ].head(10)
    )

else:

    print(
        "Season validation: PASSED"
    )


# ============================================================
# 11. VALIDATE TEAM DATA
# ============================================================

required_team_columns = [
    "team1",
    "team2",
]

for column in required_team_columns:

    if column in matches.columns:

        missing_count = matches[column].isna().sum()

        print(
            f"Missing {column}: "
            f"{missing_count}"
        )


if "winner" in matches.columns:

    missing_winners = (
        matches["winner"]
        .isna()
        .sum()
    )

    print(
        f"Missing winners: "
        f"{missing_winners}"
    )


# ============================================================
# 12. CHECK TEAM CONSISTENCY
# ============================================================

team_columns = [
    "team1",
    "team2",
    "winner",
    "toss_winner",
]

available_team_columns = [
    col
    for col in team_columns
    if col in matches.columns
]

all_teams = set()

for column in available_team_columns:

    all_teams.update(
        matches[column]
        .dropna()
        .astype(str)
        .unique()
    )


print()
print("=" * 70)
print("TEAMS FOUND IN 2008-2026 DATA")
print("=" * 70)

for team in sorted(all_teams):

    print(team)


# ============================================================
# 13. SEASON-WISE MATCH COUNT
# ============================================================

season_summary = (
    matches
    .groupby("season")
    .size()
    .reset_index(name="matches")
    .sort_values("season")
)


print()
print("=" * 70)
print("SEASON-WISE MATCH COUNT")
print("=" * 70)

print(
    season_summary.to_string(
        index=False
    )
)


# ============================================================
# 14. FINAL DATA QUALITY CHECK
# ============================================================

print()
print("=" * 70)
print("FINAL DATA QUALITY CHECK")
print("=" * 70)

print(
    f"Total records: {len(matches)}"
)

print(
    f"Total seasons: "
    f"{matches['season'].nunique()}"
)

print(
    f"Season range: "
    f"{matches['season'].min()} - "
    f"{matches['season'].max()}"
)

print(
    f"Unique match IDs: "
    f"{matches['match_id'].nunique()}"
)

if len(matches) == matches["match_id"].nunique():

    print(
        "Match ID uniqueness: PASSED"
    )

else:

    print(
        "Match ID uniqueness: FAILED"
    )


# ============================================================
# 15. SAVE CLEAN MASTER DATASET
# ============================================================

output_file = (
    PROCESSED_DIR
    / "ipl_matches_clean_2008_2026.csv"
)

matches.to_csv(
    output_file,
    index=False
)


# ============================================================
# 16. SAVE SEASON SUMMARY
# ============================================================

season_summary_file = (
    PROCESSED_DIR
    / "season_match_summary.csv"
)

season_summary.to_csv(
    season_summary_file,
    index=False
)


# ============================================================
# 17. FINAL MESSAGE
# ============================================================

print()
print("=" * 70)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    f"Master dataset:\n{output_file}"
)

print(
    f"Season summary:\n{season_summary_file}"
)

print()
print(
    "Next step: Historical IPL analysis"
)