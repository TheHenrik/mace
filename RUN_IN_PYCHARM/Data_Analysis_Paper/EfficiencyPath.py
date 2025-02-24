import matplotlib.pyplot as plt

# Neue Start- und Endpunkte basierend auf der Beschreibung
x1_start, y1_start = 0, 50  # Start der ersten blauen Linie
x1_end, y1_end = 40, 80  # Ende der ersten blauen Linie

x2_start, y2_start = 40, 90  # Start der zweiten blauen Linie (nach der gestrichelten Linie)
x2_end, y2_end = 90, 10  # Ende der zweiten blauen Linie

fontsize = 22
# Plot
plt.figure()

# Erste blaue Linie plotten (von x=0, y=50 bis x=40, y=80)
plt.plot([x1_start, x1_end], [y1_start, y1_end], 'blue', alpha=0.9, label=r'$v_1$')

# Gestrichelte Linie plotten (von x=40, y=80 bis x=40, y=90)
plt.plot([x1_end, x2_start], [y1_end, y2_start], 'k--', lw=1, label=r'$\Delta h$')

# Zweite blaue Linie plotten (von x=40, y=90 bis x=90, y=10)
plt.plot([x2_start, x2_end], [y2_start, y2_end], 'blue', alpha=0.9, label=r'$v_2$')

# Durchgezogene gepunktete Linie (von der gestrichelten Linie zur x-Achse bei x=40)
plt.plot([x1_end, x1_end], [0, y1_end], 'k:', lw=1)  # Gepunktete Linie

# Labels und Text
plt.text(10, 64, r'$v_1$', color='blue', fontsize=fontsize)
plt.text(70, 43, r'$v_2$', color='blue', fontsize=fontsize)
plt.text(x1_end - 2, (y1_end + y2_start) / 2 - 2, r'$\Delta h$', color='black', fontsize=fontsize, horizontalalignment='right')

# Achsen und Limits
plt.xlim([0, 90])
plt.ylim([0, 100])
plt.xlabel(r'$t$ [s]', fontsize=fontsize)
plt.ylabel(r'$h$ [m]', fontsize=fontsize)

# Ticks nur für Minimal- und Maximalwerte, t1 auf der x-Achse und h0 auf der y-Achse
plt.xticks([0, 40, 90], [r'$0$', r'$t_1$', r'$90$'], fontsize=fontsize)
plt.yticks([0, 50, 100], [r'$0$', r'$h_0$', r'$100$'], fontsize=fontsize)

# Achsen anzeigen
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)

# Plot anzeigen
plt.savefig('plot.pdf', format='pdf', bbox_inches='tight')  # PDF exportieren

plt.show()
