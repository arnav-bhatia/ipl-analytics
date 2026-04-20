import requests
import zipfile
import io
import os
import shutil

from config import RAW_FOLDER, TEMP_FOLDER, LOG_FILE, CRICSHEET_URL

def download_new_matches():
    with open(LOG_FILE, "r") as f:
        existing_ids = set(line.strip() for line in f)

    response = requests.get(CRICSHEET_URL)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(TEMP_FOLDER)

    print("Matches extracted")

    new_ids = []

    for file in os.listdir(TEMP_FOLDER):
        if file.endswith(".json"):
            match_id = file.replace(".json", "")

            if match_id not in existing_ids:
                src = os.path.join(TEMP_FOLDER, file)
                dst = os.path.join(RAW_FOLDER, file)

                shutil.move(src, dst)
                new_ids.append(match_id)

    with open(LOG_FILE, "a") as f:
        for match_id in new_ids:
            f.write(match_id + "\n")

    for file in os.listdir(TEMP_FOLDER):
        file_path = os.path.join(TEMP_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    print(f"{len(new_ids)} new matches added.")

    return len(new_ids)

if __name__ == "__main__":
    download_new_matches()