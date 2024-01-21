### Experiment design

We need to replay a production VM arrival trace on the system. We can evaluate different packing strategies
then.

Limitation is inventory of the deployment(36 cpu cores) is smaller than of a cloud inventory (~15k+ machines).

Solution is generating a vm trace suitable for the deployment, based on the production trace.

We need to decide followings.

Trace features.

- VM arrival rate: How many VMs arrive at a given time
- VM size: vCPU count
- VM type: Evictable or Regular

Experiment settings.

- Total duration for the experiment
- Time period of Renewable availability

#### Inventory

A five node Openstack cluster with green cores enabled.

- 16 cores: 12 Regular + 4 Green
- 8 cores: 5 Regular + 3 Green
- 4 cores: 4 Regular + 1 Green
- 4 cores: 4 Regular + 1 Green
- 4 cores: 4 Regular + 1 Green \[Physical Access\]

One of the machine provides admin access to bios, and provides host os that runs on bare-metal.

Physical access machine provides power stats, as well as true control over CPU core power management. All machines
provide a packing inventory. Therefore, packing metrics such as green score, density and utilization are calculated
all over the cluster and physical machine provide power consumption metrics.

### Trace goals

Generated trace should roughly utilize inventory around 70-80% (=production cloud inventory data)

#### pre-process

We select X-percentile of the workload. say 90th percentile.

We further pick a time period, t1 and t2. ex: 0.0 - 1.0.

Within the time period, we explore each time step. calculate number of requests in each step, to get request distribution. obtain vcpu distribution
and lifetime distribution. then for the X-th percentile, we find the max number for each (y for vcp, z for requests, etc).

We then reduce the trace by converting each time step via the calculate max values.

if count is too much, we omit all requests from that step. if vcpu is too much, we omit that vm request. likewise.

result is reduced trace.

when pre-process script ran, initially it prits max values. so percentile can be adjusted by guessing for the size of the
inventory we have.

ex: for 26 cores inventory, maybe 4 requests max at a time suits. then 70th percentile is better.