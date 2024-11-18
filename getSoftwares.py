import os
import json
import subprocess
from datetime import datetime
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print a stylish banner."""
    banner = pyfiglet.figlet_format("Get Softwares", font="slant")
    print(Fore.CYAN + banner)
    print(Fore.GREEN + "A tool to list all installed software with versions and save them in JSON format.\n")


def run_dpkg_query_command():
    """Run the dpkg-query command and return its output."""
    try:
        result = subprocess.run(
            ["dpkg-query", "-l"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error running dpkg-query command: {e}")
        exit(1)


def parse_software_output(output):
    """Parse the output of the dpkg-query command into a list of dictionaries."""
    software_list = []
    lines = output.strip().split("\n")
    # Skip headers (first 5 lines) and process the rest
    for line in lines[5:]:
        if line.strip():  # Skip empty lines
            parts = line.split()
            name = parts[1]  # Second column is the package name
            version = parts[2]  # Third column is the version
            software_list.append({"Name": name, "Version": version})
    return software_list


def save_software_to_json(software_list, output_dir):
    """Save the software data to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}_softwares.json")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(software_list, f, indent=4)

    print(Fore.GREEN + f"Software data saved to {Fore.CYAN}{output_file}")


def main():
    # Print the banner
    print_banner()

    # Define the output directory
    base_dir = os.path.expanduser("./application/data/softwares")

    # Run dpkg-query command
    print(Fore.YELLOW + "Running dpkg-query command...")
    output = run_dpkg_query_command()

    # Parse the output
    print(Fore.YELLOW + "Parsing installed software output...")
    software_list = parse_software_output(output)

    # Save software data to JSON
    print(Fore.YELLOW + "Saving installed software to JSON file...")
    save_software_to_json(software_list, base_dir)


if __name__ == "__main__":
    main()
