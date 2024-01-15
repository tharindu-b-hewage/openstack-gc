# import pyyaml module
import sys
import json
import subprocess

import yaml
from yaml.loader import SafeLoader
import requests

# Open the file and load the file
with open('conf.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    print('configs:',json.dumps(data, indent=2))

    # test gc-emulation service
    print("1. checking health of gc-emulation-service...")
    r = requests.get(url='http://'+sys.argv[1]+':4000/gc/is-asleep')
    print('\tresponse: ',r.json())
    if r.status_code != 200:
        print("\tgc-emulation-service health failed: GET at ", sys.argv[1])
    else:
        print('\t['+u'\u2713'+'] gc-emulation is healthy at ', sys.argv[1])
    for host in data['compute-hosts']:
        ip = host['ip']
        user = host['user']
        dynamic_core_ids = host['dynamic-core-ids']

        # test gc-controller service
        print("2. checking health of gc-controller-service: ", ip)
        r = requests.get(url='http://'+ip+':3000/gc-controller/sleep-info')
        print('\tresponse: ',r.json())
        if r.status_code != 200:
            print("\tgc-emulation-service health failed: GET at ", sys.argv[1])
        else:
            print('\t['+u'\u2713'+'] gc-controller is healthy at ', ip)

        # test virsh connection
        subprocess.run('virsh -c qemu+ssh://'+user+'@'+ip+'/system list | virsh-json', shell=True, executable="/bin/bash")