echo "All cores needs awaken in Openstack-GC prior executing this script."

echo "Creating two VMs..."
sh launch-vm.sh
sh launch-vm.sh

echo "Resting 5 minutes..."
sleep 300

echo "Dropping renewables to zero..."
curl -v --location --request POST 'http://'$1':'$2'/gc/dev/switch'

echo "Resting 5 minutes..."
sleep 300

echo "Done!"