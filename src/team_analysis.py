from pathlib import Path
from collections import defaultdict
import json

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

JSON_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "cricsheet_ipl"
)

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

REPORT_DIR = (
    BASE_DIR
    / "outputs"
    / "reports"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CURRENT IPL TEAMS - 2027 PREDICTION
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
# HISTORICAL TEAM NAME NORMALIZATION
# ============================================================

TEAM_ALIASES = {

    # RCB
    "Royal Challengers Bangalore":
        "Royal Challengers Bengaluru",

    "Royal Challengers Bengaluru":
        "Royal Challengers Bengaluru",

    # Delhi
    "Delhi Daredevils":
        "Delhi Capitals",

    "Delhi Capitals":
        "Delhi Capitals",

    # Punjab
    "Kings XI Punjab":
        "Punjab Kings",

    "Punjab Kings":
        "Punjab Kings",

    # Pune
    "Pune Warriors":
        "Pune Warriors India",

    "Pune Warriors India":
        "Pune Warriors India",

    "Rising Pune Supergiant":
        "Rising Pune Supergiants",

    "Rising Pune Supergiants":
        "Rising Pune Supergiants",

    # Current teams
    "Chennai Super Kings":
        "Chennai Super Kings",

    "Mumbai Indians":
        "Mumbai Indians",

    "Kolkata Knight Riders":
        "Kolkata Knight Riders",

    "Rajasthan Royals":
        "Rajasthan Royals",

    "Sunrisers Hyderabad":
        "Sunrisers Hyderabad",

    "Gujarat Titans":
        "Gujarat Titans",

    "Lucknow Super Giants":
        "Lucknow Super Giants",

    # Historical teams
    "Deccan Chargers":
        "Deccan Chargers",

    "Gujarat Lions":
        "Gujarat Lions",

    "Kochi Tuskers Kerala":
        "Kochi Tuskers Kerala",
}


# ============================================================
# TEAM NAME FUNCTION
# ============================================================

def normalize_team(team):

    if team is None:
        return ""

    team = str(team).strip()

    return TEAM_ALIASES.get(
        team,
        team
    )


# ============================================================
# IPL CHAMPIONS - 2008 TO 2026
# ============================================================

CHAMPIONS = {

    2008: "Rajasthan Royals",
    2009: "Deccan Chargers",
    2010: "Chennai Super Kings",
    2011: "Chennai Super Kings",
    2012: "Kolkata Knight Riders",
    2013: "Mumbai Indians",
    2014: "Kolkata Knight Riders",
    2015: "Mumbai Indians",
    2016: "Sunrisers Hyderabad",
    2017: "Mumbai Indians",
    2018: "Chennai Super Kings",
    2019: "Mumbai Indians",
    2020: "Mumbai Indians",
    2021: "Chennai Super Kings",
    2022: "Gujarat Titans",
    2023: "Chennai Super Kings",
    2024: "Kolkata Knight Riders",
    2025: "Royal Challengers Bengaluru",
    2026: "Royal Challengers Bengaluru",
}


# ============================================================
# IPL RUNNERS-UP - 2008 TO 2026
# ============================================================

RUNNERS_UP = {

    2008: "Chennai Super Kings",
    2009: "Royal Challengers Bengaluru",
    2010: "Mumbai Indians",
    2011: "Royal Challengers Bengaluru",
    2012: "Chennai Super Kings",
    2013: "Chennai Super Kings",
    2014: "Punjab Kings",
    2015: "Chennai Super Kings",
    2016: "Royal Challengers Bengaluru",
    2017: "Rising Pune Supergiants",
    2018: "Sunrisers Hyderabad",
    2019: "Chennai Super Kings",
    2020: "Delhi Capitals",
    2021: "Kolkata Knight Riders",
    2022: "Rajasthan Royals",
    2023: "Gujarat Titans",
    2024: "Sunrisers Hyderabad",
    2025: "Punjab Kings",
    2026: "Gujarat Titans",
}


# ============================================================
# GET SEASON YEAR
# ============================================================

def get_match_year(info):

    dates = info.get(
        "dates",
        []
    )

    if not dates:
        return None

    try:

        date_value = str(
            dates[0]
        )

        return int(
            date_value[:4]
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# ============================================================
# GET EVENT NAME
# ============================================================

def get_event_name(info):

    event = info.get(
        "event",
        {}
    )

    if isinstance(
        event,
        dict
    ):

        return str(
            event.get(
                "name",
                ""
            )
        ).strip()

    return str(
        event
    ).strip()


# ============================================================
# GET WINNER
# ============================================================

def get_winner(info):

    outcome = info.get(
        "outcome",
        {}
    )

    if not isinstance(
        outcome,
        dict
    ):
        return ""

    winner = outcome.get(
        "winner",
        ""
    )

    if not winner:
        return ""

    return normalize_team(
        winner
    )


# ============================================================
# READ ONE CRICSHEET MATCH
# ============================================================

def read_match(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    info = data.get(
        "info",
        {}
    )

    # --------------------------------------------------------
    # Only IPL
    # --------------------------------------------------------

    event_name = get_event_name(
        info
    )

    if event_name.lower() != (
        "indian premier league"
    ):
        return None

    # --------------------------------------------------------
    # Season
    # --------------------------------------------------------

    season = get_match_year(
        info
    )

    if season is None:
        return None

    if not (
        2008
        <= season
        <= 2026
    ):
        return None

    # --------------------------------------------------------
    # Teams
    # --------------------------------------------------------

    teams = info.get(
        "teams",
        []
    )

    teams = [
        normalize_team(team)
        for team in teams
    ]

    teams = [
        team
        for team in teams
        if team
    ]

    if len(teams) != 2:
        return None

    # --------------------------------------------------------
    # Winner
    # --------------------------------------------------------

    winner = get_winner(
        info
    )

    # --------------------------------------------------------
    # Runs by team
    # --------------------------------------------------------

    team_runs = defaultdict(int)

    innings_list = data.get(
        "innings",
        []
    )

    for innings in innings_list:

        if not isinstance(
            innings,
            dict
        ):
            continue

        batting_team = normalize_team(
            innings.get(
                "team",
                ""
            )
        )

        if not batting_team:
            continue

        overs = innings.get(
            "overs",
            []
        )

        for over in overs:

            deliveries = over.get(
                "deliveries",
                []
            )

            for delivery in deliveries:

                runs = delivery.get(
                    "runs",
                    {}
                )

                total_runs = runs.get(
                    "total",
                    0
                )

                try:

                    total_runs = int(
                        total_runs
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    total_runs = 0

                team_runs[
                    batting_team
                ] += total_runs

    # --------------------------------------------------------
    # Return match
    # --------------------------------------------------------

    return {

        "match_id":
            file_path.stem,

        "season":
            season,

        "team1":
            teams[0],

        "team2":
            teams[1],

        "winner":
            winner,

        "team_runs":
            dict(team_runs),
    }


# ============================================================
# LOAD ALL 1243 IPL MATCHES
# ============================================================

def load_all_matches():

    if not JSON_DIR.exists():

        raise FileNotFoundError(
            "\nCricsheet IPL folder not found:\n"
            f"{JSON_DIR}\n\n"
            "Make sure the folder is:\n"
            "data/raw/cricsheet_ipl/"
        )

    json_files = sorted(
        JSON_DIR.rglob(
            "*.json"
        )
    )

    print(
        f"JSON files found: "
        f"{len(json_files)}"
    )

    matches = []

    failed_files = []

    for index, file_path in enumerate(
        json_files,
        start=1
    ):

        try:

            match = read_match(
                file_path
            )

            if match is not None:

                matches.append(
                    match
                )

        except Exception as error:

            failed_files.append(
                (
                    file_path.name,
                    str(error)
                )
            )

        if index % 200 == 0:

            print(
                f"Files checked: "
                f"{index}"
            )

    return (
        matches,
        failed_files
    )


# ============================================================
# CREATE TEAM-MATCH RECORDS
# ============================================================

def create_team_match_records(
    matches
):

    rows = []

    for match in matches:

        team1 = match[
            "team1"
        ]

        team2 = match[
            "team2"
        ]

        winner = match[
            "winner"
        ]

        # ----------------------------------------------------
        # Team 1 result
        # ----------------------------------------------------

        if winner == team1:

            result1 = "Win"

        elif winner == team2:

            result1 = "Loss"

        else:

            result1 = "No Result / Tie"

        # ----------------------------------------------------
        # Team 2 result
        # ----------------------------------------------------

        if winner == team2:

            result2 = "Win"

        elif winner == team1:

            result2 = "Loss"

        else:

            result2 = "No Result / Tie"

        # ----------------------------------------------------
        # Team 1 record
        # ----------------------------------------------------

        rows.append({

            "season":
                match["season"],

            "match_id":
                match["match_id"],

            "team":
                team1,

            "opponent":
                team2,

            "result":
                result1,

            "winner":
                winner,

            "runs_scored":
                match[
                    "team_runs"
                ].get(
                    team1,
                    0
                ),

            "runs_conceded":
                match[
                    "team_runs"
                ].get(
                    team2,
                    0
                ),
        })

        # ----------------------------------------------------
        # Team 2 record
        # ----------------------------------------------------

        rows.append({

            "season":
                match["season"],

            "match_id":
                match["match_id"],

            "team":
                team2,

            "opponent":
                team1,

            "result":
                result2,

            "winner":
                winner,

            "runs_scored":
                match[
                    "team_runs"
                ].get(
                    team2,
                    0
                ),

            "runs_conceded":
                match[
                    "team_runs"
                ].get(
                    team1,
                    0
                ),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# SEASON-WISE TEAM ANALYSIS
# ============================================================

def create_season_analysis(
    team_matches
):

    rows = []

    grouped = team_matches.groupby(
        [
            "season",
            "team"
        ]
    )

    for (
        season,
        team
    ), group in grouped:

        matches = len(
            group
        )

        wins = int(
            (
                group["result"]
                == "Win"
            ).sum()
        )

        losses = int(
            (
                group["result"]
                == "Loss"
            ).sum()
        )

        no_results = int(
            (
                group["result"]
                == "No Result / Tie"
            ).sum()
        )

        decided = (
            wins
            + losses
        )

        if decided > 0:

            win_percentage = (
                wins
                * 100
                / decided
            )

        else:

            win_percentage = 0

        runs_scored = int(
            group[
                "runs_scored"
            ].sum()
        )

        runs_conceded = int(
            group[
                "runs_conceded"
            ].sum()
        )

        run_difference = (
            runs_scored
            - runs_conceded
        )

        champion = int(
            CHAMPIONS.get(
                int(season),
                ""
            )
            == team
        )

        runner_up = int(
            RUNNERS_UP.get(
                int(season),
                ""
            )
            == team
        )

        rows.append({

            "season":
                int(season),

            "team":
                team,

            "matches":
                matches,

            "wins":
                wins,

            "losses":
                losses,

            "no_results_or_ties":
                no_results,

            "win_percentage":
                round(
                    win_percentage,
                    2
                ),

            "runs_scored":
                runs_scored,

            "runs_conceded":
                runs_conceded,

            "run_difference":
                run_difference,

            "champion":
                champion,

            "runner_up":
                runner_up,
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# OVERALL TEAM ANALYSIS
# ============================================================

def create_overall_analysis(
    season_df
):

    rows = []

    for (
        team,
        group
    ) in season_df.groupby(
        "team"
    ):

        matches = int(
            group[
                "matches"
            ].sum()
        )

        wins = int(
            group[
                "wins"
            ].sum()
        )

        losses = int(
            group[
                "losses"
            ].sum()
        )

        no_results = int(
            group[
                "no_results_or_ties"
            ].sum()
        )

        decided = (
            wins
            + losses
        )

        if decided > 0:

            win_percentage = (
                wins
                * 100
                / decided
            )

        else:

            win_percentage = 0

        championships = int(
            group[
                "champion"
            ].sum()
        )

        runner_ups = int(
            group[
                "runner_up"
            ].sum()
        )

        total_runs = int(
            group[
                "runs_scored"
            ].sum()
        )

        total_conceded = int(
            group[
                "runs_conceded"
            ].sum()
        )

        run_difference = (
            total_runs
            - total_conceded
        )

        # ----------------------------------------------------
        # Consistency
        # ----------------------------------------------------

        std = group[
            "win_percentage"
        ].std()

        if pd.isna(std):

            consistency_score = 100.0

        else:

            consistency_score = max(
                0,
                100 - float(std)
            )

        rows.append({

            "team":
                team,

            "seasons_played":
                int(
                    group[
                        "season"
                    ].nunique()
                ),

            "matches":
                matches,

            "wins":
                wins,

            "losses":
                losses,

            "no_results_or_ties":
                no_results,

            "overall_win_percentage":
                round(
                    win_percentage,
                    2
                ),

            "runs_scored":
                total_runs,

            "runs_conceded":
                total_conceded,

            "run_difference":
                run_difference,

            "championships":
                championships,

            "runner_ups":
                runner_ups,

            "consistency_score":
                round(
                    consistency_score,
                    2
                ),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# RECENT FORM - 2024 TO 2026
# ============================================================

def create_recent_form(
    team_matches
):

    recent = team_matches[
        team_matches[
            "season"
        ].isin(
            [
                2024,
                2025,
                2026
            ]
        )
    ].copy()

    rows = []

    for (
        team,
        group
    ) in recent.groupby(
        "team"
    ):

        wins = int(
            (
                group["result"]
                == "Win"
            ).sum()
        )

        losses = int(
            (
                group["result"]
                == "Loss"
            ).sum()
        )

        no_results = int(
            (
                group["result"]
                == "No Result / Tie"
            ).sum()
        )

        decided = (
            wins
            + losses
        )

        if decided > 0:

            recent_win_percentage = (
                wins
                * 100
                / decided
            )

        else:

            recent_win_percentage = 0

        yearly_percentages = {}

        for year in [
            2024,
            2025,
            2026
        ]:

            year_data = group[
                group["season"]
                == year
            ]

            year_wins = int(
                (
                    year_data["result"]
                    == "Win"
                ).sum()
            )

            year_losses = int(
                (
                    year_data["result"]
                    == "Loss"
                ).sum()
            )

            year_decided = (
                year_wins
                + year_losses
            )

            if year_decided > 0:

                percentage = (
                    year_wins
                    * 100
                    / year_decided
                )

            else:

                percentage = 0

            yearly_percentages[
                year
            ] = percentage

        # ----------------------------------------------------
        # Recent form weighting
        # ----------------------------------------------------

        weighted_recent_form = (

            yearly_percentages[
                2024
            ] * 0.20

            +

            yearly_percentages[
                2025
            ] * 0.30

            +

            yearly_percentages[
                2026
            ] * 0.50
        )

        rows.append({

            "team":
                team,

            "matches_2024_2026":
                len(group),

            "wins_2024_2026":
                wins,

            "losses_2024_2026":
                losses,

            "no_results_2024_2026":
                no_results,

            "recent_win_percentage":
                round(
                    recent_win_percentage,
                    2
                ),

            "win_percentage_2024":
                round(
                    yearly_percentages[
                        2024
                    ],
                    2
                ),

            "win_percentage_2025":
                round(
                    yearly_percentages[
                        2025
                    ],
                    2
                ),

            "win_percentage_2026":
                round(
                    yearly_percentages[
                        2026
                    ],
                    2
                ),

            "weighted_recent_form":
                round(
                    weighted_recent_form,
                    2
                ),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# 2026 TEAM ANALYSIS
# ============================================================

def create_2026_analysis(
    team_matches
):

    data = team_matches[
        team_matches[
            "season"
        ] == 2026
    ].copy()

    rows = []

    for team in CURRENT_TEAMS:

        group = data[
            data["team"]
            == team
        ]

        matches = len(
            group
        )

        wins = int(
            (
                group["result"]
                == "Win"
            ).sum()
        )

        losses = int(
            (
                group["result"]
                == "Loss"
            ).sum()
        )

        no_results = int(
            (
                group["result"]
                == "No Result / Tie"
            ).sum()
        )

        decided = (
            wins
            + losses
        )

        if decided > 0:

            win_percentage = (
                wins
                * 100
                / decided
            )

        else:

            win_percentage = 0

        runs_scored = int(
            group[
                "runs_scored"
            ].sum()
        )

        runs_conceded = int(
            group[
                "runs_conceded"
            ].sum()
        )

        run_difference = (
            runs_scored
            - runs_conceded
        )

        rows.append({

            "team":
                team,

            "matches_2026":
                matches,

            "wins_2026":
                wins,

            "losses_2026":
                losses,

            "no_results_2026":
                no_results,

            "win_percentage_2026":
                round(
                    win_percentage,
                    2
                ),

            "runs_scored_2026":
                runs_scored,

            "runs_conceded_2026":
                runs_conceded,

            "run_difference_2026":
                run_difference,
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# HEAD-TO-HEAD
# ============================================================

def create_head_to_head(
    team_matches
):

    current = team_matches[
        team_matches[
            "team"
        ].isin(
            CURRENT_TEAMS
        )
        &
        team_matches[
            "opponent"
        ].isin(
            CURRENT_TEAMS
        )
    ].copy()

    rows = []

    for (
        team,
        opponent
    ), group in current.groupby(
        [
            "team",
            "opponent"
        ]
    ):

        matches = len(
            group
        )

        wins = int(
            (
                group["result"]
                == "Win"
            ).sum()
        )

        losses = int(
            (
                group["result"]
                == "Loss"
            ).sum()
        )

        if matches > 0:

            win_percentage = (
                wins
                * 100
                / matches
            )

        else:

            win_percentage = 0

        rows.append({

            "team":
                team,

            "opponent":
                opponent,

            "matches":
                matches,

            "wins":
                wins,

            "losses":
                losses,

            "win_percentage":
                round(
                    win_percentage,
                    2
                ),
        })

    return pd.DataFrame(
        rows
    )


# ============================================================
# MIN-MAX NORMALIZATION
# ============================================================

def minmax(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    minimum = series.min()
    maximum = series.max()

    if minimum == maximum:

        return pd.Series(
            [50.0] * len(series),
            index=series.index
        )

    return (
        (
            series
            - minimum
        )
        /
        (
            maximum
            - minimum
        )
        * 100
    )


# ============================================================
# 2027 TEAM STRENGTH FEATURES
# ============================================================

def create_strength_features(
    overall_df,
    recent_df,
    current_2026_df
):

    # ========================================================
    # Start with CURRENT 10 teams only
    # ========================================================

    df = pd.DataFrame({
        "team": CURRENT_TEAMS
    })

    # ========================================================
    # OVERALL FEATURES
    # ========================================================

    overall_columns = [
        "team",
        "overall_win_percentage",
        "championships",
        "runner_ups",
        "consistency_score",
        "run_difference"
    ]

    overall_columns = [
        col
        for col in overall_columns
        if col in overall_df.columns
    ]

    overall_temp = overall_df[
        overall_columns
    ].copy()

    df = df.merge(
        overall_temp,
        on="team",
        how="left"
    )

    # ========================================================
    # RECENT FEATURES
    # ========================================================

    recent_columns = [
        "team",
        "recent_win_percentage",
        "win_percentage_2024",
        "win_percentage_2025",
        "win_percentage_2026",
        "weighted_recent_form"
    ]

    recent_columns = [
        col
        for col in recent_columns
        if col in recent_df.columns
    ]

    recent_temp = recent_df[
        recent_columns
    ].copy()

    # --------------------------------------------------------
    # IMPORTANT:
    # Recent dataframe already contains
    # win_percentage_2026.
    # So merge it first.
    # --------------------------------------------------------

    df = df.merge(
        recent_temp,
        on="team",
        how="left"
    )

    # ========================================================
    # 2026 FEATURES
    # ========================================================

    current_columns = [
        "team",
        "matches_2026",
        "wins_2026",
        "losses_2026",
        "no_results_2026",
        "win_percentage_2026",
        "run_difference_2026"
    ]

    current_columns = [
        col
        for col in current_columns
        if col in current_2026_df.columns
    ]

    current_temp = current_2026_df[
        current_columns
    ].copy()

    # --------------------------------------------------------
    # Rename duplicate win percentage BEFORE merge
    # --------------------------------------------------------

    if (
        "win_percentage_2026"
        in current_temp.columns
    ):

        current_temp = current_temp.rename(
            columns={
                "win_percentage_2026":
                    "current_2026_win_percentage"
            }
        )

    df = df.merge(
        current_temp,
        on="team",
        how="left"
    )

    # ========================================================
    # CREATE MISSING NUMERIC COLUMNS
    # ========================================================

    required_columns = [

        "overall_win_percentage",

        "championships",

        "runner_ups",

        "consistency_score",

        "run_difference",

        "recent_win_percentage",

        "win_percentage_2024",

        "win_percentage_2025",

        "win_percentage_2026",

        "weighted_recent_form",

        "matches_2026",

        "wins_2026",

        "losses_2026",

        "no_results_2026",

        "run_difference_2026",
    ]

    for column in required_columns:

        if column not in df.columns:

            df[column] = 0

    # ========================================================
    # NUMERIC CLEANING
    # ========================================================

    for column in required_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

    # ========================================================
    # STRENGTH 1
    # HISTORICAL STRENGTH
    # ========================================================

    df[
        "historical_strength"
    ] = minmax(
        df[
            "overall_win_percentage"
        ]
    )

    # ========================================================
    # STRENGTH 2
    # RECENT FORM
    # ========================================================

    df[
        "recent_strength"
    ] = minmax(
        df[
            "weighted_recent_form"
        ]
    )

    # ========================================================
    # STRENGTH 3
    # LATEST 2026 FORM
    # ========================================================

    df[
        "latest_strength"
    ] = minmax(
        df[
            "win_percentage_2026"
        ]
    )

    # ========================================================
    # STRENGTH 4
    # CONSISTENCY
    # ========================================================

    df[
        "consistency_strength"
    ] = minmax(
        df[
            "consistency_score"
        ]
    )

    # ========================================================
    # STRENGTH 5
    # 2026 RUN DIFFERENCE
    # ========================================================

    df[
        "run_strength"
    ] = minmax(
        df[
            "run_difference_2026"
        ]
    )

    # ========================================================
    # COMPOSITE TEAM STRENGTH
    # ========================================================

    df[
        "team_strength_score"
    ] = (

        df[
            "historical_strength"
        ] * 0.20

        +

        df[
            "recent_strength"
        ] * 0.30

        +

        df[
            "latest_strength"
        ] * 0.30

        +

        df[
            "consistency_strength"
        ] * 0.10

        +

        df[
            "run_strength"
        ] * 0.10
    )

    df[
        "team_strength_score"
    ] = df[
        "team_strength_score"
    ].round(2)

    # ========================================================
    # CURRENT IPL TEAM FLAG
    # ========================================================

    df[
        "current_ipl_team"
    ] = 1

    # ========================================================
    # FINAL COLUMN ORDER
    # ========================================================

    final_columns = [

        "team",

        "overall_win_percentage",

        "championships",

        "runner_ups",

        "consistency_score",

        "run_difference",

        "recent_win_percentage",

        "win_percentage_2024",

        "win_percentage_2025",

        "win_percentage_2026",

        "weighted_recent_form",

        "matches_2026",

        "wins_2026",

        "losses_2026",

        "no_results_2026",

        "run_difference_2026",

        "historical_strength",

        "recent_strength",

        "latest_strength",

        "consistency_strength",

        "run_strength",

        "team_strength_score",

        "current_ipl_team",
    ]

    final_columns = [
        col
        for col in final_columns
        if col in df.columns
    ]

    df = df[
        final_columns
    ]

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print(
        "IPL TEAM ANALYSIS - 2008 TO 2026"
    )
    print("=" * 70)

    # ========================================================
    # LOAD MATCHES
    # ========================================================

    matches, failed_files = (
        load_all_matches()
    )

    print()

    print(
        "IPL matches successfully loaded:",
        len(matches)
    )

    print(
        "Failed files:",
        len(failed_files)
    )

    # ========================================================
    # VALIDATE MATCH COUNT
    # ========================================================

    if len(matches) != 1243:

        raise ValueError(
            "\nExpected 1243 IPL matches "
            f"but loaded {len(matches)}.\n"
            "Please check Cricsheet data."
        )

    # ========================================================
    # TEAM-MATCH RECORDS
    # ========================================================

    team_matches = (
        create_team_match_records(
            matches
        )
    )

    print(
        "Team-match records:",
        len(team_matches)
    )

    # ========================================================
    # SEASON ANALYSIS
    # ========================================================

    season_df = (
        create_season_analysis(
            team_matches
        )
    )

    # ========================================================
    # OVERALL ANALYSIS
    # ========================================================

    overall_df = (
        create_overall_analysis(
            season_df
        )
    )

    # ========================================================
    # RECENT FORM
    # ========================================================

    recent_df = (
        create_recent_form(
            team_matches
        )
    )

    # ========================================================
    # 2026 ANALYSIS
    # ========================================================

    current_2026_df = (
        create_2026_analysis(
            team_matches
        )
    )

    # ========================================================
    # HEAD-TO-HEAD
    # ========================================================

    head_to_head_df = (
        create_head_to_head(
            team_matches
        )
    )

    # ========================================================
    # 2027 TEAM STRENGTH
    # ========================================================

    strength_df = (
        create_strength_features(
            overall_df,
            recent_df,
            current_2026_df
        )
    )

    # ========================================================
    # SAVE PROCESSED FILES
    # ========================================================

    season_df.to_csv(
        PROCESSED_DIR
        / "team_season_analysis.csv",
        index=False
    )

    overall_df.to_csv(
        PROCESSED_DIR
        / "team_overall_analysis.csv",
        index=False
    )

    recent_df.to_csv(
        PROCESSED_DIR
        / "team_recent_form_2024_2026.csv",
        index=False
    )

    current_2026_df.to_csv(
        PROCESSED_DIR
        / "current_team_analysis_2026.csv",
        index=False
    )

    strength_df.to_csv(
        PROCESSED_DIR
        / "team_strength_features_2027.csv",
        index=False
    )

    head_to_head_df.to_csv(
        PROCESSED_DIR
        / "head_to_head_2008_2026.csv",
        index=False
    )

    # ========================================================
    # CHAMPION REPORT
    # ========================================================

    champion_rows = []

    for season, team in CHAMPIONS.items():

        champion_rows.append({

            "season":
                season,

            "champion":
                team
        })

    champion_df = pd.DataFrame(
        champion_rows
    )

    champion_df.to_csv(
        REPORT_DIR
        / "ipl_champions_2008_2026.csv",
        index=False
    )

    # ========================================================
    # RUNNER-UP REPORT
    # ========================================================

    runner_rows = []

    for season, team in RUNNERS_UP.items():

        runner_rows.append({

            "season":
                season,

            "runner_up":
                team
        })

    runner_df = pd.DataFrame(
        runner_rows
    )

    runner_df.to_csv(
        REPORT_DIR
        / "ipl_runners_up_2008_2026.csv",
        index=False
    )

    # ========================================================
    # CURRENT TEAM STRENGTH REPORT
    # ========================================================

    strength_report = (
        strength_df
        .sort_values(
            "team_strength_score",
            ascending=False
        )
    )

    strength_report.to_csv(
        REPORT_DIR
        / "current_10_team_strength_report.csv",
        index=False
    )

    # ========================================================
    # CURRENT 10 TEAM VALIDATION
    # ========================================================

    print()
    print("=" * 70)
    print(
        "CURRENT IPL 10-TEAM VALIDATION"
    )
    print("=" * 70)

    for team in CURRENT_TEAMS:

        exists = (
            team
            in strength_df[
                "team"
            ].tolist()
        )

        if exists:

            print(
                "[OK]",
                team
            )

        else:

            print(
                "[MISSING]",
                team
            )

    # ========================================================
    # 2026 PERFORMANCE
    # ========================================================

    print()
    print("=" * 70)
    print(
        "2026 TEAM PERFORMANCE"
    )
    print("=" * 70)

    print(
        current_2026_df[
            [
                "team",
                "matches_2026",
                "wins_2026",
                "losses_2026",
                "no_results_2026",
                "win_percentage_2026"
            ]
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # RECENT FORM
    # ========================================================

    print()
    print("=" * 70)
    print(
        "RECENT FORM - 2024 TO 2026"
    )
    print("=" * 70)

    print(
        recent_df[
            [
                "team",
                "win_percentage_2024",
                "win_percentage_2025",
                "win_percentage_2026",
                "weighted_recent_form"
            ]
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # 2027 TEAM STRENGTH
    # ========================================================

    print()
    print("=" * 70)
    print(
        "2027 TEAM STRENGTH FEATURES"
    )
    print("=" * 70)

    print(
        strength_report[
            [
                "team",
                "historical_strength",
                "recent_strength",
                "latest_strength",
                "consistency_strength",
                "run_strength",
                "team_strength_score"
            ]
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # FILES CREATED
    # ========================================================

    print()
    print("=" * 70)
    print(
        "FILES CREATED"
    )
    print("=" * 70)

    print(
        "1. data/processed/"
        "team_season_analysis.csv"
    )

    print(
        "2. data/processed/"
        "team_overall_analysis.csv"
    )

    print(
        "3. data/processed/"
        "team_recent_form_2024_2026.csv"
    )

    print(
        "4. data/processed/"
        "current_team_analysis_2026.csv"
    )

    print(
        "5. data/processed/"
        "team_strength_features_2027.csv"
    )

    print(
        "6. data/processed/"
        "head_to_head_2008_2026.csv"
    )

    print(
        "7. outputs/reports/"
        "ipl_champions_2008_2026.csv"
    )

    print(
        "8. outputs/reports/"
        "ipl_runners_up_2008_2026.csv"
    )

    print(
        "9. outputs/reports/"
        "current_10_team_strength_report.csv"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 70)
    print(
        "STEP 4 TEAM ANALYSIS COMPLETED SUCCESSFULLY"
    )
    print("=" * 70)
    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()