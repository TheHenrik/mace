import matplotlib.pyplot as plt
import numpy as np
#import seaborn as sns
import statistics


# Höhen nach 30s
# 56.5, 60.2, 68.2
# Berechnet
# 59.42, 63

# relative höhen
# 0.95085, 0.9555, 1.08 avg
# 1, 1, 1

# Stil einstellen
#sns.set(style="whitegrid", palette="muted")
#plt.style.use('ggplot')
# plt.style.use('seaborn-whitegrid')
# colors = sns.color_palette('deep')

from matplotlib import font_manager, rcParams
font_path = "/Users/jannik/Library/Fonts/NewCMMath-Book.otf"
font_prop = font_manager.FontProperties(fname=font_path, size=20)
font_prop_large = font_manager.FontProperties(fname=font_path, size=24)

Effiency_Scores = [0.6017, 0.4164, 0.5018]
efficiency_score_mean = statistics.mean(Effiency_Scores)
efficiency_score_std = statistics.stdev(Effiency_Scores)

Distances = np.array([2.867, 2.829, 2.776])
speeds = Distances * 1000 / 90
avg_speed = statistics.mean(speeds)
std_speed = statistics.stdev(speeds)

Climbs = np.array([0.95085, 0.9555, 1.08])
avg_climb = statistics.mean(Climbs)
std_climbs = statistics.stdev(Climbs)

# Daten
labels = ['Empty mass', 'MTOM for 40 m take-off', 'Climb height', 'Efficiency Scoring', 'Distance Scoring']
Group_labels = ['Calculated', 'Measured']
group1_means = [2.1, 1, 1, 0.684, 34.17] # climb rate 2.503
group2_means = [2.55, 1, avg_climb, efficiency_score_mean, avg_speed] # climb rate 2.393
group2_errors = [0, 0, std_climbs, efficiency_score_std, std_speed] # climb rate 1.148


# Normierung auf 100% für Gruppe 1
group1_means_normalized = [100] * len(group1_means)
group2_means_normalized = [(g2 / g1) * 100 for g1, g2 in zip(group1_means, group2_means)]

#group1_errors_normalized = [(err / mean) * 100 for err, mean in zip(group1_errors, group1_means)]
group2_errors_normalized = [(err / mean) * 100 for err, mean in zip(group2_errors, group2_means)]

x = np.arange(len(labels))  # die Label-Positionen
width = 0.3  # die Breite der Balken

fig, ax = plt.subplots(figsize=(15, 6))
plt.grid(axis='y', zorder=0, alpha = 0.7)

# Balken für Gruppe 1
rects1 = ax.bar(x - width/2, group1_means_normalized, width, label=Group_labels[0], capsize=5, alpha=0.75, color='green', zorder=2, edgecolor='black', hatch = 'x')
# Balken für Gruppe 2
rects2 = ax.bar(x + width/2, group2_means_normalized, width, label=Group_labels[1], alpha=0.75, color='blue', zorder=2, edgecolor='black', hatch = '/', yerr=group2_errors_normalized, error_kw={'color': 'red', 'elinewidth': 3, 'capsize': 10})
fontsize=20
# Titel und Labels setzen
ax.set_ylabel('Percent (%)', fontproperties=font_prop)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontproperties=font_prop)
ax.set_ylim([0,200])
plt.yticks(fontproperties=font_prop)
ax.legend(prop=font_prop, facecolor='white', edgecolor='black', framealpha = 1)

# Balkenbeschriftung
def autolabel(rects):
    """Hängt die Werte oberhalb der Balken an"""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(3, 0),  # 3 Punkte Vertikaloffset
                    textcoords="offset points",
                    ha='left', va='bottom')

# Layout anpassen
fig.tight_layout()

# Plot als SVG exportieren
plt.savefig('barchart_with_relative_errorbars.pdf', format='pdf')

# Plot anzeigen (optional)
plt.show()