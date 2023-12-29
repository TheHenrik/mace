import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import RegularGridInterpolator

# Beispiel: Wing loading x Wing Area

dir_path = "aka_v9.csv"
plot_type = "2d"  # options: 2d, meshgrid, trisurf, contourf
x_name = "mass_payload"
y_name = "main_wing_airfoil"  # in 2d this is separate lines
z_name = "score_round"  # in 2d this is y-axis
cmap = "viridis_r"
sep = ","
interpol = False
show_plots = True
zlim = [0, 0]
constant_parameters = {  # "num_fowler_segments": 4,
    #"mass_payload": 4.25,
    #"wing_area": 0.65,
    #"aspect_ratio": 10.,
    # "fowler_affected_area_ratio": 0,
    # "propeller": "freudenthaler14x8",
    # "main_wing_airfoil": "LAK24_v1",
}


def plot_function(
    df, x_name, y_name, z_name, plot_type, cmap, dir_path, file_name, show=False
):

    # set the X, Y, Z coordinates for plotting
    x_data = df[x_name].to_numpy()
    y_data = df[y_name].to_numpy()
    z_data = df[z_name].to_numpy()

    x_dimension = np.unique(x_data)
    y_dimension = np.unique(y_data)

    X, Y = np.meshgrid(x_dimension, y_dimension)
    Z = np.empty([len(y_dimension), len(x_dimension)])

    for i, y in enumerate(y_dimension):
        for j, x in enumerate(x_dimension):
            index = np.where((x_data == x) & (y_data == y))
            if len(index[0]) > 1:
                raise ValueError(
                    "More than one occasion found. Multiple datasets present."
                )
            elif len(index[0]) == 0:
                Z[i][j] = np.nan
            else:
                Z[i][j] = z_data[index[0][0]]

    print(np.rint(Z))

    if plot_type == "2d":
        # create the figure to plot
        fig = plt.figure(z_name)
        ax = plt.subplot(1, 1, 1)
        for i, y in enumerate(y_dimension):
            xy = np.array([X[i, :], Z[i, :]])
            xy = xy[:, ~np.isnan(xy).any(axis=0)]
            ax.plot(xy[0, :], xy[1, :], label=y_name + " = " + str(y), marker="x")
            plt.legend()
        ax.set_xlabel(x_name)
        ax.set_ylabel(z_name)
        ax.set_ylim([500, 2500])
        plt.grid()
        plt.savefig(dir_path + "/" + file_name + "_" + z_name + ".png")
    elif plot_type == "contourf":
        # create the figure to plot
        if interpol is True:
            interp = RegularGridInterpolator((X, Y), Z.T, method="cubic")

            x_int_vec = np.linspace(min(x_data), max(x_data), 100)
            y_int_vec = np.linspace(min(y_data), max(y_data), 100)
            X, Y = np.meshgrid(x_int_vec, y_int_vec)
            Z = np.empty([len(x_int_vec), len(y_int_vec)])


            for i, x in enumerate(x_int_vec):
                for j, y in enumerate(y_int_vec):
                    Z[j, i] = interp([x, y]).T
                    # Zd[j, i] = interpn((machs, altitudes), Z.T, [ma, alt], method="linear")

        fig = plt.figure(z_name)
        ax = plt.subplot(1, 1, 1)
        CS = ax.contourf(X, Y, Z, cmap=cmap)
        C = ax.contour(X, Y, Z, colors="black", linewidths=0.5)
        ax.clabel(CS, inline=1, fontsize=10)
        plt.colorbar(CS, label='Competition Score')
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        #plt.savefig(dir_path + "/" + file_name + "_" + z_name + ".png")
    else:
        # create the figure to plot
        fig = plt.figure(z_name)
        ax = fig.add_subplot(111, projection="3d")
        if plot_type == "meshgrid":
            surf = ax.plot_surface(X, Y, Z, cmap=cmap, lw=0.5, rstride=1, cstride=1)
        elif plot_type == "trisurf":
            surf = ax.plot_trisurf(x_data, y_data, z_data, cmap=cmap)
        ax.set_xlabel(x_name)
        ax.set_ylabel(y_name)
        ax.set_zlabel(z_name)
        ax.set_proj_type("ortho")
        if zlim != [0, 0]:
            ax.set_zlim(zlim)
        cbaxes = fig.add_axes(
            [0.9, 0.2, 0.02, 0.6]
        )  # x-pos, y-pos, width, height -> measured from bottom left corner
        fig.colorbar(surf, shrink=0.5, cax=cbaxes)
        # for i in range(4):
        # ax.view_init(elev=30, azim=45 + i*90)
        # plt.savefig(dir_path + '/' + file_name + '_' + z_name + '_view_' + str(i) + '.png')

    # display the figure for the user
    if show:
        plt.show()

    # TODO print out/save the figure


dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir_path)
df = pd.read_csv(dir_path, sep=sep)
file_name = dir_path.rsplit("/", 1)[-1].split(".")[0]

dir_path = os.path.join(dir_path.rsplit("/", 1)[0], "plots")
Path(dir_path).mkdir(exist_ok=True)

for key, value in constant_parameters.items():
    if type(value) == str:
        df = df[df[key] == value]
    else:
        df = df[np.isclose(df[key], value, rtol=1e-03)]

df = df[df["score_round"] > 0.0]
#df = df[df["wing_loading"] < 9.6]
if z_name == "all":
    cols = list(df.columns)
    cols = cols[2:]
    num_cols = len(cols)
    cols.remove(x_name)
    cols.remove(y_name)
    for col in cols:
        plot_function(
            df, x_name, y_name, col, plot_type, cmap, dir_path, file_name, show_plots
        )
else:
    plot_function(
        df, x_name, y_name, z_name, plot_type, cmap, dir_path, file_name, show_plots
    )
