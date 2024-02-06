import pandas as pd
from matplotlib import pyplot as plt


def draw_trace(name,csv):
    df = pd.read_csv(csv)
    df.plot(x='clk', y=['pd', 'gs'], figsize=(7, 6))
    plt.legend()
    plt.savefig(name, bbox_inches='tight')


draw_trace('pract-packing-0.svg', '../data/pre-processed_cluster-data_evict-0.1179.csv')
draw_trace('pract-packing-1.svg', '../data/pre-processed_cluster-data_evict-1.0.csv')
draw_trace('pract-packing-mixed.svg', '../data/pre-processed_cluster-data_evict-0.0.csv')
