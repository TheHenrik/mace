import os
import numpy as np
import mace.aero.implementations.xfoil.xfoilpolars as xfoilpolars
from pathlib import Path

class Airfoil:
    # This class is used for analyzing airfoils
    def __init__(self, foil_name):
        # Initialize the airfoil
        tool_path = Path(__file__).resolve().parents[4]
        self.airfoil_path = os.path.join(tool_path, "data", "airfoils", foil_name+".dat")
        self.surrogate_path = os.path.join(tool_path, "data", "surrogates", foil_name+".csv")
        self.foil_name = foil_name

        self.re_min = 5e4
        self.re_max = 1e6
        self.re_step = 5e4

        self.alpha_min = -10
        self.alpha_max = 15
        self.alpha_step = 0.1

        self.mach = 0
        self.n_crit = 9
        self.n_iter = 100
        self.xtr_top = 100
        self.xtr_bot = 100

        self.must_rebuild_surrogate = False

    def build_surrogate(self):
        # This function builds a surrogate model for the airfoil
        re_list = np.arange(self.re_min, self.re_max, self.re_step)

        alpha_min = self.alpha_min
        alpha_max = self.alpha_max

        header = ["RE", "ALPHA", "CL", "CD", "CDP", "CM", "TOP_XTR", "BOT_XTR"]
        polar_data = np.array([])

        for i, re in enumerate(re_list):
            if alpha_min < 0:
                neg_polar_data = xfoilpolars.get_xfoil_polar(self.airfoil_path, reynoldsnumber=re, alfa_start=0,
                                                     alfa_end=self.alpha_min, alfa_step=self.alpha_step, mach=self.mach,
                                                     n_crit=self.n_crit, n_iter=self.n_iter,
                                                     x_transition_top=self.xtr_top, x_transition_bottom=self.xtr_bot)
                # cut polar
                cl_min_index = np.argmin(neg_polar_data[:, 1])
                neg_polar_data = neg_polar_data[:cl_min_index, :]
                # flip polar to make it attachable to the positive polar
                neg_polar_data = np.flip(neg_polar_data, axis=0)
            else:
                neg_polar_data = np.array([])

            if alpha_max > 0:
                pos_polar_data = xfoilpolars.get_xfoil_polar(self.airfoil_path, reynoldsnumber=re, alfa_start=0,
                                                     alfa_end=self.alpha_max, alfa_step=self.alpha_step, mach=self.mach,
                                                     n_crit=self.n_crit, n_iter=self.n_iter,
                                                     x_transition_top=self.xtr_top, x_transition_bottom=self.xtr_bot)
                # cut polar
                cl_max_index = np.argmax(pos_polar_data[:, 1])
                pos_polar_data = pos_polar_data[:cl_max_index+1, :]
            else:
                pos_polar_data = np.array([])

            actual_re_polar_data = np.concatenate((neg_polar_data, pos_polar_data), axis=0)
            actual_re_polar_data = np.hstack((re*np.ones((actual_re_polar_data.shape[0], 1)), actual_re_polar_data))

            if i == 0:
                polar_data = actual_re_polar_data
            else:
                polar_data = np.concatenate((polar_data, actual_re_polar_data), axis=0)

        np.savetxt(self.surrogate_path, polar_data, fmt='%.6f', delimiter=",", header=" ".join(header), comments="")

    def check_for_surrogate(self):
        # This function checks if a surrogate model exists for the airfoil
        # TODO: Check if surrogate fits Ncrit and Mach number
        return os.path.isfile(self.surrogate_path)

    def get_cd(self, re, cl):
        # This function evaluates the airfoil at a given reynolds number and cl
        if not self.check_for_surrogate() or self.must_rebuild_surrogate:
            self.build_surrogate()

        polar_data = np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1)
        
        re_list = np.unique(polar_data[:, 0])
        
        if re > re_list[-1]:
            print("Warning: Reynolds number is above the maximum reynolds number in the surrogate model")
            re = re_list[-1]
        upper_re = re_list[np.where(re_list >= re)[0][0]]
        if np.where(re_list >= re)[0][0] == 0:
            lower_re = re_list[np.where(re_list >= re)[0][0]]
            print("Warning: Reynolds number is below the minimum reynolds number in the surrogate model")
        else:
            lower_re = re_list[np.where(re_list >= re)[0][0] - 1]

        polar_data_upper = polar_data[np.where(polar_data[:, 0] == upper_re)[0], :]
        polar_data_lower = polar_data[np.where(polar_data[:, 0] == lower_re)[0], :]

        CDv_upper = np.interp(cl, polar_data_upper[:, 2], polar_data_upper[:, 3])
        CDv_lower = np.interp(cl, polar_data_lower[:, 2], polar_data_lower[:, 3])

        CD = np.interp(re, [lower_re, upper_re], [CDv_lower, CDv_upper])

        return CD

    def get_cl_max(self, re):
        # This function evaluates the airfoil at a given reynolds number and cl
        if not self.check_for_surrogate() or self.must_rebuild_surrogate:
            self.build_surrogate()

        polar_data = np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1)

        re_list = np.unique(polar_data[:, 0])

        if re > re_list[-1]:
            print("Warning: Reynolds number is above the maximum reynolds number in the surrogate model")
            re = re_list[-1]
        upper_re = re_list[np.where(re_list >= re)[0][0]]
        if np.where(re_list >= re)[0][0] == 0:
            lower_re = re_list[np.where(re_list >= re)[0][0]]
            print("Warning: Reynolds number is below the minimum reynolds number in the surrogate model")
        else:
            lower_re = re_list[np.where(re_list >= re)[0][0] - 1]

        polar_data_upper = polar_data[np.where(polar_data[:, 0] == upper_re)[0], :]
        polar_data_lower = polar_data[np.where(polar_data[:, 0] == lower_re)[0], :]

        cl_max_upper = np.max(polar_data_upper[:, 2])
        cl_max_lower = np.max(polar_data_lower[:, 2])

        cl_max = np.interp(re, [lower_re, upper_re], [cl_max_lower, cl_max_upper])

        return cl_max

if __name__ == "__main__":

    ag19 = Airfoil("ag19")

    ag19.re_min = 20000.
    ag19.re_max = 500000.
    ag19.re_step = 30000.

    ag19.alpha_min = -5
    ag19.alpha_max = 10
    ag19.alpha_step = 0.1

    CD = ag19.get_cd(100000, 1.0)
    CL_max = ag19.get_cl_max(100000)

    print('CL_max: %.3e' % CL_max)
    print('CD:     %.3e' % CD)
