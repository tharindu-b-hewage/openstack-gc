### Filter Scheduler: CPU Weighter

1. Clean project in MANO.
```shell
echo "cleaning critical slice..."
osm nsi-delete crit-slice
echo "cleaning best-effort slice..."
osm nsi-delete be-slice
```
2. Ensure Openstack-GC is clean, and Renewables is at 100% = all green cores are available.
```shell
3. open `/etc/noca/nova.conf`.
4. under `[filter_scheduler]` section, add:
```shell
weight_classes = nova.scheduler.weights.cpu.CPUWeigher
```
5. Restart nova services in devstack.
```shell
sudo systemctl restart devstack@n-*
```
6. Deploy the critical slice. Wait and verify its up.
7. Deploy the best-effort slice. Wait and verify its up.
8. Reduce renewables to zero.
```shell
curl --location --request POST 'http://<gc-emulation-host>:<service-ip>/gc/dev/switch'
```
9. Observe VM evictions and re-deployments. Keep a count.
10. Let the infra to reconfigure and heal.
11. End of experiment.

Then for each weighter, do the same thing and replace the weight class name.