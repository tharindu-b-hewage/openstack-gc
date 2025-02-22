import pandas as pd

def parse_configs():
    df = pd.read_csv('secrets.csv')
    df_dict = dict(zip(df['key'], df['value']))
    print(df_dict)
    return df_dict