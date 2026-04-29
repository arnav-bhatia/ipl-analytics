import pandas as pd
import numpy as np

from config import PROCESSED_FOLDER


def prepare_bowling_columns():

    NON_BOWLER_WICKETS = [
    "run out",
    "retired hurt",
    "obstructing the field",
    "retired out"
    ]

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

def calculate_bowling_metrics(df):
    df["overs_float"] = df["balls"] / 6

    df["overs"] = (
        (df["balls"] // 6).astype(str)
        + "."
        + (df["balls"] % 6).astype(str)
    )

    df["economy_rate"] = (
        df["runs_given"] / df["overs_float"]
    ).round(2)

    df["strike_rate"] = np.where(
        df["wickets"] > 0,
        df["balls"] / df["wickets"],
        np.nan
    ).round(2)

    df["average"] = np.where(
        df["wickets"] > 0,
        df["runs_given"] / df["wickets"],
        np.nan
    ).round(2)

    df["boundaries_conceded"] = (
        df["fours"] + df["sixes"]
    )

    return df