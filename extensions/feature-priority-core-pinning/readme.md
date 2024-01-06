[continuing from [support-green-cores.md](readme)...]
### Openstack Priority Core Pinning

In order to pack regular cores first, and green cores next, we perform followings.

In Openstack, order of mapping available pCPU to vCPU is not deterministic, and cannot be configured. Therefore, we 
implement an experimental feature to achieve this.

#### Priority core pinning

Existing core pinning does not allow pinning order. We allow configuring two core priority levels; high and low. Below config makes first three cores high priority.

```
[compute]
cpu_high_priority_set=[0,1,2]
```
During pinning, if available, high priority cores are attempted first. If not enough, low priority cores are used.

Implementation is captured in https://github.com/crunchycookie/openstack-gc/issues/13.

#### Realising Req. 02

We set first three regular cores as priority cores. Since common flavour of VMs pin cores, we achieve expected behaviour.

```
[compute]
cpu_high_priority_set=[0,1,2]
```

#### Deploy instructions
1. Run [deploy.sh](..%2F..%2Fdeploy.sh).
2. Set the config,
    ```
    [compute]
    cpu_high_priority_set=[0,1,2]
    ```
    in /etc/nova/nova.conf file.
3. Restart services with [restart-devstack-services.sh](..%2Frestart-devstack-services.sh)

Note: Current PoC version hardcode the config as `cpu_high_priority_set=[0,1,2]`. This will be fixed in future.