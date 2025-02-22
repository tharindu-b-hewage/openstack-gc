# Script runs the packing experiment on a two node openstack-gc deployment.
# It replays a scaled Azure VM packing trace and ELIA solar energy dynamics.
# It monitors for VM evictions, eviction severity through normalized lifetimes, and CPU package power consumption.

# note: duration typically needs to be set more than VM trace length to accommodate overhead times.

NODE_1_USER=$1
NODE_1_IP=$2
NODE_2_USER=$3
NODE_2_IP=$4
DURATION=$5
RNW_TRACE_CSV=$6
VM_TRACE_CSV=$7
SCHEDULER=$8

# Adjust accordingly.
GC_EMUL_SERVICE_IP=$NODE_1_IP
GC_EMUL_SERVICE_PORT=2000

echo "Step 01: Cleaning the openstack-gc deployment..."
rm exp_rnw_dynamics.log
rm exp_turbostat.log
rm exp_vm_trace.log
rm results/*
sh clean.sh

echo "Step 02: Starting VM trace..."
VM_TRACE_LOG=exp_vm_trace.log
python3 run_vm_trace.py $VM_TRACE_CSV $SCHEDULER > $VM_TRACE_LOG &
PID_VM_TRACE=$!
echo " - VM trace: ${PID_VM_TRACE}"

echo "--- Waiting for VM trace init..."
tail -f "$VM_TRACE_LOG" | while IFS= read -r line
do
    # Check if the line contains the desired text:
    if echo "$line" | grep -q "created successfully"
    then
        echo "Detected success message. Continue experiment..."
        break
    fi
done

echo "Step 03: Starting power monitoring..."
TURBOSTAT_LOG_FILE=exp_turbostat.log
./run_turbostat.sh $NODE_1_USER@$NODE_1_IP $NODE_2_USER@$NODE_2_IP $DURATION > exp_turbostat.log &
PID_TURBOSTAT=$!
echo " - Turbostat: ${PID_TURBOSTAT}"

echo "Step 04: Emulating renewable dynamics..."
python3 run_rnw_trace.py $RNW_TRACE_CSV $GC_EMUL_SERVICE_IP $GC_EMUL_SERVICE_PORT > exp_rnw_dynamics.log &
PID_RNW_TRACE=$!
echo " - Renewable dynamics: ${PID_RNW_TRACE}"

echo "Step 05: Awaiting experiment completion..."
tail -f "$VM_TRACE_LOG" | while IFS= read -r line
do
    # Check if the line contains the desired text:
    if echo "$line" | grep -q "experiment completed successfully"
    then
        echo "Detected success message with VM trace. Exiting..."
        break
    fi
done
tail -f "$TURBOSTAT_LOG_FILE" | while IFS= read -r line
do
    # Check if the line contains the desired text:
    if echo "$line" | grep -q "Done!"
    then
        echo "Detected success message with power monitoring. Exiting..."
        break
    fi
done

echo "Step 06: Done! Please refer to VM and power data collected in the results folder."


