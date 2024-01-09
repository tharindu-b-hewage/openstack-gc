#### Green cores emulation service

This service provide green cores-application specific functionality.

It reads Renewables trace and facilitates core sleeping and VM evictions in Openstack.

- Keep an internal state about Green Core sleep state.
- Exposes internal state via a REST api, such that nova-compute can query from it.
- Upon core awake, internal state is changed, and expects Openstack to query and make core available for scheduling.
- Upon core sleep, change internal state, and invoke Openstack apis to shelve_offload all instances pinned to green
  core.

We use minimum invasive approach in this proof-of-concept implementation. We expect openstack to poll and identify 
green core sleep status. To identify which openstack guests are pinned to the green core, we talk directly to the 
virtualization service `libvirt`, obtain an id, then ask openstack about the guest name by providing this id. This way
we work with currently available APIs. Also, we do not depend on 3rd party SDKs, but rather call first-party CLIs 
through this service. In this manner we primarily depend on APIs, making sure that our implementation will be supported
with new versions of the software. At the same time, multiple API calls can incur delay, thus high transition time on
power states. This can put stress on the power delivery system (for example, gc awake -> sleep duration might add more
pressure to the UPS system). Such bottlenecks can be avoided in production by providing first-class support to green 
cores in openstack.

##### APIs

- `/gc/begin`:
    1. Starts a routine to read Renewables trace and change Green Core power status accordingly.
        - **to-sleep:**
            1. Change poll api response to sleep.
            2. Talks to Openstack, and shelve_offload all instances using the Green Core -- synchronous
            3. Talks to core-power-mgt apis and put physical core to sleep mode
        - **to-awake:**
            1. Talks to core-power-mgt apis and put physical core to sleep mode
            2. Change poll api response to awake.
- `/gc/is-asleep`: polling api, which returns true if the green core is asleep
    1. External apis can poll. Returns current sleep state of the Green Core.
- `/gc/dev/switch`: development: change sleep state; sleep to wake, or vice-versa.
    1. Change power status manually, and perform same **to-sleep** and **to-awake** tasks as in `/gc/begin`.

#### Pre-requisites

- Configure libvirt permission through SSH
    - This service talks directly to libvirt to obtain specific core-pinning information
    - First, allow SSH access from client to remote machine
    - Seconds, at the remote, `sudo usermod -G libvirt -a <username>`, to grant permission to the connecting SSH user.
    - Run `virsh -c qemu+ssh://<username>@<remote-ip>/system` to verify.
- Install virsh json parser
    - Run `go install github.com/a-h/virshjson/cmd/virsh-json@latest`
- Install Openstack CLI client
- Make scripts runnable
    - `sudo chmod +x *.sh`

#### Build

[build-for-linux-amd64.sh](build-for-linux-amd64.sh) will build the service for Linux + amd64 platform.

#### Run

- Make sure `virsh-json` command runs the tool. If terminal says it cannot be found, make sure to put it in the path
  variable (example: `~/go/bin` folder is in your path)
- Edit to set correct values and run, `source gc-emul-envs.sh`
- Start the service via `./gc-emulator-service`