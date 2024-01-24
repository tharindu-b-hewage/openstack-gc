import json

import pandas as pd

from const import init_inv_gc_awake
from nova_sch_greenfit_weight import get_final_weight


def get_inventory(json_string):
    return json.loads(json_string.replace("\'", "\""))


inventory = get_inventory(init_inv_gc_awake)

df = pd.read_csv('validation-trace-files/validation-trace_evict-prob-0.0.csv')
df = df.sort_values(by=['time'])

for index, row in df.iterrows():
    did_fail = row['did-fail']
    if did_fail:
        print(row['vm-name'], '---vm rq failed. not relevant for verification. so skipping...')
        continue
    type = row['type']
    vm_vcpus = row['vm-vcpus']
    weighted_host = []
    for host in inventory:
        rcpu_avl = host['reg-cores-avl']
        gcpu_avl = host['green-cores-avl']
        rcpu_used = host['reg-cores-usg']
        gcpu_used = host['green-cores-usg']
        gcpu_free = gcpu_avl - gcpu_used
        rcpu_free = rcpu_avl - rcpu_used

        # mimic compute filter behaviour, which we verified already (manually).
        if rcpu_free < vm_vcpus:
            continue

        weight = get_final_weight(gcpus_free=gcpu_free, gcpus_used=gcpu_used, rcpus_free=rcpu_free,
                                  rcpus_used=rcpu_used,
                                  type=type, vcpus_free=(gcpu_free + rcpu_free), vcpus_used=(gcpu_used + rcpu_used),
                                  vm_vcpus=vm_vcpus)
        weighted_host.append({'host-ip': host['host-ip'], 'weight': weight})
    sorted_list = sorted(weighted_host, key=lambda k: k['weight'], reverse=True)
    candidate = sorted_list[0]
    best_weight = candidate['weight']

    real_inv_after_placement = get_inventory(row['inventory'])
    print('--------- inv after placement at ', row['time'])
    for host in real_inv_after_placement:
        print(host['host-ip'], host['reg-cores-usg'], 'of', host['reg-cores-avl'],)

    placed_host = None
    for host in real_inv_after_placement:
        ip = host['host-ip']
        before_host = list(filter(lambda x: x['host-ip'] == ip, inventory))[0]
        if host['reg-cores-usg'] != before_host['reg-cores-usg']:
            placed_host = host
            break
    is_success = list(filter(lambda x: x['host-ip'] == placed_host['host-ip'], sorted_list))[0]['weight'] == best_weight

    if not is_success:
        print(row['vm-name'], 'failed!')
        # print('failed! candidate: ', candidate, 'before: ', inventory, 'after: ', real_inv_after_placement)
    # else:
    #     print(row['vm-name'], 'Success!')
    inventory = real_inv_after_placement
