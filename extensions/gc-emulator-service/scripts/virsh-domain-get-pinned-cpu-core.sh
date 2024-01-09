# set/source env vars first.
# $1 = domain name
virsh -c qemu+ssh://$NOVA_COMPUTE_NODE_USER@$NOVA_COMPUTE_NODE_IP/system emulatorpin $1 | virsh-json