### Deployment creation guide for openstack

We create a single node Openstack deployment with DevStack. The same node hosts both Openstack services, and
the allocated VMs.

This means CPU cores are shared for execution of Openstack orchestration, and any other services that host os runs. It 
increases CPU core utilization.

This is fair for our prototype. 

Because, our initial setup keeps each CPU core at maximum performance (clock speed) without going into idle mode. 
Therefore, the additional load should not impact on power readings. The prototype is a proof-of-concept on how practical 
the system can be implemented, mimicking an extreme setup where all cores are at maximum performance -> ready to serve
latency sensitive workloads.

--- monitor system just before creating VMs using htop. Each core utilization is around 20%

#### Prerequisites

Node has the following environment.

- Ubuntu 22.04 Jammy LTS

Start with a clean install if possible, to avoid any issues.

#### Steps

In the hopes of avoiding complex configs in networking, we will create a vpn and connect both nodes to it. This will 
eliminate discoverable issues and emulates nodes in a private network, which is the case for datacenter networks of 
internet providers.

PS: At the time of creating this setup, we used https://login.tailscale.com to create a vpn. Note that this can introduce 
comm. latencies that are not favorable for experiments. To the scope of our experiments, this was irrelevant. 

Before begin with next steps, make sure that both nodes are in the private network and they can ping each other.


1. Create a user named `stack` with sudo privileges.
    - Run `./add-stack-user.sh` ([add-stack-user.sh](add-stack-user.sh))
2. Login as `stack` user.
    - `sudo -u stack -i`
3. Download devstack, navigate to the repo, and pick a stable branch.
    - `git clone https://opendev.org/openstack/devstack`
    - `cd devstack`
    - `git checkout stable/2023.2`
4. Create a file named `local.conf` with the following content. Make sure to replace placeholders.
```bash
[[post-config|$NOVA_CONF]]
[DEFAULT]
cpu_allocation_ratio=1.0
[compute]
cpu_stable_set=0-2
cpu_dynamic_set=3
cpu_sleep_info_endpoint=http://<emulation-service-node-ip>:(emulation-service-port)/gc/is-asleep
[libvirt]
cpu_power_management=False
```
5. Run `./stack.sh`

If success, the final output will look like something similar to this.

```bash
This is your host IP address: <ip-of-control-plane-node>
This is your host IPv6 address: <>
Horizon is now available at http://<ip-of-control-plane-node>/dashboard
Keystone is serving at http://<ip-of-control-plane-node>/identity/
The default users are: <your values>
The password: <your values>

Services are running under systemd unit files.
For more information see: 
https://docs.openstack.org/devstack/latest/systemd.html

DevStack Version: 2023.2
Change: b082d3fed3fe05228dabaab31bff592dbbaccbd9 Make multiple attempts to download image 2023-12-12 08:07:39 +0000
OS Version: Ubuntu 22.04 jammy

2024-01-04 03:50:48.345 | stack.sh completed in 553 seconds.
```
6. Make vm flavor `m1.nano` for pinned cores.
    - `openstack flavor set "m1.nano" --property hw:cpu_policy=dedicated`

#### Post deployment

To stop the services, run `./unstack.sh` in both nodes.

To clean up the deployment, run `./clean.sh` in both nodes.

PS: make sure to use the ip address.