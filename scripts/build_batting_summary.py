import pandas as pd
import numpy as np
from config import PROCESSED_FOLDER

def build_batting_summary():
    file_path = f"{PROCESSED_FOLDER}/deliveries.csv"
    df = pd.read_csv(file_path)

    df["is_ball_faced"] = np.where(df["extra_type"] == "wides", 0, 1)

    batting = df.groupby(["season", "batter", "batting_team"]).agg(
        innings=("match_id", "nunique"),
        runs=("runs_batter", "sum"),
        balls=("is_ball_faced", "sum"),
        fours=("is_four", "sum"),
        sixes=("is_six", "sum")
    ).reset_index()

    outs = (
        df[df["player_out"].notna()]
        .groupby(["season", "player_out"])
        .size()
        .reset_index(name="outs")
        .rename(columns={"player_out": "batter"})
    )

    batting = batting.merge(
        outs,
        on=["season", "batter"],
        how="left"
    )

    batting["outs"] = batting["outs"].fillna(0)

    batting["average"] = np.where(
        batting["outs"] > 0,
        batting["runs"] / batting["outs"],
        np.nan
    )

    batting["strike_rate"] = np.where(
        batting["balls"] > 0,
        batting["runs"] / batting["balls"] * 100,
        np.nan
    )

    innings_scores = df.groupby(
        ["season", "match_id", "innings", "batter"]
    )["runs_batter"].sum().reset_index()

    fifties = innings_scores[
        (innings_scores["runs_batter"] >= 50) &
        (innings_scores["runs_batter"] < 100)
    ].groupby(["season", "batter"]).size().reset_index(name="fifties")

    hundreds = innings_scores[
        innings_scores["runs_batter"] >= 100
    ].groupby(["season", "batter"]).size().reset_index(name="hundreds")

    batting = batting.merge(fifties, on=["season", "batter"], how="left")
    batting = batting.merge(hundreds, on=["season", "batter"], how="left")

    batting["fifties"] = batting["fifties"].fillna(0).astype(int)
    batting["hundreds"] = batting["hundreds"].fillna(0).astype(int)

    batting = batting.rename(columns={
        "season": "Year",
        "batter": "Player",
        "batting_team": "Team",
        "innings": "Innings",
        "outs": "Outs",
        "runs": "Runs",
        "balls": "Balls",
        "average": "Average",
        "strike_rate": "Strike Rate",
        "fours": "4s",
        "sixes": "6s",
        "fifties": "50s",
        "hundreds": "100s"
    })

    batting.to_csv(
        f"{PROCESSED_FOLDER}/batting_summary.csv",
        index=False
    )

    print("batting_summary.csv created")

if __name__ == "__main__":
    build_batting_summary()