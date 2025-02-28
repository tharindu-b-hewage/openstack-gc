import pandas as pd
import csv
import math
import random

SCALED_TRACE = "AzureTraceAdjustLife.csv"

def adjust_lifetime():
    thinned_trace = pd.read_csv("AzureTraceThinned.csv")

    scale_factor = 0.02
    thinned_trace['lifetime'] = thinned_trace['lifetime'] * scale_factor
    thinned_trace.to_csv("./" + SCALED_TRACE, index=False)


def burst_trace(
        input_csv,
        output_csv,
        k=2,  # factor to multiply arrivals
        bin_size=0.01  # size of each time bin in 'days'
):
    # Read entire trace into memory
    col_names_row = None
    with open(input_csv, 'r', newline='') as fin:
        reader = csv.reader(fin)

        # Store events as a list of tuples
        events = []
        max_time = 0.0
        for row in reader:
            try: # omit column names row.
                float(row[0])
            except ValueError:
                col_names_row = row
                continue

            t = float(row[0])  # arrival time
            cores = int(row[1])
            lifetime = float(row[2])
            is_evictable = row[3]  # "True"/"False".

            events.append((t, cores, lifetime, is_evictable))
            max_time = max(max_time, t)

    # Sort by arrival time (just in case)
    events.sort(key=lambda e: e[0])

    # We will create a new list of events
    new_events = []

    # Let's define bin boundaries from 0 to max_time
    num_bins = math.ceil(max_time / bin_size)

    # For convenience, group original events by bin
    bins = [[] for _ in range(num_bins)]
    for (t, cores, lifetime, is_evictable) in events:
        bin_idx = int(t // bin_size)
        bins[bin_idx].append((t, cores, lifetime, is_evictable))

    # For each bin, replicate arrivals
    for bin_idx in range(num_bins):
        # Original events in this bin
        these_arrivals = bins[bin_idx]
        original_count = len(these_arrivals)

        if original_count == 0:
            # No arrivals in this bin, skip
            continue

        # We want about k times more
        target_count = int(round(k * original_count))
        # We already have 'original_count'

        # Keep the original events as-is
        for ev in these_arrivals:
            new_events.append(ev)

        # We need (target_count - original_count) more
        extra_needed = target_count - original_count

        # The time window for this bin is [bin_start, bin_end)
        bin_start = bin_idx * bin_size
        bin_end = (bin_idx + 1) * bin_size
        if bin_idx == num_bins - 1:
            # last bin might exceed max_time
            bin_end = max_time

        # We can distribute new arrivals around the times of existing arrivals
        # or just place them uniformly in [bin_start, bin_end].

        for _ in range(extra_needed):
            # Option: pick a random event time from existing arrivals,
            # then add a small random offset.
            base_arrival = random.choice(these_arrivals)
            base_t = base_arrival[0]
            # small offset in [-delta, delta]
            delta = (bin_end - bin_start) * 0.1  # some fraction of bin
            offset = random.uniform(-delta, delta)
            new_t = base_t + offset

            # clamp to bin boundaries
            new_t = max(new_t, bin_start)
            new_t = min(new_t, bin_end)

            # spread the arrivals.


            # replicate the same cores, lifetime, etc.
            # or you could vary them slightly if desired
            new_event = (
                new_t,
                base_arrival[1],  # same cores
                min(0.00694444, base_arrival[2] * (1 + random.random())),  # randomly increase lifetime.
                base_arrival[3]  # same isEvictable
            )
            new_events.append(new_event)

    # Finally, sort the new_events by their arrival time
    new_events.sort(key=lambda e: e[0])

    # Write out the new trace
    with open(output_csv, 'w', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(col_names_row)
        for (t, cores, lifetime, is_evictable) in new_events:
            writer.writerow([t, cores, lifetime, is_evictable])

    print(f"Original events: {len(events)}, New events: {len(new_events)}")
    print(f"Last arrival time ~ {new_events[-1][0]:.4f} (should be <= {max_time:.4f})")

adjust_lifetime()
burst_trace(input_csv=SCALED_TRACE, output_csv="AzureTraceScaled.csv", k=8, bin_size=0.01)