from get_configs import parse_configs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data_root = parse_configs()["data-root"]

def analyse_nlt(exp_type):
    """
    exp_type: 'debug' or 'full'
    """

    # --- Read in the two distributions ---
    df_nova = pd.read_csv(f"{data_root}/{exp_type}/with-nova/vm_nLT_details.csv")
    df_proposed = pd.read_csv(f"{data_root}/{exp_type}/proposed/vm_nLT_details.csv")

    def pre_process_nlt(df_nlt):
        # Cap all values at 1.0
        df_nlt['nLT'] = df_nlt['nLT'].clip(upper=1.0)

        return df_nlt

    nlt_dst_nova = pre_process_nlt(df_nova)['nLT'].dropna()
    nlt_dst_proposed = pre_process_nlt(df_proposed)['nLT'].dropna()

    # --- Helper function to compute empirical CDF ---
    def ecdf(data):
        x = np.sort(data)
        y = np.arange(1, len(x) + 1) / len(x)
        return x, y

    # --- Compute CDFs for each distribution ---
    x_nova, cdf_nova = ecdf(nlt_dst_nova)
    x_proposed, cdf_proposed = ecdf(nlt_dst_proposed)

    # --- Create the plot ---
    fig, ax = plt.subplots(figsize=(4,2.0))
    ax.plot(x_nova, cdf_nova, label='Nova', color='red', lw=2, ls='solid')
    ax.plot(x_proposed, cdf_proposed, label='Proposed', color='blue', lw=2, ls='dashed')

    # --- Use a log scale for the CDF (y-axis) ---
    ax.set_yscale('log')

    # --- Mark nLT = 0.90 with a vertical line ---
    ax.axvline(0.90, color='gray', linestyle='--', label='nLT=0.90')

    # --- Compute fraction of VMs that have nLT <= 0.90 for each curve ---
    cdf_nova_90 = (nlt_dst_nova <= 0.90).mean() * 100
    cdf_proposed_90 = (nlt_dst_proposed <= 0.90).mean() * 100

    # # You can annotate these percentages in the plot; for a simple text box:
    # ax.text(0.95, 5e-2,  # x=0.95, y=5e-2 (pick any suitable spot)
    #         f"Nova: {cdf_nova_90:.2f}%\nProposed: {cdf_proposed_90:.2f}%",
    #         va='top', ha='left', fontsize=9,
    #         bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # --- Labeling and legend ---
    #ax.set_xlabel("Norm. Lifetime (nLT) of an Evicted VM")
    ax.set_xlabel("Norm. Lifetime (nLT) of VMs")
    ax.set_ylabel("CDF (log scale)")
    ax.set_xlim([0,1])
    ax.grid(True, which='both', linestyle=':', alpha=0.8)
    ax.legend()

    plt.tight_layout()
    plt.savefig("./results/pack-proto_nlt.svg")
