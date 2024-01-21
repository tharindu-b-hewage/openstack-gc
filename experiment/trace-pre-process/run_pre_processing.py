import csv
import sys
from pre_process_reader import get_trace_at, get_time_after, get_headers, get_bounds_for_percentile

#     make sure to set envs
#     USER = os.getenv("USER")
#     PASSWORD = os.getenv("PASSWORD")
#     HOST = os.getenv("HOST")
#     DB = os.getenv("DB")

interval_start = float(sys.argv[1])
interval_ends = float(sys.argv[2])

print("analyzing from: ", interval_start)
print("analyzing to: ", interval_ends)

max_consts = get_bounds_for_percentile(time_from=interval_start, time_to=interval_ends)

time = interval_start
records = []
with open('4-min-data/nrl_azure_packing_2020.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=get_headers())
    writer.writeheader()
    while time < interval_ends:
        time = get_time_after(time_in_days_fraction=time)
        data = get_trace_at(time_in_days_fraction=time, max_consts=max_consts)
        writer.writerow(data)
        csvfile.flush()
        print("analyze-- time: ", time)

print("Done! Please check the csv file at current directory")



#todo lifetime is -1 observed. fix this!
