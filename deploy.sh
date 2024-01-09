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
scp ./extensions/feature-priority-core-pinning/apply-priority-core-pinning-patch.sh $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/apply-priority-core-pinning-patch.sh
scp $OS_CORE_PINNING_FEATURE_REPO/nova/virt/libvirt/host.py $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/host.py
scp ./extensions/workaround-omit-sleeping-core-from-pcpu/apply-omit-sleeping-core-patch.sh $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/apply-omit-sleeping-core-patch.sh
scp ./extensions/restart-devstack-services.sh $DEVSTACK_USER@$DEVSTACK_HOST:$DEVSTACK_WORKPLACE/restart-devstack-services.sh

# deploy gc emulation service.
cd ./extensions/gc-emulator-service
scp ./gc-emulator-service $USER@$HOST:$WORKPLACE/gc-emulator-service
scp ./scripts/virsh-list-domains.sh $USER@$HOST:$WORKPLACE/virsh-list-domains.sh
scp ./scripts/virsh-domain-get-pinned-cpu-core.sh $USER@$HOST:$WORKPLACE/virsh-domain-get-pinned-cpu-core.sh
scp ./scripts/openstack-get-server-by-domain.sh $USER@$HOST:$WORKPLACE/openstack-get-server-by-domain.sh
scp ./scripts/openstack-shelve-offload-server.sh $USER@$HOST:$WORKPLACE/openstack-shelve-offload-server.sh
scp ./scripts/gc-emul-envs.sh $USER@$HOST:$WORKPLACE/gc-emul-envs.sh
cd ../../
