#openstack security group rule create --proto icmp --dst-port 0 91ba4d3e-3eed-4e11-92a8-0ddcc6f2c363
openstack security group rule create --proto icmp --dst-port 0 $1
openstack security group rule create --proto tcp --dst-port 22 $1