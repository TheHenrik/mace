import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.gaussian_process import GaussianProcessRegressor
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor


parameter_x = "wing_loading"

csv = pd.read_csv("sweep_finished_mit_luecken.csv")
csv = csv[np.isclose(csv["fowler_affected_span"],0,atol=1e-2)]
csv = csv[csv["main_wing_airfoil"] == "LAK24_v2"]
#csv = csv[csv["propeller"] == "freudenthaler14x8"]


print(csv)
X = csv[parameter_x].values.reshape(-1, 1)

# fit = LinearRegression().fit(csv["payload"].values.reshape(-1, 1), csv["take_off_length"].values.reshape(-1, 1))
# fit = GaussianProcessRegressor().fit(csv["payload"].values.reshape(-1, 1), csv["take_off_length"].values.reshape(-1, 1))
# fit = GradientBoostingRegressor().fit(csv["payload"].values.reshape(-1, 1), csv["take_off_length"].values.reshape(-1, 1))
# fit = DecisionTreeRegressor().fit(csv["payload"].values.reshape(-1, 1), csv["take_off_length"].values.reshape(-1, 1))
fit = SVR(kernel='poly', degree=2).fit(csv[parameter_x].values.reshape(-1, 1), csv["take_off_length"].values.reshape(-1, 1))
fit = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500).fit(X, csv["take_off_length"].values.reshape(-1, 1))

plt.scatter(csv[parameter_x], csv["take_off_length"])

X = np.linspace(2, 15, 100)
Y = fit.predict(X.reshape(-1, 1))
plt.plot(X, Y, linestyle="--", color="red")

plt.show()
