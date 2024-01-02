# 1. set correct values in the shell prior executing.
# example: REMOTE_IP=<your-ip> REMOTE_USER=<your-host> sh build-debug.sh
# 2. Might need to enable SSH tunneling for ease of testing.
# Ex: ssh -L 3000:localhost:3000 <your-ip>
echo "---- Preparing remote dev env ----"
echo "remote host: $REMOTE_IP, and remote user: $REMOTE_USER"

REMOTE_WORKSPACE=/home/$REMOTE_USER/workspace/gc-remote-work

echo "--> building go service for debugging..."
GOOS=linux GOARCH=amd64 go build -gcflags="-N -l" -o gc-controller

echo "--> cleaning remote workspace..."
ssh $REMOTE_USER@$REMOTE_IP "rm -rf $REMOTE_WORKSPACE/*"

echo "--> copying files..."
scp ./gc-controller $REMOTE_USER@$REMOTE_IP:$REMOTE_WORKSPACE
scp ./run-at-remote-for-debug.sh $REMOTE_USER@$REMOTE_IP:$REMOTE_WORKSPACE

echo "--> done!"
