echo "restarting all devstack services..."
sudo systemctl restart devstack@*
# monitor nova compute logs
# sudo journalctl -f -u devstack@n-cpu.service