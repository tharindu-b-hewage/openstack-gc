import pandas as pd

df_original = pd.read_csv("elia-solar-trace.csv")
df_original = df_original[df_original['days'] <= 1.0]

# Scale the 'day' column from [0,1] -> [0, 28 minutes]
df_compressed = df_original.copy()
df_compressed['days'] = df_compressed['days'] * 0.02083333

# The intensity remains the same
df_compressed['intensity'] = df_original['intensity']

print("Original data:")
print(df_original)
print("\nCompressed (28-min) data:")
print(df_compressed)

df_compressed[['days','intensity']].to_csv("./EliaSolarTraceThinned.csv", index=False)