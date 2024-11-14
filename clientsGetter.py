import subprocess

def run_powershell_command():
    ps_command = (
        "Get-ADComputer -Filter * -Property Name,OperatingSystem,IPv4Address | Select-Object Name,OperatingSystem,IPv4Address | ConvertTo-Csv -NoTypeInformation"
    )

    # Splitting the command into a list of arguments
    command_args = ["powershell.exe", "-Command", ps_command]

    # Execute the command without shell=True
    try:
        result = subprocess.run(command_args, capture_output=True, text=True, check=True)
        csv_output = result.stdout.strip()  # Get the CSV output and strip any surrounding whitespace

        # Write the CSV output to windows.txt and others.txt in the required format
        with open("windows.txt", "w", encoding="utf-8") as windows_file, \
             open("others.txt", "w", encoding="utf-8") as others_file:

            # Write headers manually
            #windows_file.write("devicename,ip_address\n")
            #others_file.write("devicename,ip_address\n")

            # Write each line of CSV output in the required format
            for line in csv_output.splitlines()[1:]:  # Skip the header line in CSV
                name, operating_system, ip_address = line.split(",")  # Assuming CSV format is consistent

                # Check if the operating system contains "Windows"
                if "Windows" in operating_system:
                    windows_file.write(f"{name.replace('\"', '')},{ip_address.replace('\"', '')}\n")
                else:
                    others_file.write(f"{name.replace('\"', '')},{ip_address.replace('\"', '')}\n")


        print("Command executed successfully and output saved to windows.txt and others.txt")

    except subprocess.CalledProcessError as e:
        print(f"Error executing PowerShell command: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_powershell_command()
