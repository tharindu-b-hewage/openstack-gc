import csv
import sys
from nrl_trace_handler import get_trace_at, get_time_after, get_headers, get_max_consts

#     make sure to set envs
#     USER = os.getenv("USER")
#     PASSWORD = os.getenv("PASSWORD")
#     HOST = os.getenv("HOST")
#     DB = os.getenv("DB")

interval_start = float(sys.argv[1])
interval_ends = float(sys.argv[2])

print("analyzing from: ", interval_start)
print("analyzing to: ", interval_ends)

max_consts = get_max_consts(time_from=interval_start, time_to=interval_ends)

time = interval_start
records = []
while time < interval_ends:
    time = get_time_after(time_in_days_fraction=time)
    data = get_trace_at(time_in_days_fraction=time, vcpu_max=max_consts["vcpu_max"], count_max=max_consts["count_max"],
                        lifetime_max=max_consts["lifetime_max"])
    print("analyze-- time: ", time)
    records.append(data)

print("dumping normalized records...")
with open('nrl_azure_packing_2020.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=get_headers())
    writer.writeheader()
    writer.writerows(records)

print("Done! Please check the csv file at current directory")
