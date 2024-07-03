while true; do (echo $(date +%s)","$[100-$(vmstat 1 2|tail -1|awk '{print $15}')]"%") >> cpu-usage.csv; sleep 5; done &

