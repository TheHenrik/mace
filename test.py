from pathlib import Path
import scipy
import matplotlib.pyplot as plt
import mace
from scipy.interpolate import griddata
import numpy as np

if __name__ == '__main__':
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    # Plot erstellen
    plt.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Matplotlib Test')
    plt.show()