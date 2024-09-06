import matplotlib.pyplot as plt


def parse_vm_latency_stats(name, raw_d):
    rt = raw_d['rteval']['Measurements']['Profile']['cyclictest']['system']['statistics']

    hst_raw = raw_d['rteval']['Measurements']['Profile']['cyclictest']['system']['histogram']
    hst = {}
    for e in hst_raw['bucket']:
        hst[int(e['@index'])] = int(e['@value'])
    print('MAD for', name, 'is:', rt['mean_absolute_deviation']['#text'])
    return {
        'name': name,
        'min': float(rt['minimum']['#text']),
        'max': float(rt['maximum']['#text']),
        'median': float(rt['median']['#text']),
        'mode': float(rt['mode']['#text']),
        'range': float(rt['range']['#text']),
        'mean': float(rt['mean']['#text']),
        'mad': float(rt['mean_absolute_deviation']['#text']),
        'sd': float(rt['standard_deviation']['#text']),
        'hst': hst
    }


def visualize(data, title, x_lbl, y_lbl, out_plot_path, type, is_h=False):
    names = [e['name'] for e in data]
    mean = [e['mean'] for e in data]
    mad = [e['mad'] for e in data]
    sds = [e['sd'] for e in data]
    means = [e['mean'] for e in data]
    max = [e['max'] for e in data]
    cv = [(e['sd'] / e['mean']) * 100 for e in data]

    print("names:", names)
    print("MAXs:", max)
    print("MADs:", mad)
    print("SDs:", sds)
    print("Means:", means)
    print("CVs:", cv)

    if type == 'eb':
        plt.rcParams.update({'font.size': 18})
        fig, ax = plt.subplots(figsize=(10, 3.4))
        bar = None
        if is_h:
            bars = ax.barh(names, mean, edgecolor="black",
                           hatch=['/', '/'],
                           zorder=4,
                           color=['#62ba97', '#62ba97'],
                           xerr=mad,
                           error_kw={'capsize': 3, 'ecolor': "red"},
                           height=-0.4,
                           align='edge',
                           label='real-time latency',
                           )
            ax.legend(['real-time latency'], loc='center right')
            ax.set_xscale('log')
            ax.set_xlabel(""r'$\mu$'"s")
            ax.set_zorder(4)

            # Create a secondary axis
            ax2 = ax.twiny()

            # Secondary bars
            print(names, mean)
            counts = [0, 1]
            bars2 = ax2.barh(names, counts, edgecolor="black",
                             hatch=['\\', '\\'],
                             zorder=4,
                             color=['#3a8aae', '#3a8aae'],
                             # xerr=second_scale_err,
                             # error_kw={'capsize': 3, 'ecolor': "blue"},
                             height=0.4,
                             align='edge',
                             label='eviction incidents',
                             )

            ax2.legend(['eviction incidents'], loc='upper right')
            ax2.set_xlabel("count")
            ax2.set_xlim(0, 10)

            bar_positions = [bar.get_y() + bar.get_height() / 2 for bar in bars2]

            # Plot a line to show the declining trend
            ax2.plot(counts, bar_positions, 'o--', color='blue', zorder=4)

            # Add error bars
            # plt.errorbar(names, mean, xerr=mad, capsize=3, fmt="r--o", ecolor="black")
            # bars[-1].set_height(0.4)
            # bars2[-1].set_height(0.4)

            for bar, value in zip(bars, mean):
                height = bar.get_width()
                ax.text(height + 0.2, bar.get_y() + (bar.get_height() / 2), f'{value:.2f}', ha='left', va='bottom',
                        fontweight='bold')
        else:
            bars = ax.bar(names, mean, edgecolor="black", zorder=2)
            # Add error bars
            plt.errorbar(names, mean, yerr=mad, capsize=3, fmt="r--o", ecolor="black")

            # Annotate each bar with the mean value
            for bar, value in zip(bars, mean):
                height = bar.get_width()
                ax.text(height, bar.get_y() + (bar.get_height() / 2), f'{value:.2f}', ha='left', va='bottom',
                        fontweight='bold')
    if title != "":
        plt.title(title)
    if not is_h:
        plt.ylabel(y_lbl)
        plt.xlabel(x_lbl)
    # else:
        #plt.legend()
        # plt.xlabel(y_lbl)
        # plt.ylabel(x_lbl)
        # plt.xscale('log')

    plt.grid(which='both', axis='x', linestyle='-', zorder=1)
    plt.minorticks_on()
    # plt.legend()
    plt.tight_layout()
    plt.savefig(out_plot_path, bbox_inches='tight')

    return {
        'names': names,
        'means': mean,
        'CVs': cv
    }


def anlz_isolated(isolated_data):
    data = [
        # parse_vm_latency_stats(name='pins_\npcpus_2', raw_d=isolated_data['PIN_1']),
        parse_vm_latency_stats(name='1', raw_d=isolated_data['FLT_1']),
        parse_vm_latency_stats(name='2', raw_d=isolated_data['FLT_2']),
        parse_vm_latency_stats(name='3', raw_d=isolated_data['FLT_3']),
        parse_vm_latency_stats(name='4', raw_d=isolated_data['FLT_4']),
        # parse_vm_latency_stats(name='pins_\npcpus_2', raw_d=isolated_data['PIN_1']),
        # parse_vm_latency_stats(name='floats_\npcpus_1', raw_d=isolated_data['FLT_1']),
        # parse_vm_latency_stats(name='floats_\npcpus_2', raw_d=isolated_data['FLT_2']),
        # parse_vm_latency_stats(name='floats_\npcpus_3', raw_d=isolated_data['FLT_3']),
        # parse_vm_latency_stats(name='floats_\npcpus_4', raw_d=isolated_data['FLT_4']),
    ]
    print("this is isolated experiment data-------------------")
    visualize(data=data,
              # x_lbl="VM (vcpus=2) Core Affinity",
              x_lbl="HVM pCPU Allocation (vCPU = 2)",
              y_lbl="Latency ("r'$\mu$'"s)",
              title="",
              out_plot_path="results/rt-vs-core-affinity.svg",
              type='eb')


def anlz_dynamic(dynamic_data):
    data = [
        parse_vm_latency_stats(name='Harvest\nVM', raw_d=dynamic_data['FLT']),
        parse_vm_latency_stats(name='Proposed', raw_d=dynamic_data['PIN']),
        # parse_vm_latency_stats(name='stable_vm\npcpus_6', raw_d=dynamic_data['PIN']),
        # parse_vm_latency_stats(name='shrinking_hvm\npcpus_6-to-1', raw_d=dynamic_data['FLT'])
    ]
    print("this is dynamic experiment data-------------------")
    r = visualize(data=data,
                  x_lbl="",
                  # x_lbl="VM (vcpus=6) Core Affinity",
                  y_lbl="Latency ("r'$\mu$'"s)",
                  title="",
                  # title="Real-Time Performance with HVM Shrink",
                  out_plot_path="results/rt-vs-hvm-shrink.svg",
                  type='eb', is_h=True)
    stbl_cv = r['CVs'][0]
    dyn_cv = r['CVs'][1]
    increase = ((dyn_cv - stbl_cv) / stbl_cv)
    print("Increase in dyn. for CVs:", str(round(increase, 2)) + 'x')


def analyse(isolated_data, dynamic_data):
    anlz_isolated(isolated_data)
    anlz_dynamic(dynamic_data)
