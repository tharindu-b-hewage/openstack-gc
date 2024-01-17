import sys
import time

import pandas as pd
from math_utils import pickRandom
from external import dispatch

nrl_trace_file = sys.argv[1]
t_start = float(sys.argv[2])
t_stop = float(sys.argv[3])

max_rq_cnt = float(sys.argv[4])
max_lft = float(sys.argv[5])
max_vcpu_cnt = float(sys.argv[6])

print("nrl_trace_file: ", nrl_trace_file, " t_start: ", t_start, " t_stop: ", t_stop, " max_rq_cnt: ", max_rq_cnt,
      "max_lft: ", max_lft, "max_vcpu_cnt: ", max_vcpu_cnt)

df = pd.read_csv(nrl_trace_file)
df = df[t_start <= df['time']]
df = df[df['time'] <= t_stop]


def generate_reg_rqs(rq_count, row, time, type, bucket):
    for rq in range(rq_count):
        lifetime = pickRandom(dst=row['lifetime_distribution'][0]) * max_lft
        vcpu = round(pickRandom(dst=row['vcpu_distribution'][0]) * max_vcpu_cnt)
        if vcpu > 0:
            bucket.append({
                'name': 'VM-' + str(time) + '-' + type + '-' + str(rq),
                'type': type,
                'lifetime': lifetime,
                'vcpu': vcpu
            })


t_s = df['time'].values
for idx, t in enumerate(t_s):
    print("time: ", t)
    row = df.loc[df['time'] == t].to_dict('list')
    print('row', row)

    vm_rqs = []
    total_rq_cnt = row['request_count'][0] * max_rq_cnt
    reg_rq_cnt = round(total_rq_cnt * row['regular_vm_count'][0])
    evct_rq_cnt = round(total_rq_cnt * row['evictable_vm_count'][0])
    print('total_rq_cnt',total_rq_cnt, 'reg_rq_cnt',reg_rq_cnt, evct_rq_cnt)
    if reg_rq_cnt > 0:
        generate_reg_rqs(rq_count=reg_rq_cnt, row=row, time=t, type='regular', bucket=vm_rqs)
    if evct_rq_cnt > 0:
        generate_reg_rqs(rq_count=evct_rq_cnt, row=row, time=t, type='evictable', bucket=vm_rqs)

    dispatch(vm_rqs=vm_rqs)

    if (idx + 1) < len(t_s):
        t_to = t_s[idx + 1] - t
        wait_for = t_to * (24 * 3600)
        print("time: ", t, "total requested: ", len(vm_rqs), "waiting for: ", wait_for)
        time.sleep(wait_for)
