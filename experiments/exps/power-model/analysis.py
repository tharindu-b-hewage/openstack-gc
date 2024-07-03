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


def isolate_switched_slots(data):
    total = len(data)
    groups = 12
    rows_per_group = total // groups
    cut_off = 100  # to omit switching data
    data = data[0:cut_off * rows_per_group]
    pass


def plot_overall_pw(data, front_clip=-1, rear_clip=-1, prefix='', ofst_strt=0, ofst_end=0):
    if front_clip >= 0 and rear_clip >= 0:
        data = data[data['Clk'] >= front_clip]
        data = data[data['Clk'] <= rear_clip]

    data = data[data['CPU'] == 'Overall']
    data = data[['Clk', 'PkgWatt']]

    # data = isolate_switched_slots(data)

    # plot raw.
    plot_pkg_pw(data, file_name='./results/' + prefix + '_pkg-pw_raw.svg')

    plt.clf()
    data = split_into_awaken_cores(data, ofst_strt=ofst_strt, ofst_end=ofst_strt)
    data.boxplot(showfliers=True)
    plt.tight_layout()
    plt.savefig('./results/' + prefix + '_pkg-pw_isolated.svg', bbox_inches='tight')

    plt.clf()
    medians = data.mean()
    iqr = data.std()
    data = pd.DataFrame({
        'mean': medians,
        'std': iqr
    })
    data = data.reset_index()
    data.plot(x='index', y='mean', kind='barh', xerr='std', capsize=3, figsize=figsize,
              title='Power Consumption as Cores Sleeps', xlabel='CPU PKG Power (W)', ylabel='Number of Active Cores')
    # data.plot(kind='bar', figsize=figsize)
    plt.tight_layout()
    plt.legend()
    plt.savefig('./results/' + prefix + '_pkg-pw_err-bar.svg', bbox_inches='tight')
    return data


def split_into_awaken_cores(data, ofst_strt=0, ofst_end=0):
    # Define the number of groups
    num_groups = 12

    # Calculate the number of rows per group
    rows_per_group = len(data) // num_groups

    # Create a new DataFrame with each group as a new column
    new_data = {}
    # offset_start = 20  # to omit switching data
    # offset_end = 2  # to omit switching data
    for i in range(num_groups):
        start_idx = i * rows_per_group + ofst_strt
        end_idx = (i + 1) * rows_per_group - ofst_end
        group_data = data['PkgWatt'][start_idx:end_idx].reset_index(drop=True)
        new_data[f'{i + 1}'] = group_data

    # Create the new DataFrame
    split = pd.DataFrame(new_data)
    return split


def plot_pkg_pw(data, file_name):
    data.plot(x='Clk', y='PkgWatt', kind='line', title='Power Consumption as Cores Awake', xlabel='Time Step',
              ylabel='CPU PKG Power (W)', figsize=figsize)
    plt.tight_layout()
    plt.legend()
    plt.savefig(file_name, bbox_inches='tight')


figsize = (10, 3)

# Active vs Sleep
csv_file = to_csv_turbostat(
    "/Users/tharindu/Library/CloudStorage/OneDrive-TheUniversityofMelbourne/phd-student/projects/green-cores/experiments/experimental/exp-3_power-model/part-01_active-vs-sleep/RAPL_turbostat.log",
    "./results/act_vs_slp_turbostat.csv")
act_vs_slp_df = pd.read_csv(csv_file)

# Remove readings before and after the experiment. Need to observe the data to determine the correct values.
# Hint: set both to -1, observe plot, and adjust accordingly.
EXP_START = 34
# EXP_START =
EXP_END = 1701
# EXP_END = 60
act_vs_slp_data = plot_overall_pw(data=act_vs_slp_df, front_clip=EXP_START, rear_clip=EXP_END, prefix='act-vs-slp',
                                  ofst_strt=20, ofst_end=2)

# Pinned vs Sleep
csv_file = to_csv_turbostat(
    "/Users/tharindu/Library/CloudStorage/OneDrive-TheUniversityofMelbourne/phd-student/projects/green-cores/experiments/experimental/exp-3_power-model/part-02_pinned-vs-sleep/RAPL_turbostat.log",
    "./results/pin_vs_slp_turbostat.csv")
act_vs_slp_df = pd.read_csv(csv_file)

# Remove readings before and after the experiment. Need to observe the data to determine the correct values.
# Hint: set both to -1, observe plot, and adjust accordingly.
# EXP_START = 45
EXP_START = 45
EXP_END = 5432
pin_vs_slp_data = plot_overall_pw(data=act_vs_slp_df, front_clip=EXP_START, rear_clip=EXP_END, prefix='pin-vs-slp',
                                  ofst_strt=38, ofst_end=2)

cmb_data = pd.DataFrame()
cmb_data['Awake'] = act_vs_slp_data['index']

cmb_data['idle'] = act_vs_slp_data['mean']
cmb_data['idle_std'] = act_vs_slp_data['std']

cmb_data['pinned'] = pin_vs_slp_data['mean']
cmb_data['pinned_std'] = pin_vs_slp_data['std']

bars = cmb_data.plot(x='Awake', y=['idle', 'pinned'], kind='barh', xerr=[cmb_data['idle_std'], cmb_data['pinned_std']],
                     capsize=2, figsize=figsize,
                     title='Power Consumption as Cores Sleep', xlabel='CPU PKG Power (W)',
                     ylabel='Number of Cores Awake',
                     width=0.7)

plt.tight_layout()
plt.legend()
plt.savefig('./results/overall_pkg-pw_err-bar.svg', bbox_inches='tight')
