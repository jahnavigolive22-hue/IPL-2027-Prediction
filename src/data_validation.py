from pathlib import Path
import json
from collections import Counter

# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

JSON_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "cricsheet_ipl"
)

EXPECTED_MATCHES = 1243

START_YEAR = 2008
END_YEAR = 2026


# =========================================================
# GET IPL YEAR FROM ACTUAL MATCH DATE
# =========================================================

def get_ipl_year(info):
    """
    Determine the IPL season year using the actual match date.

    Example:
        2020-09-19 -> 2020
        2021-04-09 -> 2021
        2026-05-31 -> 2026

    This avoids problems with Cricsheet season values such as:
        2007/08
        2020/21
    """

    dates = info.get("dates", [])

    if not dates:
        return None

    first_date = str(dates[0]).strip()

    try:
        year = int(first_date[:4])
        return year

    except (ValueError, TypeError):
        return None


# =========================================================
# MAIN
# =========================================================

print("=" * 70)
print("CRICSHEET IPL DATA VALIDATION - FINAL VERSION")
print("=" * 70)


# =========================================================
# CHECK FOLDER
# =========================================================

if not JSON_DIR.exists():

    raise FileNotFoundError(
        f"\nCricsheet folder not found:\n{JSON_DIR}"
    )


# =========================================================
# FIND JSON FILES
# =========================================================

json_files = sorted(
    JSON_DIR.rglob("*.json")
)

print()
print(
    f"JSON files physically present: "
    f"{len(json_files)}"
)


# =========================================================
# COUNTERS
# =========================================================

season_counts = Counter()

event_counts = Counter()

valid_ipl_matches = 0

invalid_files = []

sample_records = []


# =========================================================
# PROCESS EVERY JSON FILE
# =========================================================

for file_path in json_files:

    try:

        # -------------------------------------------------
        # READ JSON
        # -------------------------------------------------

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)


        # -------------------------------------------------
        # INFO
        # -------------------------------------------------

        info = data.get(
            "info",
            {}
        )


        # -------------------------------------------------
        # EVENT
        # -------------------------------------------------

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


        event_name = str(
            event_name
        ).strip()


        event_counts[event_name] += 1


        # -------------------------------------------------
        # IPL CHECK
        # -------------------------------------------------

        is_ipl = (
            event_name.lower()
            == "indian premier league"
        )


        if not is_ipl:

            continue


        # -------------------------------------------------
        # ACTUAL IPL YEAR
        # -------------------------------------------------

        ipl_year = get_ipl_year(
            info
        )


        # -------------------------------------------------
        # YEAR VALIDATION
        # -------------------------------------------------

        if ipl_year is None:

            continue


        if not (
            START_YEAR
            <= ipl_year
            <= END_YEAR
        ):

            continue


        # -------------------------------------------------
        # COUNT
        # -------------------------------------------------

        season_counts[
            ipl_year
        ] += 1

        valid_ipl_matches += 1


        # -------------------------------------------------
        # SAMPLE
        # -------------------------------------------------

        if len(sample_records) < 10:

            original_season = info.get(
                "season",
                "N/A"
            )

            sample_records.append(
                (
                    file_path.name,
                    original_season,
                    ipl_year
                )
            )


    except Exception as error:

        invalid_files.append(
            (
                file_path.name,
                str(error)
            )
        )


# =========================================================
# IPL SEASON-WISE COUNT
# =========================================================

print()
print("=" * 70)
print("IPL SEASON-WISE MATCH COUNT")
print("=" * 70)


for year in range(
    START_YEAR,
    END_YEAR + 1
):

    count = season_counts.get(
        year,
        0
    )

    print(
        f"{year}: {count}"
    )


# =========================================================
# EVENT VALIDATION
# =========================================================

print()
print("=" * 70)
print("EVENT VALIDATION")
print("=" * 70)


for event_name, count in (
    event_counts
    .most_common()
):

    print(
        f"{event_name}: {count}"
    )


# =========================================================
# VALIDATION SUMMARY
# =========================================================

print()
print("=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)


print(
    f"JSON files physically present: "
    f"{len(json_files)}"
)


print(
    f"Valid IPL matches "
    f"(2008-2026): "
    f"{valid_ipl_matches}"
)


print(
    f"Expected IPL coverage: "
    f"{EXPECTED_MATCHES}"
)


difference = (
    EXPECTED_MATCHES
    - valid_ipl_matches
)


print(
    f"Difference: "
    f"{difference}"
)


print(
    f"Invalid/unreadable JSON files: "
    f"{len(invalid_files)}"
)


# =========================================================
# STATUS
# =========================================================

print()
print("=" * 70)


if (
    valid_ipl_matches
    == EXPECTED_MATCHES
    and len(invalid_files) == 0
):

    print("STATUS: PASSED")

    print(
        "All 1243 IPL matches from "
        "2008-2026 are correctly detected."
    )

else:

    print("STATUS: NEEDS REVIEW")

    print(
        "IPL data validation is not complete."
    )


# =========================================================
# INVALID FILES
# =========================================================

print()
print("=" * 70)
print("INVALID / UNREADABLE FILES")
print("=" * 70)


if not invalid_files:

    print(
        "No invalid JSON files."
    )

else:

    for filename, error in invalid_files:

        print(
            f"{filename} -> {error}"
        )


# =========================================================
# SAMPLE MATCHES
# =========================================================

print()
print("=" * 70)
print("SAMPLE IPL MATCHES")
print("=" * 70)


for (
    filename,
    original_season,
    converted_year
) in sample_records:

    print(
        f"{filename} | "
        f"Original season: {original_season} | "
        f"IPL year: {converted_year}"
    )


# =========================================================
# FINAL
# =========================================================

print()
print("=" * 70)
print("VALIDATION COMPLETE")
print("=" * 70)