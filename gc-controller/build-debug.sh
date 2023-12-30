# 1. set correct values in the shell prior executing.
# example: REMOTE_HOST_IP=<your-ip> REMOTE_USER=<your-host> sh build-debug.sh
# 2. Might need to enable SSH tunneling for ease of testing.
# Ex: ssh -L 3000:localhost:3000 <your-ip>
echo "======== Deploying dev environment with remote debugging"
echo "remote host: $REMOTE_HOST_IP, and remote user: $REMOTE_USER"

REMOTE_WORKSPACE=/home/$REMOTE_USER/workspace/gc-remote-work

GOOS=linux GOARCH=amd64 go build -gcflags="-N -l" -o gc-controller
ssh $REMOTE_USER@$REMOTE_HOST_IP "rm -rf $REMOTE_WORKSPACE/*"
scp ./gc-controller $REMOTE_USER@$REMOTE_HOST_IP:$REMOTE_WORKSPACE
scp ./run-at-remote-for-debug.sh $REMOTE_USER@$REMOTE_HOST_IP:$REMOTE_WORKSPACE