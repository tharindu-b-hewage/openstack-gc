#### Monitoring guide

Upon successful integration, the system is ready to be monitored for its performance.

We measure followings.

System metrics,

- Green score
- Power consumption

Application metrics,

- `nLT`: Normalized lifetime
- Eviction counts

##### Setting up

In each computing node,

1. Green Score
   1. `core-power-mgt` service expose an endpoint to obtain green score at a given time: `/gc-controller/dev/green-score`
   2. In a new linux screen session,
      1. Run `python3 [dump-green-score.py](dump-green-score.py) <node-ip> <path-to-a-csv-file>`
      2. csv file should be created and its column names are `timestamp` and `g-score`
      3. The above script poll endpoint, dumps green score as a new row in the csv file.
      4. detach from the screen session
7. Power consumption
   1. In a new linux screen session,
      1. Run `sudo turbostat --quiet -out reports/power-stats.csv`. This will keep dumping power stats to the csv file.
      2. detach from the session.

Application metrics are tracked and logged by the vm arrival trace generation.

##### Post process

In each node, collect power stats and green score csv files. These data needs to be processed and system behaviour 
can be analyzed.

Once collected, kill all monitoring screen sessions.