## HVM Infeasibility for RT Workloads

Harvesting Renewables with HVM is proposed in the literature when cores are dynamically enabled with Renewable 
energy. We show that for RT VMs such approach compromises the RT performance. Instead, evictability provides 
uncompromised RT performance.

### CPU affinity towards RT performance

First, we conduct the following test to show CPU affinity towards RT performance.

1. We deploy 6 VMs each with 2 vcpus in a 12-core server processor where H/T is disabled. Core pinning is enabled for 
all VMs.
2. First VM is pinned to 2 pcpus. Second floats above 1 pcpu. Third has 2 pcpus. Fourth has 3 cpus, and it goes on.
3. We execute the RTEval in all VMs and collect performance.

![rt-vs-core-affinity.svg](analysis%2Fresults%2Frt-vs-core-affinity.svg)

Results show reduced pcpus can significantly impact latency performance.

### Dynamic CPU affinity of HVM towards RT performance

Then we investigate dynamic affinity of HVM towards RT performance.

1. In a 12-core server processor where H/T is disabled, we deploy 2 VMs with 6 vcpus. Core pinning is enabled for both.
2. Then we execute RTEval tool in both VMs and monitor latency performance.
3. During the test, from a one VM, we remove a pinned pcpu and let vcpu which was pinned to that to float in the 
   remaining pcpus. This is done periodically until that VM only has 1 pcpu pinned.
4. During the end, we collect latency performance reports from both VMs.

![rt-vs-hvm-shrink.svg](analysis%2Fresults%2Frt-vs-hvm-shrink.svg)

During the time, HVM incur large latency performance degradation.