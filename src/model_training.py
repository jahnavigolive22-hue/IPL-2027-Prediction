"""
IPL 2027 PREDICTION - MODEL TRAINING

Historical IPL team-season data:
    2008-2026

Target:
    Champion = 1
    Non-champion = 0

The model learns from previous-season team performance
to reduce direct future-season information leakage.

Outputs:
    models/champion_prediction_model.pkl
    outputs/reports/model_training_results.csv
    outputs/reports/model_feature_importance.csv
"""

from pathlib import Path
import warnings
import pickle

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORT_DIR = BASE_DIR / "outputs" / "reports"
MODEL_DIR = BASE_DIR / "models"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)


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
# TEAM NAME ALIASES
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

    "Rising Pune Supergiants":
        "Rising Pune Supergiants",

    "Rising Pune Supergiant":
        "Rising Pune Supergiants",

    "Pune Warriors":
        "Pune Warriors India",

    "Pune Warriors India":
        "Pune Warriors India",
}


def normalize_team(team):

    if pd.isna(team):
        return team

    team = str(team).strip()

    return TEAM_ALIASES.get(team, team)


# ============================================================
# SAFE NUMERIC
# ============================================================

def to_numeric(series):

    return pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)


# ============================================================
# LOAD TEAM SEASON DATA
# ============================================================

def load_team_season_data():

    path = (
        PROCESSED_DIR /
        "team_season_analysis.csv"
    )

    if not path.exists():

        raise FileNotFoundError(
            "team_season_analysis.csv not found."
        )

    df = pd.read_csv(path)

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]

    # --------------------------------------------------------
    # TEAM
    # --------------------------------------------------------

    team_col = None

    for col in ["team", "Team", "TEAM"]:

        if col in df.columns:
            team_col = col
            break

    if team_col is None:

        raise ValueError(
            "Team column not found."
        )

    df["team"] = (
        df[team_col]
        .apply(normalize_team)
    )

    # --------------------------------------------------------
    # SEASON
    # --------------------------------------------------------

    season_col = None

    for col in [
        "season",
        "Season",
        "year",
        "Year"
    ]:

        if col in df.columns:

            season_col = col
            break

    if season_col is None:

        raise ValueError(
            "Season column not found."
        )

    df["season"] = pd.to_numeric(
        df[season_col],
        errors="coerce"
    )

    df = df.dropna(
        subset=["season"]
    )

    df["season"] = (
        df["season"]
        .astype(int)
    )

    # --------------------------------------------------------
    # MATCHES
    # --------------------------------------------------------

    matches_col = None

    for col in [
        "matches",
        "Matches",
        "matches_played",
        "Matches_Played"
    ]:

        if col in df.columns:

            matches_col = col
            break

    if matches_col:

        df["matches"] = to_numeric(
            df[matches_col]
        )

    else:

        df["matches"] = 0

    # --------------------------------------------------------
    # WINS
    # --------------------------------------------------------

    wins_col = None

    for col in [
        "wins",
        "Wins",
        "win"
    ]:

        if col in df.columns:

            wins_col = col
            break

    if wins_col:

        df["wins"] = to_numeric(
            df[wins_col]
        )

    else:

        df["wins"] = 0

    # --------------------------------------------------------
    # LOSSES
    # --------------------------------------------------------

    losses_col = None

    for col in [
        "losses",
        "Losses",
        "loss"
    ]:

        if col in df.columns:

            losses_col = col
            break

    if losses_col:

        df["losses"] = to_numeric(
            df[losses_col]
        )

    else:

        df["losses"] = np.maximum(
            df["matches"] - df["wins"],
            0
        )

    # --------------------------------------------------------
    # WIN PERCENTAGE
    # --------------------------------------------------------

    if "win_percentage" in df.columns:

        df["win_percentage"] = to_numeric(
            df["win_percentage"]
        )

    elif "win_pct" in df.columns:

        df["win_percentage"] = to_numeric(
            df["win_pct"]
        )

    else:

        df["win_percentage"] = np.where(
            df["matches"] > 0,
            df["wins"] /
            df["matches"] * 100,
            0
        )

    return df


# ============================================================
# LOAD CHAMPION HISTORY
# ============================================================

def load_champions():

    path = (
        REPORT_DIR /
        "ipl_champions_2008_2026.csv"
    )

    if not path.exists():

        raise FileNotFoundError(
            "ipl_champions_2008_2026.csv not found."
        )

    champions = pd.read_csv(path)

    champions.columns = [
        str(col).strip()
        for col in champions.columns
    ]

    # Find season column
    season_col = None

    for col in [
        "season",
        "Season",
        "year",
        "Year"
    ]:

        if col in champions.columns:

            season_col = col
            break

    if season_col is None:

        raise ValueError(
            "Season column not found "
            "in champion file."
        )

    # Find champion column
    champion_col = None

    for col in [
        "champion",
        "Champion",
        "winner",
        "Winner",
        "team",
        "Team"
    ]:

        if col in champions.columns:

            champion_col = col
            break

    if champion_col is None:

        raise ValueError(
            "Champion column not found."
        )

    champions = champions[
        [season_col, champion_col]
    ].copy()

    champions.columns = [
        "season",
        "champion"
    ]

    champions["season"] = pd.to_numeric(
        champions["season"],
        errors="coerce"
    )

    champions["champion"] = (
        champions["champion"]
        .apply(normalize_team)
    )

    champions = champions.dropna(
        subset=["season", "champion"]
    )

    champions["season"] = (
        champions["season"]
        .astype(int)
    )

    return champions


# ============================================================
# CREATE LEAKAGE-SAFE TRAINING DATA
# ============================================================

def create_training_data(
    team_df,
    champions
):

    df = team_df.copy()

    # --------------------------------------------------------
    # Champion label for each season
    # --------------------------------------------------------

    champion_map = dict(
        zip(
            champions["season"],
            champions["champion"]
        )
    )

    df["champion_team"] = (
        df["season"]
        .map(champion_map)
    )

    df["champion"] = (
        df["team"] ==
        df["champion_team"]
    ).astype(int)

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    df = df.sort_values(
        ["team", "season"]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Previous-season features
    # --------------------------------------------------------

    base_features = [
        "matches",
        "wins",
        "losses",
        "win_percentage",
    ]

    for feature in base_features:

        df[
            f"previous_{feature}"
        ] = (
            df
            .groupby("team")[feature]
            .shift(1)
        )

    # --------------------------------------------------------
    # Rolling performance
    # --------------------------------------------------------

    df["previous_2_season_win_pct"] = (
        df
        .groupby("team")["win_percentage"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=2,
                min_periods=1
            )
            .mean()
        )
    )

    df["previous_3_season_win_pct"] = (
        df
        .groupby("team")["win_percentage"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=3,
                min_periods=1
            )
            .mean()
        )
    )

    # --------------------------------------------------------
    # Historical title count BEFORE current season
    # --------------------------------------------------------

    df["previous_titles"] = 0

    for team in df["team"].unique():

        team_mask = (
            df["team"] == team
        )

        count = 0

        indices = df[
            team_mask
        ].index.tolist()

        for idx in indices:

            df.loc[
                idx,
                "previous_titles"
            ] = count

            if df.loc[
                idx,
                "champion"
            ] == 1:

                count += 1

    # --------------------------------------------------------
    # Drop first season for teams
    # --------------------------------------------------------

    df = df[
        df["previous_matches"].notna()
    ].copy()

    return df


# ============================================================
# FEATURE LIST
# ============================================================

FEATURES = [
    "previous_matches",
    "previous_wins",
    "previous_losses",
    "previous_win_percentage",
    "previous_2_season_win_pct",
    "previous_3_season_win_pct",
    "previous_titles",
]


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model(training_df):

    X = training_df[
        FEATURES
    ].copy()

    y = training_df[
        "champion"
    ].astype(int)

    # --------------------------------------------------------
    # Fill missing values
    # --------------------------------------------------------

    X = X.replace(
        [np.inf, -np.inf],
        np.nan
    )

    X = X.fillna(0)

    # --------------------------------------------------------
    # Chronological split
    # --------------------------------------------------------

    train_mask = (
        training_df["season"] <= 2023
    )

    test_mask = (
        training_df["season"] >= 2024
    )

    X_train = X.loc[
        train_mask
    ]

    y_train = y.loc[
        train_mask
    ]

    X_test = X.loc[
        test_mask
    ]

    y_test = y.loc[
        test_mask
    ]

    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=7,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    try:

        roc_auc = roc_auc_score(
            y_test,
            probabilities
        )

    except ValueError:

        roc_auc = np.nan

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1]
    )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results = pd.DataFrame({
        "metric": [
            "training_records",
            "test_records",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "roc_auc",
            "true_negative",
            "false_positive",
            "false_negative",
            "true_positive",
        ],
        "value": [
            len(X_train),
            len(X_test),
            round(accuracy, 4),
            round(precision, 4),
            round(recall, 4),
            round(f1, 4),
            round(roc_auc, 4)
            if not np.isnan(roc_auc)
            else np.nan,
            int(cm[0, 0]),
            int(cm[0, 1]),
            int(cm[1, 0]),
            int(cm[1, 1]),
        ]
    })

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance = pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_,
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    ).reset_index(drop=True)

    importance["importance"] = (
        importance["importance"]
        .round(6)
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    model_path = (
        MODEL_DIR /
        "champion_prediction_model.pkl"
    )

    model_package = {
        "model": model,
        "features": FEATURES,
        "training_period": "2009-2023",
        "validation_period": "2024-2026",
        "target": "champion",
        "model_type": "RandomForestClassifier",
    }

    with open(
        model_path,
        "wb"
    ) as file:

        pickle.dump(
            model_package,
            file
        )

    # --------------------------------------------------------
    # Save reports
    # --------------------------------------------------------

    results_path = (
        REPORT_DIR /
        "model_training_results.csv"
    )

    importance_path = (
        REPORT_DIR /
        "model_feature_importance.csv"
    )

    results.to_csv(
        results_path,
        index=False
    )

    importance.to_csv(
        importance_path,
        index=False
    )

    return (
        model,
        results,
        importance,
        model_path
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("IPL CHAMPION PREDICTION MODEL TRAINING")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # Load data
        # ----------------------------------------------------

        print()
        print(
            "Loading team-season data..."
        )

        team_df = (
            load_team_season_data()
        )

        print(
            f"Team-season records: "
            f"{len(team_df)}"
        )

        # ----------------------------------------------------
        # Load champions
        # ----------------------------------------------------

        print()
        print(
            "Loading champion history..."
        )

        champions = (
            load_champions()
        )

        print(
            f"Champion seasons: "
            f"{len(champions)}"
        )

        # ----------------------------------------------------
        # Create training dataset
        # ----------------------------------------------------

        print()
        print(
            "Creating leakage-safe "
            "training features..."
        )

        training_df = (
            create_training_data(
                team_df,
                champions
            )
        )

        print(
            f"Training records created: "
            f"{len(training_df)}"
        )

        print(
            f"Feature count: "
            f"{len(FEATURES)}"
        )

        # ----------------------------------------------------
        # Target distribution
        # ----------------------------------------------------

        print()
        print(
            "Champion / non-champion "
            "distribution:"
        )

        print(
            training_df[
                "champion"
            ].value_counts()
            .sort_index()
            .to_string()
        )

        # ----------------------------------------------------
        # Train
        # ----------------------------------------------------

        print()
        print(
            "Training prediction model..."
        )

        (
            model,
            results,
            importance,
            model_path
        ) = train_model(
            training_df
        )

        # ----------------------------------------------------
        # Print metrics
        # ----------------------------------------------------

        print()
        print(
            "MODEL VALIDATION RESULTS"
        )

        print("-" * 50)

        print(
            results.to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # Feature importance
        # ----------------------------------------------------

        print()
        print(
            "FEATURE IMPORTANCE"
        )

        print("-" * 50)

        print(
            importance.to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # Final files
        # ----------------------------------------------------

        print()
        print(
            "MODEL FILE:"
        )

        print(
            model_path
        )

        print()
        print(
            "REPORTS:"
        )

        print(
            REPORT_DIR /
            "model_training_results.csv"
        )

        print(
            REPORT_DIR /
            "model_feature_importance.csv"
        )

        print()
        print(
            "=" * 70
        )

        print(
            "MODEL TRAINING COMPLETED SUCCESSFULLY"
        )

        print(
            "=" * 70
        )

    except Exception as error:

        print()
        print(
            "[ERROR]",
            str(error)
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()