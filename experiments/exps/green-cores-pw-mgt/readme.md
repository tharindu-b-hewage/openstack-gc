## Green Cores as a Power Management Technique

This experiment investigates capability of Green Cores as a 
power management technique. A server in the RT-Cloud runs at 
their maximum performance to guarantee the real-time readiness. 
We emulate a scenario where a heavy RT workload is executed in a
Openstack-GC private cloud, and Renewables drop from 100% to 0%.
We observe the power consumption controlled by the Green Cores.

### Setup

- HP server with Intel Xeon Silver CPU with 12 cores
- Server act as a compute node in Openstack-GC
- Initially, Renewables are at 100% = All cores idle
- Then we deploy two VMs with 6 vcpus each.
- VMs run RTEval to match a complex RT use-case.
- Once the workload is settled in, we drop Renewables to 0%.
- We measure power and CPU characteristics through turbostat.

### Expectation

- Green cores safely dropping service power consumption
  - Observerd via CPU package power drop through RAPL
- Only one VM is evicted. Remaining VM exhibit intact RT performance.

PS: turbostat readings are for every 0.5 seconds.