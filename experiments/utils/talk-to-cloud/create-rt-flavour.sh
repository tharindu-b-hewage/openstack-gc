NAME="pinned-centos7-flvr"
openstack flavor create $NAME --ram 2048 --disk 10 --vcpus 2
openstack flavor set --property hw:cpu_policy=dedicated $NAME