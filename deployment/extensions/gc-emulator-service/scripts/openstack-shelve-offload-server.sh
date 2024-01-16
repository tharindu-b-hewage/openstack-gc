#!/bin/bash
# $1 = server name
#openstack server shelve --offload --wait $1
openstack server delete --force --wait --all-projects $1