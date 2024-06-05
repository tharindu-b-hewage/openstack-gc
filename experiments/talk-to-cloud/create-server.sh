#sh create-server.sh "m1.nano" "cirros-0.6.2-x86_64-disk" "regular" "s1"
# gc-vm is a custom flavor with cpu pinning enabled.
openstack server create --flavor gc-vm --image cirros-0.6.2-x86_64-disk --network public --hint "type=$1" $2