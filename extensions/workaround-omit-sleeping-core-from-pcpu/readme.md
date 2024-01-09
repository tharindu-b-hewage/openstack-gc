#### Omit sleeping core from vm packing

Once green cores are in sleep mode, this core should be reflected in 
openstack as an offline core. Currently there is no way to dynamically put a core offline.

The worker node service of Openstack is nova-compute, and it achieves virtualization through a library. It supports 
multiple such libraries, and one in our deployment is `libvirt`. Openstack has a wrapper layer for libvirt, and this 
layer exposes host related operations to the compute service. We intercept cpu reading operation of this layer, and
present sleeping green core as an offline core. 

The actual core power management is handled via a custom microservice: [gc-emulator-service](..%2Fgc-emulator-service). 
Our intercepting operation polls this service to identify sleeping cores. This approach is not ideal, because it can 
introduce an additional latency to the operation. However, implementing a proper feature falls out of scope of this 
project. If such feature arrives in the future, we can replace this workaround with the proper feature.

##### Deploy instructions

1. Run [deploy.sh](..%2F..%2Fdeploy.sh).
2. Apply patch [apply-patch.sh](apply-omit-sleeping-core-patch.sh).
3. Restart services with [restart-devstack-services.sh](..%2Frestart-devstack-services.sh)

