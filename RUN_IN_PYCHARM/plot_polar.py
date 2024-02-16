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

airfoils = ['LAK24_v1', 'acc24', 'acc24cl']
re = 300_000
flap_setting = 0

global_cl_max = 0
global_cl_min = 0

for airfoil_name in airfoils:
    foil = Airfoil(airfoil_name, flap_angle=flap_setting)
    cl_max = foil.get_cl_max(re)
    cl_min = foil.get_cl_min(re)
    cl_vec = np.linspace(cl_min, cl_max, 100)
    cd_vec = np.zeros_like(cl_vec)

    global_cl_max = max(global_cl_max, cl_max)
    global_cl_min = min(global_cl_min, cl_min)

    for i, cl in enumerate(cl_vec):
        cd_vec[i] = foil.get_cd(re, cl)
    plt.plot(cd_vec, cl_vec, label=airfoil_name)

    thickness_to_chord = get_profil_thickness(airfoil_name)
    print(f'{airfoil_name}: {thickness_to_chord}')


plt.grid()
plt.ylim([global_cl_min, global_cl_max])
plt.xlim([0, 0.05])
plt.xlabel(r'$c_d$')
plt.ylabel(r'$c_l$')
plt.legend()
plt.show()