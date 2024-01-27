### Power experiment

This document describe testing power consumption in the openstack-gc.

Our physical node consists of 04 cores, prepped for realtime workload(=hyperthreading-disabled).

1. Fire up gc-controller. Set all cores to awake state. This sets all cores at peak performance with power management features disabled.
2. We deploy a minimal cent os 7 with CERN realtime kernel modules installed. A VM with this, is ready for realtime.
3. For all metrics, the script that collects green score, and turbostat collecting power stats should be up and running.

#### Experiment 1: Power usage with realtime workloads

Deploy 04 VMs with the said configuration (centos + cern realtime). Use virsh command to pin each VM to 
a single core.
```bash
virsh vcpupin <vm-name> # observe pin config
virsh vcpupin <vm-name> 0 <desired pin> # our vm only has a single core. So we pin that core (0th one) to a pcpu.
virsh vcpupin <vm-name> # observe and validate.
```
Start rteval tool for 15 minutes in each vm. For
this task, we can directly connect to the node with virt-manager and use the GUI.

Allow system to stabilize (wait at least 2-5 minutes, observe cpu utilization is at high level). 

Force delete vm on the 4th core (green core). Signal gc-controller to put that core into sleep mode.

Allow system to stabilize again (wait at least 2-5 minutes, observe cpu utilization is at relatively low level).

Experiment is done. stop all VMs, kill gc-controller service with cntrl + c.

#### Experiment 2: Power usage with non-realtime workloads

Do the same, without starting rteval. Also, repeat without any VMs at all.