#!/bin/bash
# set/source env vars first.
# $1 = domain name
virsh -c qemu+ssh://$1@$2/system emulatorpin $3 | virsh-json