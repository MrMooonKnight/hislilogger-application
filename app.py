from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import subprocess
import os
import json
import re


############################################################################################################################

app = Flask(__name__)
app.secret_key = 'your_secret_key'

############################################################################################################################

@app.route('/')
def home():
    return render_template('index.html')

############################################################################################################################
@app.route('/firefox_history', methods=['GET'])
def firefox_history():
    # Path to the directory containing the history files
    history_dir = "application/data/firefox/history"
    
    try:
        print(f"Checking directory: {history_dir}")  # Debug
        files = [f for f in os.listdir(history_dir) if os.path.isfile(os.path.join(history_dir, f))]
        print(f"Files found: {files}")  # Debug
    except FileNotFoundError:
        files = []
        flash(f"Directory {history_dir} not found.")
    
    return render_template('firefoxhistory.html', files=files)


@app.route('/update_firefox_history', methods=['POST'])
def update_firefox_history():
    # Ensure the script path is correct and Linux-compatible
    script_path = "application/getHistory.py"
    
    try:
        # Use subprocess to run the Python script on Linux
        subprocess.run(["python3", script_path, "100"], check=True)
        flash("Firefox history has been updated successfully.")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e}")
    except FileNotFoundError:
        flash(f"Script not found at {script_path}.")
    
    return redirect(url_for('firefox_history'))


@app.route('/select_history', methods=['POST'])
def select_history():
    selected_file = request.form['data_file']
    return redirect(url_for('view_history', file_name=selected_file))

@app.route('/view/<file_name>')
def view_history(file_name):
    with open(f'application/data/firefox/history/{file_name}') as f:
        data = json.load(f)
    return render_template('view_history.html', file_name=file_name, data=data)

############################################################################################################################

@app.route('/firefox_bookmarks', methods=['GET'])
def firefox_bookmarks():
    # Path to the directory containing the bookmarks files
    bookmarks_dir = "application/data/firefox/bookmarks"
    
    try:
        print(f"Checking directory: {bookmarks_dir}")  # Debug
        files = [f for f in os.listdir(bookmarks_dir) if os.path.isfile(os.path.join(bookmarks_dir, f))]
        print(f"Files found: {files}")  # Debug
    except FileNotFoundError:
        files = []
        flash(f"Directory {bookmarks_dir} not found.")
    
    return render_template('firefoxbookmarks.html', files=files)

@app.route('/update_firefox_bookmarks', methods=['POST'])
def update_firefox_bookmarks():
    # Ensure the script path is correct and Linux-compatible
    script_path = "application/getBookmarks.py"
    
    try:
        # Use subprocess to run the Python script on Linux
        subprocess.run(["python3", script_path, "-a"], check=True)
        flash("Firefox bookmarks has been updated successfully.")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e}")
    except FileNotFoundError:
        flash(f"Script not found at {script_path}.")
    
    return redirect(url_for('firefox_bookmarks'))

@app.route('/select_bookmarks', methods=['POST'])
def select_bookmarks():
    selected_file = request.form['data_file']
    return redirect(url_for('view_bookmarks', file_name=selected_file))

@app.route('/view_bookmarks/<file_name>')
def view_bookmarks(file_name):
    with open(f'application/data/firefox/bookmarks/{file_name}') as f:
        data = json.load(f)
    return render_template('view_bookmarks.html', file_name=file_name, data=data)

############################################################################################################################

@app.route('/bash_history', methods=['GET'])
def bash_history():
    # Path to the directory containing the bash history files
    bash_dir = "application/data/bash_history"
    
    try:
        print(f"Checking directory: {bash_dir}")  # Debug
        files = [f for f in os.listdir(bash_dir) if os.path.isfile(os.path.join(bash_dir, f))]
        print(f"Files found: {files}")  # Debug
    except FileNotFoundError:
        files = []
        flash(f"Directory {bash_dir} not found.")
    
    return render_template('bashhistory.html', files=files)


@app.route('/update_bash_history', methods=['POST'])
def update_bash_history():
    # Ensure the script path is correct and Linux-compatible
    script_path = "application/getBashHistory.py"
    
    try:
        # Use subprocess to run the Python script on Linux
        subprocess.run(["python3", script_path, "100"], check=True)
        flash("Bash history has been retrieved successfully.")
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while running the script: {e}")
    except FileNotFoundError:
        flash(f"Script not found at {script_path}.")
    
    return redirect(url_for('bash_history'))


@app.route('/select_bashhistory', methods=['POST'])
def select_bashhistory():
    selected_file = request.form['data_file']
    return redirect(url_for('view_bashhistory', file_name=selected_file))

@app.route('/view_bashhistory/<file_name>')
def view_bashhistory(file_name):
    bash_dir = "application/data/bash_history"
    file_path = os.path.join(bash_dir, file_name)
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        commands = data.get("commands", [])
    except (FileNotFoundError, json.JSONDecodeError):
        flash(f"Failed to read or parse the file: {file_name}")
        commands = []

    return render_template('view_bashhistory.html', file_name=file_name, commands=commands)

############################################################################################################################

@app.route('/device')
def device():
    # Execute the command and clean up the output
    device_info = subprocess.check_output(["./application/fastfetch"], text=True)
    device_info_clean = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', device_info)  # Strip ANSI escape codes

    # Split into lines and separate logo and info parts
    lines = device_info_clean.splitlines()
    logo_part = '\n'.join(lines[:20])  # First 20 lines for logo
    info_part = '\n'.join(lines[21:])  # Remaining lines for device info

    # Remove `username@username` from the last line of the logo
    logo_lines = logo_part.splitlines()
    logo_lines[-1] = re.sub(r'\b\w+@\w+\b', '', logo_lines[-1])  # Remove `username@username`
    logo_part = '\n'.join(logo_lines)

    # Render the template
    return render_template('device.html', logo_part=logo_part, info_part=info_part)


############################################################################################################################

@app.route('/about')
def about():
    return render_template('about.html')

############################################################################################################################


if __name__ == "__main__":
    app.run(debug=True)

############################################################################################################################
