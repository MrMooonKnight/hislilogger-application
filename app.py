from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/update_clients', methods=['POST'])
def update_clients():
    script_path = "python clientsGetter.py"
    try:
        subprocess.run(["powershell", "-Command", script_path], check=True)
        flash("Clients list has been updated")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e}")
    return redirect(url_for('view_clients'))

@app.route('/view_clients', methods=['GET', 'POST'])
def view_clients():
    clients = []
    try:
        with open('windows.txt', 'r') as file:
            clients += [line.strip().split(',') for line in file.readlines()]
    except FileNotFoundError:
        flash("The file windows.txt was not found.")
    
    try:
        with open('others.txt', 'r') as file:
            clients += [line.strip().split(',') for line in file.readlines()]
    except FileNotFoundError:
        flash("The file others.txt was not found.")
    
    return render_template('clients.html', clients=clients)

@app.route('/windows')
def windows():
    devices = []
    try:
        with open('windows.txt', 'r') as file:
            devices = [line.strip().split(',') for line in file.readlines()]
    except FileNotFoundError:
        flash("The file windows.txt was not found.")
    return render_template('windows.html', devices=devices)

@app.route('/device/<device_name>', methods=['GET', 'POST'])
def device(device_name):
    data_folder = os.path.join('Data', device_name)
    data_files = []
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        data_files = os.listdir(data_folder)
    else:
        flash(f"The data folder for device {device_name} was not found.")
    
    # Fetch any flash messages before rendering
    messages = get_flashed_messages()
    
    return render_template('device.html', device_name=device_name, data_files=data_files, messages=messages)

@app.route('/get_data/<device_name>', methods=['POST'])
def get_data(device_name):
    script_path = "python getWindowsData.py"
    try:
        subprocess.run(["powershell", "-Command", f"{script_path} {device_name}"], check=True)
        flash(f"Data for device {device_name} has been retrieved.")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e}")
    return redirect(url_for('device', device_name=device_name))

@app.route('/select_file/<device_name>', methods=['POST'])
def select_file(device_name):
    selected_file = request.form['data_file']
    return redirect(url_for('view_file', device_name=device_name, file_name=selected_file))

@app.route('/view_file/<device_name>/<file_name>')
def view_file(device_name, file_name):
    file_path = os.path.join('Data', device_name, file_name)
    data = {}
    try:
        with open(file_path, 'r') as file:
            current_header = None
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line.endswith('_Information'):
                    current_header = line
                    data[current_header] = []
                elif current_header and ',' in line:
                    data[current_header].append(line.split(','))
    except FileNotFoundError:
        flash(f"The file {file_name} was not found for device {device_name}.")
    
    return render_template('view_file.html', device_name=device_name, file_name=file_name, data=data)

@app.route('/linux')
def linux():
    devices = []
    with open('others.txt', 'r') as file:
        for line in file:
            device_info = line.strip().split(',')
            devices.append(device_info)
    return render_template('linux.html', devices=devices)

@app.route('/linux_device', methods=['POST'])
def linux_device():
    device_ip = request.form['device_ip']
    return redirect(url_for('device_by_ip', device_ip=device_ip))

@app.route('/device_by_ip/<device_ip>', methods=['GET', 'POST'])
def device_by_ip(device_ip):
    data_folder = os.path.join('Data', device_ip)
    data_files = []
    if os.path.exists(data_folder) and os.path.isdir(data_folder):
        data_files = os.listdir(data_folder)
    else:
        flash(f"The data folder for device with IP {device_ip} was not found.")
    
    # Fetch any flash messages before rendering
    messages = get_flashed_messages()
    
    return render_template('linux_device.html', device_name=device_ip, data_files=data_files, messages=messages)




@app.route('/get_linux_data/<device_name>', methods=['POST'])
def get_linux_data(device_name):
    script_path = "python getLinuxData.py"
    try:
        subprocess.run(["powershell", "-Command", f"{script_path} {device_name}"], check=True)
        flash(f"Data for device {device_name} has been retrieved.")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e}")
    return redirect(url_for('device', device_ip=device_name))



@app.route('/check_status/<ip_address>', methods=['GET', 'POST'])
def check_status(ip_address):
    script_path = "python checkStatus.py"
    try:
        # Capture the output of the script
        result = subprocess.run(
            ["powershell", "-Command", f"{script_path} {ip_address}"],
            check=True,
            capture_output=True,
            text=True
        )
        # Flash the output of the script
        flash(f"Status for {ip_address} checked: {result.stdout}")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e.stderr}")
    return redirect(url_for('windows'))



@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faheem')
def faheem():
    return render_template('faheem.html')

if __name__ == "__main__":
    app.run(debug=True)
