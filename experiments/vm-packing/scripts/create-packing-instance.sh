SCHEDULER=$1
NAME=$2

echo "===== Usage: sh create-rt-server.sh <type> <name>"
echo "===== Example: sh create-rt-server.sh evictable example-server-1 rt_3_PIN"
echo "===== Important! Make sure to source the demo-openrc.sh file before running this script."

echo "Creating server $NAME with $SCHEDULER..."

FLAVOR=$3
NETWORK="private"
IMAGE="cirros-0.6.2-x86_64-disk"
KEY="common-kp"

IS_LOW_LOWLATENCY=false
if echo "$NAME" | grep -q "LOWLATENCY"; then
    IS_LOW_LOWLATENCY=true
fi

#if [ "$SCHEDULER" = "with-nova" ]; then
  # set nova as default, so that gc cpu weighter is not enabled for smt experiment.
openstack server create \
        --flavor $FLAVOR \
          --image $IMAGE \
            --key-name $KEY \
              --hint "is_low_latency=$IS_LOW_LOWLATENCY" \
                --hint "scheduler=$SCHEDULER" \
                  --network "private" \
                    --property hw:cpu_policy=dedicated \
                      --boot-from-volume 1 \
                      $NAME
#else
#  openstack server create \
#          --flavor $FLAVOR \
#            --image $IMAGE \
#              --key-name $KEY \
#                --hint "type=$SCHEDULER" \
#                  --network "private" \
#                    --property hw:cpu_policy=dedicated \
#                      --boot-from-volume 1 \
#                      $NAME
#fi

echo "Server $NAME created successfully."

#echo "Assigning floating IP to server $NAME..."
#available_ip=$(openstack floating ip list --status DOWN -f value -c "Floating IP Address" | head -n 1)
#
## If no available floating IPs, create a new one
#if [ -z "$available_ip" ]; then
#          echo "No available floating IPs. Creating a new one..."
#            available_ip=$(openstack floating ip create "public" -f value -c floating_ip_address)
#fi
#
#echo "Assigning floating IP $available_ip to server $NAME..."
#openstack server add floating ip $NAME $available_ip