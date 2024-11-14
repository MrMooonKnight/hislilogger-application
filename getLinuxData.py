import os
import sys
import paramiko
from datetime import datetime

# Function to execute SSH commands and capture output
def execute_ssh_commands(ip_address, username, password, commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(ip_address, username=username, password=password, timeout=20)
        stdin, stdout, stderr = client.exec_command(commands)
        
        # Read the output from stdout
        output = stdout.read().decode()
        
        # Read any errors from stderr
        error = stderr.read().decode()
        if error:
            print(f"Error executing commands on {ip_address}: {error}")
        
        return output
        
    except paramiko.AuthenticationException as e:
        print(f"Authentication failed for {username}@{ip_address}: {str(e)}")
    except paramiko.SSHException as e:
        print(f"SSH connection error for {ip_address}: {str(e)}")
    except Exception as e:
        print(f"Error connecting to {ip_address}: {str(e)}")
    finally:
        client.close()

    return None

def format_information(text):
    lines = text.splitlines()
    formatted_lines = []

    for line in lines:
        # Remove leading and trailing whitespace
        line = line.strip()
        if line.startswith('ii'):
            line = line[3:]  # Remove the 'ii ' prefix
        # Exclude lines with package status headers and explanations
        if line and not line.startswith(('Desired=', '| Status=', '|/ Err?=', '+++-', '||/')):
            # Replace colons with commas
            line = line.replace(":", ",")
            # Remove extra spaces between words
            line = " ".join(line.split())
            formatted_lines.append(line)
    
    return "\n".join(formatted_lines)

# Main function
def main():    
    ip_address = sys.argv[1]
    
    print(f"Selected device IP: {ip_address}")
    
    # SSH credentials
    username = 'fsociety\\Administrator'  # Replace with actual username
    password = 'Admin@123'      # Replace with actual password
    
    # Commands to execute on remote machine
    commands = "echo System_Information; uname -a; echo Release_Information; lsb_release -a; cat /etc/os-release;echo Network_Adapter_Information; ifconfig; echo Software_Information; dpkg -l | grep security; dpkg -l;"  # Example command
    
    output = execute_ssh_commands(ip_address, username, password, commands)
    
    if output:
        # Create a filename with the current time
        base_dir = 'Data'
        os.makedirs(base_dir, exist_ok=True)
        
        ip_dir = os.path.join(base_dir, ip_address)
        os.makedirs(ip_dir, exist_ok=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(ip_dir, f"{ip_address}_{current_time}.txt")
        
        output = format_information(output)

        # Write the output to the file
        with open(filename, 'w') as file:
            file.write(output)
        
        print(f"Output saved to {filename}")
    else:
        print("No output received. Check SSH connection and command execution.")

if __name__ == "__main__":
    main()
