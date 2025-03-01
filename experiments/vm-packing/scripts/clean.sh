#!/bin/bash

echo "Fetching list of all VMs..."
VM_LIST=$(openstack server list -f value -c ID)

if [ -z "$VM_LIST" ]; then
    echo "No VMs found. Exiting."
    exit 0
fi

echo "Deleting all VMs..."
for VM_ID in $VM_LIST; do
    echo "Deleting VM: $VM_ID"
    openstack server delete "$VM_ID"
done

echo "All VMs have been deleted."

echo "Fetching list of all volumes..."
VOLUME_LIST=$(openstack volume list -f value -c ID)

if [ -z "$VOLUME_LIST" ]; then
    echo "No volumes found. Exiting."
    exit 0
fi

echo "Deleting all volumes..."
for VOLUME_ID in $VOLUME_LIST; do
    STATUS=$(openstack volume show "$VOLUME_ID" -f value -c status)

    if [[ "$STATUS" == "in-use" ]]; then
        echo "Detaching volume: $VOLUME_ID"
        ATTACHED_SERVER=$(openstack volume show "$VOLUME_ID" -f value -c attachments | grep -oP '(?<=server_id": ")[^"]*')
        if [ -n "$ATTACHED_SERVER" ]; then
            openstack server remove volume "$ATTACHED_SERVER" "$VOLUME_ID"
            sleep 3  # Wait for detachment to complete
        fi
    fi

    echo "Deleting volume: $VOLUME_ID"
    openstack volume delete "$VOLUME_ID"
done

echo "All volumes have been deleted."