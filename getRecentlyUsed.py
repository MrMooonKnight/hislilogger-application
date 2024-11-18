import os
import json
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from colorama import Fore, Style, init
# Initialize colorama for Windows compatibility
init(autoreset=True)

def print_banner():
    """Print a stylish banner."""
    try:
        import pyfiglet
        banner = pyfiglet.figlet_format("XBEL Parser", font="slant")
        print(Fore.CYAN + banner)
    except ImportError:
        print(Fore.CYAN + "=== XBEL Parser ===")
    print(Fore.GREEN + "A tool to parse XBEL bookmarks and extract metadata.\n")

def parse_xbel_file(file_path, num_entries=None):
    """Parse the XBEL file and extract bookmark metadata."""
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # List to store bookmark data
    bookmarks = []
    
    # Find all bookmark elements recursively
    for bookmark in root.findall(".//bookmark"):
        # Get the file path from href attribute
        file_path = bookmark.get('href')
        
        # Get the last accessed time (visited attribute)
        last_accessed = (bookmark.get('visited') or 
                        bookmark.get('modified') or 
                        bookmark.get('added'))
        
        # Convert the ISO timestamp to desired format
        if last_accessed:
            dt = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        
            # Create bookmark entry
            bookmark_entry = {
                "file": file_path,
                "last_accessed": formatted_time
            }
            
            bookmarks.append(bookmark_entry)
    
    # Sort bookmarks by last_accessed in descending order
    bookmarks.sort(key=lambda x: x['last_accessed'], reverse=True)
    
    # If num_entries is specified, limit the result
    if num_entries:
        bookmarks = bookmarks[:num_entries]
    
    return bookmarks

def save_to_json(data, output_dir):
    """Save the parsed data to a JSON file."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate the filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}_recently_used.json")
    
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(Fore.RED + f"Error saving to JSON: {e}")
        return False

def main():
    # Print the banner
    print_banner()
    
    # XBEL file path and output directory as fixed paths
    xbel_file_path = os.path.expanduser('~/.local/share/recently-used.xbel')
    output_dir = 'application/data/recently_used'
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Parse XBEL file and extract metadata.")
    parser.add_argument("-n", "--num_entries", type=int, 
                        help="Number of entries to retrieve (default: all)")
    args = parser.parse_args()
    
    # Parse and save data
    print(Fore.YELLOW + "Parsing XBEL file...")
    data = parse_xbel_file(xbel_file_path, args.num_entries)
    
    if data:
        if save_to_json(data, output_dir):
            print(Fore.GREEN + "Operation completed successfully.")
            print(Fore.CYAN + f"Extracted data is stored in: {output_dir}")
        else:
            print(Fore.RED + "Failed to save the output file.")
    else:
        print(Fore.RED + "Failed to parse the XBEL file.")

if __name__ == "__main__":
    main()