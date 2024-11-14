import os
import argparse

def ping_device(ip_address):
    # Use the ping command
    response = os.system(f"ping -c 1 {ip_address}")
    
    # Check the response
    if response == 0:
        print(f"Device {ip_address} is up!")
    else:
        print(f"Device {ip_address} is down!")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Ping a device to check if it is up or down.')
    parser.add_argument('ip_address', type=str, help='The IP address of the device to ping')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Ping the device with the provided IP address
    ping_device(args.ip_address)
