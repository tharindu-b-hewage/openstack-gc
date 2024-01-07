#### Green cores emulation service

This service provide green cores-application specific functionality.

It reads Renewables trace and facilitates core sleeping and VM evictions in Openstack.

- Keep an internal state about Green Core sleep state.
- Exposes internal state via a REST api, such that nova-compute can query from it.
- Upon core awake, internal state is changed, and expects Openstack to query and make core available for scheduling.
- Upon core sleep, change internal state, and invoke Openstack apis to shelve_offload all instances pinned to green core.

##### APIs

- `/gc/begin` : starts monitoring renewables states
- `/gc/is-asleep`: polling api, which returns true if the green core is asleep
- `/gc/dev/begin`: development: devs need to manually change internal state.
- `/gc/dev/switch`: development: change sleep state; sleep to wake, or vice-versa.