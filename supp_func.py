import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Palatino Linotype'] + plt.rcParams['font.serif']

plt.rcParams['font.size'] = 25
plt.rcParams['lines.linewidth'] = 3

def plot_selected_columns(df, allowed_columns, max_time, xtick, save_path='plot.png', figsize=(8, 8), min_time=0,
                          legend=False):

    high_contrast_colors = [
        (0, 0, 0, 0.7),
        (1, 0, 0, 0.7),
        (0, 0, 1, 0.7),
        (0, 0.5, 0, 0.7),
        (0.75, 0, 0.75, 0.7),
        (0.75, 0.75, 0, 0.7),
        (0, 0.75, 0.75, 0.7),
        (1, 0.5, 0, 0.7),
        (0.55, 0.27, 0.07, 0.7),
        (0.5, 0, 0.5, 0.7)
    ]

    df = df[(df['Time'] >= min_time) & (df['Time'] <= max_time)]

    plt.figure(figsize=figsize)

    for i, col in enumerate(df.columns[:-1]):
        if col in allowed_columns:

            color = high_contrast_colors[i % len(high_contrast_colors)]
            plt.plot(df['Time'], df[col],
                     label=col,
                     color=color,
                     linewidth=3,
                     alpha=0.7)

    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.spines['left'].set_position(('data', min_time))

    ax.set_xlim([min_time, max_time])

    ax.set_ylim([None, 100])

    xticks = [x for x in range(min_time, max_time + 1, xtick)]
    ax.set_xticks(xticks)

    if legend:
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Выносим легенду за пределы графика

    plt.savefig(save_path, dpi=300, bbox_inches='tight', transparent=True)
    plt.show()