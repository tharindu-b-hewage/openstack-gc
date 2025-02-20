import pandas as pd
import time
import requests
import sys
import threading

# Configuration
TRACE_NAME = sys.argv[1]
CSV_FILE = "traces/" + TRACE_NAME + ".csv"  # Path to CSV file
THRESHOLD = 0.1  # Set intensity threshold
SWITCH_API_URL = "http://172.23.13.34:2000/gc/dev/switch"  # curl --request POST --location 'http://172.23.13.34:2000/gc/dev/switch'


# Function to poll switch API
def poll_switch(action):
    """Send a request to the switch API to turn cores on/off in a separate thread."""

    def _request():
        payload = {"action": action}
        try:
            response = requests.post(SWITCH_API_URL, json=payload)
            response.raise_for_status()
            print(f"Switch API polled: {action}")
        except requests.RequestException as e:
            print(f"Error polling switch API: {e}")

    # Start the request in a background thread
    thread = threading.Thread(target=_request)
    thread.start()


# Load CSV data
df = pd.read_csv(CSV_FILE)


def check_core_status():
    url = "http://172.23.13.34:2000/gc/core-usage"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for host in data:
            if host["host-ip"] == "172.23.13.34":
                if int(host["reg-cores-avl"]) == 6:  # cores are off
                    return False
                else:
                    return True
        print("Host 172.23.13.34 not found in response.")
    else:
        print("Failed to fetch data from API.")


def replay_trace():
    """Replay the trace and poll the switch API based on intensity."""
    cores_on = check_core_status()

    # Assume cores are initially off
    if cores_on:
        print("Found cores on. Turning cores off for the experiment.")
        poll_switch("OFF")  # Turn cores off

    t_begin = 0.0
    for index, row in df.iterrows():
        timestamp, intensity = row["days"], row["intensity"]  # Adjust column names if needed
        print(f"Time: {timestamp}, Intensity: {intensity}")

        if intensity > THRESHOLD and not cores_on:
            poll_switch("ON")  # Turn cores on
            cores_on = True
        elif intensity <= THRESHOLD and cores_on:
            poll_switch("OFF")  # Turn cores off
            cores_on = False

        t_secs = (timestamp - t_begin) * 24 * 60 * 60
        time.sleep(t_secs)  # Simulate real-time progression


if __name__ == "__main__":
    replay_trace()
