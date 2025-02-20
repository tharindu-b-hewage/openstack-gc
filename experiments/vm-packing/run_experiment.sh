# start dumping power data.
# todo: execute turbostat dumping command async yet keep track of process id. do for both nodes.

# replay rnw trace.
python3 run_rnw_trace.py

# replay VM trace.
python3 run_vm_trace.py

# stop dumping power data.

# collect power data from both nodes.