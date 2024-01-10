# openstack-gc

![Go Build](https://github.com/crunchycookie/openstack-gc/actions/workflows/go.yml/badge.svg)

Practical implementation of VM packing with Green Cores via Openstack.

## System architecture

![system-architecture.png](system-architecture.png)

- #### VM Allocator
    - A standard OpenStack deployment with DevStack
- #### VM trace
    - A workload generator (bash script + cron job -> calls Openstack APIs to create a VM request) to emulate a VM
      arrival trace
- #### Green Cores
    1. **Renewable Dynamics**
        - Emulate ELIA traces
    2. **Controller**
        - A Go microservice that utilizes Intel power libraries to control CPU core C-states
        - As instructed by Renewable Dynamics, Core sleep states are managed and Openstack is alerted.

## Deployment

1. Configure single node devstack deployment: [deployment](deployment)
    1. Host is 4 core Intel CPU with hyperthreading disabled. Furthermore, it needs to support C-states of `POLL` and
       `C3_ACPI`, and cpu frequency scaling.
    2. Make sure to create a vm flavor with pinned core property and use it exclusively for all vm creation requests.
2. Run `deploy.sh` to upload files. Make sure to inject required env. vars.
3. Apply Openstack extensions
    1. Feature: Priority core pinning
        1. [readme.md](extensions%2Ffeature-priority-core-pinning%2Freadme.md)
    2. Workaround: Omit sleeping cores from VM packing
        1. [readme.md](extensions%2Fworkaround-omit-sleeping-core-from-pcpu%2Freadme.md)
    3. Restart all devstack services.
4. Deploy green core emulation service
    1. Make sure to edit `gc-emul-vars.sh` file to set remote node details (assumes SSH connection is established.
       refer to feature readme file).
    2. [readme.md](extensions%2Fgc-emulator-service%2Freadme.md)
5. Deploy core-power-mgt service at the compute note ([core-power-mgt](https://github.com/crunchycookie/core-power-mgt))
    1. `wget https://github.com/crunchycookie/core-power-mgt/releases/download/v1.0.0-alpha/gc-controller`
    2. Create a `conf.yaml`
        ```yaml
         host:
             name: <ip>
             port: 3000
         gc:
             pool-size: 4
        ```
    3. Run `sudo ./gc-controller conf.yaml`

## Deployment verification

1. Initially, the green core is asleep by default. So we have three cores available for VM packing. Verify this by
   logging into horizon dashboard under compute -> hypervisors -> vcpu section.
2. Create three VMs. You may
   use [create-vm.sh](vm-trace%2Faz-trace-gen%2Fsrc%2Fmain%2Fresources%2Fos-client%2Fcreate-vm.sh).
3. Poll green-core-emulator api `/is-asleep` and observe that current green core shows asleep. This is not reflected on
   the core
   yet. The first call to the service will fix the sync. Call `/dev/switch` to manually toggle the core state. Now it
   should show awake.
    - At physical host, monitor core state via `i7z` and `turbostat`. All cores should be at `POLL` state, and highest
      frequency.
3. Create the fourth VM.
2. Openstack dashboard now shows 4 vcpus. Also in the physical host, verify core pinning with `virsh`
    1. `virsh list` -> for each, `virsh emulatorpin <domain>`
    2. Each VM (or domain, in virsh terms), should be pinned to a single core. First three should occupy first three
       VMs and the last one pinned to the 3rd core, which is our green core. This means prioritized core pinning works.
4. Toggle `/dev/switch` again. The core should go into sleep mode and shelve its pinned vm.
    - At physical host, monitor core state via `i7z` and `turbostat`. The 3rd core should be at `C3_ACPI` state, and
      lowest frequency.
    - At openstack dashboard (login as admin), the VM that was pinned to the 3rd core should `shelve_offloaded`.
5. Create the 5th VM. The request should fail, because there is no available core to pin (green core is sleeping).
    - At openstack dashboard (login as admin), latest request should be at failed state.
6. Toggle `/dev/switch` again. The core should go into awake mode.
    - At physical host, monitor core state via `i7z`. All cores should be at `POLL` state, and highest frequency.
7. Create the 5th VM. The request should succeed, because there is an available core to pin (green core is awake).
    - At openstack dashboard (login as admin), latest request should be at active state.

## Experiment flow

1. Start green core simulation by talking to the green core emulator service: `/begin`.
2. Start vm trace emulation: Launch the java workload generator.