import matplotlib.pyplot as plt
import numpy as np

# Daten ohne "Efficiency"
parameter_names = [r'$C_{l,max}$', r'$t/c$', r'$C_{d,Climb}$',  r'$C_{d,Efficiency1}$', r'$C_{d,Efficiency2}$', r'$C_{d,Distance}$']

# Relatives Scoring ohne "Efficiency"
clmax_scores = [0.99476696, 1.006098608]
dicke_scores = [0.999630628, 1.000306049]
climb_scores = [1.00041059, 0.999588353]
cruise_scores = [1.00260463, 0.999017649]
eff1_scores = [1.003308499, 0.997650073]
eff2_scores = [1.001839464, 0.999208016]

from matplotlib import font_manager, rcParams
font_path = "/Users/jannik/Library/Fonts/NewCMMath-Book.otf"
font_prop = font_manager.FontProperties(fname=font_path, size=24)
font_prop_large = font_manager.FontProperties(fname=font_path, size=24)

# Daten in ein Array packen, ohne "Efficiency"
scores = np.array([clmax_scores, dicke_scores, climb_scores, eff1_scores, eff2_scores, cruise_scores])

# Plot erstellen
plt.figure(figsize=(12, 7))  # Kompaktere Abmessungen
bar_width = 0.6  # Breite der Balken

# X-Positionen für die Bargruppen
index = np.arange(len(parameter_names))

# Gestapelte Balken erstellen, die bei 1 beginnen
bars_95 = plt.bar(index, scores[:, 0] - 1, bar_width, bottom=1, label='Parameter factor = 0.95', hatch = '/', edgecolor='black', color='green', alpha=0.7)
bars_105 = plt.bar(index, scores[:, 1] - 1, bar_width, bottom=1, label='Parameter factor = 1.05', hatch = 'x', edgecolor='black', alpha=0.7, color ='blue')

fontsize = 20
# Titel und Achsenbeschriftungen
# plt.title('Sensitivitätsanalyse des Scorings (gestapelte Balken bei y=1, ohne Efficiency)')
plt.xlabel('Parameter', fontproperties=font_prop)
plt.ylabel('Effect on Scoring', fontproperties=font_prop)
plt.xticks(index, parameter_names, fontsize=fontsize)
plt.yticks(fontproperties=font_prop)

# Null-Linie einzeichnen
plt.axhline(1, color='black', linewidth=0.5)

# Legende hinzufügen
plt.legend(prop=font_prop)

# for i in range(len(parameter_names)):
#     plt.text(index[i], scores[i, 0], f"{scores[i, 0]:.2f}", ha='center', va='bottom', fontsize=9)
#     plt.text(index[i] + bar_width, scores[i, 1], f"{scores[i, 1]:.4f}", ha='center', va='bottom', fontsize=9)


# Diagramm anzeigen
#plt.grid(True)
plt.savefig('sensitivities.pdf')
plt.show()
