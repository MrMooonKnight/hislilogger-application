import os
import json
import sqlite3
import shutil
import argparse
from datetime import datetime

# Set up argument parser
parser = argparse.ArgumentParser(description="Retrieve browsing history entries from Firefox.")
parser.add_argument("num_entries", type=int, help="Number of history entries to retrieve.")
args = parser.parse_args()

# Set up directories for history
base_dir = os.path.expanduser("data")
firefox_dir = os.path.join(base_dir, "firefox")
history_dir = os.path.join(firefox_dir, "history")

# Ensure necessary directories exist
os.makedirs(history_dir, exist_ok=True)

# Path to Firefox places.sqlite database (original Snap path)
original_db_path = os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/8ve3ga0x.default/places.sqlite")
# Path to copy of the database in application data folder
copied_db_path = os.path.join(firefox_dir, "places.sqlite")

# Copy the database file to application/data/firefox
try:
    shutil.copy2(original_db_path, copied_db_path)
    print(f"Copied database to {copied_db_path}")
except Exception as e:
    print("Error copying database file:", e)
    exit(1)

# Initialize connection variable
conn = None

# Connect to the copied database and extract history
try:
    conn = sqlite3.connect(copied_db_path)
    cursor = conn.cursor()

    # Query to retrieve specified number of history entries
    query = f"""
        SELECT url, datetime(visit_date/1000000, 'unixepoch') AS time
        FROM moz_places
        JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
        ORDER BY time DESC
        LIMIT {args.num_entries};
    """
    cursor.execute(query)
    history_data = [{"url": row[0], "time": row[1]} for row in cursor.fetchall()]

    # Generate unique filename with timestamp for the history file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    history_file = os.path.join(history_dir, f"{timestamp}_history.json")

    # Write history data to JSON
    with open(history_file, "w") as f:
        json.dump(history_data, f, indent=4)
    print(f"History data saved to {history_file}")

except sqlite3.Error as e:
    print("SQLite error:", e)

finally:
    if conn:
        conn.close()
