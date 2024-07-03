source admin-openrc.sh

IMG_NAME="centos7-rt"

# Upload the image
openstack image create $IMG_NAME --file $1 --disk-format qcow2 --container-format bare --public

# Set CPU policy to dedicated
openstack image set --property hw:cpu_policy=dedicated $IMG_NAME