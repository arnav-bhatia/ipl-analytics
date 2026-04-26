import pandas as pd
import numpy as np
from config import PROCESSED_FOLDER

def assign_role(avg_position):
    if avg_position <= 3:
        return "Top Order"
    elif avg_position <= 6:
        return "Middle Order"
    else:
        return "Lower Order"

def build_batting_summary():
    file_path = f"{PROCESSED_FOLDER}/deliveries.csv"
    df = pd.read_csv(file_path)


    df["is_ball_faced"] = np.where(df["extra_type"] == "wides", 0, 1)


    positions = []

    innings_groups = df.groupby(["match_id", "innings"])

    for (match_id, innings), group in innings_groups:

        seen = []
        batting_order = {}

        for _, row in group.iterrows():

            batter = row["batter"]
            non_striker = row["non_striker"]

            for player in [batter, non_striker]:
                if player not in seen:
                    seen.append(player)
                    batting_order[player] = len(seen)

        for player, pos in batting_order.items():
            positions.append({
                "match_id": match_id,
                "innings": innings,
                "Player": player,
                "Position": pos
            })

    positions_df = pd.DataFrame(positions)

    season_lookup = df[["match_id", "season"]].drop_duplicates()
    positions_df = positions_df.merge(season_lookup, on="match_id", how="left")

    avg_pos = positions_df.groupby(
        ["season", "Player"]
    )["Position"].mean().reset_index()

    avg_pos["Role"] = avg_pos["Position"].apply(assign_role)


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

    batting = batting.merge(
        avg_pos[["season", "Player", "Role"]],
        left_on=["season", "batter"],
        right_on=["season", "Player"],
        how="left"
    )

    batting = batting.drop(columns=["Player"])

    batting["average"] = pd.to_numeric(
        batting["average"], errors="coerce"
    ).round(2)

    batting["strike_rate"] = pd.to_numeric(
        batting["strike_rate"], errors="coerce"
    ).round(2)

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

    batting = batting[
        [
            "Year", "Player", "Team", "Role",
            "Innings", "Outs", "Runs", "Balls",
            "Average", "Strike Rate",
            "50s", "100s", "4s", "6s"
        ]
    ]

    batting.to_csv(
        f"{PROCESSED_FOLDER}/batting_summary.csv",
        index=False
    )

    print("batting_summary.csv created")


if __name__ == "__main__":
    build_batting_summary()