import os
import json
import sqlite3
import shutil
import argparse
from datetime import datetime

# Set up argument parser
parser = argparse.ArgumentParser(description="Retrieve bookmark entries from Firefox.")
parser.add_argument("num_entries", type=int, help="Number of bookmark entries to retrieve.")
args = parser.parse_args()

# Set up directories for bookmarks
base_dir = os.path.expanduser("./data")
firefox_dir = os.path.join(base_dir, "firefox")
bookmark_dir = os.path.join(firefox_dir, "bookmarks")

# Ensure necessary directories exist
os.makedirs(bookmark_dir, exist_ok=True)

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

# Connect to the copied database and extract bookmarks
try:
    conn = sqlite3.connect(copied_db_path)
    cursor = conn.cursor()

    # Query to retrieve specified number of bookmark entries
    query = f"""
        SELECT url, datetime(dateAdded/1000000, 'unixepoch') AS time
        FROM moz_places
        JOIN moz_bookmarks ON moz_places.id = moz_bookmarks.fk
        WHERE moz_bookmarks.type = 1
        ORDER BY time DESC
        LIMIT {args.num_entries};
    """
    cursor.execute(query)
    bookmark_data = [{"url": row[0], "time": row[1]} for row in cursor.fetchall()]

    # Generate unique filename with timestamp for the bookmark file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    bookmark_file = os.path.join(bookmark_dir, f"{timestamp}_bookmark.json")

    # Write bookmark data to JSON
    with open(bookmark_file, "w") as f:
        json.dump(bookmark_data, f, indent=4)
    print(f"Bookmark data saved to {bookmark_file}")

except sqlite3.Error as e:
    print("SQLite error:", e)

finally:
    if conn:
        conn.close()
