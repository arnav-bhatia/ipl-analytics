import pandas as pd
import numpy as np
from config import PROCESSED_FOLDER


def build_batting_innings():

    deliveries = pd.read_csv(f"{PROCESSED_FOLDER}/deliveries.csv")
    matches = pd.read_csv(f"{PROCESSED_FOLDER}/matches.csv")

    deliveries["is_ball_faced"] = np.where(
        deliveries["extra_type"] == "wides",
        0,
        1
    )


    batting = deliveries.groupby(
        [
            "season",
            "match_id",
            "innings",
            "batter",
            "batting_team"
        ]
    ).agg(
        runs=("runs_batter", "sum"),
        balls=("is_ball_faced", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum")
    ).reset_index()


    outs = deliveries[
        deliveries["player_out"].notna()
    ][["season", "match_id", "innings", "player_out"]].drop_duplicates()

    outs["out_flag"] = 1

    batting = batting.merge(
        outs,
        left_on=["season", "match_id", "innings", "batter"],
        right_on=["season", "match_id", "innings", "player_out"],
        how="left"
    )

    batting["not_out"] = np.where(
        batting["out_flag"] == 1,
        "No",
        "Yes"
    )

    batting.drop(
        columns=["player_out", "out_flag"],
        inplace=True
    )


    batting["strike_rate"] = np.where(
        batting["balls"] > 0,
        batting["runs"] / batting["balls"] * 100,
        np.nan
    ).round(2)


    batting = batting.merge(
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

    batting["opposition"] = np.where(
        batting["batting_team"] == batting["team1"],
        batting["team2"],
        batting["team1"]
    )

    batting["result"] = np.where(
        batting["batting_team"] == batting["winner"],
        "Won",
        "Lost"
    )

    batting = batting.sort_values(
        by=["season", "batting_team", "date", "match_id"]
    )

    batting["match_no"] = (
        batting.groupby(
            ["season", "batting_team"]
        )["match_id"]
        .rank(method="dense")
        .astype(int)
    )

    batting = batting.rename(columns={
        "batter": "player",
        "batting_team": "team",
        "fours": "4s",
        "sixes": "6s"
    })

    batting = batting[
        [
            "season",
            "match_id",
            "match_no",
            "date",
            "player",
            "team",
            "opposition",
            "innings",
            "runs",
            "balls",
            "not_out",
            "strike_rate",
            "4s",
            "6s",
            "result"
        ]
    ]

    batting.to_csv(
        f"{PROCESSED_FOLDER}/batting_innings.csv",
        index=False
    )

    print("batting_innings.csv created")

if __name__ == "__main__":
    build_batting_innings()