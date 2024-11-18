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
    banner = pyfiglet.figlet_format("Get Services", font="slant")
    print(Fore.CYAN + banner)
    print(Fore.GREEN + "A tool to list all system services and save them in JSON format.\n")


def run_systemctl_command():
    """Run the systemctl command and return its output."""
    try:
        result = subprocess.run(
            ["systemctl", "list-unit-files", "--type=service"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error running systemctl command: {e}")
        exit(1)


def parse_services_output(output):
    """Parse the output of the systemctl command into a list of dictionaries."""
    services = []
    lines = output.strip().split("\n")
    header_line = lines[0]
    headers = [header.strip() for header in header_line.split()]
    
    for line in lines[1:]:
        if line.strip():  # Skip empty lines
            parts = line.split()
            # UNIT_FILE might contain spaces; adjust splitting logic
            unit_file = " ".join(parts[:-2])
            state, preset = parts[-2], parts[-1]
            services.append({
                "UNIT_FILE": unit_file,
                "STATE": state,
                "PRESET": preset
            })
    return services


def save_services_to_json(services, output_dir):
    """Save the services data to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{timestamp}_services.json")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(services, f, indent=4)

    print(Fore.GREEN + f"Services data saved to {Fore.CYAN}{output_file}")


def main():
    # Print the banner
    print_banner()

    # Define the output directory
    base_dir = os.path.expanduser("./application/data/services")
    
    # Run systemctl command
    print(Fore.YELLOW + "Running systemctl command...")
    output = run_systemctl_command()

    # Parse the output
    print(Fore.YELLOW + "Parsing services output...")
    services = parse_services_output(output)

    # Save services data to JSON
    print(Fore.YELLOW + "Saving services to JSON file...")
    save_services_to_json(services, base_dir)


if __name__ == "__main__":
    main()
