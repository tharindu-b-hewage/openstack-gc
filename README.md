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

We build on top of the latest stable openstack version, `stable/2023.2`.

1. Configure a single node devstack deployment. Below is the environment tested.
    - CPU: 11th Gen Intel(R) Core(TM) i7-1165G7 + hyper-threading disabled (supports 4 cores with `POLL` and `C3_ACPI`
      idle states)
    - OS: Ubuntu Jammy
    - Note: a separator user created for devstack deployment, under the name `stack` is assumed and used in scripts.
    - Download `admin-openrc.sh` file in the admin project under the `API ACCESS` tab in the dashboard.
2. Apply feature patches.
    - Clone nova-compute source code mirror - https://github.com/openstack/nova.git.
    - Checkout to `stable/2023.2` branch.
    - Apply
      patch [nove-compute-feature-branch-diff-with-stable_2023.2.diff](extensions%2Fnove-compute-feature-branch-diff-with-stable_2023.2.diff).
        - `0e296ed1b97e5998add512a6294109d3613b0f8a`: Enables add priority during pinning vcpu to pcpu
        - `30f8635b72128b6cf3b63a05fa09e0e0a79a14c3`: Enables core isolation when a cpu is identified as sleeping. This
          extends offline cpu detection feature to be aware of sleeping cores, which is provided by polling an external
          endpoint in the same node. This polling ip is hardcoded, so upon applying patch, make sure to update the ip.
3. Prepare deployment environment
    - We use two nodes.
        - `Controller`: Runs emulation service. A VM can be used.
        - `compute`: Runs Openstack services, and `gc-controller` service. This is the same devstack deployment node as
          of
          step 01. Need to make sure that its ubuntu running on bare-metal, and not a VM. This way power metrics are
          accurate, because `gc-controller` need to control physical core through kernel.
    - Configure [deploy.sh](deploy.sh) with correct node details, according to the above (need to set env vars).
    - `Controller` should be able to access `compute` node via SSH. Configure this by adding private key to `Controller`
      node. Attempt `ssh <compute-ip>` from `Controller` node to verify and setup initial trust (this is required for
      emulation service to talk with `libvirt` running at `compute`).
4. Run `deploy.sh` to upload files. Make sure to inject required env. vars.
    - Ex. `USER=ubuntu HOST=<controller-ip> WORKPLACE=<controller-workspace> OS_CORE_PINNING_FEATURE_REPO="
      <cloned-feature-applied-nova-compute-repo-path>" DEVSTACK_USER=stack DEVSTACK_HOST=<compute-ip> DEVSTACK_WORKPLACE=<compute-workspace> sh deploy.sh`
    - Make sure that corresponding workspace folders are created upfront. In devstack node, workspace needs to be
      created under `stack` user.
    - This will upload files to respective nodes.
5. Apply patched in the compute node by
   running [apply-omit-sleeping-core-patch.sh](extensions%2Fworkaround-omit-sleeping-core-from-pcpu%2Fapply-omit-sleeping-core-patch.sh)
   and
   [apply-priority-core-pinning-patch.sh](extensions%2Ffeature-priority-core-pinning%2Fapply-priority-core-pinning-patch.sh).
6. Start `gc-controller` service at the compute node.
    - Create a `conf.yaml` file with following content.
        ```yaml
        host:
            name: <compute-ip>
            port: 3000
        gc:
            pool-size: 4
        ```
    - Run `sudo ./gc-controller conf.yaml` (might need to set ownership via `sudo chmod +x gc-controller`).
    - Service should be up and ready to serve without any errors.
7. Start `gc-emulator-service` service at the controller node.
    - Source openstack configs with `source admin-openrc.sh`.
    - Source gc communication configs with `source gc-emul-envs.sh` (make sure to check whether it has correct values).
    - Run `sudo ./gc-emulator-service` (might need to set ownership via `sudo chmod +x gc-emulator-service`).
    - Service should be up and ready to serve without any errors.
8. Finally, restart all devstack services with `sh restart-devstack-services.sh`. Logs should not cont

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