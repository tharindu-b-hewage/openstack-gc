## Support green cores

To implement and observe green cores, compute node behaviour is expected as follows.

- **Req. 01:** Each vCPU is pinned to a physical CPU core
- **Req. 02:** Pack regular cores first, and then pack green cores. Note that its possible an instance having both types.

Its worth noting that there can be multiple other ways to make use of dynamics of green cores. However, based on the
approach, application performance van vary. For example, if we allow vCPU floating on pCPU, and derive an approach
to best make use of green cores, that approach will not be suitable for near real-time applications that require 
core pinning. Our approach captures most workloads, including near realtime, at the expense of high physical resources.
Therefore, the prototype suits best for servers that cater near real-time workloads, which still wants to achieve 
sustainability, which is incredibly difficult since workload migration is not an option in this case.

(we disable hyper-threading. Which further reduces resource contention and favour near-realtime workloads.)

Provisioning an instance in openstack involves hierarchical scheduling. At the controller node, nova-scheduler 
determines which host to place the instance. Then, nova-compute at the host node first decide NUMA node/s. Finally, 
nova-compute decides which pCPU to place the instance.

For green cores, scheduling at nova-scheduler is done by GreenFit. Since it's a separate topic, we will discuss it 
separately.
##todo add link once doc is ready

Out prototype has a single host with a single NUMA node. Therefore, NUMA node scheduling is not involved in our scope. 
This further narrows down to hosts that incur zero costs from memory non-uniform memory access (NUMA) effects, which 
favours near-realtime workloads.

### Req. 01

At vCPU to pCPU mapping, we use a specific flavor for all VMs, in which `hw:cpu_policy` is set to `dedicated`. This 
satisfy **Req. 01:**. This is done by creating the flavor as follows.

`openstack flavor set "m1.nano" --property hw:cpu_policy=dedicated`

Above sets the flavour `m1.nano` to have `hw:cpu_policy` set to `dedicated`. This is the flavor all our VMs use.

#### Impact from emulator threads sharing cpu time with cores

For near-realtime applications, there is a small overhead created by emulator threads. Which means, even if vCPU is 
pinned on pCPU, an emulator thread can steal CPU cycles from the pCPU. To avoid this, Openstack supports isolating 
emulator threads to a certain number of dedicated cores. This is an interesting case for green cores, since such threads
are part of the orchestration, it's under 100% control of the host. A dynamic approach to move emulation to green cores
when its available would be an interesting case to increase its utilization without involving user workloads at all. 
However this is a room for future work. For now, given that we have limited number of cores in the host, we will 
omit the impact from the smaller overhead of emulator threads.

#### Configuring libvirt inventory for pinning

Our host uses libvirt as the hypervisor.

In the `nova.conf`file, we set the below.

```bash
[DEFAULT]
cpu_allocation_ratio=1.0

[compute]
cpu_dedicated_set=1-4
```

Since our host has 4 cores (because H/T is disabled), the above will reserve all cores for flavours using CPU pinning. 
Setting the allocation ratio to 1.0 means core are not overcommited.

We set these values to reduce confusion as much as possible, and to make it straightforward to measure effect of power
consumption. For example, if cores are overcommited, we cannot simply map how sleeping a core would take effect. 

At the same time, near real-time applications would not take much difference from this configuration, because they have 
a dedicated pCPUs pinned.

#### Turning off core power management from Openstack

Openstack can power manage cores. Once enabled, if the core is not allocated, the core would be offline. Just before allocation, it 
will be brought online (performance mode). This is done via dynamic frequency scaling. This feature negatively affects
the experiment.

1. We cannot isolate power savings from green cores. Now power consumption dynamics would be complex.
2. An increased latency to create a VM, because the core needs to be brought online.

Thus, turning off the feature still favours better for near-realtime workloads and allow capturing effects from green 
cores.

To turn off the feature, we set the below in `nova.conf`.

```bash
[libvirt]
cpu_power_management=False
```
It is worth mentioning that the gc-controller microservice that we implement puts the core into even deeper power saving
mode by turning off parts of the core via c-states, in case if someone curious about core offline state controlled by 
Openstack. Thus, we manage it separately. 

#### To summarize on Req. 01,

Below is all the tasks we did so far.

1. Set common flavour to use pinned cores.
2. Set libvirt to use all cores for core pinning.
3. Turn off core power management from Openstack.



