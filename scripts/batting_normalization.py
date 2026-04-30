import pandas as pd

from config import PROCESSED_FOLDER

batting_summary = pd.read_csv(
    f"{PROCESSED_FOLDER}/batting_summary.csv"
)

batting_context = batting_summary.groupby(
    ["Year", "Role"]
).agg(
    Runs=("Runs", "sum"),
    Balls=("Balls", "sum"),
    Outs=("Outs", "sum"),
    Innings=("Innings", "sum"),
    Players=("Player", "nunique")
).reset_index()

batting_context["Average"] = (
    batting_context["Runs"] / batting_context["Outs"]
)

batting_context["Strike Rate"] = (
    batting_context["Runs"] / batting_context["Balls"] * 100
)

batting_context["Average"] = batting_context["Average"].fillna(0)
batting_context["Strike Rate"] = batting_context["Strike Rate"].fillna(0)

batting_context[["Average", "Strike Rate"]] = (
    batting_context[["Average", "Strike Rate"]]
    .round(2)
)


batting_context.to_csv(
    f"{PROCESSED_FOLDER}/batting_context.csv",
    index=False
)

print("batting_context.csv created")