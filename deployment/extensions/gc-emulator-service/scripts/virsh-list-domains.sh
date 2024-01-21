#!/bin/bash
# set/source env vars first.
virsh -c qemu+ssh://$1@$2/system list | virsh-json