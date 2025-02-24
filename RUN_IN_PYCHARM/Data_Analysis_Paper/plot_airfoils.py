import matplotlib.pyplot as plt
import numpy as np

from matplotlib import font_manager, rcParams
font_path = "/Users/jannik/Library/Fonts/NewCMMath-Book.otf"
font_prop = font_manager.FontProperties(fname=font_path, size=11)
def plot_airfoils(file1, file2):
    """
    Plots two airfoils from .dat files overlaid in a single plot.

    Parameters:
    - file1: str, path to the first airfoil .dat file
    - file2: str, path to the second airfoil .dat file
    """
    def load_airfoil(filepath):
        """
        Loads airfoil coordinates from a .dat file.

        Parameters:
        - filepath: str, path to the .dat file

        Returns:
        - tuple of two lists: (x_coords, y_coords)
        """
        with open(filepath, 'r') as f:
            lines = f.readlines()
        # Skip the first line (title or metadata), parse the rest
        data = [list(map(float, line.split())) for line in lines[1:] if line.strip()]
        x_coords, y_coords = zip(*data)  # Unpack into x and y
        return x_coords, y_coords

    # Load airfoil data
    x1, y1 = load_airfoil(file1)
    x2, y2 = load_airfoil(file2)

    # Plot the airfoils
    fig = plt.figure(figsize=(10, 1.6))
    # linewidth=1.5, color=colors[j], alpha=1, linestyle=linestyles[j], marker=markers[j], markersize=markersizes[j], markevery=8, fillstyle='none'
    # airfoils = ['ag45c', 'acc24p']
    # airfoil_name_plot = ['AG45c', 'Xoptfoil2 optimized Airfoil']
    # colors = ['blue', 'green']
    # linestyles = [(0, (3, 1, 1, 1)), (5, (10, 3))]
    # markers = ['o', 'v']
    # markersizes = [6, 6]
    plt.plot(x2, y2, label='AG45c', linewidth=1, linestyle=(0, (3, 1, 1, 1)), color='blue', marker='o', markersize=6, fillstyle='none', markevery=10)
    plt.plot(x1, y1, label='Xoptfoil2 optimized Airfoil', linewidth=1, linestyle=(5, (10, 3)), color = 'green', marker='v', markersize=6, fillstyle='none', markevery=10)

    plt.xlabel('x/c', fontproperties=font_prop)
    plt.ylabel('y/c', fontproperties=font_prop)
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.axvline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(np.arange(0, 1.01, 0.1), fontproperties=font_prop)
    plt.yticks(np.arange(-0.5, 0.51, 0.1), fontproperties=font_prop)
    plt.tick_params(axis='y', left=False)
    plt.tick_params(axis='x', bottom=False)
    plt.gca().set_yticklabels([])  # Entfernt nur die Beschriftungen der y-Ticks
    #plt.gca().set_xticklabels([])  # Entfernt nur die Beschriftungen der x-Ticks
    plt.xlim((0, 1))
    #plt.legend(loc='upper right', prop=font_prop)
    plt.axis('equal')  # Ensure the aspect ratio is equal for proper comparison
    fig.tight_layout()
    plt.savefig('airfoil_geometry.pdf', format='pdf')
    plt.show()


file_path1 = '/Users/jannik/Documents/GitHub/mace/data/airfoils/acc24p.dat'
file_path2 = '/Users/jannik/Documents/GitHub/mace/data/airfoils/ag45c.dat'
plot_airfoils(file_path1, file_path2)