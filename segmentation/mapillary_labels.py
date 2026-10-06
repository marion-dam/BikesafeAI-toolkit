import json
import os

import matplotlib.pyplot as plt
import numpy as np


def semantic_colormap():
    return np.asarray([
        [165, 42, 42],
        [0, 192, 0],
        [196, 196, 196],
        [190, 153, 153],
        [180, 165, 180],
        [102, 102, 156],
        [102, 102, 156],
        [128, 64, 255],
        [140, 140, 200],
        [170, 170, 170],
        [250, 170, 160],
        [96, 96, 96],
        [230, 150, 140],
        [128, 64, 128],
        [110, 110, 110],
        [244, 35, 232],
        [150, 100, 100],
        [70, 70, 70],
        [150, 120, 90],
        [220, 20, 60],
        [255, 0, 0],
        [255, 0, 0],
        [255, 0, 0],
        [200, 128, 128],
        [255, 255, 255],
        [64, 170, 64],
        [128, 64, 64],
        [70, 130, 180],
        [255, 255, 255],
        [152, 251, 152],
        [107, 142, 35],
        [0, 170, 30],
        [255, 255, 128],
        [250, 0, 30],
        [0, 0, 0],
        [220, 220, 220],
        [170, 170, 170],
        [222, 40, 40],
        [100, 170, 30],
        [40, 40, 40],
        [33, 33, 33],
        [170, 170, 170],
        [0, 0, 142],
        [170, 170, 170],
        [210, 170, 100],
        [153, 153, 153],
        [128, 128, 128],
        [0, 0, 142],
        [250, 170, 30],
        [192, 192, 192],
        [220, 220, 0],
        [180, 165, 180],
        [119, 11, 32],
        [0, 0, 142],
        [0, 60, 100],
        [0, 0, 142],
        [0, 0, 90],
        [0, 0, 230],
        [0, 80, 100],
        [128, 64, 64],
        [0, 0, 110],
        [0, 0, 70],
        [0, 0, 192],
        [32, 32, 32],
        [0, 0, 0],
        [0, 0, 0],
    ])


def plot_semantic_legend(config_path: str=None, visualize: bool=False, output_path: str=None):
    if config_path is None:
        return
    if not os.path.exists(config_path):
        raise FileNotFoundError(config_path)
    with open(config_path) as config_file:
        config = json.load(config_file)

    labels = config['labels']

    print("There are {} labels in the config file".format(len(labels)))

    label_names = []
    label_colors = []

    for label_id, label in enumerate(labels):
        label_names.append(label["readable"])
        # Convert RGB values to a valid color specification
        label_colors.append('#{:02x}{:02x}{:02x}'.format(label["color"][0], label["color"][1], label["color"][2]))

    # Create a dummy plot to add legend
    plt.figure(figsize=(8, 6))

    # Plot a single point to represent each label with its color
    for name, color in zip(label_names, label_colors):
        plt.scatter([], [], color=color, label=name)

    # Hide the axis ticks and labels
    plt.gca().axes.get_xaxis().set_visible(False)
    plt.gca().axes.get_yaxis().set_visible(False)

    # Add legend
    plt.legend(loc='center', title='Legend', fontsize='small', ncol=5)

    # Show the plot
    plt.tight_layout()
    if output_path is not None:
        plt.savefig(os.path.join(output_path, 'legend.png'))
    if visualize:
        plt.show()
    return os.path.join(output_path, 'legend.png')


# plot_semantic_legend()
