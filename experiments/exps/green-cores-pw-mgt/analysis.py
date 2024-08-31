import csv
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 16})


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
    middle = max_val / 2 - 0.3
    offset = 12

    # Raw power plotting.
    data = data[data['CPU'] == 'Overall']
    data = data[['Clk', 'PkgWatt']]
    plot_pkg_pw(data, middle=middle, offset=offset, file_name='./results/pkg-pw_raw.svg')

    # Residency plotting.
    plot_metrics(c_data, middle, offset, param='C6%',
                 title='C6-state Residencies',
                 ylbl="Sleep Residency (%)",
                 out='results/sleep-residency.svg', yshift=60)

    # Frequency plotting.
    plot_metrics(c_data, middle, offset, param='Avg_MHz',
                 title='Operating Frequency',
                 ylbl="Frequency (MHz)",
                 out='results/op-frq.svg', shift=280, yshift=1000)

    # Temp. plotting.
    plot_metrics(c_data, middle, offset, param='CoreTmp', title='Temperature Variation', ylbl="Temperature (°C)",
                 out='results/core-temp.svg', shift=0.9)


def plot_metrics(c_data, middle, offset, param='C6%', title='C6-state Residencies', ylbl="Residency (%)",
                 out='results/sleep-residency.svg', shift=9, yshift=0.09):
    plt.rcParams.update({'font.size': 20})

    plt.clf()
    figsize = (12, 3.7)
    plt.figure(figsize=figsize)

    x_min = 350
    x_max = 600

    vline_x1 = middle - offset
    vline_x2 = middle + offset
    vline_x3 = 508.7

    overall = c_data[c_data['CPU'] == 'Overall'][['Clk', param]]
    if param == 'CoreTmp':
        overall[param] = c_data[c_data['CPU'] == 'Overall']['PkgTmp']
    n_data = c_data[c_data['CPU'] != 'Overall']
    reg = n_data[n_data['CPU'].astype(int) < 6][['Clk', param]].groupby('Clk').mean().reset_index()
    green = n_data[n_data['CPU'].astype(int) >= 6][['Clk', param]].groupby('Clk').mean().reset_index()

    plt.plot(overall['Clk'], overall[param], color='b', label='CPU Package Average', linewidth=2.5, marker='o', markevery=7)
    plt.plot(reg['Clk'], reg[param], color='brown', label='Regular Cores', linewidth=2.5, marker='s', markevery=9)
    plt.plot(green['Clk'], green[param], color='g', label='Renewables-driven Cores', linewidth=2.5, marker='^', markevery=11)

    add_vlines(None, ymin=0, vline_x1=vline_x1, vline_x2=vline_x2, vline_x3=vline_x3, yshift=yshift)

    # plt.axvline(x=middle - offset, color='r', linestyle='--', linewidth=1)
    # plt.axvline(x=middle + offset, color='r', linestyle='--', linewidth=1)
    arrow_y = green[param].min()
    gap = 2 * offset
    # plt.text(middle, arrow_y - shift, r'$\Delta t$', color='red', ha='center', va='top')
    # plt.text(middle, arrow_y - shift, r'$\Delta t \approx $' + f'{int(gap * 0.5)}' + 's',color='red', ha='center', va='top')

    # plt.title(title)
    # plt.xlabel("Measurement (0.5 second intervals)")
    plt.xlim(x_min, x_max)
    plt.grid(which='major', axis='both', linestyle='-')
    plt.minorticks_on()
    plt.ylabel(ylbl)
    plt.tight_layout()
    plt.legend(loc='upper left')
    plt.savefig(out, bbox_inches='tight')


def plot_pkg_pw(data, middle=0, offset=0, file_name=""):
    plt.rcParams.update({'font.size': 13})

    x_min = 370
    x_max = 650
    # normalize PkgWatt.
    #data['PkgWatt'] = data['PkgWatt'] / data['PkgWatt'].max()

    # max_val = data['Clk'].max()
    # middle = max_val / 2
    # offset = 13
    # Add vertical lines at x=10 and x=20
    vline_x1 = middle - offset
    vline_x2 = middle + offset
    vline_x3 = 508.7

    # plot a binary signal where until vline_x1 its 1 and 0 after that.
    data['RnwSignal'] = data['Clk'].apply(lambda x: 1 if x < (480) else 0)
    print(data[['RnwSignal', 'Clk'
                             '']])
    data.plot(x='Clk', y='RnwSignal', kind='line')

    figsize = (12, 2.5)
    data.plot(x='Clk', y='PkgWatt', kind='line',
              # title='Server Power Management with Green Cores',
              xlabel='',
              # xlabel='Measurement (0.5 second intervals)',
              ylabel='Power (W)',
              figsize=figsize, linewidth=2.5, label="CPU package power", marker='o', markevery=5)

    color = 'green'
    high_mean = data[data['Clk'] < vline_x1]['PkgWatt'].max()
    low_mean = data[data['Clk'] > vline_x2]['PkgWatt'].max()
    plt.axhline(y=high_mean, color=color, linestyle='--', linewidth=1)
    plt.text(x_min + 1, high_mean, ('Max ' + r'$t \leq t_1$' + ': ' + str(high_mean)),
             color=color, va='bottom', ha='left', fontweight='bold')

    # intermediate
    pw_intr = 69.3
    plt.axhline(y=pw_intr, color=color, linestyle='--', linewidth=1)
    plt.text(x_min + 1, pw_intr, ('Max ' + r'$t_2 \leq t \leq t_3$' + ': ' + str(pw_intr)),
             color=color, va='bottom', ha='left', fontweight='bold')

    # max after delta t
    plt.axhline(y=low_mean, color=color, linestyle='--', linewidth=1)
    plt.text(x_min + 1, low_mean, ('Max ' + r'$t \geq t_3$' + ': ' + f'{round(low_mean, 2)}'), color=color,
             va='bottom', ha='left', fontweight='bold')

    add_vlines(data, ymin=min(data['PkgWatt']), vline_x1=vline_x1, vline_x2=vline_x2, vline_x3=vline_x3, yshift=8)
    #
    # arrow_y = min(data['PkgWatt'])
    # gap = vline_x2 - vline_x1
    # plt.text((vline_x1 + vline_x2) / 2, arrow_y + 0.012, r'$\Delta t$',
    #          color='red', ha='center', va='top')

    plt.ylim(55, 82)
    plt.xlim(x_min, x_max)
    plt.grid(which='major', axis='both', linestyle='-')
    plt.minorticks_on()
    plt.tight_layout()
    plt.legend()
    plt.savefig(file_name, bbox_inches='tight')


def add_vlines(data, ymin=0, vline_x1=10, vline_x2=20, vline_x3=20, yshift=0.09):
    # yshift = 0.045

    plt.axvline(x=vline_x1, color='r', linestyle='--', linewidth=1, label=r'$t_1$' + ': Energy loss signal arrives')
    plt.text(vline_x1 - 1, ymin + yshift, r'$t_1$', color='red', ha='right', va='bottom', fontweight='bold')

    plt.axvline(x=vline_x3, color='r', linestyle='--', linewidth=1, label=r'$t_2$' + ': VM eviction completes')
    plt.text(vline_x3 - 1, ymin + yshift, r'$t_2$', color='red', ha='right', va='bottom', fontweight='bold')

    plt.axvline(x=vline_x2, color='r', linestyle='--', linewidth=1, label=r'$t_3$' + ': Cores set to sleep')
    plt.text(vline_x2 + 1, ymin + yshift, r'$t_3$', color='red', ha='left', va='bottom', fontweight='bold')


figsize = (10, 3)

# Active vs Sleep
csv_file = to_csv_turbostat(
    "/Users/tharindu/Library/CloudStorage/OneDrive-TheUniversityofMelbourne/phd-student/projects/green-cores/experiments/experimental/exp-4_power-mgt/RAPL_turbostat.log",
    "./results/turbostat.csv")
df = pd.read_csv(csv_file)

MID = 1716
SCOPE = 500
plot_overall_pw(df, front_clip=MID - SCOPE, rear_clip=MID + SCOPE)
