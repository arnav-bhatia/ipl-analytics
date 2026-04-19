import json
import os
import pandas as pd

DATA_PATH = "data/raw_json"
OUTPUT_PATH = "data/processed"

os.makedirs(OUTPUT_PATH, exist_ok=True)

match_rows = []
delivery_rows = []

for filename in os.listdir(DATA_PATH):
    
    if filename.endswith(".json"):
        
        file_path = os.path.join(DATA_PATH, filename)

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

                    batter = delivery.get("batter")
                    bowler = delivery.get("bowler")
                    non_striker = delivery.get("non_striker")

                    runs_batter = delivery["runs"].get("batter", 0)
                    runs_extras = delivery["runs"].get("extras", 0)
                    runs_total = delivery["runs"].get("total", 0)

                    extras = delivery.get("extras", {})
                    extra_type = ",".join(extras.keys()) if extras else None

                    is_wicket = 1 if "wickets" in delivery else 0

                    if is_wicket:
                        wicket_info = delivery["wickets"][0]
                        player_out = wicket_info.get("player_out")
                        kind = wicket_info.get("kind")

                        fielders = ",".join(
                            f["name"] for f in wicket_info.get("fielders", [])
                        ) or None
                    else:
                        player_out = None
                        kind = None
                        fielders = None

                    is_four = 1 if runs_batter == 4 else 0
                    is_six = 1 if runs_batter == 6 else 0
                    is_dot = 1 if runs_total == 0 else 0

                    if over_num <= 6:
                        phase = "Powerplay"
                    elif over_num <= 15:
                        phase = "Middle"
                    else:
                        phase = "Death"

                    delivery_row = {
                        "match_id": match_id,
                        "innings": innings_num,
                        "batting_team": batting_team,
                        "over": over_num,
                        "ball": ball_idx,
                        "batter": batter,
                        "bowler": bowler,
                        "non_striker": non_striker,
                        "runs_batter": runs_batter,
                        "runs_extras": runs_extras,
                        "runs_total": runs_total,
                        "extra_type": extra_type,
                        "is_wicket": is_wicket,
                        "player_out": player_out,
                        "dismissal_type": kind,
                        "fielders": fielders,
                        "is_four": is_four,
                        "is_six": is_six,
                        "is_dot": is_dot,
                        "phase": phase
                    }

                    delivery_rows.append(delivery_row)

matches_df = pd.DataFrame(match_rows)
deliveries_df = pd.DataFrame(delivery_rows)

matches_df.to_csv("data/processed/matches.csv", index=False)
deliveries_df.to_csv("data/processed/deliveries.csv", index=False)

print("CSV files created!")
print(f"Matches: {len(matches_df)}")
print(f"Deliveries: {len(deliveries_df)}")