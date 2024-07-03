import csv
import sys
import time

import numpy
import openstack
import requests

'''Packing experiment

This script is used to generate a trace of VM requests. It will create VMs with a given probability of being evictable.
Furthermore, it will also record the inventory of the hosts at the time of the VM request. Here inventory means the core 
usage of the hosts, for stable and green cores.

`python3 run_experiment.py <evictable-probability> <max-servers-to-create>`

<max-servers-to-create> is optional. If not provided, it will create a maximum of 36 VMs. If provided, say 200, it will
 keep generating 200 VM requests.
 
Say to generate a trace with 0.5 probability of being evictable, but we also need to run the experiment until cluster is 
fully utilized. Then we can set the max count to a large number with the evictable probability set to 0.5. Then all 
regular cores will be utilized and green cores will be filled as evictables arrive - in-between on-demand VMs will be
rejected by openstack.
``python3 run_experiment.py 0.5 200``

Firstly, run this script and get data from the cluster.
Then, pre-process data to convert into metrics: `pre_process_data.py`.
Finally, plot the metrics: `results/plot.py`.
'''


def create_server(conn, vm_name, type):
    print("Create Server:")

    image = conn.image.find_image('cirros-0.6.2-x86_64-disk')
    flavor = conn.compute.find_flavor('pinned.vcpu-1') # make sure to create this favour in openstack, with core pinning enabled as flavour attribute
    network = conn.network.find_network('public')

    server = conn.compute.create_server(
        name=vm_name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": network.id}],
        scheduler_hints={'type': type}
    )

    return conn.compute.wait_for_server(server)


conn = openstack.connect(cloud='devstack-admin')

header = ['time', 'vm-name', 'type', 'vm-vcpus', 'did-fail', 'inventory']

with open('data/cluster-data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    servers_created = 0

    max_created_servers = None
    if sys.argv[2] is not None:
        max_created_servers = int(sys.argv[2])

    count_upper_limit = 200
    if max_created_servers is None:
        count_upper_limit = 36
    for count in range(count_upper_limit):

        if max_created_servers is not None and servers_created >= max_created_servers:
            break

        t = time.time()

        vm_name = 'vm-validation-' + str(count)

        evictable_prob = float(sys.argv[1])
        r_choice = numpy.random.choice(numpy.arange(0, 2), p=[(1 - evictable_prob), evictable_prob])
        type = 'regular' if r_choice == 0 else 'evictable'

        vm_vcpu = 1

        didFail = False
        try:
            server = create_server(conn=conn, vm_name=vm_name, type=type)
            servers_created += 1
        except Exception as e:
            didFail = True
            print(e)

        inventory = requests.get(url='http://<control-plane-ip>:4000/gc/core-usage').json()

        data = [t, vm_name, type, vm_vcpu, didFail, inventory]
        writer.writerow(data)
        f.flush()
        print('processed ' + str(count) + '', 'servers created: ' + str(servers_created))
