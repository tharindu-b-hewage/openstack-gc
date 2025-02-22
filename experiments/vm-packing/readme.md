### VM Packing with OpenStack-GC

This experiment demonstrates the VM packing capabilities of the OpenStack-GC prototype.  
It implements the proposed packing algorithm from the OpenStack-GC paper.

**Note:** This experiment showcases the practicality of the packing algorithm and evaluates certain aspects of its performance. However, a detailed performance evaluation would require a hyper-scale deployment.

We conduct a scaled-down experiment on VM packing and renewable energy integration. Specifically, we scale a 24-hour experiment down to 30 minutes. The scaling process involves:

- **VM Arrivals:** The Azure Packing trace is scaled down to 2% of the original 24-hour trace. This is done by:
  - Randomly selecting 2% of VM arrivals.
  - Sampling 2% of each VM deployment request.
  - Scaling the time to 2%.

  As a result, a ~28-minute trace is synthesized, closely matching the characteristics of the original Azure trace for a single day. The dataset is available at [AzureTraceThinned.csv](data/AzureTraceThinned.csv).
- **Renewable Dynamics:** We scale the time axis of the Elia solar trace from 1.0 (a full day) to 0.02083 (~2% of a day).  
  The trace intensity is already normalized (0–1), so we use it as is.

#### Testbed

We use a two-node deployment of Openstack-GC on two HPE Proliant server-grade machines with Intel
Xeon silver CPUs. One server contains 12 cores, whereas the other has 24, reflecting heterogeneous
availability of cores in cloud environments. In both machines we drive half of the cores with 
renewable dynamics (6/12 and 12/24).

#### Experiment

Decide a cutoff threshold for the solar intensity, beyond that, we consider sufficient power
is available to enable additional cores in both machines. Write a script to replay renwable dynamics
according to the cutoff value.

Create VM flavours in the deployment that can support core counts of all vm request in the thinned trace. 
Use a script to adjust VM lifetimes to 2%. Write a script to replay VM deployment requests.

Write a script/methods to gather performance metrics. i.e., analyze before and after VM deployments to collect the
number of evicted VMs and their priority, nLT of the evicted VMs, and potential renewable energy that was harnessed.

Verify implementation of our packing algorithm. Possibly compare against Openstack's default scheduling mechanism.

---
1. [run_vm_trace.py](run_vm_trace.py): emulate renewable dynamics. Here, define a threshold. If the intensity
goes beyond the threshold, poll the switch API. Note that cores must be turned off (low-energy scenario)
prior to experiment. Then if intensity drops below threshold, switch API is again polled.
2. Run power monitoring through RAPL. Continuously log power information in both nodes.
3. [run_vm_trace.py](run_vm_trace.py): Replay VM trace, and log nLT, eviction counts at the end.


-----

1. If the vm request has 'type' as the scheduling hint, which is used to state VM as an evictable VM, then the proposed
scheduling algorithm get engaged. Without that, default implementation follows.
2. Running the experiment with and without the scheduling hint allows us to get data for proposed vs default.