CORE_PW_MGT_TOOL=~/core-power-mgt
TOTAL_CORES=12
RESTING_SECONDS=60

ask_yes_no() {
  while true; do
    read -p "$1 (y/n): " answer
    case $answer in
      [Yy]* ) return 0;;
      [Nn]* ) return 1;;
      * ) echo "Please answer yes (y) or no (n).";;
    esac
  done
}

update_cores() {
  TO_AWAKE=$1
  DYNAMIC_CORE=$((TOTAL_CORES-TO_AWAKE))
  echo "set core counts..."
  echo "-- to awake = " "$TO_AWAKE"
  echo "-- to sleep = " "$DYNAMIC_CORE"
  sed -i "s/stable-core-count: [0-9]*/stable-core-count: $TO_AWAKE/" $CORE_PW_MGT_TOOL/conf.yaml
  sed -i "s/dynamic-core-count: [0-9]*/dynamic-core-count: $DYNAMIC_CORE/" $CORE_PW_MGT_TOOL/conf.yaml
  echo "updated conf.yaml"
  cat $CORE_PW_MGT_TOOL/conf.yaml
}

run_core_pw_mgt() {
  # Start the process in the background
  echo "---- Starting the core power management tool..."
  sudo $CORE_PW_MGT_TOOL/gc-controller.linux-amd64 $CORE_PW_MGT_TOOL/conf.yaml &

  echo "---- Waiting 10 seconds until service is up..."
  sleep 10

  echo "---- Obtaining service PID..."
  PORT=$(sed -n 's/.*port: \([0-9]*\).*/\1/p' $CORE_PW_MGT_TOOL/conf.yaml)
  HOST=$(sed -n 's/.*name: \([0-9.]*\).*/\1/p' $CORE_PW_MGT_TOOL/conf.yaml)
  PID=$(sudo lsof -i :"$PORT" -t)

  echo "---- Set cores to sleep..."
  URL=$(echo 'http://'$HOST':'$PORT'/gc-controller/sleep')
  echo "---- URL: $URL"
  curl -v --location --request PUT "$URL"

  # rest.
  echo "---- Resting for $RESTING_SECONDS seconds..."
  sleep $RESTING_SECONDS

  # Kill the process
  echo "---- Killing the core power management tool..."
  sudo kill -SIGINT "$PID"
}

if ask_yes_no "Any running core-power-mgt should be stopped and optionally power measuring should be enabled. Did you do these?"; then
  for ((i=1; i<=TOTAL_CORES; i++)); do
    echo "Number of Cores to be Awake: $i"
    update_cores "$i"
    run_core_pw_mgt
  done
  echo "Done."
else
  echo "Should not run otherwise."
fi