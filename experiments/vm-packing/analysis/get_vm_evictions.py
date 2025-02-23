from get_configs import parse_configs
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data_root = parse_configs()["data-root"]


def analyze_vm_evictions(exp_type):
    """
    Loads VM summary data from three experiment variants (with-nova, proposed, crit-aware),
    computes the fraction of evicted VMs (BestEffort vs. Critical) relative to the total VM
    arrivals, and plots a stacked bar chart.
    """

    # 1) Read data from three setups:
    #    - 'with-nova' is assumed to be the "Nova" scenario
    #    - 'proposed' is the improved approach
    df_with_nova = pd.read_csv(f"{data_root}/{exp_type}/with-nova/vm_summary.csv")
    df_proposed = pd.read_csv(f"{data_root}/{exp_type}/proposed/vm_summary.csv")
    #df_crit_aware = pd.read_csv(f"{data_root}/{exp_type}/crit-aware/vm_summary.csv")

    # 2) Define a small helper to compute eviction fractions by VM type:
    def get_eviction_fractions(df):
        """
        Returns the fraction of evicted best-effort VMs and fraction of evicted
        critical VMs over the entire set of VM arrivals in 'df'.

        We assume:
          - 'vm_type' column in { 'best_effort', 'critical' }
          - 'evicted' column is boolean or in {0, 1}
          - Each row = 1 VM arrival
        Adjust as needed for your CSV schema.
        """
        total_vms = df['arrived'].sum()
        if total_vms == 0:
            return (0, 0)

        # Filter for best-effort and critical:
        df_best_effort = df[df['is_evictable'] == True]
        df_critical = df[df['is_evictable'] == False]

        best_effort_evicted = df_best_effort['prematurely_killed'].sum()  # sum of 1's if 'evicted' is {0,1}
        critical_evicted = df_critical['prematurely_killed'].sum()

        # Fractions:
        frac_be = best_effort_evicted / total_vms
        frac_cr = critical_evicted / total_vms
        return (frac_be, frac_cr)

    # 3) Compute the two stacked fractions for each scenario
    with_nova_be, with_nova_cr = get_eviction_fractions(df_with_nova)
    prop_be, prop_cr = get_eviction_fractions(df_proposed)

    # 4) Build the stacked bar chart
    labels = ['nova', 'proposed']
    be_values = [with_nova_be, prop_be]
    cr_values = [with_nova_cr, prop_cr]

    x = np.arange(len(labels))
    width = 0.5

    fig, ax = plt.subplots(figsize=(3, 2.1))

    # Plot best-effort portion
    p1 = ax.bar(x, be_values, width, label='BestEffort', color='#6EC2E8', linewidth=1, edgecolor='black')
    # Plot critical portion stacked on top
    p2 = ax.bar(x, cr_values, width, bottom=be_values, label='Critical', color='#ED7777', linewidth=1, edgecolor='black'
                #, hatch='///'
                )

    # Add some text labels inside each bar
    for i in range(len(labels)):
        # BestEffort label near the midpoint of its bar
        ax.text(x[i],
                be_values[i] / 2,
                f"{be_values[i]:.3g}",
                ha='center', va='center', color='black')

        # Critical label near the midpoint of the top region
        ax.text(x[i],
                be_values[i] + cr_values[i] / 2,
                f"{cr_values[i]:.3g}",
                ha='center', va='center', color='black')

    # 5) Final formatting
    ax.set_ylabel('% of total VM arrivals')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    #ax.set_title('VM Eviction Incidents')
    ax.legend(ncol=2,  columnspacing=0.3)

    # Optional: tweak the y-axis to show values more like "0.0, 0.5, 1.0, 1.5..."
    # If you prefer actual percentages, multiply values by 100 above or
    # use a formatter for percentage labels.
    ax.set_ylim(0, max(be_values[i] + cr_values[i] for i in range(len(labels))) * 1.2)

    plt.tight_layout()
    plt.savefig("./results/pack-proto_vm-evictions.svg")