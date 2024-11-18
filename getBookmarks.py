import os
import json
import sqlite3
import shutil
import argparse
from datetime import datetime
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama for Windows compatibility
init(autoreset=True)

def print_banner():
    """Print a stylish banner."""
    banner = pyfiglet.figlet_format("Firefox Bookmarks", font="slant")
    print(Fore.CYAN + banner)
    print(Fore.GREEN + "A tool to retrieve and save Firefox bookmarks in JSON format.\n")


def copy_database(original_db_path, copied_db_path):
    """Copy the database to the application directory."""
    try:
        shutil.copy2(original_db_path, copied_db_path)
        print(Fore.GREEN + f"Copied database to {Fore.CYAN}{copied_db_path}")
    except Exception as e:
        print(Fore.RED + "Error copying database file:", e)
        exit(1)


def extract_bookmarks(db_path, num_entries, bookmark_dir, retrieve_all=False):
    """Extract bookmarks from the copied database and save them to a JSON file."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Adjust query based on the retrieve_all flag
        if retrieve_all:
            query = """
                SELECT url, datetime(dateAdded/1000000, 'unixepoch') AS time
                FROM moz_places
                JOIN moz_bookmarks ON moz_places.id = moz_bookmarks.fk
                WHERE moz_bookmarks.type = 1
                ORDER BY time DESC;
            """
        else:
            query = f"""
                SELECT url, datetime(dateAdded/1000000, 'unixepoch') AS time
                FROM moz_places
                JOIN moz_bookmarks ON moz_places.id = moz_bookmarks.fk
                WHERE moz_bookmarks.type = 1
                ORDER BY time DESC
                LIMIT {num_entries};
            """

        cursor.execute(query)
        bookmark_data = [{"url": row[0], "time": row[1]} for row in cursor.fetchall()]

        # Save bookmarks to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        bookmark_file = os.path.join(bookmark_dir, f"{timestamp}_bookmark.json")

        with open(bookmark_file, "w") as f:
            json.dump(bookmark_data, f, indent=4)

        print(Fore.GREEN + f"Bookmark data saved to {Fore.CYAN}{bookmark_file}")

    except sqlite3.Error as e:
        print(Fore.RED + "SQLite error:", e)

    finally:
        if conn:
            conn.close()


def main():
    # Display banner
    print_banner()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Retrieve bookmark entries from Firefox.")
    parser.add_argument("num_entries", type=int, nargs='?', default=None, help="Number of bookmark entries to retrieve.")
    parser.add_argument("-a", "--all", action="store_true", help="Retrieve all bookmark entries.")
    args = parser.parse_args()

    # Set up directories
    base_dir = os.path.expanduser("./application/data")
    firefox_dir = os.path.join(base_dir, "firefox")
    bookmark_dir = os.path.join(firefox_dir, "bookmarks")
    os.makedirs(bookmark_dir, exist_ok=True)

    # Firefox database paths
    original_db_path = os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/8ve3ga0x.default/places.sqlite")

    copied_db_path = os.path.join(firefox_dir, "places.sqlite")

    print(Fore.YELLOW + "Preparing to copy Firefox database...")
    copy_database(original_db_path, copied_db_path)

    if args.all:
        print(Fore.YELLOW + "Extracting all bookmarks...")
        extract_bookmarks(copied_db_path, None, bookmark_dir, retrieve_all=True)
    elif args.num_entries:
        print(Fore.YELLOW + f"Extracting {args.num_entries} bookmarks...")
        extract_bookmarks(copied_db_path, args.num_entries, bookmark_dir, retrieve_all=False)
    else:
        print(Fore.RED + "You must specify the number of entries or use the '-a' flag to retrieve all.")


if __name__ == "__main__":
    main()
