from scripts import build_batting_summary, build_batting_innings, build_bowling_summary, build_bowling_innings
from utils import bowling_helper_functions

def create_summaries():

    print("Creating batting summary...")
    build_batting_summary.build_batting_summary()

    print("Creating batting innings...")
    build_batting_innings.build_batting_innings()

    print("Preparing bowling data...")
    deliveries_df = bowling_helper_functions.prepare_bowling_columns()

    print("Creating bowling summary...")
    build_bowling_summary.build_bowling_summary(deliveries_df)

    print("Creating bowling innings...")
    build_bowling_innings.build_bowling_innings(deliveries_df)

    print("All summaries created successfully!")

if __name__ == "__main__":
    create_summaries()