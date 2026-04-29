import pandas as pd
import numpy as np

from config import PROCESSED_FOLDER
from utils import bowling_helper_functions

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

    bowling = bowling_helper_functions.calculate_bowling_metrics(bowling)

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
    deliveries_df = bowling_helper_functions.prepare_bowling_columns()
    build_bowling_summary(deliveries_df)