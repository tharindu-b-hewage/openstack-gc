# install 'pip3 install python-ilorest-library'
import json
import os
import sys
import time
import uuid

from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError

SYSTEM_URL = "https://" + sys.argv[1]
LOGIN_ACCOUNT = sys.argv[2]
LOGIN_PASSWORD = sys.argv[3]
DATA_DUMP = sys.argv[4]

if __name__ == "__main__":
    DISABLE_RESOURCE_DIR = False
    exp_folder = str(uuid.uuid4())
    exp_folder = DATA_DUMP + '/' + exp_folder
    os.makedirs(exp_folder)
    data_file = exp_folder + '/ilo-readings.log'
    with open(data_file, 'w') as dump:
        count = 1
        while True:
            print(count)
            try:
                # Create a Redfish client object
                REDFISHOBJ = RedfishClient(base_url=SYSTEM_URL, username=LOGIN_ACCOUNT, password=LOGIN_PASSWORD)
                # Login with the Redfish client
                REDFISHOBJ.login()
            except ServerDownOrUnreachableError as excp:
                sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
                sys.exit()

            r = REDFISHOBJ.get("/redfish/v1/Chassis/1/Power")

            json_rsp = json.loads(json.dumps(r.obj, indent=4))
            dump.write(json_rsp + '\n')
            dump.flush()
            REDFISHOBJ.logout()
            time.sleep(0.5)
            count += 1
