import pandas as pd
import numpy as np

from config import PROCESSED_FOLDER
from utils import bowling_helper_functions
    
def build_bowling_innings(df):
    matches = pd.read_csv(f"{PROCESSED_FOLDER}/matches.csv")
    bowling = df.groupby(["season", "bowler", "match_id", "bowling_team"]).agg(
        balls=("legal_delivery", "sum"),
        runs_given=("bowler_runs_given", "sum"),
        wickets = ("is_bowler_wicket", "sum"),
        dots = ("is_dot", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum"),
        wides = ("wide_runs", "sum"),
        no_balls = ("no_ball_runs", "sum"),
        extras_given = ("bowler_extras_given", "sum")
    ).reset_index()

    bowling = bowling_helper_functions.calculate_bowling_metrics(bowling)

    bowling = bowling.merge(
        matches[
            [
                "match_id",
                "date",
                "team1",
                "team2",
                "winner"
            ]
        ],
        on="match_id",
        how="left"
    )

    bowling["opposition"] = np.where(
        bowling["bowling_team"] == bowling["team1"],
        bowling["team2"],
        bowling["team1"]
    )

    bowling["result"] = np.where(
        bowling["winner"].isna(),
        "No Result",
        np.where(
            bowling["bowling_team"] == bowling["winner"],
            "Won",
            "Lost"
        )
    )   

    bowling = bowling.sort_values(
    by=["season", "bowling_team", "date", "match_id"]
    )

    bowling["match_no"] = (
        bowling.groupby(
            ["season", "bowling_team"]
        )["match_id"]
        .rank(method="dense")
        .astype(int)
    )

    bowling.drop(columns=["overs_float"], inplace=True)

    bowling = bowling.rename(columns={
        "season": "Year",
        "date": "Date",
        "match_no": "Match Number",
        "bowler": "Player",
        "bowling_team": "Team",
        "opposition": "Opposition",
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
        "boundaries_conceded": "Boundaries Conceded",
        "result": "Result"
    })

    bowling = bowling[
        [
            "Year", "Player", "Team", "Match Number", "Opposition", "Date",
            "Balls", "Overs", "Runs Given",
            "Wickets", "Economy Rate",
            "Average", "Strike Rate",
            "Dots", "4s", "6s",
            "Boundaries Conceded",
            "Wides", "No Balls", 
            "Extras Given", "Result"
        ]
    ]

    bowling.to_csv(
        f"{PROCESSED_FOLDER}/bowling_innings.csv",
        index=False
    )

    print("bowling_innings.csv created")

if __name__ == "__main__":
    deliveries_df = bowling_helper_functions.prepare_bowling_columns()
    build_bowling_innings(deliveries_df)