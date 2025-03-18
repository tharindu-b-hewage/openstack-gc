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


def parse_conf_file(conf_file_path):
    # Expected output: {'smt_host': '192.168.1.10',
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
    result = subprocess.run(
        ['sh', path] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # ensures output is returned as strings
        check=True
    )

    print("Output:", result.stdout)
    print("Errors:", result.stderr)


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
if para_rnw_event == 'peak':
    print("rnw: peak")
    handle_rnw_peak(host_names=host_names)
elif para_rnw_event == 'valley':
    print("rnw: valley")
    handle_rnw_valley(host_names=host_names)
