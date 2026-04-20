import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FOLDER = os.path.join(BASE_DIR, "data")

RAW_FOLDER = os.path.join(DATA_FOLDER, "raw_json")
TEMP_FOLDER = os.path.join(DATA_FOLDER, "temp_download")
PROCESSED_FOLDER = os.path.join(DATA_FOLDER, "processed")
LOG_FOLDER = os.path.join(DATA_FOLDER, "logs")

LOG_FILE = os.path.join(LOG_FOLDER, "used_match_ids.txt")

CRICSHEET_URL = "https://cricsheet.org/downloads/ipl_male_json.zip"