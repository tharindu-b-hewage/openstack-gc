#!/usr/bin/env python3

import csv
import time
import subprocess
import os
import sys
import uuid
import threading

# CONSTANTS
SECONDS_PER_DAY = 86400
POLL_INTERVAL = 10  # seconds (adjust for desired polling frequency)

stop_event = threading.Event()


def get_property_value(filename, key):
    """
    Reads the specified property file, searches for the given key
    and returns its value. If the file or key is missing, returns None.
    """
    if not os.path.exists(filename):
        return None

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip blank lines and commented lines
            if not line or line.startswith('#'):
                continue

            if '=' in line:
                k, v = line.split('=', 1)
                if k.strip() == key:
                    return v.strip()
    return None


def wait_until_switching_false(filename, key='switching', poll_interval=5):
    filename = '/data/tsaryakarahe/openstack/opt/stack3/openstack-gc/major-revision-experiments/scripts/' + filename
    """
    Polls the property file every `poll_interval` seconds until the
    `switching` attribute is 'false' (case-insensitive).
    If it's missing or not 'true', we assume we can proceed.
    """
    while True:
        value = get_property_value(filename, key)

        # If 'switching' is strictly 'true', wait; otherwise, proceed
        if value and value.lower() == 'true':
            print(f"switching is true, waiting {poll_interval} seconds...")
            time.sleep(poll_interval)
        else:
            # Once 'switching' is false or not present, proceed
            print("switching is false (or not found). Proceeding...")
            break


def create_vm(is_evictable, vm_name, core_count, scheduler):
    """
    Create a VM using your custom create-rt-server.sh script.
    For instance:
      sh create-rt-server.sh evictable <vm_name> rt_3_PIN
    or
      sh create-rt-server.sh no_evictable <vm_name> rt_3_PIN


    scheduler = proposed / load_shift
    """
    #evictable_arg = "evictable" if is_evictable else "regular"
    # if scheduler == 'with-nova':
    #     # Whether to use the default scheduler. Otherwise, the proposed algorithm is requested.
    #     evictable_arg = scheduler
    command = ["sh", "create-packing-instance.sh", scheduler, vm_name, "pack_" + str(core_count)]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # If the command succeeds, you can process/log stdout as needed
        print(f"[INFO] VM {vm_name} created successfully.")
        print("[INFO] Script output:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed with exit code {e.returncode}")
        if e.stdout:
            print("Script STDOUT:\n", e.stdout)
        if e.stderr:
            print("Script STDERR:\n", e.stderr)
        return False


def delete_vm(vm_name):
    """
    Delete a VM from OpenStack using the CLI.
    """
    command = ["openstack", "server", "delete", vm_name]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        # This likely means the VM is already gone or name is invalid
        pass


def is_vm_active(vm_name):
    """
    Check whether a VM is active in OpenStack.
    Returns:
        (is_active, non_active_type).
    """
    command = ["openstack", "server", "show", vm_name, "-f", "value", "-c", "status"]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode().strip()
        print(f"[INFO] VM {vm_name} status is: {output}")
        if output == 'ERROR':
            print(f"[ERROR] VM status: {output} indicates that VM was not admitted")
            return False, 'not-admitted'

        print("[INFO] VM is active.")
        return True, 'active'  # no errors, means some status exist.
    except subprocess.CalledProcessError as e:
        # The VM was not found at
        print(f"[ERROR] Indicates VM was prematurely killed. Command failed with exit code {e.returncode} and output: {e.output}")
        return False, 'prematurely-killed'


def get_uuid():
    return str(uuid.uuid4())


def main():
    # CSV Input and Output paths
    input_csv = sys.argv[1]  # path to trace csv.
    scheduler = sys.argv[2]
    detailed_output_csv = "results/vm_nLT_details.csv"
    summary_output_csv = "results/vm_summary.csv"

    exp_id = get_uuid()
    print(f"[INFO] Starting experiment {exp_id}")

    # Read the arrival trace
    print(f"[INFO] Parsing the trace {input_csv}")
    arrivals = []
    with open(input_csv, "r", newline="") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            is_evictable = row["isEvictable"].strip().lower() in ["true", "1", "yes"]

            evictable_prefix = 'BESTEFFORT' if is_evictable else 'LOWLATENCY'
            vm_name = "packing-exp_" + evictable_prefix + "_" + exp_id + "_" + get_uuid()
            days = float(row["days"])
            lifetime = float(row["lifetime"])
            cores = int(row["cores"])
            #cores = 3  # hardcoded.
            # Convert the isEvictable column to bool if needed

            arrivals.append({
                "vm_name": vm_name,
                "days": days,
                "lifetime": lifetime,
                "is_evictable": is_evictable,
                "cores": cores,
            })

    # Sort by arrival time (if not already)
    arrivals.sort(key=lambda x: x["days"])

    # Prepare data structures to keep track of results
    results = []  # Will hold row-wise data for each VM
    start_time = time.time()

    # Track counts for summary
    stats = {
        True: {"arrived": 0, "prematurely_killed": 0, "not_admitted": 0},
        False: {"arrived": 0, "prematurely_killed": 0, "not_admitted": 0}
    }

    vm_management_threads = []
    for arrival in arrivals:
        print(f"[INFO] deploying VM management for {arrival}")

        def _manage_vm_lifecycle(arrival):
            vm_name = arrival["vm_name"]
            arrival_days = arrival["days"]
            lifetime_days = arrival["lifetime"]
            is_evictable = arrival["is_evictable"]
            cores = arrival["cores"]

            # Convert from fractional days to seconds
            arrival_time_sec = arrival_days * SECONDS_PER_DAY
            lifetime_sec = lifetime_days * SECONDS_PER_DAY

            # 1) Wait until the arrival time
            now = time.time()
            elapsed_since_start = now - start_time
            wait_time = arrival_time_sec - elapsed_since_start
            if wait_time > 0:
                time.sleep(wait_time)

            # wait if its a renewable transition.
            wait_until_switching_false('sync_vm-trace_rnw-mgt.properties')

            # 2) Create the VM
            create_time = time.time()
            is_creation_success = create_vm(is_evictable, vm_name, cores, scheduler)
            stats[is_evictable]["arrived"] += 1

            # 3) Poll for up to lifetime_sec to see if the VM is prematurely deleted
            actual_alive_time = 0.0
            prematurely_killed = False
            not_admitted = False

            while True:
                if stop_event.is_set():
                    return

                time.sleep(POLL_INTERVAL)
                print("[INFO] monitor | vm: ", vm_name, "elapsed time:", time.time() - create_time, "lifetime(s):",
                      lifetime_sec)

                # If VMs are transitioning, wait until that happens.
                wait_until_switching_false('sync_vm-trace_rnw-mgt.properties')

                if is_creation_success:
                    # VM creation success. Check its status.
                    is_active, status = is_vm_active(vm_name)
                else:
                    # VM creation fails. Assumes it was migrated out from the data center.
                    is_active = False
                    status = "not-admitted"

                if not is_active:
                    # The VM has been removed (or is no longer ACTIVE) before lifetime ended
                    prematurely_killed = True if status == 'prematurely-killed' else False
                    not_admitted = True if status == 'not-admitted' else False

                    actual_alive_time = time.time() - create_time
                    if prematurely_killed:
                        stats[is_evictable]["prematurely_killed"] += 1
                    if not_admitted:
                        stats[is_evictable]["not_admitted"] += 1

                    print("[INFO] monitor | vm: ", vm_name, "is not active since ", status)

                    if not_admitted:
                        print(f"[INFO] deleting the error record of the server: {vm_name} to free resources...")
                        command = ["openstack", "server", "delete", vm_name]
                        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode().strip()
                        print(f"[INFO] deletion status of VM: {vm_name} is: {output}")

                    break

                # If we've reached (or exceeded) the total lifetime, break and delete
                now_p = time.time()
                if now_p - create_time >= lifetime_sec:
                    # VM has run its full lifetime
                    actual_alive_time = now_p - create_time
                    # Delete the VM
                    delete_vm(vm_name)
                    print("[INFO] monitor | vm: ", vm_name, "reached lifetime, so deleted", "prematurely_killed: ",
                          prematurely_killed)
                    break

            # 4) Compute nLT = (actual_alive_time) / (lifetime_in_seconds)
            nLT = 0.0
            if lifetime_sec > 0:
                nLT = actual_alive_time / lifetime_sec

            results.append({
                "time": time.time(),
                "vm_name": vm_name,
                "days": arrival_days,
                "lifetime_days": lifetime_days,
                "is_evictable": is_evictable,
                "actual_alive_time_sec": f"{actual_alive_time:.2f}",
                "nLT": f"{nLT:.4f}",
                "prematurely_killed": prematurely_killed,
                "not_admitted": not_admitted,
            })

        thread = threading.Thread(
            target=_manage_vm_lifecycle,
            args=(arrival,)
        )
        thread.daemon = True
        thread.start()
        vm_management_threads.append(thread)

    # wait until all completes.
    print(f"[INFO] awaiting VM lifecycle completion...")
    for thread in vm_management_threads:
        thread.join()

    # --- End of arrivals processing ---
    print(f"[INFO] experiment completed successfully. logging...")
    # Now output the per-VM results to a CSV (for nLT metrics).
    fieldnames_detailed = [
        "time",
        "vm_name",
        "days",
        "lifetime_days",
        "is_evictable",
        "actual_alive_time_sec",
        "nLT",
        "prematurely_killed",
        "not_admitted"
    ]

    with open(detailed_output_csv, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames_detailed)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # Output the summary CSV with the number of VMs arrived, how many were prematurely killed, etc.
    fieldnames_summary = [
        "is_evictable",
        "arrived",
        "prematurely_killed",
        "not_admitted"
    ]

    with open(summary_output_csv, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames_summary)
        writer.writeheader()
        for evictable_val in [True, False]:
            row = {
                "is_evictable": evictable_val,
                "arrived": stats[evictable_val]["arrived"],
                "prematurely_killed": stats[evictable_val]["prematurely_killed"],
                "not_admitted": stats[evictable_val]["not_admitted"],
            }
            writer.writerow(row)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # This ensures that pressing Ctrl+C signals all threads to stop
        print("[WARN] Caught Ctrl+C in main; telling threads to stop...")
        stop_event.set()
        sys.exit(0)
