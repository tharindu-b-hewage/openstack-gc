import pandas as pd
from matplotlib import pyplot as plt

from pre_process import get_power_stats, get_green_scores

power_stats = get_power_stats()
green_scores = get_green_scores()

figsize = (10, 5)


def draw_power_figure(output, metric):
    plt.clf()
    t1 = pd.pivot_table(power_stats.reset_index(), index='Clk', columns='Core', values=[metric]).plot(subplots=True,
                                                                                                      figsize=figsize)
    plt.legend()
    plt.savefig(output)


power_stats['GScore'] = power_stats[power_stats['Core'] == 'Core-3']['Avg_MHz'].apply(lambda x: 1 if x > 1000 else 0)

draw_power_figure(output='results/stats__idle-states__poll.png', metric='POLL%')
draw_power_figure(output='results/stats__idle-states__c1acpi.png', metric='C1ACPI%')
draw_power_figure(output='results/stats__idle-states__c2acpi.png', metric='C2ACPI%')
draw_power_figure(output='results/stats__idle-states__c3acpi.png', metric='C3ACPI%')
draw_power_figure(output='results/stats__power__package.png', metric='PkgWatt')
draw_power_figure(output='results/stats__frq__operating-fq.png', metric='Avg_MHz')
draw_power_figure(output='results/stats__busy__package.png', metric='Busy%')
draw_power_figure(output='results/stats__gscore.png', metric='GScore')
