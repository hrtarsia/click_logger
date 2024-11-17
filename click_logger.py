from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import pytz
import os
import requests
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
    <a href="/LinkedIn">Click Me!</a>
</body>
</html>
"""

# Function to get geolocation and timezone from IP using ipinfo.io API
def get_geolocation_from_ip(ip_address):
    try:
        # Use ipinfo.io API to get geolocation data, including timezone and latitude/longitude
        response = requests.get(f'https://ipinfo.io/{ip_address}/json')
        data = response.json()

        # Extract geolocation and timezone
        timezone = data.get('timezone', 'Unknown')
        return timezone
    except Exception as e:
        print(f"Error getting geolocation: {e}")
        return 'Unknown'
        
def get_device_type(user_agent):
    parsed_user_agent = parse(user_agent)

    # Check if it's a mobile device
    if parsed_user_agent.is_mobile:
        return "Mobile"
    # Check if it's a tablet
    elif parsed_user_agent.is_tablet:
        return "Tablet"
    # Check if it's a desktop/laptop
    elif parsed_user_agent.is_pc:
        return "PC"
    else:
        return "Other"

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/LinkedIn', methods=['GET'])
    ip_address = request.remote_addr

    # Get the timezone and geolocation (latitude and longitude) based on the user's IP address
    timezone = get_geolocation_from_ip(ip_address)

    # Log timestamp in UTC
    utc_time = datetime.now(pytz.utc)
    timestamp = utc_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    # User-Agent (type of browser or tool used)
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Parse the User-Agent string
    parsed_user_agent = parse(user_agent)

    # Extract OS, device, and browser
    os = parsed_user_agent.os.family
    device = get_device_type(user_agent)
    browser = parsed_user_agent.browser.family

    # Language settings of the user's browser
    language = request.headers.get('Accept-Language', 'Unknown')

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

    # Print log to console as well
    print(f"Log Entry:\n{formatted_entry}")

    # Return log information as a response
    return jsonify({
        "message": "Oh no, you have been phished!!! Thank you for clicking the link :)",
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
