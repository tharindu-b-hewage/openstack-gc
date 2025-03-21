import pandas as pd
import time
import requests
import sys
import logging

# Configure logging to write messages to a file
logging.basicConfig(
    filename='rnw_trace_mgt.log',              # Log file name
    filemode='w',                    # 'w' to overwrite the file, 'a' to append to it
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',       # Format for the timestamp
    level=logging.INFO               # Set the logging level
)

# Configuration
CSV_FILE = sys.argv[1]  # Path to trace CSV file
THRESHOLD = 0.1  # Set intensity threshold
SWITCH_API_URL = "http://" + sys.argv[2] + ":" + sys.argv[3] + "/gc/dev/switch"


# Function to poll switch API
def poll_switch(action):
    """Send a request to the switch API to turn cores on/off in a separate thread."""



    def _request():
        payload = {"action": action}
        try:
            response = requests.post(SWITCH_API_URL, json=payload)
            response.raise_for_status()
            logging.info(f"Switch API polled: {action}")
        except requests.RequestException as e:
            logging.info(f"Error polling switch API: {e}")

    _request()
    # # Start the request in a background thread
    # thread = threading.Thread(target=_request)
    # thread.start()


# Load CSV data
df = pd.read_csv(CSV_FILE)


def is_cores_awake():
    logging.info("Polling to see if cores are awake")
    url = "http://" + sys.argv[2] + ":" + sys.argv[3] +"/gc/is-asleep"
    response = requests.get(url)
    # Check if the response was successful.
    if response.status_code == 200:
        data = response.json()
        logging.info("Response received", data)
        # The value of the "is-awake" key is important:
        # If the value is True, the cores are awake; otherwise, they are asleep.
        if data.get("is-awake") == True:
            logging.info("cores are awake")
            return True
        else:
            logging.info("cores are not awake")
            return False
    else:
        logging.info("Error: Received status code", response.status_code)


def replay_trace():
    """Replay the trace and poll the switch API based on intensity."""
    cores_on = is_cores_awake()
    # Assume cores are initially off
    if cores_on:
        logging.info("Found cores on. Turning cores off for the experiment.")
        poll_switch("OFF")  # Turn cores off

    t_begin = 0.0
    for index, row in df.iterrows():
        timestamp, intensity = row["days"], row["intensity"]  # Adjust column names if needed
        logging.info(f"Time: {timestamp}, Intensity: {intensity}")

        cores_on = is_cores_awake()
        if intensity > THRESHOLD and not cores_on:
            logging.info("Turning cores ON")
            poll_switch("ON")  # Turn cores on
            #cores_on = True
        elif intensity <= THRESHOLD and cores_on:
            logging.info("Turning cores OFF")
            poll_switch("OFF")  # Turn cores off
            #cores_on = False

        t_secs = (timestamp - t_begin) * 24 * 60 * 60
        time.sleep(max(2,t_secs))  # Simulate real-time progression

        t_begin = timestamp


if __name__ == "__main__":
    replay_trace()
