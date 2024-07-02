'''setup
12 core CPU - H/T disabled, Frequency scaling disabled.

VM - 2 vcpu

30 - pinned, each core to pcpu
31 - floats on core 2
32 - floats on core 3 and 4
33 - floats on cores 5,6,7
34 - floats on cores 8,9,10,11

Pinning is verified. See pinning verification.

Each runs RTEval for 3600 seconds.

Each VM collects cpu usage and latency performance.
'''
from rteval.utils import parse_xml


def get(exp_root):
    PIN_VM_DATA = exp_root + '/exp-1_pin-vs-float-static/pinned/PIN_1/rteval-20240613-2/summary.xml'
    FLT_VM_OVR_1_DATA = exp_root + '/exp-1_pin-vs-float-static/floating/FLT_1/rteval-20240613-2/summary.xml'
    FLT_VM_OVR_2_DATA = exp_root + '/exp-1_pin-vs-float-static/floating/FLT_2/rteval-20240613-2/summary.xml'
    FLT_VM_OVR_3_DATA = exp_root + '/exp-1_pin-vs-float-static/floating/FLT_3/rteval-20240613-2/summary.xml'
    FLT_VM_OVR_4_DATA = exp_root + '/exp-1_pin-vs-float-static/floating/FLT_4/rteval-20240613-2/summary.xml'

    return {
        'PIN_1': parse_xml(PIN_VM_DATA),
        'FLT_1': parse_xml(FLT_VM_OVR_1_DATA),
        'FLT_2': parse_xml(FLT_VM_OVR_2_DATA),
        'FLT_3': parse_xml(FLT_VM_OVR_3_DATA),
        'FLT_4': parse_xml(FLT_VM_OVR_4_DATA)
    }
