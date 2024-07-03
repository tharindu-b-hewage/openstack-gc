import csv
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 12})


def to_csv_turbostat(logfile_path, csvfile_path):
    # Read the logfile and process the data
    with open(logfile_path, 'r') as logfile, open(csvfile_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header_found = False
        clk_value = 0

        clk = 0
        for line in logfile:
            if not header_found:
                # Check if the line contains the headers
                if line.startswith("Core\tCPU"):
                    headers = line.strip().split('\t')
                    headers.insert(0, 'Clk')  # Add 'Clk' column at the beginning
                    writer.writerow(headers)
                    header_found = True
            else:
                if line.startswith("Core\tCPU"):
                    clk += 1
                    continue
                else:
                    # Write the data rows
                    if line.strip() == "":
                        continue  # Skip empty lines
                    data = line.strip().split('\t')
                    data.insert(0, str(clk))
                    if len(data) == len(headers) - 1:  # Ensure the data row has the correct number of columns
                        clk_value += 1  # Increment the 'Clk' value for each new time step
                    data = ['Overall' if x == '-' else x for x in data]  # Replace '-' with 'Overall'
                    writer.writerow(data)
    return csvfile_path


def plot_overall_pw(data, front_clip=-1, rear_clip=-1):
    if front_clip >= 0 and rear_clip >= 0:
        data = data[data['Clk'] >= front_clip]
        data = data[data['Clk'] <= rear_clip]

    min_clk = data['Clk'].min()
    data['Clk'] = data['Clk'] - min_clk

    c_data = data.copy()

    # middle is the mid point of power transition. offset is the half of the transition period.
    max_val = data['Clk'].max()
    middle = max_val / 2
    offset = 13

    # Raw power plotting.
    data = data[data['CPU'] == 'Overall']
    data = data[['Clk', 'PkgWatt']]
    plot_pkg_pw(data, middle=middle, offset=offset, file_name='./results/pkg-pw_raw.svg')

    # Residency plotting.
    plot_metrics(c_data, middle, offset, param='C6%', title='C6-state Residencies', ylbl="Residency (%)",
                 out='results/sleep-residency.svg')

    # Frequency plotting.
    plot_metrics(c_data, middle, offset, param='Avg_MHz', title='Operating Frequency', ylbl="MHz",
                 out='results/op-frq.svg', shift=280)

    # Temp. plotting.
    plot_metrics(c_data, middle, offset, param='CoreTmp', title='Temperature Variation', ylbl="Temperature (°C)",
                 out='results/core-temp.svg', shift=0.9)


def plot_metrics(c_data, middle, offset, param='C6%', title='C6-state Residencies', ylbl="Residency (%)",
                 out='results/sleep-residency.svg', shift=9):
    plt.clf()
    overall = c_data[c_data['CPU'] == 'Overall'][['Clk', param]]
    if param == 'CoreTmp':
        overall[param] = c_data[c_data['CPU'] == 'Overall']['PkgTmp']
    n_data = c_data[c_data['CPU'] != 'Overall']
    reg = n_data[n_data['CPU'].astype(int) < 6][['Clk', param]].groupby('Clk').mean().reset_index()
    green = n_data[n_data['CPU'].astype(int) >= 6][['Clk', param]].groupby('Clk').mean().reset_index()

    plt.plot(overall['Clk'], overall[param], color='b', label='CPU Package')
    plt.plot(reg['Clk'], reg[param], color='brown', label='Regular Cores')
    plt.plot(green['Clk'], green[param], color='g', label='Green Cores')

    plt.axvline(x=middle - offset, color='r', linestyle='--', linewidth=1)
    plt.axvline(x=middle + offset, color='r', linestyle='--', linewidth=1)
    arrow_y = green[param].min()
    gap = 2 * offset
    plt.text(middle, arrow_y - shift, r'$\Delta t < $' + f'{int(gap * 0.5)}' + 's',
             color='red', ha='center', va='top')

    plt.title(title)
    plt.xlabel("Measurement (0.5 second intervals)")
    plt.ylabel(ylbl)
    plt.tight_layout()
    plt.legend()
    plt.savefig(out, bbox_inches='tight')


def plot_pkg_pw(data, middle=0, offset=0, file_name=""):
    # normalize PkgWatt.
    data['PkgWatt'] = data['PkgWatt'] / data['PkgWatt'].max()

    data.plot(x='Clk', y='PkgWatt', kind='line', title='Server Power Management with Green Cores',
              xlabel='Measurement (0.5 second intervals)',
              ylabel='Normalized Power Draw', figsize=figsize, linewidth=2.5, label="Measured Power")

    # max_val = data['Clk'].max()
    # middle = max_val / 2
    # offset = 13
    # Add vertical lines at x=10 and x=20
    vline_x1 = middle - offset
    vline_x2 = middle + offset

    color = 'green'
    high_mean = data[data['Clk'] < vline_x1]['PkgWatt'].max()
    low_mean = data[data['Clk'] > vline_x2]['PkgWatt'].max()
    plt.axhline(y=high_mean, color=color, linestyle='--', linewidth=1)
    # plt.text(data['Clk'].min(), high_mean, f'{round(high_mean,2)}', color=color, va='bottom', ha='right')

    plt.axhline(y=low_mean, color=color, linestyle='--', linewidth=1)
    plt.text(data['Clk'].min(), low_mean, f'{round(low_mean, 2)}', color=color, va='bottom', ha='right')

    add_vlines(data, vline_x1=vline_x1, vline_x2=vline_x2)

    arrow_y = min(data['PkgWatt'])
    gap = vline_x2 - vline_x1
    plt.text((vline_x1 + vline_x2) / 2, arrow_y - (arrow_y * 0.035), r'$\Delta t < $' + f'{int(gap * 0.5)}' + 's',
             color='red', ha='center', va='top')

    plt.tight_layout()
    plt.legend()
    plt.savefig(file_name, bbox_inches='tight')


def add_vlines(data, vline_x1=10, vline_x2=20):
    plt.axvline(x=vline_x1, color='r', linestyle='--', linewidth=1)
    plt.axvline(x=vline_x2, color='r', linestyle='--', linewidth=1)


figsize = (10, 3)

# Active vs Sleep
csv_file = to_csv_turbostat(
    "/Users/tharindu/Library/CloudStorage/OneDrive-TheUniversityofMelbourne/phd-student/projects/green-cores/experiments/experimental/exp-4_power-mgt/RAPL_turbostat.log",
    "./results/turbostat.csv")
df = pd.read_csv(csv_file)

MID = 1716
SCOPE = 500
plot_overall_pw(df, front_clip=MID - SCOPE, rear_clip=MID + SCOPE)
