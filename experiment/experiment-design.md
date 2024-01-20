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

### Workload sampling

#### Trace normalization

First, we derive a normalized arrival trace. i.e. We calculate normalized values for the followings in a given time
point, `t`.

Pre-values

- `VCPU_MAX`: Maximum number of vcpu count in an arrived VM
- `Count_MAX`: Maximum number of arrived VMs in a given time
- `LIFETIME_MAX`: Largest VM lifetime

At `t=t`

1. `Request Count` = `actual requests`/`COUNT_MAX`
2. `Regular VMs` = `regular vm count`/`actual requests`
3. `Evictable VMs` = `evictable vm count`/`actual requests`
4. `VM type` = Distribution of `vcpu count`/`VCPU_MAX`
5. `Lifetime` = Distribution of `lifetime`/`LIFETIME_MAX`

Doing this for all time-points yields a normalized trace.

[trace-normalization](trace-pre-process) module contains work for this.

#### Trace Generation

The generator takes 3 arguments.

1. Maximum number of VM requests at a time
2. Maximum lifetime of a VM in fraction of days
3. Maximum vcpu size a VM can take

It monitors the time, and in each time step, generates a certain number of VM requests.

- Number of requests
  - Max. value x normalized request count. Then those requests are grouped into regulars and evictables.
  - If values do not derive integers, none of the requests are generated. Otherwise they are rounded to the nearest int value.
  - For each request,
    - VM lifetime
      - Sampled from the probabilistic model sourced from lifetime distribution * Max. value.
    - VM vcpu
        - Sampled from the probabilistic model sourced from vcpu distribution * Max. value.
