from mace.aero.implementations.xfoil.xfoilpolars import get_xfoil_polar
import numpy as np

ncrit = 8
res = np.linspace(8e4, 5e5, num=100)
alfa_min = -5
alfa_max = 10
num_alfa = 100
alfa_step = (alfa_max - alfa_min) / num_alfa
airfoil_path = '../data/airfoils/ag40.dat'
import time
time1 = time.time()
for re in res:
    get_xfoil_polar(
                        airfoil_path,
                        reynoldsnumber=re,
                        alfa_start=0,
                        alfa_end=alfa_min,
                        alfa_step=alfa_step,
                        n_crit=ncrit,
                    )
    get_xfoil_polar(
                        airfoil_path,
                        reynoldsnumber=re,
                        alfa_start=0,
                        alfa_end=alfa_max,
                        alfa_step=alfa_step,
                        n_crit=ncrit,
                    )
time2 = time.time()
print(time2-time1)