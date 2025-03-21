"""smt-pooling-carbon
This script intercepts OpenstackGC's core-sleep-based power management mechanism.

Default: Find which VMs pins to the dynamic core set and evict those.

This script: Before an eviction process, evict all VMs in the non-SMT server (assuming they get migrated out from the
data center), live-migrate all low-latency VMs in the SMT server.

Example conf file with machine IPs.

"
smt_ip = 192.168.1.10
non_smt_ip = 192.168.1.20
"

# v1: During chasing, low-lat VMs are prioritized. All VMs in the best-effort server is evicted and low-late VMs are
      then live migrated.
"""
import sys
import subprocess
import os


def update_property_file(filename, key, value):
    filename = '/data/tsaryakarahe/openstack/opt/stack3/openstack-gc/major-revision-experiments/scripts/' + filename
    # A dictionary to store existing properties
    properties = {}

    # If the file exists, read and store current properties
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines or commented lines
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    properties[k.strip()] = v.strip()

    # Set/update the given property
    properties[key] = value

    # Write all properties back to the file
    with open(filename, 'w') as f:
        for k, v in properties.items():
            f.write(f"{k}={v}\n")


def parse_conf_file(conf_file_path):
    # Expected output: {'enable': 'true',
    #                   'smt_host': '192.168.1.10',
    #                   'non_smt_host': '192.168.1.20'}
    parsed_data = {}
    with open(conf_file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip empty lines or comment lines
            if not line or line.startswith('#'):
                continue

            # Split on the first '='
            key, value = line.split('=', 1)
            parsed_data[key.strip()] = value.strip()
    return parsed_data


def run_script(path, args):
    try:
        result = subprocess.run(
            ['sh', path] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # ensures output is returned as strings
            check=True
        )

        print("Output:", result.stdout)
        print("Errors:", result.stderr)
    except Exception as e:
        print("Error calling external script", e)


def evict_all_besteffort_vms(host):
    print("evict_all_besteffort_vms(host=%s)" % host)
    run_script("evict-be-vms.sh", [host])


def live_migrate_low_lat_vms(from_host, to_host):
    print("live_migrate_low_lat_vms(host=%s)" % from_host)
    run_script("live-migrate-vms.sh", [from_host, to_host])


def handle_rnw_peak(host_names):
    """Handle migration when renewables capacity increases."""
    evict_all_besteffort_vms(host_names['non_smt_host'])
    live_migrate_low_lat_vms(from_host=host_names['smt_host'], to_host=host_names['non_smt_host'])


def handle_rnw_valley(host_names):
    """Handle migration when renewables capacity decreases."""
    evict_all_besteffort_vms(host_names['smt_host'])
    live_migrate_low_lat_vms(from_host=host_names['non_smt_host'], to_host=host_names['smt_host'])


para_rnw_event = sys.argv[1]
host_names = parse_conf_file("host_names.properties")
is_enabled = host_names['enable'] == 'true'

if not is_enabled:
    print("SMT chasing is disabled. Exiting...")
    sys.exit(0)

update_property_file('sync_vm-trace_rnw-mgt.properties', 'switching', 'true')
if para_rnw_event == 'peak':
    print("rnw: peak")
    handle_rnw_peak(host_names=host_names)
elif para_rnw_event == 'valley':
    print("rnw: valley")
    handle_rnw_valley(host_names=host_names)
update_property_file('sync_vm-trace_rnw-mgt.properties', 'switching', 'false')
