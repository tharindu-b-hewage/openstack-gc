""" Experiment: Comparing Our Proposed Method with HVM

We set up two OpenStack nodes, each using 12-core servers. One of these nodes remains free, while the other is filled
with two virtual machines (VMs), each using 6 cores.

To simulate renewable energy loss, we reduce the available cores on one server from 12 to 7. Here’s how each method
responds:

•	Proposed Method: One of the VMs is automatically evicted and redeployed to the free node using MANO’s
auto-healing feature.
•	HVM Method: Instead of moving the VM, it is shrunk to operate on just a single core.

Throughout the experiment, we measure real-time latency performance on all the VMs to compare the two approaches.
"""

import matplotlib.pyplot as plt
import numpy as np

data = {
    'duration_secs': 300,
    'hvm': {  # seconds
        'before': {
            'mean': 8.12734267115,
            'stddev': 4.09052044752,
            'mad': 0.783319556211
        },
        'after': {
            'mean': 37.6544072859,
            'stddev': 142.45803518,
            'mad': 49.311604126
        },
    },
    'proposed': {
        'before': {
            'mean': 8.12734267115,
            'stddev': 4.09052044752,
            'mad': 0.783319556211
        },
        'after': {
            'mean': 8.12734267115,
            'stddev': 4.09052044752,
            'mad': 0.783319556211
        },
        'heal_time_secs': 30
    }
}

def_font_size = 18
plt.rcParams.update({'font.size': def_font_size})

# Data from the experiment
duration_secs = data['duration_secs']
heal_time_secs = data['proposed']['heal_time_secs']

# HVM method (before and after healing)
hvm_before_mean = data['hvm']['before']['mean']
hvm_after_mean = data['hvm']['after']['mean']

# Proposed method (before healing and after healing)
proposed_before_mean = data['proposed']['before']['mean']
proposed_after_mean = data['proposed']['after']['mean']

# Time axis generation
total_time = duration_secs * 2 + heal_time_secs
time_axis = np.arange(0, total_time)

# Latency values for each method over time
hvm_latency = np.concatenate((
    np.full(duration_secs, hvm_before_mean),  # Before healing
    np.full(heal_time_secs, hvm_after_mean),  # During healing
    np.full(duration_secs, hvm_after_mean)  # After healing
))

proposed_latency = np.concatenate((
    np.full(duration_secs, proposed_before_mean),  # Before healing
    np.full(heal_time_secs, np.nan),  # Service unavailable during healing
    np.full(duration_secs, proposed_after_mean)  # After healing
))

# Plotting the time series graph
plt.figure(figsize=(10, 3))
plt.plot(time_axis, hvm_latency, label='Harvest VM', linestyle='-', marker='s', color='brown', markevery=17,
         markersize=5, linewidth=3)
plt.plot(time_axis, proposed_latency, label='Proposed', linestyle='-', marker='^', color='green', markevery=20,
         markersize=5, linewidth=3)

# Indicate heal time
t_start = duration_secs
t_end = duration_secs + heal_time_secs

plt.axvline(x=t_start, color='blue', linestyle='--',
            label='MANO Auto-Healing:\nReconfiguration time'
            )

plt.axvline(x=t_end, color='blue', linestyle='--'
            #, label='MANO auto-heal: end'
            )

# Plot a two-headed arrow between the vertical lines
plt.annotate(
    '', xy=(t_end, 20), xytext=(t_start, 20),  # Arrow between the two x positions
    arrowprops=dict(arrowstyle='<->', color='red', lw=2),  # Custom arrow style,
    #label='autoheal time'
)

# Add text showing the gap
plt.text((t_start + t_end) / 2 + 7, 15, str(heal_time_secs) + 's', ha='center', fontsize=def_font_size)

# Labels and title
# plt.xlabel('Time (seconds)')
plt.ylabel('Mean Latency ' + r'($\mu s$)')
# plt.title('Latency Comparison Between HVM and Proposed Method')
plt.legend(loc='upper left')

plt.grid(which='both', linestyle='-', zorder=1)
plt.minorticks_on()
# y axis to log
plt.yscale('log')
# set x limit
plt.xlim(0, 600)
plt.tight_layout()
plt.savefig("rt-perf_proposed_vs_hvm.svg", bbox_inches='tight')

hvm_after_cv = data['hvm']['after']['stddev'] / data['hvm']['after']['mean']
proposed_after_cv = data['proposed']['after']['stddev'] / data['proposed']['after']['mean']
cv_increase_of_hvm_over_ours = (hvm_after_cv - proposed_after_cv) / proposed_after_cv

print("hvm mean latency increase: ", cv_increase_of_hvm_over_ours, 'X')
