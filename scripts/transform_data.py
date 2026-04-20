import json
import os
import pandas as pd

from config import RAW_FOLDER, PROCESSED_FOLDER

def build_csvs():
    match_rows = []
    delivery_rows = []

    for filename in os.listdir(RAW_FOLDER):

        if filename.endswith(".json"):

            file_path = os.path.join(RAW_FOLDER, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            match_id = filename.replace(".json", "")
            match_info = data["info"]

            match_row = {
                "match_id": match_id,
                "season": match_info.get("season"),
                "date": match_info.get("dates", [None])[0],
                "team1": match_info.get("teams", [None, None])[0],
                "team2": match_info.get("teams", [None, None])[1],
                "venue": match_info.get("venue"),
                "city": match_info.get("city"),
                "toss_winner": match_info.get("toss", {}).get("winner"),
                "toss_decision": match_info.get("toss", {}).get("decision"),
                "winner": match_info.get("outcome", {}).get("winner")
            }

            match_rows.append(match_row)

            for innings_num, innings in enumerate(data["innings"], start=1):

                batting_team = innings["team"]

                for over_data in innings["overs"]:

                    over_num = over_data["over"] + 1

                    for ball_idx, delivery in enumerate(over_data["deliveries"], start=1):

                        runs_batter = delivery["runs"].get("batter", 0)
                        runs_total = delivery["runs"].get("total", 0)

                        extras = delivery.get("extras", {})
                        extra_type = ",".join(extras.keys()) if extras else None

                        is_wicket = 1 if "wickets" in delivery else 0

                        if is_wicket:
                            wicket_info = delivery["wickets"][0]
                            player_out = wicket_info.get("player_out")
                            dismissal_type = wicket_info.get("kind")
                            fielders = ",".join(
                                f["name"] for f in wicket_info.get("fielders", [])
                            ) or None
                        else:
                            player_out = None
                            dismissal_type = None
                            fielders = None

                        if over_num <= 6:
                            phase = "Powerplay"
                        elif over_num <= 15:
                            phase = "Middle"
                        else:
                            phase = "Death"

                        delivery_rows.append({
                            "match_id": match_id,
                            "innings": innings_num,
                            "batting_team": batting_team,
                            "over": over_num,
                            "ball": ball_idx,
                            "batter": delivery.get("batter"),
                            "bowler": delivery.get("bowler"),
                            "non_striker": delivery.get("non_striker"),
                            "runs_batter": runs_batter,
                            "runs_extras": delivery["runs"].get("extras", 0),
                            "runs_total": runs_total,
                            "extra_type": extra_type,
                            "is_wicket": is_wicket,
                            "player_out": player_out,
                            "dismissal_type": dismissal_type,
                            "fielders": fielders,
                            "is_four": 1 if runs_batter == 4 else 0,
                            "is_six": 1 if runs_batter == 6 else 0,
                            "is_dot": 1 if runs_total == 0 else 0,
                            "phase": phase
                        })

    matches_df = pd.DataFrame(match_rows)
    deliveries_df = pd.DataFrame(delivery_rows)

    matches_path = os.path.join(PROCESSED_FOLDER, "matches.csv")
    deliveries_path = os.path.join(PROCESSED_FOLDER, "deliveries.csv")

    matches_df.to_csv(matches_path, index=False)
    deliveries_df.to_csv(deliveries_path, index=False)

    print("CSV files created!")
    print(f"Matches: {len(matches_df)}")
    print(f"Deliveries: {len(deliveries_df)}")

    return len(matches_df), len(deliveries_df)

if __name__ == "__main__":
    build_csvs()