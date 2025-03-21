#!/bin/bash

SRC_HOST=$1  # Replace with your source compute host name
DST_HOST=$2   # Replace with your destination compute host name

# 1. List all servers (all projects) on the source host.
# 2. Extract ID & Name in plain-text format.
# 3. Filter to keep only those whose Name contains 'LOWLATENCY'.
# 4. Loop over each matching server and perform the live migration.

NETWORK="private"
IMAGE="cirros-0.6.2-x86_64-disk"
KEY="common-kp"

openstack server list --host "$SRC_HOST" \
  -f value -c ID -c Name \
| grep LOWLATENCY \
| while read -r SERVER_ID SERVER_NAME; do
    echo "Emulation: Live migrating '$SERVER_NAME' ($SERVER_ID) from $SRC_HOST to $DST_HOST ..."

    # TODO: fix this.
    # for some reason, live migration crashes in the deployment. since we do not evaluate the state of VM, we emulate
    # resource usage by deleting and creating the VM. Further, emulation do not capture real migration time. Which we
    # assume as nil since migration is always within data center on its fast network fabric.
    echo "deleting the instance: "$SERVER_NAME
    openstack server delete "$SERVER_ID" --wait

    echo "creating the instance: "$SERVER_NAME
    openstack server create \
          --flavor pack_2 \
            --image $IMAGE \
              --key-name $KEY \
                --hint "type=evictable" \
                  --network "private" \
                    --property hw:cpu_policy=dedicated \
                      --boot-from-volume 1 \
                        --availability-zone nova:$DST_HOST \
                          --wait \
                          $SERVER_NAME

    # Append a timestamped log line
    echo "DATE: $(date '+%Y-%m-%d %H:%M:%S') | EVENT: LIVE_MIGRATE | DATA: {ID:$SERVER_ID, NAME:$SERVER_NAME, FROM:$SRC_HOST, TO:$DST_HOST}" >> /data/tsaryakarahe/openstack/opt/stack3/openstack-gc/major-revision-experiments/scripts/results/smt-chasing.log
done