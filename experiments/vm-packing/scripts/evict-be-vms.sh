#!/bin/bash

HOST_NAME=$1

# 1. List all servers on the specified host (across all projects)
# 2. Extract just the ID and NAME in a text format
# 3. Filter to keep only those whose NAME contains 'BESTEFFORT'
# 4. Read each line of output (ID NAME) in a loop

openstack server list \
    --all-projects \
    --host "$HOST_NAME" \
    -f value -c ID -c Name \
| grep BESTEFFORT \
| while read -r ID NAME; do
    echo "Deleting server: ID=$ID, NAME=$NAME"

    # 5. Delete each server in its own request:
    openstack server delete "$ID" --wait
done