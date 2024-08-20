import sys
import matplotlib.pyplot as plt

import data.dynamic.get_data as dynamic_data
import data.isolated.get_data as isolated_data
from evictvshvm.analyse import analyse as evict_vs_hvm_analyse

plt.rcParams.update({'font.size': 16})
plt.rcParams["figure.figsize"] = (6,2.2)

root = sys.argv[1]

d_data = dynamic_data.get(exp_root=root)
s_data = isolated_data.get(exp_root=root)

evict_vs_hvm_analyse(isolated_data=s_data, dynamic_data=d_data)
