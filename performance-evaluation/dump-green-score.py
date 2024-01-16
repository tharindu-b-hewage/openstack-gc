import time

import requests as rq
import sys
import csv

# 1: local node ip
# 2: dump csv file.
print('ip:', sys.argv[1])
print('dump file:', sys.argv[2])
print('begin dumping green-score...')
while True:
    response = rq.get(url='http://' + sys.argv[1] + ':3000/gc-controller/dev/green-score').json()
    print('received response:', response)
    # fields = ['timestamp', 'gs']
    with open(sys.argv[2], 'a') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), response['green-score']])

    time.sleep(5)
