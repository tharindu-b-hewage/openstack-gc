#### Pre-steps
- In the physically accessible node, make sure hyper-threading and power management is disabled.
- Get a CentOS7 image and apply CERN real-time linux kernel modules. Upload this image to Openstack-GC.
- Fill the cluster with VMs based on the uploaded image, until all cores in physical node is occupied.

##### Monitoring
- In each VM, run RTEval benchmark for the duration of the experiment.
- Start running turbostat at the node and dump power data to csv.
- In parallel, collect measurements for Green Score.

#### Experiment
- Wait until system stabilize (VMs running RTEval).
- Reduce Renewables via emulation API, such that Green Cores are put to sleep.
- Wait till stabilize.

#### Post-steps
- Gather data collected, pre-process, and analyze.
- Gather reports from RTEval.