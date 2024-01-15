#!/bin/bash

# net-id=<you may use public network's id (can be found in the horizon dashboard)>
# default in devstack: --image "cirros-0.6.2-x86_64-disk" --flavor "m1.nano"
openstack server create --nic net-id="public" --image "cirros-0.6.2-x86_64-disk" --flavor "m1.nano" "$1"