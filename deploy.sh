# ENVs:
# HOST: Remote host
# USER: Remote user
# WORKPLACE: Remote workplace
# OS_CORE_PINNING_FEATURE_REPO: Repo path of the core pinning feature

# Build and deploy tracegen.
scp ./admin-openrc.sh $USER@$HOST:$WORKPLACE/openrc.sh
cd ./vm-trace/az-trace-gen

mvn clean install
scp ./target/az-trace-gen-1.0-SNAPSHOT-jar-with-dependencies.jar $USER@$HOST:$WORKPLACE/trace-gen.jar
scp ./src/main/resources/configs.properties $USER@$HOST:$WORKPLACE/configs.properties
scp ./remote-exec-debug.sh $USER@$HOST:$WORKPLACE/remote-exec-debug.sh

scp ./src/main/resources/os-client/image-list.sh $USER@$HOST:$WORKPLACE/image-list.sh
scp ./src/main/resources/os-client/create-vm.sh $USER@$HOST:$WORKPLACE/create-vm.sh
scp ./src/main/resources/os-client/delete-vm.sh $USER@$HOST:$WORKPLACE/delete-vm.sh

cd ../../

# Deploy features.
# Refer extensions/feature-priority-core-pinning/readme.md first.
scp $OS_CORE_PINNING_FEATURE_REPO/nova/conf/compute.py $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/compute.py
scp $OS_CORE_PINNING_FEATURE_REPO/nova/virt/hardware.py $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/hardware.py
scp ./extensions/feature-priority-core-pinning/apply-patch.sh $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/apply-patch.sh
scp ./extensions/restart-devstack-services.sh $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/restart-devstack-services.sh