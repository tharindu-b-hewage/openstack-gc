import sys

from get_nLT import analyse_nlt
from get_vm_evictions import analyze_vm_evictions
from get_rnw_harvest import analyze_rnw_harvest

if len(sys.argv) == 1:
    exp_type = "debug"
else:
    exp_type = sys.argv[1]

exp_type = "full"

analyse_nlt(exp_type=exp_type)
analyze_vm_evictions(exp_type=exp_type)
analyze_rnw_harvest(exp_type=exp_type)