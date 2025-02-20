import pandas as pd

# Thinned trace obtained did not scale VM running lifetime. This script
# adjusts that.

thinned_trace = pd.read_csv("AzureTraceThinned.csv")

scale_factor = 0.02
thinned_trace['lifetime'] = thinned_trace['lifetime'] * scale_factor

thinned_trace.to_csv("./AzureTraceScaled.csv", index=False)