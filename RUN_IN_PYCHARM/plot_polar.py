import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from mace.utils.file_path import root
from mace.aero.implementations.airfoil_analyses import Airfoil
from mace.utils.mesh import get_profil_thickness
import os

tool_path = root()
airfoil_surrogate_path = Path(tool_path, "data", "surrogates")

airfoils = ['ag45c', 'acc24p']
airfoil_name_plot = ['AG45c', 'Xoptfoil2 optimized Airfoil']
colors = ['blue', 'green']
linestyles = [(0, (3, 1, 1, 1)), (5, (10, 3))]
markers = ['o', 'v']
markersizes = [6, 6]
re = 400_000
flap_setting = 0

global_cl_max = 0
global_cl_min = 0

for j, airfoil_name in enumerate(airfoils):
    foil = Airfoil(airfoil_name, flap_angle=flap_setting)
    cl_max = foil.get_cl_max(re)
    cl_min = -0.1
    cl_vec = np.linspace(cl_min, cl_max, 100)
    cd_vec = np.zeros_like(cl_vec)

    global_cl_max = max(global_cl_max, cl_max)
    global_cl_min = min(global_cl_min, cl_min)

    for i, cl in enumerate(cl_vec):
        cd_vec[i] = foil.get_cd(re, cl)
    plt.plot(cd_vec, cl_vec, label=airfoil_name_plot[j], linewidth=1.5, color=colors[j], alpha=1, linestyle=linestyles[j], marker=markers[j], markersize=markersizes[j], markevery=8, fillstyle='none')

    thickness_to_chord = get_profil_thickness(airfoil_name)
    print(f'{airfoil_name}: {thickness_to_chord}')


plt.grid()
plt.ylim([global_cl_min, global_cl_max])
plt.xlim([0, 0.04])
plt.ylim([0, 1.6])
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)


from matplotlib import font_manager, rcParams
font_path = "/Users/jannik/Library/Fonts/NewCMMath-Book.otf"
font_prop = font_manager.FontProperties(fname=font_path, size=15)

import os
print(os.environ['PATH'])
os.environ['PATH'] = '/Library/TeX/texbin:' + os.environ['PATH']

# Setze die Schriftart in den rcParams für den gesamten Text und den Mathematikmodus
plt.rcParams['text.usetex'] = True  # Aktiviert LaTeX für Text und Mathematik
plt.rcParams['font.family'] = font_prop.get_name()  # Setze die Schriftart
plt.rcParams['text.latex.preamble'] = r'\usepackage{amsmath}'  # Optional: um mehr mathematische Funktionen zu verwenden


plt.xticks(fontsize=12, fontproperties=font_prop)
plt.yticks(fontsize=12, fontproperties=font_prop)
plt.xlabel(r"$C_d$", fontproperties=font_prop)
plt.ylabel(r'$C_l$', fontproperties=font_prop)
plt.legend(facecolor='white', edgecolor='black', framealpha = 1, fontsize=14, prop=font_prop)
plt.savefig('airfoil_comparison.pdf')
plt.show()