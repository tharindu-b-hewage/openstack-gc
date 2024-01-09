# set/source env vars first.
virsh -c qemu+ssh://$NOVA_COMPUTE_NODE_USER@$NOVA_COMPUTE_NODE_IP/system list | virsh-json