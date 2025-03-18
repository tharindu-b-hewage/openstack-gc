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


def create_vm(is_evictable, vm_name, core_count, scheduler):
    """
    Create a VM using your custom create-rt-server.sh script.
    For instance:
      sh create-rt-server.sh evictable <vm_name> rt_3_PIN
    or
      sh create-rt-server.sh no_evictable <vm_name> rt_3_PIN
    """
    evictable_arg = "evictable" if is_evictable else "regular"
    if scheduler == 'with-nova':
        # Whether to use the default scheduler. Otherwise, the proposed algorithm is requested.
        evictable_arg = scheduler
    command = ["sh", "create-packing-instance.sh", evictable_arg, vm_name, "pack_" + str(core_count)]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # If the command succeeds, you can process/log stdout as needed
        print(f"[INFO] VM {vm_name} created successfully.")
        print("[INFO] Script output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Script failed with exit code {e.returncode}")
        if e.stdout:
            print("Script STDOUT:\n", e.stdout)
        if e.stderr:
            print("Script STDERR:\n", e.stderr)


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
        bool: True if the VM is found and in status=ACTIVE, False otherwise.
    """
    command = ["openstack", "server", "show", vm_name, "-f", "value", "-c", "status"]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode().strip()
        print(f"[INFO] VM {vm_name} status is: {output}")
        return True  # no errors, means some status exist.
    except subprocess.CalledProcessError as e:
        # The VM was not found at
        print(f"[ERROR] Command failed with exit code {e.returncode}")
        print("[ERROR] Output:", e.output)
        return False


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
            #cores = int(row["cores"])
            cores = 2 # hardcoded.
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
        True: {"arrived": 0, "prematurely_killed": 0},
        False: {"arrived": 0, "prematurely_killed": 0}
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

            # 2) Create the VM
            create_time = time.time()
            create_vm(is_evictable, vm_name, cores, scheduler)
            stats[is_evictable]["arrived"] += 1

            # 3) Poll for up to lifetime_sec to see if the VM is prematurely deleted
            actual_alive_time = 0.0
            prematurely_killed = False

            while True:
                if stop_event.is_set():
                    return

                time.sleep(POLL_INTERVAL)
                print("[INFO] monitor | vm: ", vm_name, "elapsed time:", time.time() - create_time, "lifetime(s):",
                      lifetime_sec)
                if not is_vm_active(vm_name):
                    # The VM has been removed (or is no longer ACTIVE) before lifetime ended
                    prematurely_killed = True
                    actual_alive_time = time.time() - create_time
                    stats[is_evictable]["prematurely_killed"] += 1
                    print("[INFO] monitor | vm: ", vm_name, "prematurely killed:", prematurely_killed)
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
                "vm_name": vm_name,
                "days": arrival_days,
                "lifetime_days": lifetime_days,
                "is_evictable": is_evictable,
                "actual_alive_time_sec": f"{actual_alive_time:.2f}",
                "nLT": f"{nLT:.4f}",
                "prematurely_killed": prematurely_killed
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
        "vm_name",
        "days",
        "lifetime_days",
        "is_evictable",
        "actual_alive_time_sec",
        "nLT",
        "prematurely_killed"
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
        "prematurely_killed"
    ]

    with open(summary_output_csv, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames_summary)
        writer.writeheader()
        for evictable_val in [True, False]:
            row = {
                "is_evictable": evictable_val,
                "arrived": stats[evictable_val]["arrived"],
                "prematurely_killed": stats[evictable_val]["prematurely_killed"]
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
