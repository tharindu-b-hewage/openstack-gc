import pandas as pd
from matplotlib import pyplot as plt

from pre_process import get_power_stats, get_green_scores

power_stats = get_power_stats()
green_scores = get_green_scores()




def draw_power_figure(output, metric, figsize):
    plt.clf()
    t1 = pd.pivot_table(power_stats.reset_index(), index='Clk', columns='Core', values=[metric]).plot(subplots=True,
                                                                                                      figsize=figsize)
    plt.legend()
    plt.savefig(output, bbox_inches='tight')


power_stats['GScore'] = power_stats[power_stats['Core'] == 'Core-3']['Avg_MHz'].apply(lambda x: 1 if x > 1000 else 0)

figsize = (10, 5)
vert_figsize=(7,8)

# draw_power_figure(output='results/stats__idle-states__poll.svg', metric='POLL%', figsize=vert_figsize)
# draw_power_figure(output='results/stats__idle-states__c3acpi.svg', metric='C3ACPI%', figsize=vert_figsize)
# draw_power_figure(output='results/stats__frq__operating-fq.svg', metric='Avg_MHz', figsize=vert_figsize)

# power_stats = power_stats[power_stats['Core'] == 'Overall']
# draw_power_figure(output='results/stats__power__package.svg', metric='PkgWatt', figsize=(10,3))
power_stats = power_stats[power_stats['Clk'] >= 50]
power_stats = power_stats[power_stats['Clk'] <= 250]
draw_power_figure(output='results/stats__gscore.svg', metric='GScore', figsize=(10, 3))

# draw_power_figure(output='results/stats__idle-states__c1acpi.png', metric='C1ACPI%', figsize=figsize)
# draw_power_figure(output='results/stats__idle-states__c2acpi.png', metric='C2ACPI%', figsize=figsize)
# draw_power_figure(output='results/stats__busy__package.png', metric='Busy%', figsize=figsize)
