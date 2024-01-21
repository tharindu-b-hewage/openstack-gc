import math
import sys
import time
import uuid

import pandas as pd

from external import RequestsManager
from math_utils import pick_random

# 1 - normalized azure trace csv
# 2 - starting time
# 3 - end time
# 4 - max number of requests at a time
# 5 - max lifetime of a vm
# 6 - max vcpu of an instant

# Example:
# python3 trace-generator.py 4-min-test/nrl_azure_packing_2020_perc_55.csv 0.819502315018326 0.8208333 5 14.93 12
# csv file is generated for 4 minutes (0.00277778 days) between 0.819502315018326 and 0.8208333. max req. set to 5 and
# max lifetime is the duration of experiment.
# Lifetime max:
# -- 24hours: 89.6387860183604 (unscaled val. in the trace)
# -- 4 min: 14.93 (above linearly scaled down for 4)

nrl_trace_file = sys.argv[1]
t_start = float(sys.argv[2])
t_stop = float(sys.argv[3])

# max_rq_cnt = float(sys.argv[4])
# max_lft = float(sys.argv[5])
# max_vcpu_cnt = float(sys.argv[6])

print("nrl_trace_file: ", nrl_trace_file, " t_start: ", t_start, " t_stop: ", t_stop)

df = pd.read_csv(nrl_trace_file)
df = df[t_start <= df['time']]
df = df[df['time'] <= t_stop]

EXPERIMENT_UUID = uuid.uuid4()


def generate_rqs(rq_count, row, time, type, bucket):
    for rq in range(rq_count):
        lifetime = pick_random(dst=eval(row['lifetime_distribution'][0]))
        vcpu = round(pick_random(dst=eval(row['vcpu_distribution'][0])))
        if vcpu > 0:
            bucket.append({
                'name': 'VM-' + str(EXPERIMENT_UUID) + '-' + str(time) + '-' + type + '-' + str(rq),
                'type': type,
                'lifetime': lifetime,
                'vcpu': vcpu
            })


t_s = df['time'].values
os_manager = RequestsManager()
for idx, t in enumerate(t_s):
    row = df.loc[df['time'] == t].to_dict('list')

    vm_rqs = []
    total_rq_cnt = row['request_count'][0]
    # here rounding is upto us. we favour more evictable vms, assuming fine-grain trace analysis allows us to realize
    # slightly larger evictable vm types.
    reg_rq_cnt = round(
        math.floor(total_rq_cnt * row['regular_vm_count'][0])
    )
    evct_rq_cnt = round(
        math.ceil(total_rq_cnt * row['evictable_vm_count'][0])
    )
    if reg_rq_cnt > 0:
        generate_rqs(rq_count=reg_rq_cnt, row=row, time=t, type='regular', bucket=vm_rqs)
    if evct_rq_cnt > 0:
        generate_rqs(rq_count=evct_rq_cnt, row=row, time=t, type='evictable', bucket=vm_rqs)

    #print('row: ', row, 'rq: ', vm_rqs, 'total rq: ', total_rq_cnt, 'evct: ', evct_rq_cnt, ' reg: ', reg_rq_cnt)

    os_manager.handle_expired_vms(clk=t)
    os_manager.dispatch(vm_rqs=vm_rqs, clk=t)

    if (idx + 1) < len(t_s):
        t_to = t_s[idx + 1] - t
        wait_for = t_to * (24 * 3600)
        print("time: ", t, "total requested: ", len(vm_rqs), "waiting for: ", wait_for, "cls util: ",
              os_manager.get_utilization())
        time.sleep(wait_for)

os_manager.dump(file_path='./trace-emulation-report_' + str(time.time()) + '.csv')
