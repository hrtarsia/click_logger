from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import pytz
import os
from user_agents import parse

app = Flask(__name__)

# HTML Template for the homepage with a clickable link
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Click Tracker</title>
</head>
<body>
    <h1>Welcome!</h1>
    <p>Click the link below to log your information:</p>
    <a href="/info">Click Me!</a>
</body>
</html>
"""

# Path for the log file
LOG_FILE_PATH = "/click_logs.txt"

# Function to append data to the log file
def append_to_log_file(data):
    with open(LOG_FILE_PATH, 'a') as file:
        file.write(f"{data}\n")

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/info', methods=['GET'])
def info():
    if 'X-Forwarded-For' in request.headers:
        # Get the first IP address in the 'X-Forwarded-For' list
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        # Fall back to the remote address if 'X-Forwarded-For' does not exist
        ip_address = request.remote_addr

    # Log timestamp in UTC
    utc_time = datetime.now(pytz.utc)
    timestamp = utc_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    # User-Agent (type of browser or tool used)
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Parse the User-Agent string
    parsed_user_agent = parse(user_agent)

    # Extract OS, device, and browser
    os = parsed_user_agent.os.family
    device = parsed_user_agent.device.family
    browser = parsed_user_agent.browser.family

    # Language settings of the user's browser
    language = request.headers.get('Accept-Language', 'Unknown')

    # Timezone (if available via header, else use a fallback)
    timezone = request.headers.get('TimeZone', 'Unknown')

    # Protocol (HTTP version)
    protocol = request.environ.get('SERVER_PROTOCOL', 'Unknown')

    # Port number
    port = request.environ.get('REMOTE_PORT', 'Unknown')

    # Log the data
    log_entry = {
        "IP Address": ip_address,
        "Timestamp (UTC)": timestamp,
        "User-Agent": user_agent,
        "OS": os,
        "Device": device,
        "Browser": browser,
        "Language": language,
        "Timezone": timezone,
        "Protocol": protocol,
        "Port": port,
    }

    # Format the log entry for file writing
    formatted_entry = "\n".join([f"{key}: {value}" for key, value in log_entry.items()])

    # Append the entry to the log file
    append_to_log_file(formatted_entry)

    # Print log to console as well
    print(f"Log Entry:\n{formatted_entry}")

    # Return log information as a response
    return jsonify({
        "message": "Thank you for clicking!",
        "logged_data": log_entry
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
