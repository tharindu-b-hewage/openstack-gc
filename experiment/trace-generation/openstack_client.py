import subprocess

cmd = "date"

# returns output as byte string
returned_output = subprocess.check_output(cmd)

# using decode() function to convert byte string to string
print('Current date is:', returned_output.decode("utf-8"))


def create_flavours():
    # flavours support upto 12 vcpu.
    for i in range(1, 13):
        try:
            cmd = "openstack flavor create --public pinned.vcpu-" + str(i) + " --id pinned.vcpu-" + str(
                i) + " --ram 256 --disk 1 --vcpus " + str(i)
            print(cmd)
            returned_output = subprocess.check_output(cmd, shell=True)
            print('flavour creation for vcpu:', i, returned_output.decode("utf-8"))
        except:
            print('failed flavour creation for vcpu:', i)
        try:
            cmd2 = "openstack flavor set pinned.vcpu-" + str(i) + " --property hw:cpu_policy=dedicated"
            print(cmd2)
            returned_output = subprocess.check_output(cmd2, shell=True)
            print('setting dedicated for flavour creation for vcpu:', i, returned_output.decode("utf-8"))
        except:
            print('failed setting dedicated for flavour creation for vcpu:', i)


def create_vm(vm):
    print('attempting to create vm: ', vm['name'])
    try:
        cmd = "openstack server create --nic net-id=\"public\" --image \"cirros-0.6.2-x86_64-disk\" --flavor \"pinned.vcpu-" + str(
            round(vm['vcpu'])) + "\" \"" + vm['name'] + "\" --wait --hint type="+vm['type']+" "
        returned_output = subprocess.check_output(cmd, shell=True)
        print('vm creation for vm:', vm, returned_output.decode("utf-8"))
        return True
    except:
        return False


def delete_vm(vm):
    print('attempting to delete vm: ', vm['name'])
    try:
        cmd = "openstack server delete " + vm['name'] + " --wait --force"
        returned_output = subprocess.check_output(cmd, shell=True)
        print('vm deletion for vm:', vm, returned_output.decode("utf-8"))
        return True
    except:
        return False
