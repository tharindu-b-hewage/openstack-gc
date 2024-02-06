import json

import pandas as pd

from const import init_inv_gc_awake
from openstackgc_packing_algorithm import get_final_weight


def get_inventory(json_string):
    return json.loads(json_string.replace("\'", "\""))


inventory = get_inventory(init_inv_gc_awake)

packing_data_from_cluster = 'cluster-data_evict-0.1179.csv'
# packing_data_from_cluster = 'cluster-data_evict-0.0.csv'
# packing_data_from_cluster = 'cluster-data_evict-1.0.csv'
df = pd.read_csv('data/' + packing_data_from_cluster)

# df = pd.read_csv(sys.argv[1])
df = pd.read_csv('data/cluster-data_evict-1.0.csv')
#df = pd.read_csv('validation-trace-files/cluster-data_evict-0.0.csv')
#df = pd.read_csv('validation-trace-files/cluster-data_evict-0.1179.csv')
df = df.sort_values(by=['time'])

inv_view = []

is_failures = False
total_vms = 0
stats=[]
clk=0
for index, row in df.iterrows():
    clk+=1
    did_fail = row['did-fail']
    if did_fail:
        print(row['vm-name'], '---vm rq failed. not relevant for verification. so skipping...')
        continue
    vm_type = row['type']
    vm_cpus = row['vm-vcpus']
    weighted_host = []
    for host in inventory:
        rcpus_avl = host['reg-cores-avl']
        gcpus_avl = host['green-cores-avl']
        rcpus_used = host['reg-cores-usg']
        gcpus_used = host['green-cores-usg']
        gcpus_free = gcpus_avl - gcpus_used
        rcpus_free = rcpus_avl - rcpus_used
        usable_cores = rcpus_avl + gcpus_avl
        used_cores = rcpus_used + gcpus_used

        # mimic compute filter behaviour, which we verified already (manually).
        if vm_type == 'regular' and rcpus_free < vm_cpus:
            continue

        #  mimic exhausted host.
        if rcpus_avl > 0 and gcpus_avl > 0 and rcpus_used == rcpus_avl and gcpus_used == gcpus_avl:
            continue


        weight = get_final_weight(
            usable_cores=usable_cores,
            used_cores=used_cores,
            gcpus_avl=gcpus_avl,
            gcpus_used=gcpus_used,
            rcpus_avl=rcpus_avl,
            rcpus_used=rcpus_used,
            type=vm_type,
            vm_cpus=vm_cpus
        )
        weighted_host.append({'host-ip': host['host-ip'], 'weight': weight})
    sorted_list = sorted(weighted_host, key=lambda k: k['weight'], reverse=True)
    candidate = sorted_list[0]
    best_weight = candidate['weight']

    real_inv_after_placement = get_inventory(row['inventory'])
    print('--------- inv after placement at ', row['time'])
    non_empty_cores=0
    non_empty_hosts_cores=0
    g_scores=[]
    transient_time=0
    for host in real_inv_after_placement:
        rused = host['reg-cores-usg']
        gused = host['green-cores-usg']
        gavl = host['green-cores-avl']
        ravl = host['reg-cores-avl']
        utlz = rused + gused
        non_empty_cores += utlz
        if utlz > 0:
            non_empty_hosts_cores+=ravl+gavl
        r_util = rused+gused-ravl
        g_score = r_util
        if r_util <= 0 or gavl <= 0:
            g_score = 0
        g_scores.append(g_score)
        inv_view.append({
            'ip': host['host-ip'],
            'reg-used': host['reg-cores-usg'],
            'reg-avl': host['reg-cores-avl'],
            'g-used': host['green-cores-usg'],
            'g-avl': host['green-cores-avl'],
        })
        print(host['host-ip'],end=': ')
        for i in range(1, host['reg-cores-avl'] + 1):
            if i <= host['reg-cores-usg']:
                print('X',end='')
            else:
                print('_',end='')
        print(' | ', end='')
        for i in range(1, host['green-cores-avl'] + 1):
            if i <= host['green-cores-usg']:
                print('X',end='')
            else:
                print('_',end='')
        print('')
        # print(host['host-ip'], '[', host['reg-cores-usg'], 'of', host['reg-cores-avl'], '] [', host['green-cores-usg'],
        #       'of', host['green-cores-avl'], ']')
    def mean(list):
        return sum(list)/len(list)
    stats.append({
        'clk': clk,
        'pd': non_empty_cores/non_empty_hosts_cores,
        'gs': mean(g_scores)
    })

    placed_host = None
    for post_host in real_inv_after_placement:
        post_ip = post_host['host-ip']
        for pre_host in inventory:
            pre_ip = pre_host['host-ip']
            if post_ip == pre_ip:
                for attr in ['reg-cores-usg', 'reg-cores-avl', 'green-cores-usg', 'green-cores-avl']:
                    if post_host[attr] != pre_host[attr]:
                        placed_host = post_host
                        break
                break

    placed_host_weight = None
    for h in sorted_list:
        if placed_host['host-ip'] == h['host-ip']:
            placed_host_weight = h['weight']
            break

    is_success = placed_host_weight == best_weight

    if not is_success:
        print(row['vm-name'], 'failed!')
        is_failures = True
        # print('failed! candidate: ', candidate, 'before: ', inventory, 'after: ', real_inv_after_placement)
    # else:
    #     print(row['vm-name'], 'Success!')
    inventory = real_inv_after_placement
    total_vms += 1
    print('Total vms:', total_vms)

df = pd.DataFrame(stats)
df.to_csv('results/pre-processed_' + str(packing_data_from_cluster), index=False)

if is_failures:
    print('There are failures...')
else:
    print('All good!')

inv_df = pd.DataFrame(inv_view)
