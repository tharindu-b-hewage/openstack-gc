#!/bin/bash

# net-id=<you may use public network's id (can be found in the horizon dashboard)>
# default in devstack: --image "cirros-0.6.2-x86_64-disk" --flavor "m1.nano"
openstack server create --nic net-id="1b980f95-b3a8-4453-813f-911dfedefded" --image "cirros-0.6.2-x86_64-disk" --flavor "m1.nano" "$1"