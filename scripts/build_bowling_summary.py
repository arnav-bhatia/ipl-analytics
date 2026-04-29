import pandas as pd
import numpy as np

from config import PROCESSED_FOLDER


NON_BOWLER_WICKETS = [
    "run out",
    "retired hurt",
    "obstructing the field",
    "retired out"
]


def prepare_bowling_columns():
    file_path = f"{PROCESSED_FOLDER}/deliveries.csv"
    df = pd.read_csv(file_path)

    illegal_extras = [
        "wides",
        "noballs",
        "byes,noballs",
        "legbyes,noballs"
    ]

    df["legal_delivery"] = np.where(
        df["extra_type"].isin(illegal_extras),
        0,
        1
    )

    df["bowler_runs_given"] = df["runs_batter"]

    wides_noballs = df["extra_type"].isin(["wides", "noballs"])
    df.loc[wides_noballs, "bowler_runs_given"] = df["runs_total"]

    combo_no_balls = df["extra_type"].isin(
        ["byes,noballs", "legbyes,noballs"]
    )
    df.loc[combo_no_balls, "bowler_runs_given"] = (
        df["runs_batter"] + 1
    )

    df["is_bowler_wicket"] = np.where(
        (df["is_wicket"] == 1)
        & (~df["dismissal_type"].isin(NON_BOWLER_WICKETS)),
        1,
        0
    )

    df["bowler_extras_given"] = np.where(
        df["extra_type"].isin(
            ["byes,noballs", "legbyes,noballs"]
        ),
        1,
        np.where(
            df["runs_extras"] > 0,
            df["bowler_runs_given"],
            0
        )
    )

    df["wide_runs"] = np.where(
        df["extra_type"] == "wides",
        df["runs_extras"],
        0
    )

    df["no_ball_runs"] = np.where(
        df["extra_type"] == "noballs",
        df["runs_total"],
        0
    )

    return df


def build_bowling_summary(df):
    bowling = df.groupby(
        ["season", "bowler", "bowling_team"]
    ).agg(
        matches=("match_id", "nunique"),
        balls=("legal_delivery", "sum"),
        runs_given=("bowler_runs_given", "sum"),
        wickets=("is_bowler_wicket", "sum"),
        dots=("is_dot", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        wides=("wide_runs", "sum"),
        no_balls=("no_ball_runs", "sum"),
        extras_given=("bowler_extras_given", "sum")
    ).reset_index()

    bowling["overs_float"] = bowling["balls"] / 6

    bowling["overs"] = (
        (bowling["balls"] // 6).astype(str)
        + "."
        + (bowling["balls"] % 6).astype(str)
    )

    bowling["economy_rate"] = (
        bowling["runs_given"] / bowling["overs_float"]
    ).round(2)

    bowling["strike_rate"] = np.where(
        bowling["wickets"] > 0,
        bowling["balls"] / bowling["wickets"],
        np.nan
    ).round(2)

    bowling["average"] = np.where(
        bowling["wickets"] > 0,
        bowling["runs_given"] / bowling["wickets"],
        np.nan
    ).round(2)

    bowling["boundaries_conceded"] = (
        bowling["fours"] + bowling["sixes"]
    )

    bowling.drop(columns=["overs_float"], inplace=True)

    bowling = bowling.rename(columns={
        "season": "Year",
        "bowler": "Player",
        "bowling_team": "Team",
        "matches": "Matches",
        "balls": "Balls",
        "overs": "Overs",
        "runs_given": "Runs Given",
        "wickets": "Wickets",
        "economy_rate": "Economy Rate",
        "strike_rate": "Strike Rate",
        "average": "Average",
        "dots": "Dots",
        "fours": "4s",
        "sixes": "6s",
        "wides": "Wides",
        "no_balls": "No Balls",
        "extras_given": "Extras Given",
        "boundaries_conceded": "Boundaries Conceded"
    })


    bowling = bowling[
        [
            "Year", "Player", "Team", "Matches",
            "Balls", "Overs", "Runs Given",
            "Wickets", "Economy Rate",
            "Average", "Strike Rate",
            "Dots", "4s", "6s",
            "Boundaries Conceded",
            "Wides", "No Balls",
            "Extras Given"
        ]
    ]

    bowling.to_csv(
        f"{PROCESSED_FOLDER}/bowling_summary.csv",
        index=False
    )

    print("bowling_summary.csv created")

if __name__ == "__main__":
    deliveries_df = prepare_bowling_columns()
    build_bowling_summary(deliveries_df)