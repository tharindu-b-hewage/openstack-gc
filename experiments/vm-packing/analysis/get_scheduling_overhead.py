import os
import re
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from get_configs import parse_configs

data_root = parse_configs()["data-root"]


def parse_timestamp(line):
    """
    Extract timestamp (e.g., 'Feb 22 09:20:26') from the beginning of a log line,
    parse with strptime, and assume the year is 2025.
    """
    # Regex to capture the substring 'Feb 22 09:20:26' at the start of the line
    pattern = r'^([A-Za-z]{3}\s+\d+\s+\d{2}:\d{2}:\d{2})'
    match = re.match(pattern, line)
    if match:
        timestr = match.group(1)  # e.g. "Feb 22 09:20:26"
        # Parse using datetime.strptime
        dt = datetime.strptime(timestr, '%b %d %H:%M:%S')
        # Override the year to a fixed year, say 2025
        dt = dt.replace(year=2025)
        return dt
    return None


def parse_uuids(line):
    """
    Extract the list of instance UUIDs from a log line.
    Assumes line has substring like "...instances: ['uuid1', 'uuid2']"
    Returns list of UUID strings.
    """
    # This simple pattern tries to capture everything inside "instances: [ ... ]"
    # Then we split on commas to get individual UUIDs.
    # You might need more robust parsing depending on your exact log format.
    pattern = r"instances:\s*\[(.*?)\]"
    match = re.search(pattern, line)
    if not match:
        return []

    inside_brackets = match.group(1).strip()
    # inside_brackets might be something like: "'uuid1', 'uuid2'"
    # Remove quotes/spaces, split by comma
    # We can do a safer approach with a small regular expression as well:
    uuids = re.findall(r"'([^']+)'", inside_brackets)
    return uuids


def analyze_scheduling_overhead(exp_type):
    logfile_path_nova = os.path.join(data_root, exp_type, "nova", "schd.log")
    logfile_path_proposed = os.path.join(data_root, exp_type, "proposed", "schd.log")

    def get_overheads(logfile_path):
        # A dictionary to track the last "start time" for each UUID
        start_times = {}
        # A list to store computed overhead times
        overheads = []

        with open(logfile_path, 'r') as f:
            for line in f:
                # Skip lines that don't mention scheduling
                if not ("schedule for instances" in line):
                    continue

                # Parse out timestamp
                ts = parse_timestamp(line)
                if ts is None:
                    continue  # skip if we can't parse a valid timestamp

                # Determine if this is a "Starting" or "Concluding" line
                if "Starting to schedule" in line:
                    # Extract all instance UUIDs
                    uuids = parse_uuids(line)
                    for uid in uuids:
                        # Record this start time
                        start_times[uid] = ts

                elif "Concluding the schedule" in line:
                    # Extract all instance UUIDs
                    uuids = parse_uuids(line)
                    for uid in uuids:
                        # Check if we have a start time for this instance
                        if uid in start_times:
                            delta = (ts - start_times[uid]).total_seconds()
                            overheads.append(delta)
                            # Remove the start time to avoid confusion with future scheduling
                            del start_times[uid]

        # Now overheads list contains all the scheduling durations we found
        if not overheads:
            print("No scheduling overhead data found. Exiting...")
            sys.exit(0)

        return overheads

    overheads_nova = get_overheads(logfile_path_nova)
    overheads_proposed = get_overheads(logfile_path_proposed)

    # Create a DataFrame in long (tidy) format
    df = pd.DataFrame({
        'Scheduler': ['nova'] * len(overheads_nova) + ['proposed'] * len(overheads_proposed),
        'Overhead': overheads_nova + overheads_proposed
    })

    sns.set(style="whitegrid")
    plt.figure(figsize=(2.5, 1.7))

    # Now specify x and y from the DataFrame
    sns.boxplot(x="Scheduler", y="Overhead", data=df, palette='Greys')

    #plt.title("Distribution of Scheduling Overheads (Box Plot)")
    plt.ylabel("Seconds")
    plt.xlabel("")

    plt.tight_layout()
    plt.savefig("./results/scheduling_overhead.svg", dpi=300, bbox_inches='tight')
