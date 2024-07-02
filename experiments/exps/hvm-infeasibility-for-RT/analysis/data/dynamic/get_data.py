'''setup
2 * VM with 6 vcpu

VM1 pins to first 6 cores
VM2 floats on remaining 6 cores

RT eval runs for 1.5 hours in both VMs.

Each 10 minutes, floating group reduces to 6 -> 5 -> 4 -> 3 -> 2 -> 1.

after 1.5 hours, Latency reports are collected.

Floating VM + dynamic pinning = HVM with renewables.

NOTE: cores are in performance mode through core-power-mgt. so high constant frequency and at c0/poll state.
'''
from rteval.utils import parse_xml


def get(exp_root):
    pin_vm_data = exp_root + '/exp-2_pin-vs-float-dynamic/data/REGULAR/summary.xml'
    flt_vm_data = exp_root + '/exp-2_pin-vs-float-dynamic/data/HVM/summary.xml'

    return {
        'PIN': parse_xml(pin_vm_data),
        'FLT': parse_xml(flt_vm_data),
    }
