from scripts.scraper import download_new_matches
from scripts.transform_data import build_csvs

def run_pipeline():
    print("Starting IPL data update...\n")

    new_matches = download_new_matches()

    print()

    matches_count, deliveries_count = build_csvs()

    print()
    print("Pipeline complete.")
    print(f"New matches added: {new_matches}")
    print(f"Total matches in dataset: {matches_count}")
    print(f"Total deliveries in dataset: {deliveries_count}")

if __name__ == "__main__":
    run_pipeline()