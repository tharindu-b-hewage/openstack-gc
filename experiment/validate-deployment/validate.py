import csv
import sys
import time

import numpy
import openstack
import requests


def create_server(conn, vm_name, type):
    print("Create Server:")

    image = conn.image.find_image('cirros-0.6.2-x86_64-disk')
    flavor = conn.compute.find_flavor('pinned.vcpu-1')
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

with open('validation-trace.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    for count in range(36):
        t = time.time()

        vm_name = 'vm-validation-' + str(count)

        evictable_prob = float(sys.argv[1])
        r_choice = numpy.random.choice(numpy.arange(0, 2), p=[(1-evictable_prob), evictable_prob])
        type = 'regular' if r_choice == 0 else 'evictable'

        vm_vcpu = 1

        didFail = False
        try:
            server = create_server(conn=conn, vm_name=vm_name, type=type)
        except Exception as e:
            didFail = True
            print(e)

        inventory = requests.get(url='http://100.64.42.11:4000/gc/core-usage').json()

        data = [t, vm_name, type, vm_vcpu, didFail, inventory]
        writer.writerow(data)
        f.flush()
        print('processed ' + str(count) + '')
