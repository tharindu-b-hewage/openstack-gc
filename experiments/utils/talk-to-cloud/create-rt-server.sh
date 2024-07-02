TYPE=$1
NAME=$2

echo "===== Usage: sh create-rt-server.sh <type> <name>"
echo "===== Example: sh create-rt-server.sh evictable example-server-1"
echo "===== Important! Make sure to source the demo-openrc.sh file before running this script."

echo "Creating server $NAME with type $TYPE..."

FLAVOR="pinned-centos7-flvr"
NETWORK="private"
IMAGE="centos7-rt"
KEY="common-kp"

openstack server create \
  --flavor $FLAVOR \
  --image $IMAGE \
  --key-name $KEY \
  --hint "type=$TYPE" \
  --network "private" \
  --property hw:cpu_policy=dedicated \
  --boot-from-volume 10 \
$NAME

echo "Server $NAME created successfully."

echo "Assigning floating IP to server $NAME..."
available_ip=$(openstack floating ip list --status DOWN -f value -c "Floating IP Address" | head -n 1)

# If no available floating IPs, create a new one
if [ -z "$available_ip" ]; then
  echo "No available floating IPs. Creating a new one..."
  available_ip=$(openstack floating ip create "public" -f value -c floating_ip_address)
fi

echo "Assigning floating IP $available_ip to server $NAME..."
openstack server add floating ip $NAME $available_ip
