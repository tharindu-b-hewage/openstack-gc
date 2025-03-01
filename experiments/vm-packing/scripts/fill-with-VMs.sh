#!/bin/bash

# OpenStack parameters (modify accordingly)
IMAGE_NAME="centos7-rt"
FLAVOR_NAME="packing_1_PIN"
NETWORK_NAME="private"
VM_PREFIX="fill-up"
KEY="common-kp"
hint="evictable"

# Get available vCPUs
AVAILABLE_VCPUS=$(openstack hypervisor stats show -f value -c vcpus_used)
TOTAL_VCPUS=$(openstack hypervisor stats show -f value -c vcpus)
FREE_VCPUS=$((TOTAL_VCPUS - AVAILABLE_VCPUS))

COUNT=1

echo "Total vCPUs: $TOTAL_VCPUS"
echo "Currently used vCPUs: $AVAILABLE_VCPUS"
echo "Available vCPUs: $FREE_VCPUS"

while [ $FREE_VCPUS -gt 0 ]; do
    echo "Creating VM: $VM_PREFIX-$COUNT"

    # Create a VM
    openstack server create \
        --image "$IMAGE_NAME" \
        --flavor "$FLAVOR_NAME" \
        --key-name $KEY \
        --hint "type=$TYPE" \
        --network "private" \
        --property hw:cpu_policy=dedicated \
        --boot-from-volume 15 \
        "$VM_PREFIX-$COUNT"

    echo "Assigning floating IP to server $NAME..."
    available_ip=$(openstack floating ip list --status DOWN -f value -c "Floating IP Address" | head -n 1)

    # If no available floating IPs, create a new one
    if [ -z "$available_ip" ]; then
              echo "No available floating IPs. Creating a new one..."
                available_ip=$(openstack floating ip create "public" -f value -c floating_ip_address)
    fi

    echo "Assigning floating IP $available_ip to server $NAME..."
    openstack server add floating ip "$VM_PREFIX-$COUNT" $available_ip

    # Recalculate available vCPUs
    AVAILABLE_VCPUS=$(openstack hypervisor stats show -f value -c vcpus_used)
    FREE_VCPUS=$((TOTAL_VCPUS - AVAILABLE_VCPUS))

    echo "Available vCPUs after creating $VM_PREFIX-$COUNT: $FREE_VCPUS"

    COUNT=$((COUNT+1))
done

echo "No more available vCPUs. Stopping VM creation."