## Green Cores Use Case: 5G Network Slicing

### Green Cores for Mixed-criticality RT-Clouds

In-place Renewables integration with Green Cores eliminate the need to shift the workloads, potentially avoiding latency
costs along the Wide Area Networks. Moreover, it provides deterministic compute. As a compromise, the RT-Clouds are
presented with tackling sleep/wake of Green Cores.

CPU-failure tolerant execution of Real-Time (RT) workloads have been well studied in the literature. A notable investigation
is the DREAMS framework: reconfiguration and adaptation of RT systems [1]. The findings show RT use-cases comprise of
critical and non-critical tasks. The avionic example shows in-flight entertainment systems and navigation system, where
former is categorised as best-effort and latter is critical. The work builds on this and propose reconfiguration and
adaptation of the avionic use-case when CPU core failures occur. They leverage best-effort tasks and compromise that to
maintain RT performance. The same framework is extended to RT-Clouds, to leverage VM scheduling for the RT use-case in [2],
where railway applications are executed on VMs. In both cases, an orchestration layer maintain failures of compute 
componentes (CPU cores/VMs) leveraging mixed-criticality of tasks involved.

Based on this body of work, we envision use-case specific RT orchestration layer is able to tolerate evictions of VMs in
the RT-Cloud. At the IaaS layer, the provider's responsibility is to reduce eviction incidents to a minimum, at the same
time harnessing Renewables reasonably well such that carbon expectations are met.

To motivate, we practically implement an RT-Cloud with Green Cores, and conduct experiments to demonstrate the role of 
the IaaS provider.

Our RT use-case is the emerging 5G network slicing with Virtualized Network Functions (VNFs). As investigated in [3], 
each network slice can involve various performance requirements. Slices such as Autonomous Driving and Remote surgery 
demands ultra-reliability and stringiest latency boundaries, whereas slices providing 4K/8K HD Video services and Mass
Gatherings provide room for temporary service disruptions. Therefore, VMs executing corresponding VNFs provide the 
opportunity to harness Renewables via careful orchestration. VNFs that can tolerate temporary disruptions are ideal for
evictability with Green Cores. They provide the opportunity for reconfiguration[1] and to restore the service.

We implement a multi-node RT-Cloud with Green Cores by extending Openstack, an IaaS platform widely used in production. 
We call the extended framework `openstack-gc`. A key metric for better utilization of machine fleets at IaaS is the 
packing density, as providers keep a certain slack of machines empty to provide the elasticity of the cloud. Thus used
machines are typically preferred to be tightly packed. This enables the opportunity to re-deploy a failed VM within the 
datacenter.

Combined, we deploy 5G network slicing with VFN usecase in `openstack-gc` by leveraging Open Source MANO framework. 
MANO handles orchestration of VFN complying with ETSI standards. We deploy MANO on a separate VM and connect `openstack-gc`
as a Virtualized Infrastructure Provider (VIM) using MANO's built-in features. This is the standard deployment pattern
where virtualization of NFVs are provided from VIM and VFN orchestration is provided from MANO. We then deploy two 
network slices in MANO, emulating a 5G network with a critical slice and a best-effort slice. We enable auto-healing
feature of MANO in VFNs, in which MANO monitors and re-deploy upon VM evictions. Our `openstack-gc` provides a total of
16 CPU cores at maximum Renewables level: two nodes where each has minimum of 4 cores and maximum of 8 cores with 
intermittent Renewables. Both network slices occupy 8 cores for VNFs, which means IaaS provider is able to provide full
compute capacity required. Cores always provide stable deterministic performance with disabled power management features
and hyper-threading. In our experiments we first deploy both slices, wait until network stabilizes, and then drop the 
Renewables to zero. At this point the auto-healing of MANO kicks in and re-deploy the VNFs to reconfigure and restore
the system. We collect number of re-deployed VMs and their corresponding network slice. Then we re-iterate the experiment
with different VM packing algorithms IaaS provides (in this case the Openstack). 

Collectively, above experiments show that RT deployment is able to leverage mixed criticality to reconfigure and restore
the service. Observing auto-healing incidents, the role of IaaS provider is to reduce the number of evictions via efficient VM
packing. While doing so, provider needs to be careful such that Renewables harvesting goals are also met. 

Therefore, to harness Renewables with Green Cores, we investigate advancing state of the art in VM packing with the
vertically scaling inventory that Green Cores provide. We conduct cloud-scale experiments, achieve computation goals in
packing algorithms, use real-production traces and propose a tunable packing algorithm that surpasses state-of-the art
mixed-criticality VM packing algorithm in power unstable clouds.

[1] Durrieu, G., Fohler, G., Gala, G., Girbal, S., Pérez, D. G., Noulard, E., Pagetti, C., & Pérez, S. (n.d.). DREAMS about reconfiguration and adaptation in avionics.

[2] Gala, G., Fohler, G., Tummeltshammer, P., Resch, S., & Hametner, R. (2021). RT-Cloud: Virtualization Technologies and Cloud Computing for Railway Use-Case. 2021 IEEE 24th International Symposium on Real-Time Distributed Computing (ISORC), 105–113. https://doi.org/10.1109/ISORC52013.2021.00024

[3] Zhang, Q., Liu, F., & Zeng, C. (2019). Adaptive Interference-Aware VNF Placement for Service-Customized 5G Network Slices. IEEE INFOCOM 2019 - IEEE Conference on Computer Communications, 2449–2457. https://doi.org/10.1109/INFOCOM.2019.8737660
