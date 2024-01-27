import re

import pandas as pd

headers_raw = "Core	CPU	Avg_MHz	Busy%	Bzy_MHz	TSC_MHz	IPC	IRQ	SMI	POLL	C1ACPI	C2ACPI	C3ACPI	POLL%	C1ACPI%	C2ACPI%	C3ACPI%	CPU%c1	CPU%c6	CPU%c7	CoreTmp	CoreThr	PkgTmp	GFX%rc6	GFXMHz	GFXAMHz	Totl%C0	Any%C0	GFX%C0	CPUGFX%	Pkg%pc2	Pkg%pc3	Pkg%pc6	Pkg%pc7	Pkg%pc8	Pkg%pc9	Pk%pc10	CPU%LPI	SYS%LPI	PkgWatt	CorWatt	GFXWatt	RAMWatt	PKG_%	RAM_%"
headers = re.split(r'\s+', headers_raw)
df = pd.DataFrame(columns=['Clk', *headers])
print('headers', headers, 'columns count', len(df.columns))


def get_power_stats():
    global df
    csv_path = './pw-exp_2024-01-27-14-06/power-stats.csv'
    with open(csv_path) as f:
        lines = f.readlines()

        clk = 0
        for row in lines:
            row_data = re.split(r'\s+', row)
            if row_data[-1] != '':
                print('final element is expected to be an empty string!')
                raise Exception
            row_data = row_data[0:-1]
            if row_data[0] == 'Core':
                clk += 1
                continue
            row_data.insert(0, str(clk))

            row_dict = {}
            idx = 0
            for col in df.columns:
                val = None
                if idx < len(row_data):
                    crnt_val = row_data[idx]
                    try:
                        if col == 'Core':
                            if crnt_val == '-':
                                crnt_val = 'Overall'
                            else:
                                crnt_val = 'Core-' + str(crnt_val)
                        else:
                            crnt_val = float(crnt_val)
                    except:
                        crnt_val = None
                    val = crnt_val
                row_dict[col] = [val]
                idx += 1
            row_df = pd.DataFrame(row_dict)
            df = pd.concat([df, row_df], ignore_index=True)
        df.reset_index(drop=True, inplace=True)
        return df


def get_green_scores():
    green_score_df = pd.read_csv('./pw-exp_2024-01-27-14-06/green-score-dump.csv')
    green_score_df['interval(s)'] = 5
    return green_score_df
