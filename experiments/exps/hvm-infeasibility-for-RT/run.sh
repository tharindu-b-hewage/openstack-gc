PINNED_IP=$1
HVM_IP=$2
HVM_VIRSH_DOMAIN=$3
USER=$4
KEY_PATH=$5

BUFFER=60
WAIT_PERIOD_SECONDS=300
HVM_CORE_COUNT=6
HVM_INITIAL_CORE_GROUP="[6,7,8,9,10,11]"

RT_EVAL_RUNTIME=$((WAIT_PERIOD_SECONDS*HVM_CORE_COUNT+5*BUFFER))
echo "RTEval runtime is "$RT_EVAL_RUNTIME

echo "Triggering RT Eval on the HVM..."
ssh -i "$KEY_PATH" "$USER"@"$HVM_IP" "sudo rteval -d $RT_EVAL_RUNTIME""s  -L -v" &

echo "Triggering RT Eval on the Pinned..."
ssh -i "$KEY_PATH" "$USER"@"$PINNED_IP" "sudo rteval -d $RT_EVAL_RUNTIME""s -L -v" &

echo "wait "$BUFFER"seconds to allow RTEval to begin..."
sleep $BUFFER

python3 shrink.py "$HVM_VIRSH_DOMAIN" "$HVM_INITIAL_CORE_GROUP" $HVM_CORE_COUNT $WAIT_PERIOD_SECONDS