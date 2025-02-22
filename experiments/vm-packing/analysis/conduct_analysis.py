import sys

from get_nLT import analyse_nlt

if len(sys.argv) == 1:
    exp_type = "debug"
else:
    exp_type = sys.argv[1]

analyse_nlt(exp_type=exp_type)
