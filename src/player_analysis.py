from pathlib import Path
import json
import zipfile
import urllib.request
from collections import defaultdict

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"

JSON_DIR = RAW_DIR / "cricsheet_ipl"

OUTPUT_DIR = BASE_DIR / "data" / "processed"

REPORT_DIR = BASE_DIR / "outputs" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


CRICSHEET_URL = (
    "https://cricsheet.org/downloads/ipl_json.zip"
)


# ============================================================
# DOWNLOAD / EXTRACT IF REQUIRED
# ============================================================

def prepare_cricsheet():

    if JSON_DIR.exists():

        json_files = list(
            JSON_DIR.rglob("*.json")
        )

        if len(json_files) >= 1243:

            print(
                f"Cricsheet JSON files available: "
                f"{len(json_files)}"
            )

            return

    print("\nDownloading Cricsheet IPL JSON...")

    zip_path = RAW_DIR / "ipl_json.zip"

    urllib.request.urlretrieve(
        CRICSHEET_URL,
        zip_path
    )

    if JSON_DIR.exists():

        import shutil

        shutil.rmtree(JSON_DIR)

    JSON_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Extracting Cricsheet data...")

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_ref:

        zip_ref.extractall(
            JSON_DIR
        )

    print("Extraction completed.")


# ============================================================
# IPL YEAR
# ============================================================

def get_ipl_year(info):

    dates = info.get(
        "dates",
        []
    )

    if not dates:

        return None

    try:

        return int(
            str(dates[0])[:4]
        )

    except:

        return None


# ============================================================
# SAFE NUMBER
# ============================================================

def number(value):

    try:

        return float(value)

    except:

        return 0.0


# ============================================================
# MAIN PLAYER ANALYSIS
# ============================================================

def main():

    print("=" * 75)
    print("IPL PLAYER ANALYSIS - 2008 TO 2026")
    print("=" * 75)

    prepare_cricsheet()

    json_files = sorted(
        JSON_DIR.rglob("*.json")
    )

    print(
        f"\nJSON files found: "
        f"{len(json_files)}"
    )


    # ========================================================
    # PLAYER STORAGE
    # ========================================================

    batting = defaultdict(
        lambda: {
            "runs": 0,
            "balls": 0,
            "fours": 0,
            "sixes": 0,
            "innings": 0,
            "dismissals": 0,
            "matches": set(),
            "teams": set(),
        }
    )


    bowling = defaultdict(
        lambda: {
            "balls": 0,
            "runs_conceded": 0,
            "wickets": 0,
            "dot_balls": 0,
            "matches": set(),
            "teams": set(),
        }
    )


    player_of_match = defaultdict(int)


    # Recent-form storage
    recent_batting = defaultdict(
        lambda: {
            "runs": 0,
            "balls": 0,
            "fours": 0,
            "sixes": 0,
            "innings": 0,
            "dismissals": 0,
        }
    )


    recent_bowling = defaultdict(
        lambda: {
            "balls": 0,
            "runs": 0,
            "wickets": 0,
            "dots": 0,
        }
    )


    latest_2026_batting = defaultdict(
        lambda: {
            "runs": 0,
            "balls": 0,
            "fours": 0,
            "sixes": 0,
            "innings": 0,
        }
    )


    latest_2026_bowling = defaultdict(
        lambda: {
            "balls": 0,
            "runs": 0,
            "wickets": 0,
            "dots": 0,
        }
    )


    season_player_batting = defaultdict(
        lambda: {
            "runs": 0,
            "balls": 0,
            "fours": 0,
            "sixes": 0,
            "innings": 0,
            "dismissals": 0,
            "matches": set(),
        }
    )


    season_player_bowling = defaultdict(
        lambda: {
            "balls": 0,
            "runs": 0,
            "wickets": 0,
            "dots": 0,
            "matches": set(),
        }
    )


    # ========================================================
    # MATCH COUNTERS
    # ========================================================

    processed_matches = 0
    skipped_matches = 0
    invalid_files = []


    # ========================================================
    # PROCESS ALL MATCHES
    # ========================================================

    for index, file_path in enumerate(
        json_files,
        start=1
    ):

        try:

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


            # ------------------------------------------------
            # IPL CHECK
            # ------------------------------------------------

            event = info.get(
                "event",
                {}
            )


            if isinstance(event, dict):

                event_name = event.get(
                    "name",
                    ""
                )

            else:

                event_name = str(event)


            if (
                str(event_name).lower()
                != "indian premier league"
            ):

                continue


            # ------------------------------------------------
            # YEAR
            # ------------------------------------------------

            year = get_ipl_year(
                info
            )


            if year is None:

                skipped_matches += 1
                continue


            if not (
                2008 <= year <= 2026
            ):

                continue


            # ------------------------------------------------
            # MATCH ID
            # ------------------------------------------------

            match_id = file_path.stem


            # ------------------------------------------------
            # PLAYER OF MATCH
            # ------------------------------------------------

            outcome = info.get(
                "players",
                {}
            )


            awards = info.get(
                "player_of_match",
                []
            )


            if isinstance(
                awards,
                str
            ):

                awards = [awards]


            for player in awards:

                player_of_match[
                    player
                ] += 1


            # ------------------------------------------------
            # INNINGS
            # ------------------------------------------------

            innings_list = data.get(
                "innings",
                []
            )


            for innings in innings_list:

                # ------------------------------------------------
                # New and old Cricsheet structures
                # ------------------------------------------------

                if not isinstance(
                    innings,
                    dict
                ):

                    continue


                team_batting = innings.get(
                    "team",
                    ""
                )


                overs = innings.get(
                    "overs",
                    []
                )


                # =================================================
                # OVERS
                # =================================================

                for over in overs:

                    deliveries = over.get(
                        "deliveries",
                        []
                    )


                    for delivery in deliveries:

                        batter = delivery.get(
                            "batter",
                            ""
                        )


                        bowler = delivery.get(
                            "bowler",
                            ""
                        )


                        runs = delivery.get(
                            "runs",
                            {}
                        )


                        batter_runs = int(
                            number(
                                runs.get(
                                    "batter",
                                    0
                                )
                            )
                        )


                        total_runs = int(
                            number(
                                runs.get(
                                    "total",
                                    0
                                )
                            )
                        )


                        extras = delivery.get(
                            "extras",
                            {}
                        )


                        wides = int(
                            number(
                                extras.get(
                                    "wides",
                                    0
                                )
                            )
                        )


                        noballs = int(
                            number(
                                extras.get(
                                    "noballs",
                                    0
                                )
                            )
                        )


                        byes = int(
                            number(
                                extras.get(
                                    "byes",
                                    0
                                )
                            )
                        )


                        legbyes = int(
                            number(
                                extras.get(
                                    "legbyes",
                                    0
                                )
                            )
                        )


                        penalty = int(
                            number(
                                extras.get(
                                    "penalty",
                                    0
                                )
                            )
                        )


                        # =================================================
                        # BATTING
                        # =================================================

                        batting[batter]["runs"] += (
                            batter_runs
                        )


                        # Wide does not count as ball faced
                        if wides == 0:

                            batting[batter]["balls"] += 1


                        if batter_runs == 4:

                            batting[batter]["fours"] += 1


                        if batter_runs == 6:

                            batting[batter]["sixes"] += 1


                        batting[batter][
                            "matches"
                        ].add(match_id)


                        batting[batter][
                            "teams"
                        ].add(team_batting)


                        # =================================================
                        # BOWLING
                        # =================================================

                        bowler_runs = (
                            total_runs
                            - byes
                            - legbyes
                            - penalty
                        )


                        bowling[bowler][
                            "runs_conceded"
                        ] += bowler_runs


                        # Wide and no-ball are not legal balls
                        if (
                            wides == 0
                            and noballs == 0
                        ):

                            bowling[bowler][
                                "balls"
                            ] += 1


                        if total_runs == 0:

                            bowling[bowler][
                                "dot_balls"
                            ] += 1


                        bowling[bowler][
                            "matches"
                        ].add(match_id)


                        bowling[bowler][
                            "teams"
                        ].add(
                            team_batting
                        )


                        # =================================================
                        # WICKETS
                        # =================================================

                        wickets = delivery.get(
                            "wickets",
                            []
                        )


                        for wicket in wickets:

                            dismissal = wicket.get(
                                "kind",
                                ""
                            )


                            player_out = wicket.get(
                                "player_out",
                                ""
                            )


                            # Do not charge bowler for
                            # run out / retired hurt /
                            # obstructing the field /
                            # retired out
                            non_bowler_wickets = {
                                "run out",
                                "retired hurt",
                                "retired out",
                                "obstructing the field",
                            }


                            if (
                                dismissal
                                not in non_bowler_wickets
                            ):

                                bowling[bowler][
                                    "wickets"
                                ] += 1


                            if player_out:

                                batting[player_out][
                                    "dismissals"
                                ] += 1


                        # =================================================
                        # RECENT FORM 2024-2026
                        # =================================================

                        if year >= 2024:

                            recent_batting[
                                batter
                            ]["runs"] += (
                                batter_runs
                            )


                            if wides == 0:

                                recent_batting[
                                    batter
                                ]["balls"] += 1


                            if batter_runs == 4:

                                recent_batting[
                                    batter
                                ]["fours"] += 1


                            if batter_runs == 6:

                                recent_batting[
                                    batter
                                ]["sixes"] += 1


                            recent_batting[
                                batter
                            ]["innings"] += 1


                            for wicket in wickets:

                                if (
                                    wicket.get(
                                        "player_out"
                                    )
                                    == batter
                                ):

                                    recent_batting[
                                        batter
                                    ]["dismissals"] += 1


                            recent_bowling[
                                bowler
                            ]["runs"] += (
                                bowler_runs
                            )


                            if (
                                wides == 0
                                and noballs == 0
                            ):

                                recent_bowling[
                                    bowler
                                ]["balls"] += 1


                            if total_runs == 0:

                                recent_bowling[
                                    bowler
                                ]["dots"] += 1


                            for wicket in wickets:

                                if (
                                    wicket.get(
                                        "kind",
                                        ""
                                    )
                                    not in non_bowler_wickets
                                ):

                                    recent_bowling[
                                        bowler
                                    ]["wickets"] += 1


                        # =================================================
                        # 2026 LATEST FORM
                        # =================================================

                        if year == 2026:

                            latest_2026_batting[
                                batter
                            ]["runs"] += (
                                batter_runs
                            )


                            if wides == 0:

                                latest_2026_batting[
                                    batter
                                ]["balls"] += 1


                            if batter_runs == 4:

                                latest_2026_batting[
                                    batter
                                ]["fours"] += 1


                            if batter_runs == 6:

                                latest_2026_batting[
                                    batter
                                ]["sixes"] += 1


                            latest_2026_batting[
                                batter
                            ]["innings"] += 1


                            latest_2026_bowling[
                                bowler
                            ]["runs"] += (
                                bowler_runs
                            )


                            if (
                                wides == 0
                                and noballs == 0
                            ):

                                latest_2026_bowling[
                                    bowler
                                ]["balls"] += 1


                            if total_runs == 0:

                                latest_2026_bowling[
                                    bowler
                                ]["dots"] += 1


                            for wicket in wickets:

                                if (
                                    wicket.get(
                                        "kind",
                                        ""
                                    )
                                    not in non_bowler_wickets
                                ):

                                    latest_2026_bowling[
                                        bowler
                                    ]["wickets"] += 1


                        # =================================================
                        # SEASON PLAYER BATTING
                        # =================================================

                        key = (
                            year,
                            batter
                        )


                        season_player_batting[
                            key
                        ]["runs"] += (
                            batter_runs
                        )


                        if wides == 0:

                            season_player_batting[
                                key
                            ]["balls"] += 1


                        if batter_runs == 4:

                            season_player_batting[
                                key
                            ]["fours"] += 1


                        if batter_runs == 6:

                            season_player_batting[
                                key
                            ]["sixes"] += 1


                        season_player_batting[
                            key
                        ]["matches"].add(
                            match_id
                        )


                        # =================================================
                        # SEASON PLAYER BOWLING
                        # =================================================

                        key = (
                            year,
                            bowler
                        )


                        season_player_bowling[
                            key
                        ]["runs"] += (
                            bowler_runs
                        )


                        if (
                            wides == 0
                            and noballs == 0
                        ):

                            season_player_bowling[
                                key
                            ]["balls"] += 1


                        if total_runs == 0:

                            season_player_bowling[
                                key
                            ]["dots"] += 1


                        for wicket in wickets:

                            if (
                                wicket.get(
                                    "kind",
                                    ""
                                )
                                not in non_bowler_wickets
                            ):

                                season_player_bowling[
                                    key
                                ]["wickets"] += 1


                        season_player_bowling[
                            key
                        ]["matches"].add(
                            match_id
                        )


            processed_matches += 1


            if (
                processed_matches % 100
                == 0
            ):

                print(
                    f"Processed matches: "
                    f"{processed_matches}"
                )


        except Exception as error:

            invalid_files.append(
                (
                    file_path.name,
                    str(error)
                )
            )


    # ========================================================
    # BATTING DATAFRAME
    # ========================================================

    batting_rows = []


    for player, values in batting.items():

        runs = values["runs"]
        balls = values["balls"]
        dismissals = values["dismissals"]


        average = (
            runs / dismissals
            if dismissals > 0
            else runs
        )


        strike_rate = (
            runs * 100 / balls
            if balls > 0
            else 0
        )


        batting_rows.append(
            {
                "player": player,
                "matches": len(
                    values["matches"]
                ),
                "teams": ", ".join(
                    sorted(
                        values["teams"]
                    )
                ),
                "innings": values["innings"],
                "runs": runs,
                "balls": balls,
                "fours": values["fours"],
                "sixes": values["sixes"],
                "dismissals": dismissals,
                "batting_average": round(
                    average,
                    2
                ),
                "strike_rate": round(
                    strike_rate,
                    2
                ),
            }
        )


    batting_df = pd.DataFrame(
        batting_rows
    )


    batting_df = batting_df.sort_values(
        by=[
            "runs",
            "strike_rate"
        ],
        ascending=[
            False,
            False
        ]
    )


    # ========================================================
    # BOWLING DATAFRAME
    # ========================================================

    bowling_rows = []


    for player, values in bowling.items():

        balls = values["balls"]
        runs = values["runs_conceded"]
        wickets = values["wickets"]


        economy = (
            runs * 6 / balls
            if balls > 0
            else 0
        )


        bowling_rows.append(
            {
                "player": player,
                "matches": len(
                    values["matches"]
                ),
                "teams": ", ".join(
                    sorted(
                        values["teams"]
                    )
                ),
                "balls": balls,
                "runs_conceded": runs,
                "wickets": wickets,
                "dot_balls": values[
                    "dot_balls"
                ],
                "economy": round(
                    economy,
                    2
                ),
            }
        )


    bowling_df = pd.DataFrame(
        bowling_rows
    )


    bowling_df = bowling_df.sort_values(
        by=[
            "wickets",
            "economy"
        ],
        ascending=[
            False,
            True
        ]
    )


    # ========================================================
    # PLAYER OF MATCH
    # ========================================================

    pom_rows = []


    for player, count in sorted(
        player_of_match.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        pom_rows.append(
            {
                "player": player,
                "player_of_match_awards": count
            }
        )


    pom_df = pd.DataFrame(
        pom_rows
    )


    # ========================================================
    # RECENT FORM
    # ========================================================

    recent_rows = []


    all_recent_players = set(
        recent_batting.keys()
    ) | set(
        recent_bowling.keys()
    )


    for player in all_recent_players:

        bat = recent_batting[
            player
        ]

        bowl = recent_bowling[
            player
        ]


        batting_sr = (
            bat["runs"] * 100 / bat["balls"]
            if bat["balls"] > 0
            else 0
        )


        bowling_economy = (
            bowl["runs"] * 6 / bowl["balls"]
            if bowl["balls"] > 0
            else 0
        )


        recent_rows.append(
            {
                "player": player,
                "recent_runs_2024_2026": bat[
                    "runs"
                ],
                "recent_balls_2024_2026": bat[
                    "balls"
                ],
                "recent_strike_rate": round(
                    batting_sr,
                    2
                ),
                "recent_fours": bat[
                    "fours"
                ],
                "recent_sixes": bat[
                    "sixes"
                ],
                "recent_wickets_2024_2026": bowl[
                    "wickets"
                ],
                "recent_bowling_runs": bowl[
                    "runs"
                ],
                "recent_bowling_balls": bowl[
                    "balls"
                ],
                "recent_economy": round(
                    bowling_economy,
                    2
                ),
                "recent_dot_balls": bowl[
                    "dots"
                ],
            }
        )


    recent_df = pd.DataFrame(
        recent_rows
    )


    # ========================================================
    # 2026 FORM
    # ========================================================

    latest_rows = []


    latest_players = set(
        latest_2026_batting.keys()
    ) | set(
        latest_2026_bowling.keys()
    )


    for player in latest_players:

        bat = latest_2026_batting[
            player
        ]

        bowl = latest_2026_bowling[
            player
        ]


        sr = (
            bat["runs"] * 100 / bat["balls"]
            if bat["balls"] > 0
            else 0
        )


        economy = (
            bowl["runs"] * 6 / bowl["balls"]
            if bowl["balls"] > 0
            else 0
        )


        latest_rows.append(
            {
                "player": player,
                "runs_2026": bat[
                    "runs"
                ],
                "balls_2026": bat[
                    "balls"
                ],
                "strike_rate_2026": round(
                    sr,
                    2
                ),
                "fours_2026": bat[
                    "fours"
                ],
                "sixes_2026": bat[
                    "sixes"
                ],
                "wickets_2026": bowl[
                    "wickets"
                ],
                "bowling_runs_2026": bowl[
                    "runs"
                ],
                "bowling_balls_2026": bowl[
                    "balls"
                ],
                "economy_2026": round(
                    economy,
                    2
                ),
                "dot_balls_2026": bowl[
                    "dots"
                ],
            }
        )


    latest_df = pd.DataFrame(
        latest_rows
    )


    # ========================================================
    # SEASON BATTING
    # ========================================================

    season_batting_rows = []


    for (
        year,
        player
    ), values in season_player_batting.items():

        balls = values["balls"]
        runs = values["runs"]


        sr = (
            runs * 100 / balls
            if balls > 0
            else 0
        )


        season_batting_rows.append(
            {
                "season": year,
                "player": player,
                "matches": len(
                    values["matches"]
                ),
                "runs": runs,
                "balls": balls,
                "fours": values["fours"],
                "sixes": values["sixes"],
                "strike_rate": round(
                    sr,
                    2
                ),
            }
        )


    season_batting_df = pd.DataFrame(
        season_batting_rows
    )


    # ========================================================
    # SEASON BOWLING
    # ========================================================

    season_bowling_rows = []


    for (
        year,
        player
    ), values in season_player_bowling.items():

        balls = values["balls"]
        runs = values["runs"]


        economy = (
            runs * 6 / balls
            if balls > 0
            else 0
        )


        season_bowling_rows.append(
            {
                "season": year,
                "player": player,
                "matches": len(
                    values["matches"]
                ),
                "balls": balls,
                "runs_conceded": runs,
                "wickets": values[
                    "wickets"
                ],
                "dot_balls": values[
                    "dots"
                ],
                "economy": round(
                    economy,
                    2
                ),
            }
        )


    season_bowling_df = pd.DataFrame(
        season_bowling_rows
    )


    # ========================================================
    # SAVE FILES
    # ========================================================

    batting_path = (
        OUTPUT_DIR
        / "player_batting_analysis.csv"
    )


    bowling_path = (
        OUTPUT_DIR
        / "player_bowling_analysis.csv"
    )


    recent_path = (
        OUTPUT_DIR
        / "player_recent_form.csv"
    )


    latest_path = (
        OUTPUT_DIR
        / "player_2026_form.csv"
    )


    pom_path = (
        OUTPUT_DIR
        / "player_of_match_counts.csv"
    )


    season_batting_path = (
        OUTPUT_DIR
        / "player_season_batting.csv"
    )


    season_bowling_path = (
        OUTPUT_DIR
        / "player_season_bowling.csv"
    )


    batting_df.to_csv(
        batting_path,
        index=False
    )


    bowling_df.to_csv(
        bowling_path,
        index=False
    )


    recent_df.to_csv(
        recent_path,
        index=False
    )


    latest_df.to_csv(
        latest_path,
        index=False
    )


    pom_df.to_csv(
        pom_path,
        index=False
    )


    season_batting_df.to_csv(
        season_batting_path,
        index=False
    )


    season_bowling_df.to_csv(
        season_bowling_path,
        index=False
    )


    # ========================================================
    # REPORTS
    # ========================================================

    batting_df.head(20).to_csv(
        REPORT_DIR / "top_20_batsmen.csv",
        index=False
    )


    bowling_df.head(20).to_csv(
        REPORT_DIR / "top_20_bowlers.csv",
        index=False
    )


    pom_df.head(20).to_csv(
        REPORT_DIR / "top_player_of_match.csv",
        index=False
    )


    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print()
    print("=" * 75)
    print("PLAYER ANALYSIS COMPLETED")
    print("=" * 75)


    print(
        f"Matches processed: "
        f"{processed_matches}"
    )


    print(
        f"Skipped matches: "
        f"{skipped_matches}"
    )


    print(
        f"Failed files: "
        f"{len(invalid_files)}"
    )


    print(
        f"Unique batsmen: "
        f"{len(batting_df)}"
    )


    print(
        f"Unique bowlers: "
        f"{len(bowling_df)}"
    )


    # ========================================================
    # TOP BATSMEN
    # ========================================================

    print()
    print("=" * 75)
    print("TOP 10 BATSMEN")
    print("=" * 75)


    if not batting_df.empty:

        print(
            batting_df[
                [
                    "player",
                    "runs",
                    "balls",
                    "batting_average",
                    "strike_rate"
                ]
            ].head(10).to_string(
                index=False
            )
        )


    # ========================================================
    # TOP BOWLERS
    # ========================================================

    print()
    print("=" * 75)
    print("TOP 10 BOWLERS")
    print("=" * 75)


    if not bowling_df.empty:

        print(
            bowling_df[
                [
                    "player",
                    "wickets",
                    "runs_conceded",
                    "economy",
                    "dot_balls"
                ]
            ].head(10).to_string(
                index=False
            )
        )


    # ========================================================
    # OUTPUT FILES
    # ========================================================

    print()
    print("=" * 75)
    print("FILES CREATED")
    print("=" * 75)


    print(
        batting_path
    )

    print(
        bowling_path
    )

    print(
        recent_path
    )

    print(
        latest_path
    )

    print(
        pom_path
    )

    print(
        season_batting_path
    )

    print(
        season_bowling_path
    )


    print()
    print("=" * 75)
    print("STEP 3 PLAYER ANALYSIS COMPLETED")
    print("=" * 75)


if __name__ == "__main__":

    main()