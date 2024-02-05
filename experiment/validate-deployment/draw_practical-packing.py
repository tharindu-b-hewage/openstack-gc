import pandas as pd
from matplotlib import pyplot as plt


def draw_trace(name,csv):
    df = pd.read_csv(csv)
    df.plot(x='clk', y=['pd', 'gs'], figsize=(7, 6))
    plt.legend()
    plt.savefig(name, bbox_inches='tight')


draw_trace('pract-packing-0.svg', '0-prob-evict-trace.csv')
draw_trace('pract-packing-1.svg', '1-prob-evict-trace.csv')
draw_trace('pract-packing-mixed.svg', 'mixed-trace.csv')
