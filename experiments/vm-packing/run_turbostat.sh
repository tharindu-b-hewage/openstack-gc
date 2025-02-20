#!/bin/bash

# example: sh run_turbostat.sh host-ip-1 host-ip-2 duration-in-seconds

# Define your remote hosts
HOSTS=("$1" "$2")

# Duration to run turbostat (in seconds)
DURATION=$3
LOG_FILE_NAME=turbostat_$(date "+%H:%M:%S-%d-%m-%y").log

# Start turbostat on each remote host
for h in "${HOSTS[@]}"; do
  echo "Starting turbostat on ${h}..."
  ssh -n "$h" "sudo turbostat --enable Time_Of_Day_Seconds --quiet --Summary --interval 1 -o ~/turbostat/$LOG_FILE_NAME &" &
done

# Wait for the desired duration
echo "Collecting data for $DURATION seconds..."
sleep $DURATION

# Retrieve the logs
for h in "${HOSTS[@]}"; do
  echo "Copying log from ${h}..."
  scp "$h:~/turbostat/$LOG_FILE_NAME" "./results/${h}-$LOG_FILE_NAME"
done

# Stop turbostat on each host (by killing the turbostat process)
for h in "${HOSTS[@]}"; do
  echo "Stopping turbostat on ${h}..."
  ssh -n "$h" "sudo pkill turbostat || true" &
done

echo "Done!"