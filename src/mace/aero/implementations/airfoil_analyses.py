import os
import numpy as np
import mace.aero.implementations.xfoil.xfoilpolars as xfoilpolars
from pathlib import Path

class Airfoil:
    """
    This class is used for analyzing airfoils
    """ 
    def __init__(self, foil_name: str, flap_angle: float = 0, use_opt_flap_setting: bool = False, x_hinge: float = 0.75, z_hinge: float = 0.):
        """
         Initialize the airfoil
        :param foil_name: Name of the airfoil. 
        The airfoil must be located in the data/airfoils folder, 
        and the name must be the same as the file name.
        """
        tool_path = Path(__file__).resolve().parents[4]
        self.airfoil_path = os.path.join(tool_path, "data", "airfoils", foil_name + ".dat")

        if use_opt_flap_setting:
            self.surrogate_path = os.path.join(tool_path, "data", "surrogates",
                                               foil_name
                                               +"_"
                                               +str(int(round((100-x_hinge*100),0)))
                                               +"f"+
                                               "opt.csv")
        elif np.isclose(flap_angle, 0):
            self.surrogate_path = os.path.join(tool_path, "data", "surrogates",
                                               foil_name
                                               +".csv")
        else:
            self.surrogate_path = os.path.join(tool_path, "data", "surrogates",
                                               foil_name
                                               +"_"
                                               +str(int(round((100-x_hinge*100),0)))
                                               +"f"+
                                               str(int(round(flap_angle,0)))+".csv")

        self.foil_name = foil_name

        self.re_min = 2e4
        self.re_max = 1e6
        self.re_step = 5e4
        self.re_list = np.arange(self.re_min, self.re_max, self.re_step)

        self.alpha_min = -10
        self.alpha_max = 15
        self.alpha_step = 0.1

        self.mach = 0
        self.n_crit = 9
        self.n_iter = 150
        self.xtr_top = 100
        self.xtr_bot = 100

        self.flap_angle = flap_angle
        self.x_hinge = 0.75
        self.z_hinge = 0.
        
        self.print_re_warnings = True
        self.must_rebuild_surrogate = False
        self.use_opt_flap_setting = use_opt_flap_setting
        self.flap_angle_list = np.arange(-4, 12, 2)

    def build_single_flap_surrogate(self):
        """
        This function builds a surrogate model for the airfoil
        """

        re_list = self.re_list

        alpha_min = self.alpha_min
        alpha_max = self.alpha_max

        header = ["RE", "ALPHA", "CL", "CD", "CDP", "CM", "TOP_XTR", "BOT_XTR"]
        polar_data = np.array([])

        for i, re in enumerate(re_list):
            if alpha_min < 0:
                neg_polar_data = xfoilpolars.get_xfoil_polar(self.airfoil_path, reynoldsnumber=re, alfa_start=0,
                                                     alfa_end=self.alpha_min, alfa_step=self.alpha_step, mach=self.mach,
                                                     n_crit=self.n_crit, n_iter=self.n_iter,
                                                     x_transition_top=self.xtr_top, x_transition_bottom=self.xtr_bot,
                                                     flap_angle=self.flap_angle, x_hinge=self.x_hinge, z_hinge=self.z_hinge)
                # cut polar
                if np.ndim(neg_polar_data) == 2:
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
                                                     x_transition_top=self.xtr_top, x_transition_bottom=self.xtr_bot,
                                                     flap_angle=self.flap_angle, x_hinge=self.x_hinge, z_hinge=self.z_hinge)
                # cut polar
                cl_max_index = np.argmax(pos_polar_data[:, 1])
                pos_polar_data = pos_polar_data[:cl_max_index+1, :]
            else:
                pos_polar_data = np.array([])

            if np.ndim(neg_polar_data) == 2:
                actual_re_polar_data = np.concatenate((neg_polar_data, pos_polar_data), axis=0)
            else:
                actual_re_polar_data = pos_polar_data
            actual_re_polar_data = np.hstack((re*np.ones((actual_re_polar_data.shape[0], 1)), actual_re_polar_data))

            if i == 0:
                polar_data = actual_re_polar_data
            else:
                polar_data = np.concatenate((polar_data, actual_re_polar_data), axis=0)

        np.savetxt(self.surrogate_path, polar_data, fmt='%.6f', delimiter=",", header=" ".join(header), comments="")

    def build_optimized_flap_surrogate(self):
        """
        This function builds a surrogate model with a single polar where the flap angle is optimized for each
        reynolds number and lift coefficient
        """
        header = ["RE", "ALPHA", "CL", "CD", "CDP", "CM", "TOP_XTR", "BOT_XTR"]
        flap_angle_list = self.flap_angle_list
        surrogate_path = self.surrogate_path
        polar_data = np.array([])
        tool_path = Path(__file__).resolve().parents[4]

        for i, flap_angle in enumerate(flap_angle_list):
            self.surrogate_path = os.path.join(tool_path, "data", "surrogates",
                                               self.foil_name
                                               +"_"
                                               +str(int(round((100-self.x_hinge*100),0)))
                                               +"f"+
                                               str(int(round(flap_angle,0)))+".csv")
            self.flap_angle = flap_angle
            if not self.check_for_surrogate() or self.must_rebuild_surrogate:
                self.build_single_flap_surrogate()
            if i == 0:
                polar_data = [np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1)]
            else:
                polar_data.append(np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1))

        for re in self.re_list:
            for i, flap_angle in enumerate(flap_angle_list):
                if i == 0:
                    polar_data_re = [polar_data[i][np.where(polar_data[i][:, 0] == re)[0], :]]
                else:
                    polar_data_re.append(polar_data[i][np.where(polar_data[i][:, 0] == re)[0], :]) #= [polar_data_re, polar_data[i][np.where(polar_data[i][:, 0] == re)[0], :]]
                if flap_angle == min(flap_angle_list):
                    cl_min = min(polar_data_re[i][:, 2])
                elif flap_angle == max(flap_angle_list):
                    cl_max = max(polar_data_re[i][:, 2])
            cl_list = np.arange(cl_min, cl_max, 0.05)
            print("Reynolds number: ", re)
            print("Lift coefficient list: ", cl_list)
            for cl in cl_list:
                cd = 1.
                for i, flap_angle in enumerate(flap_angle_list):
                    current_cd = np.interp(cl, polar_data_re[i][:, 2], polar_data_re[i][:, 3], right=1., left=1.)
                    if current_cd < cd:
                        alpha = np.interp(cl, polar_data_re[i][:, 2], polar_data_re[i][:, 1])
                        cd = current_cd
                        cdp = np.interp(cl, polar_data_re[i][:, 2], polar_data_re[i][:, 4])
                        cm = np.interp(cl, polar_data_re[i][:, 2], polar_data_re[i][:, 5])
                        top_xtr = np.interp(cl, polar_data_re[i][:, 2], polar_data_re[i][:, 6])
                        bot_xtr = np.interp(cl, polar_data_re[i][:, 2], polar_data_re[i][:, 7])
                if cl == cl_min and re == self.re_list[0]:
                    res_polar_data = np.array([re, alpha, cl, cd, cdp, cm, top_xtr, bot_xtr])
                else:
                    res_polar_data = np.vstack((res_polar_data, np.array([re, alpha, cl, cd, cdp, cm, top_xtr, bot_xtr])))

        self.surrogate_path = surrogate_path
        np.savetxt(self.surrogate_path, res_polar_data, fmt='%.6f', delimiter=",", header=" ".join(header), comments="")

    def check_for_best_flap_setting(self, re: float, cl: float) -> int:
        flap_angle_list = self.flap_angle_list
        original_flap_angle = self.flap_angle
        original_surrogate_path = self.surrogate_path
        tool_path = Path(__file__).resolve().parents[4]

        for i, flap_angle in enumerate(flap_angle_list):
            self.surrogate_path = os.path.join(tool_path, "data", "surrogates",
                                               self.foil_name
                                               + "_"
                                               + str(int(round((100 - self.x_hinge * 100), 0)))
                                               + "f" +
                                               str(int(round(flap_angle, 0))) + ".csv")
            self.flap_angle = flap_angle
            if i == 0:
                cd = self.get_cd(re, cl)
                best_flap_angle = flap_angle
            else:
                if cd > self.get_cd(re, cl):
                    best_flap_angle = flap_angle
                    cd = self.get_cd(re, cl)

        self.flap_angle = original_flap_angle
        self.surrogate_path = original_surrogate_path
        return best_flap_angle

    def build_surrogate(self):
        """
        This function calls either the build_single_flap_surrogate or the build_optimized_flap_surrogate function
        """
        if self.use_opt_flap_setting == False:
            self.build_single_flap_surrogate()
        else:
            self.build_optimized_flap_surrogate()

    def check_for_surrogate(self):
        """
        This function checks if a surrogate model exists for the airfoil
        """
        # TODO: Check if surrogate fits Ncrit and Mach number
        return os.path.isfile(self.surrogate_path)

    def get_cd(self, re: float, cl: float) -> float:
        """
        This function evaluates the airfoil at a given reynolds number and cl and returns the drag coefficient
        """
        if not self.check_for_surrogate() or self.must_rebuild_surrogate:
            self.build_surrogate()

        polar_data = np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1)
        
        re_list = np.unique(polar_data[:, 0])
        
        if re > re_list[-1]:
            if self.print_re_warnings:
                print("Warning: Airfoil: %s -> Re=%.0f above max Re in surrogate model" % (self.foil_name, re))
            re = re_list[-1]
        upper_re = re_list[np.where(re_list >= re)[0][0]]
        if np.where(re_list >= re)[0][0] == 0:
            lower_re = re_list[np.where(re_list >= re)[0][0]]
            if self.print_re_warnings:
                print("Warning: Airfoil: %s -> Re=%.0f below min Re in surrogate model" % (self.foil_name, re))
        else:
            lower_re = re_list[np.where(re_list >= re)[0][0] - 1]

        polar_data_upper = polar_data[np.where(polar_data[:, 0] == upper_re)[0], :]
        polar_data_lower = polar_data[np.where(polar_data[:, 0] == lower_re)[0], :]

        CDv_upper = np.interp(cl, polar_data_upper[:, 2], polar_data_upper[:, 3], left=1., right=1.)
        CDv_lower = np.interp(cl, polar_data_lower[:, 2], polar_data_lower[:, 3], left=1., right=1.)

        CD = np.interp(re, [lower_re, upper_re], [CDv_lower, CDv_upper])

        return CD

    def get_cl_max(self, re: float) -> float:
        """
        This function evaluates the airfoil at a given reynolds number and returns the maximum cl
        """
        if not self.check_for_surrogate() or self.must_rebuild_surrogate:
            self.build_surrogate()

        polar_data = np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1)

        re_list = np.unique(polar_data[:, 0])

        if re > re_list[-1]:
            if self.print_re_warnings:
                print("Warning: Airfoil: %s -> Re=%.0f above max Re in surrogate model" % (self.foil_name, re))
            re = re_list[-1]
        upper_re = re_list[np.where(re_list >= re)[0][0]]
        if np.where(re_list >= re)[0][0] == 0:
            lower_re = re_list[np.where(re_list >= re)[0][0]]
            if self.print_re_warnings:
                print("Warning: Airfoil: %s -> Re=%.0f below min Re in surrogate model" % (self.foil_name, re))
        else:
            lower_re = re_list[np.where(re_list >= re)[0][0] - 1]

        polar_data_upper = polar_data[np.where(polar_data[:, 0] == upper_re)[0], :]
        polar_data_lower = polar_data[np.where(polar_data[:, 0] == lower_re)[0], :]

        cl_max_upper = np.max(polar_data_upper[:, 2])
        cl_max_lower = np.max(polar_data_lower[:, 2])

        cl_max = np.interp(re, [lower_re, upper_re], [cl_max_lower, cl_max_upper])

        return cl_max

    def get_cl_min(self, re: float) -> float:
        """
        This function evaluates the airfoil at a given reynolds number and returns the minium cl
        """
        if not self.check_for_surrogate() or self.must_rebuild_surrogate:
            self.build_surrogate()

        polar_data = np.loadtxt(self.surrogate_path, delimiter=",", skiprows=1)

        re_list = np.unique(polar_data[:, 0])

        if re > re_list[-1]:
            if self.print_re_warnings:
                print("Warning: Airfoil: %s -> Re=%.0f above max Re in surrogate model" % (self.foil_name, re))
            re = re_list[-1]
        upper_re = re_list[np.where(re_list >= re)[0][0]]
        if np.where(re_list >= re)[0][0] == 0:
            lower_re = re_list[np.where(re_list >= re)[0][0]]
            if self.print_re_warnings:
                print("Warning: Airfoil: %s -> Re=%.0f below min Re in surrogate model" % (self.foil_name, re))
        else:
            lower_re = re_list[np.where(re_list >= re)[0][0] - 1]

        polar_data_upper = polar_data[np.where(polar_data[:, 0] == upper_re)[0], :]
        polar_data_lower = polar_data[np.where(polar_data[:, 0] == lower_re)[0], :]

        cl_min_upper = np.min(polar_data_upper[:, 2])
        cl_min_lower = np.min(polar_data_lower[:, 2])

        cl_min = np.interp(re, [lower_re, upper_re], [cl_min_lower, cl_min_upper])

        return cl_min

if __name__ == "__main__":

    ag19 = Airfoil("ag19", use_opt_flap_setting=True)
    ag19.flap_angle_list = np.array([0, 6])
    ag19.must_rebuild_surrogate = True
    ag19.re_list = np.array([100000, 200000])

    CD = ag19.get_cd(136000, 1.0)
    print('CD:     %.3e' % CD)


