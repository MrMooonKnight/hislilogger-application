import os
import subprocess
import argparse
from datetime import datetime

# Function to execute PowerShell command to enter a remote session and run the script
def enter_powershell_session(device_name):
    # PowerShell command to enter remote session and run the script
    powershell_cmd = f"""
    $password = ConvertTo-SecureString 'Admin@123' -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ('Administrator', $password)
    Invoke-Command -ComputerName {device_name} -Credential $credential -ScriptBlock {{
        $publicIP = Invoke-RestMethod -Uri "http://ipinfo.io/ip" 
        $location = Invoke-RestMethod -Uri "http://ipinfo.io/$publicIP/json"

        echo Location_Information

        $location

        echo System_Information

        Get-ComputerInfo | Select-Object CsName, WindowsVersion, WindowsBuildLabEx, OsArchitecture

        echo Network_Adapter_Information

        Get-NetAdapter | Select-Object Name, MacAddress

        $software32 = Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
              Select-Object DisplayName, DisplayVersion, Publisher
        $software64 = Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* |
              Select-Object DisplayName, DisplayVersion, Publisher
        $software = $software32 + $software64 | Sort-Object DisplayName

        echo Software_Information

        $software

        $firewallProfiles = Get-NetFirewallProfile

        echo Firewall_Information

        $firewallProfiles


    }}
    """
    
    result = subprocess.run(['powershell.exe', '-Command', powershell_cmd], capture_output=True, text=True)
    return result.stdout

def format_information(text):
    lines = text.splitlines()
    formatted_lines = []

    for line in lines:
        # Remove leading and trailing whitespace
        line = line.strip()
        if line:
            # Replace semicolons with commas
            line = line.replace(":", ",")
            # Remove extra spaces between words
            line = "".join(line.split())
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Enter a remote PowerShell session and gather system information.")
    parser.add_argument('device_name', type=str, help='The name of the device')
    
    args = parser.parse_args()
    
    device_name = args.device_name
    print(f"Selected device: {device_name}")
    
    output = enter_powershell_session(device_name)
    if output:
        # Create a filename with the device name and current time
        base_dir = 'Data'
        os.makedirs(base_dir, exist_ok=True)
        
        # Create a subfolder for the device if it doesn't exist
        device_dir = os.path.join(base_dir, device_name)
        os.makedirs(device_dir, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(device_dir, f"{device_name}_{current_time}.txt")
        output = format_information(output)
        # Write the output to the file
        with open(filename, 'w') as file:
            file.write(output)
        
        print(f"Output saved to {filename}")
    else:
        print(f"Output not received")

if __name__ == "__main__":
    main()
