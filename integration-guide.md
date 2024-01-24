### Integration Guide

This document describes how to integrate GreenFit into Openstack.

Before we begin, it might be easier to create a vpn and connect all nodes to it. We tested the setup with `tailscale` vpn.

Decide an IP plan. We use 
```bash
HOST_IP=100.64.42.XX
FIXED_RANGE=10.4.128.0/20
FLOATING_RANGE=100.64.42.128/25
```
Host IPs are set from 100.64.42.11 to .99.

1. Go to controller node, and run [add-stack-user.sh](deployment%2Fadd-stack-user.sh) to add a user named `stack` with sudo privileges.
2. Login as `stack` user.
    - `sudo -u stack -i`
3. Download devstack, navigate to the repo, and checkout to `stable/2023.2` branch.
4. Create a file named `local.conf` with the following content.
```bash
[[local|localrc]]
ADMIN_PASSWORD=secret
DATABASE_PASSWORD=$ADMIN_PASSWORD
RABBIT_PASSWORD=$ADMIN_PASSWORD
SERVICE_PASSWORD=$ADMIN_PASSWORD
HOST_IP=100.64.42.XX
FIXED_RANGE=10.4.128.0/20
FLOATING_RANGE=100.64.42.128/25

[[post-config|$NOVA_CONF]]
[DEFAULT]
cpu_allocation_ratio=1.0
[compute]
cpu_sleep_info_endpoint=http://<controller-node-ip>:<emulation-service-port>/gc/is-asleep
cpu_stable_set=<core ids of stable cores. ex: 0-4>
cpu_dynamic_set=<core ids of dynamic cores. ex: 5-7>
[libvirt]
cpu_power_management=False
```
5. Let's deploy emulation service. Build by running [build-for-linux-amd64.sh](extensions%2Fgc-emulator-service%2Fbuild-for-linux-amd64.sh). 
Then copy [gc-emulator-service](extensions%2Fgc-emulator-service%2Fgc-emulator-service) binary to the same controller node.
6. Create a config file named `conf.yaml` with the following content. Add all compute host details.
```yaml
compute-hosts:
  - ip: 100.100.100.100
    user: ubuntu
    dynamic-core-ids: [3,4,5]
  - ip: 100.100.100.101
    user: ubuntu
    dynamic-core-ids: [4,5]
```
7. Now, setup SSH access from controller node to all compute nodes (copy public key to authorized keys in compute nodes: do it for the current node as well-controller to controller as we run a nova service there too). Test connection by `ssh <user>@<ip>` for all computing nodes.
8. Upload all 3rd party scripts to the same location as the emulator service: [scripts](extensions%2Fgc-emulator-service%2Fscripts)
9. Install json parser for virsh. - Install virsh json parser
   - Run `go install github.com/a-h/virshjson/cmd/virsh-json@latest`
   - Make sure `virsh-json` is detected and identified as a command.
10. Run `./gc-emulator-service conf.yaml` to start the service (consider creating a screen `screen -S gc-emulation-scr` -> run and detach, if you wish to run as a background process - so chances for os to terminate will be limited).
9. In each compute host, copy `gc-controller` binary from the latest release. Refer core-power-mgt repo and create a config file. Make sure
core ids and sleep states are correct. In the same repo, copy all `.sh` scripts as well. Also, install `virsh-json` via go and copy that binary to the same folder. Then run `./gc-controller conf.yaml` to start the service, in each compute host. Do the same in the controller node, as we use it as a compute node as well  (consider creating a screen `screen -S gc-emulation-scr` -> run and detach, if you wish to run as a background process - so chances for os to terminate will be limited).
10. Allow controller to discover all nodes with `nova-manage cell_v2 discover_hosts --verbose`
11. Now all supplementary services are up and running. Lets deploy Openstack. In the controller node, run `./stack.sh`.
11. Once Openstack is up and running, deploy devstack in each compute node. But for them we use below `local.conf` file.
```bash
[[local|localrc]]
HOST_IP=100.64.42.XX
FIXED_RANGE=10.4.128.0/20
FLOATING_RANGE=100.64.42.128/25
LOGFILE=/opt/stack/logs/stack.sh.log
ADMIN_PASSWORD=secret
DATABASE_PASSWORD=secret
RABBIT_PASSWORD=secret
SERVICE_PASSWORD=secret
DATABASE_TYPE=mysql
SERVICE_HOST=<controller-node-ip>
MYSQL_HOST=$SERVICE_HOST
RABBIT_HOST=$SERVICE_HOST
GLANCE_HOSTPORT=$SERVICE_HOST:9292
ENABLED_SERVICES=n-cpu,c-vol,placement-client,ovn-controller,ovs-vswitchd,ovsdb-server,q-ovn-metadata-agent
NOVA_VNC_ENABLED=True
NOVNCPROXY_URL="http://$SERVICE_HOST:6080/vnc_lite.html"
VNCSERVER_LISTEN=$HOST_IP
VNCSERVER_PROXYCLIENT_ADDRESS=$VNCSERVER_LISTEN
[[post-config|$NOVA_CONF]]
[DEFAULT]
cpu_allocation_ratio=1.0
[compute]
cpu_sleep_info_endpoint=http://<controller-node-ip>:<emulation-service-port>/gc/is-asleep
cpu_stable_set=<core ids of stable cores. ex: 0-4>
cpu_dynamic_set=<core ids of dynamic cores. ex: 5-7>
[libvirt]
cpu_power_management=False
```
12. Run Openstack via `./stack.sh`.
13. In all nodes, apply feature patches. [nova-feature-diff.patch](extensions%2Fnova-feature-diff.patch) is the comparison between features and `stable/2023.2` branch. Use
`nova` git repo to apply the patch and copy all changed files to all nodes. You can live patch these files in `/opt/stack/nova/nova/` directory in each node.
13. After patching, restart all services in all nodes. first controller, and then others. `sudo systemctl restart devstack@*`
14. Now, we have a working Openstack deployment with GreenFit. Let's create a VM. First, lets create a flavor for pinned cores. Log into dashboard and select the 
flavour `m1.nano`. Add and attribute `hw:cpu_policy` with value `dedicated`.
14. In the dashboard, inspect compute hosts. We should see all compute nodes.
15. In the dashboard, upgrade quota limits. Calculate total number of cores, and set the limit to that number. (admin->system->default)
15. Now, create a VM with the flavor `m1.nano`. This will be pinned to the stable cores. [create-vm.sh](vm-trace%2Faz-trace-gen%2Fsrc%2Fmain%2Fresources%2Fos-client%2Fcreate-vm.sh)
will do this, but make sure to download `admin-openrc.sh` from dashboard under `API Access`, and source it in the terminal. Since emulation service uses this file to 
authenticate with Openstack APIs, stop and restart the emulation service once the file is sourced. Also, find the public network's ID from dashboard and update the `create-vm.sh` script.
16. Run `./create-vm.sh` to create a VM. Verify that the VM is created in the dashboard.
17. Initially all green cores are asleep. So call emulation API and switch the status to wake them up. Then keep creating VMs to consume all cores in the mini-cluster.
18. Now switch the green cores to sleep through emulation API. This should delete all VMs occupied green cores.
19. Ta da! You have a working cluster with Green Cores. Try experimenting with different scheduling approaches so that unstable Green Cores can be effectively utilized.
+
20. feature patch includes green fit via modified compute filter and cpu weighter. Make sure to configure nova.conf, such that only weighter used is the cpu weighter.

For health check, run [health-check.py](health-check.py) in the same folder as `gc-emulator-service` binary. 
`python3 health-check.py <controller-node-ip>`. It reads config file, and check health for `gc-emulation` and all `gc-controller` services.