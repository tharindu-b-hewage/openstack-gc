import os
import re
import glob
import pandas as pd
import matplotlib.pyplot as plt
from get_configs import parse_configs

data_root = parse_configs()["data-root"]

# ---------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------
# LOGS_FOLDER = "path_to_turbostat_logs"  # Replace with your folder path
FILE_PATTERN = "*turbostat_*.log"  # Or use "*.txt" depending on your file suffix
TIME_COLUMN = "Time_Of_Day_Seconds"
PKG_WATT_COLUMN = "PkgWatt"


def analyze_rnw_harvest(exp_type):
    def process_sch():
        LOGS_FOLDER_NOVA = f"{data_root}/{exp_type}/with-nova"
        LOGS_FOLDER_PROPOSED = f"{data_root}/{exp_type}/proposed"

        # LOGS_FOLDER_proposed = f"{data_root}/{exp_type}/proposed"

        # ---------------------------------------------------------------
        # Helper function to parse server name from filename
        # ---------------------------------------------------------------
        def parse_server_name_from_filename(fname):
            """
            Example expected pattern: "stack3@<server-ip>_turbostat_2025-02-18.log"
            We want to capture everything from "stack3@" up to the next underscore.
            Adjust regex if your filenames differ.
            """
            # Example match: stack3@192.168.0.1
            # Then remove "stack3@" if you only want the IP, or keep it to maintain uniqueness
            match = re.search(r"(stack3@[^_]+)", os.path.basename(fname))
            if match:
                return match.group(1)
            else:
                # fallback to filename if pattern not found
                return os.path.basename(fname)

        # ---------------------------------------------------------------
        # Gather files and group them by server
        # ---------------------------------------------------------------
        def get_files(LOGS_FOLDER):
            raw_path = os.path.join(LOGS_FOLDER)
            raw_path = glob.escape(raw_path)
            files = glob.glob(os.path.join(raw_path, FILE_PATTERN))
            return files

        # Get data files for both scheduling techniques.
        files = get_files(LOGS_FOLDER_NOVA)
        files.extend(get_files(LOGS_FOLDER_PROPOSED))

        # Dictionary: server_name -> list_of_files
        server_files = {}
        for f in files:
            server_name = parse_server_name_from_filename(f)
            server_files.setdefault(server_name, []).append(f)

        # ---------------------------------------------------------------
        # Read each server's files into a single DataFrame
        # ---------------------------------------------------------------
        server_data = {}
        for server_name, file_list in server_files.items():
            # Read & concatenate data for one server
            df_list = []
            for log_file in file_list:
                # Adjust delimiter, skiprows, or header arguments to match your file format.
                # Example: if the first line is a header with column names including "time_of_day_seconds" etc.
                # If there's a different format, you may need more sophisticated parsing.
                df_temp = pd.read_csv(
                    log_file,
                    delimiter=r"\s+",
                    header=0  # Assuming first row is the header
                )
                schd = "nova" if "with-nova" in log_file else "proposed"
                df_temp["schd"] = schd
                df_temp[TIME_COLUMN] = df_temp[TIME_COLUMN] - df_temp[TIME_COLUMN].min()
                #df_temp = df_temp[df_temp[TIME_COLUMN] >= 0]
                #df_temp = df_temp[df_temp[TIME_COLUMN] <= 1600]
                #df_temp[PKG_WATT_COLUMN] = df_temp[PKG_WATT_COLUMN].rolling(window=50, center=True).mean()
                #df_temp[PKG_WATT_COLUMN] = df_temp[PKG_WATT_COLUMN]
                df_list.append(df_temp)

            # Combine all data for that server
            df = pd.concat(df_list, ignore_index=True)

            # Make sure we have the correct columns
            if TIME_COLUMN not in df.columns or PKG_WATT_COLUMN not in df.columns:
                print(f"[Warning] {server_name} missing expected columns in DataFrame.")
                continue

            # Sort by time_of_day_seconds
            df.sort_values(by=TIME_COLUMN, inplace=True)

            # Reset index after sorting
            df.reset_index(drop=True, inplace=True)

            # Store
            server_data[server_name] = df

        # ---------------------------------------------------------------
        # Identify period of increased PkgWatt for each server
        # ---------------------------------------------------------------
        # This step can be as simple or as complex as needed.
        # For demonstration, we look for when PkgWatt is above some threshold.
        # If you have a known baseline or a specific timestamp, adapt accordingly.

        def find_increased_power_periods(df, power_col=PKG_WATT_COLUMN, threshold=None):
            """
            Return a list of (start_index, end_index) for periods
            in which PkgWatt is above the given threshold.
            If threshold is None, automatically pick e.g. mean + 2*std as threshold.
            """
            if threshold is None:
                # Example dynamic threshold: mean + 2 std dev
                threshold = df[power_col].mean() + 2 * df[power_col].std()

            above_threshold = df[power_col] > threshold

            periods = []
            in_period = False
            start_idx = None

            for i in range(len(df)):
                if above_threshold.iloc[i] and not in_period:
                    # start new period
                    in_period = True
                    start_idx = i
                elif not above_threshold.iloc[i] and in_period:
                    # end current period
                    in_period = False
                    end_idx = i - 1
                    periods.append((start_idx, end_idx))

            # If the last segment is open-ended
            if in_period:
                periods.append((start_idx, len(df) - 1))

            return periods

        # Example usage: find periods for each server
        server_increased_power_periods = {}
        for server_name, df in server_data.items():
            periods = find_increased_power_periods(df, PKG_WATT_COLUMN)
            server_increased_power_periods[server_name] = periods

            # Print them out for clarity
            print(f"Server: {server_name}")
            print(f"Increased power periods (threshold-based): {periods}")

        # name mapping
        server_name_mapping = {
            "stack3@172.23.13.34-turbostat": "node-1",
            "stack3@172.23.13.35-turbostat": "node-2",
        }

        # ---------------------------------------------------------------
        # Plot time series for each server, marking the increased PkgWatt region
        # ---------------------------------------------------------------
        for server_name, df in server_data.items():
            #plt.figure(figsize=(3, 2))
            # Plot the 'nova' schedule and get the axis
            ax = df[df["schd"] == "nova"].plot(x=TIME_COLUMN, y=PKG_WATT_COLUMN, label="nova", figsize=(3.2, 1.6), linewidth=0.5)

            # Plot the 'proposed' schedule on the same axis
            df[df["schd"] == "proposed"].plot(x=TIME_COLUMN, y=PKG_WATT_COLUMN, label="proposed", linewidth=0.5, ax=ax)

            # Optionally highlight the periods
            # periods = server_increased_power_periods[server_name]
            # for (start_idx, end_idx) in periods:
            #     start_time = df.loc[start_idx, TIME_COLUMN]
            #     end_time = df.loc[end_idx, TIME_COLUMN]
            #     # fill the region on the plot for clarity
            #     plt.axvspan(start_time, end_time, color='red', alpha=0.2)

            #ax.set_xlim(500, 1500)

            #plt.title(f"PkgWatt Time Series - {server_name}")
            plt.xlabel("Measurements")
            plt.ylabel("CPU Pkg Power \n(Watts)")
            plt.legend()
            plt.tight_layout()
            plt.minorticks_on()
            plt.savefig("./results/pack-proto_rnw_" + str(server_name) + ".svg")

        # ---------------------------------------------------------------
        # Calculate total energy consumption
        # ---------------------------------------------------------------
        # Assume each row’s PkgWatt is the average
        # over the interval from the previous row’s time to the current row’s time.
        # Energy = Power * time. If the units are PkgWatt (W) and time in seconds,
        # then Energy is in Joules (W*s).

        energy_table = []

        for server_name, df in server_data.items():
            # Ensure sorted by time
            df.sort_values(by=TIME_COLUMN, inplace=True)

            max_power = df[PKG_WATT_COLUMN].max()
            min_power = df[PKG_WATT_COLUMN].min()
            grid_power_limit = (max_power - min_power) / 2 + min_power
            df.loc[df[PKG_WATT_COLUMN] <= grid_power_limit, PKG_WATT_COLUMN] = 0

            def get_energy(df):
                # Calculate time deltas (seconds)
                # We can use consecutive differences in time_of_day_seconds
                df["time_delta"] = df[TIME_COLUMN].diff().fillna(0.0)  # first row has no previous
                # Energy for each row = PkgWatt * time_delta
                # If we treat the PkgWatt reading as representative of the interval that follows:
                # Or you could shift or do an average with the next row, depending on how your data is measured.
                df["interval_energy_J"] = df[PKG_WATT_COLUMN] * df["time_delta"]

                total_energy_J = df["interval_energy_J"].sum()

                # Convert Joules to Wh if desired: 1 Wh = 3600 J
                total_energy_Wh = total_energy_J / 3600.0
                return total_energy_J, total_energy_Wh

            df_nova = df[df["schd"] == "nova"]
            en_j, en_Wh = get_energy(df_nova)

            df_proposed = df[df["schd"] == "proposed"]
            ep_j, ep_Wh = get_energy(df_proposed)

            energy_table.append({
                "Server": server_name,
                "nova_energy_J": en_j,
                "nova_energy_Wh": en_Wh,
                "proposed_energy_J": ep_j,
                "proposed_energy_Wh": ep_Wh,
            })

        # Create a summary table DataFrame
        energy_df = pd.DataFrame(energy_table)

        nova_harnessed_wh = energy_df['nova_energy_Wh'].sum()
        proposed_harnessed_wh = energy_df['proposed_energy_Wh'].sum()

        if proposed_harnessed_wh > nova_harnessed_wh:
            print("proposed harvested more than nova!")
        else:
            print("nova's harvested more than proposed!")
        print(f"\nNova harnessed power: {nova_harnessed_wh}, proposed harnessed power: {proposed_harnessed_wh}")

        energy_df.to_csv("./results/pack-proto_rnw_data.csv", index=False)

    #process_sch(schd="with-nova")
    process_sch()
