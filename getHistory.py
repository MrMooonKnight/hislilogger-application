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
    banner = pyfiglet.figlet_format("Firefox History", font="slant")
    print(Fore.CYAN + banner)
    print(Fore.GREEN + "A tool to retrieve and save Firefox browsing history in JSON format.\n")


def copy_database(original_db_path, copied_db_path):
    """Copy the Firefox database to the application directory."""
    try:
        shutil.copy2(original_db_path, copied_db_path)
        print(Fore.GREEN + f"Copied database to {Fore.CYAN}{copied_db_path}")
    except Exception as e:
        print(Fore.RED + f"Error copying database file: {e}")
        exit(1)


def extract_history(db_path, num_entries, history_dir, retrieve_all=False):
    """Extract browsing history from the database and save it to a JSON file."""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Adjust query based on retrieve_all flag
        if retrieve_all:
            query = """
                SELECT url, datetime(visit_date/1000000, 'unixepoch') AS time
                FROM moz_places
                JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
                ORDER BY time DESC;
            """
        else:
            query = f"""
                SELECT url, datetime(visit_date/1000000, 'unixepoch') AS time
                FROM moz_places
                JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
                ORDER BY time DESC
                LIMIT {num_entries};
            """

        cursor.execute(query)
        history_data = [{"url": row[0], "time": row[1]} for row in cursor.fetchall()]

        # Save history to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        history_file = os.path.join(history_dir, f"{timestamp}_history.json")

        with open(history_file, "w") as f:
            json.dump(history_data, f, indent=4)

        print(Fore.GREEN + f"History data saved to {Fore.CYAN}{history_file}")

    except sqlite3.Error as e:
        print(Fore.RED + f"SQLite error: {e}")

    finally:
        if conn:
            conn.close()


def main():
    # Print the banner
    print_banner()

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Retrieve browsing history entries from Firefox.")
    parser.add_argument("num_entries", type=int, nargs='?', default=None, help="Number of history entries to retrieve.")
    parser.add_argument("-a", "--all", action="store_true", help="Retrieve all browsing history entries.")
    args = parser.parse_args()

    # Set up directories
    base_dir = os.path.expanduser("data")
    firefox_dir = os.path.join(base_dir, "firefox")
    history_dir = os.path.join(firefox_dir, "history")
    os.makedirs(history_dir, exist_ok=True)

    # Firefox database paths
    original_db_path = os.path.expanduser("~/snap/firefox/common/.mozilla/firefox/8ve3ga0x.default/places.sqlite")
    copied_db_path = os.path.join(firefox_dir, "places.sqlite")

    # Copy and extract data
    print(Fore.YELLOW + "Preparing to copy Firefox database...")
    copy_database(original_db_path, copied_db_path)

    if args.all:
        print(Fore.YELLOW + "Extracting all browsing history...")
        extract_history(copied_db_path, None, history_dir, retrieve_all=True)
    elif args.num_entries:
        print(Fore.YELLOW + f"Extracting {args.num_entries} browsing history entries...")
        extract_history(copied_db_path, args.num_entries, history_dir, retrieve_all=False)
    else:
        print(Fore.RED + "You must specify the number of entries or use the '-a' flag to retrieve all.")


if __name__ == "__main__":
    main()
