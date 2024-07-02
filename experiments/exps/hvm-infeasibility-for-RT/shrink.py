import ast
import subprocess
import sys
import time

'''Example
python3 shrink.py 35 "[6,7,8,9,10,11]" 6 5
'''

domain = sys.argv[1]
core_group = ast.literal_eval(sys.argv[2])
hvm_vcpus = int(sys.argv[3])
wait_seconds = int(sys.argv[4])

# print out all parameters
print(domain, core_group, hvm_vcpus, wait_seconds)

print("Begin shrinking of virsh domain: ", domain, "...")

core_group_as_string = ",".join(map(str, core_group))
while len(core_group) > 0:
    subprocess.call(['virsh', 'emulatorpin', domain, core_group_as_string, '--live'])
    for idx in range(hvm_vcpus):
        subprocess.call(['virsh', 'vcpupin', domain, str(idx), core_group_as_string, '--live'])

    subprocess.call(['virsh', 'emulatorpin', domain])
    subprocess.call(['virsh', 'vcpupin', domain])

    print("sleeping for ", wait_seconds, "seconds..")
    time.sleep(wait_seconds)
    core_group = core_group[:-1]
    core_group_as_string = ",".join(map(str, core_group))

print("done!")
