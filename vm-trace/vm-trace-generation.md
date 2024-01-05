#### VM trace generation

Ideally we want to run the Azure packing trace on the system.

However, Azure trace cannot be handled by a single computing node.

Therefore, we extract evictable VM dynamics from the Azure trace and generate a new trace.

The generated trace has the same evictable vm probability, and it can test packing capability of GreenFit.

##### Trace period

24 hours: from the beginning of the trace.

##### Extracting real trace dynamics

We normalize number of VMs arrived in a given time, using the largest number of vm arrivals in a given time point. We 
also collect percentage of evictable and non-evictable vms.

Together, we have a time series in which, in a given time point,
- number of vms arrived (0-1)
- amount of evictable/non-evictable vms

##### Generating a new trace

As the compute node has only 4 cores, it's unrealistic to test dynamics of core sizes. Therefore, we set prototype 
system scope to real dynamics of number of vms and evictable/non-evictable vms distribution.

- vm size: 1 core + close to zero RAM and other resources.
- max vm count size: set to 4

Then,
- VM count: from real trace
- evictable/non-evictable vms: from real trace

#### Implementation

A java application that generates the API calls for creation and deletion of VMs, based on the generated trace.

Implementation is found in [az-trace-gen](az-trace-gen).

#### Usage

First, install openstack cli client. We directly use this client to interact with Openstack APIs, without depending
on any third party libraries.

`sudo pip3 install python-openstackclient`

(in Mac OSX, add `~/Libary/Python/3.X/bin` to PATH).

Then, login to Openstack Horizon dashboard (http://<ip>/dashboard) and sign as the admin. Go to the admin project.

Under project section, select API access.

From here, click the button to download the Openstack RC file. This file contains the credentials to access APIs.

This file sets environment variables used by the client. 

Source the file.

`source ***-openrc.sh`

Then make all scripts runnable, such that the client can run them.

`chmod +x *.sh`

Then, run the client (a sample config file is found [configs.properties](az-trace-gen%2Fsrc%2Fmain%2Fresources%2Fconfigs.properties)).

`java -jar trace-gen.jar ./configs.properties`