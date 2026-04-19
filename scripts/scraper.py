import requests
import zipfile
import io
import os
import shutil

RAW_FOLDER = "data/raw_json"
TEMP_FOLDER = "data/temp_download"
LOG_FILE = "data/logs/used_match_ids.txt"

URL = "https://cricsheet.org/downloads/ipl_male_json.zip"


with open(LOG_FILE, "r") as f:
    existing_ids = set(line.strip() for line in f)

r = requests.get(URL)
r.raise_for_status()

with zipfile.ZipFile(io.BytesIO(r.content)) as z:
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
    os.remove(os.path.join(TEMP_FOLDER, file))

print(f"{len(new_ids)} new matches added.")
print("Done.")