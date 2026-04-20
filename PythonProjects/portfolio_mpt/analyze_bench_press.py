import os
import sys

import numpy as np
import scipy.stats as stats
from matplotlib import pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.plot_style import apply_plot_style, subtitle, finish_figure, FRONTIER, MVP, MUTED

# Data from images
strength_no_music = [
    160,
    155,
    105,
    135,
    205,
    185,
    90,
    210,
    110,
    115,
    125,
    95,
    105,
    180,
    225,
    145,
    100,
    90,
    95,
    120,
    140,
    155,
    105,
    195,
    95,
    130,
    115,
    120,
    85,
    65,
]
strength_music = [
    165,
    155,
    110,
    130,
    205,
    190,
    95,
    220,
    110,
    110,
    125,
    95,
    105,
    185,
    225,
    150,
    105,
    90,
    95,
    115,
    140,
    155,
    105,
    195,
    100,
    135,
    120,
    120,
    80,
    70,
]

endurance_no_music = [
    12,
    12,
    9,
    14,
    11,
    10,
    9,
    12,
    14,
    8,
    10,
    11,
    13,
    9,
    10,
    14,
    12,
    14,
    9,
    10,
    11,
    12,
    9,
    11,
    10,
    12,
    13,
    10,
    8,
    11,
]
endurance_music = [
    14,
    12,
    11,
    15,
    14,
    12,
    11,
    12,
    17,
    10,
    13,
    13,
    15,
    11,
    12,
    16,
    14,
    17,
    11,
    12,
    13,
    15,
    11,
    12,
    12,
    14,
    16,
    11,
    10,
    12,
]


def get_stats(data, name):
    return {
        "Name": name,
        "Mean": np.mean(data),
        "Median": np.median(data),
        "SD": np.std(data, ddof=1),
        "Var": np.var(data, ddof=1),
        "Min": np.min(data),
        "Max": np.max(data),
    }


print("--- Descriptive Statistics ---")
all_stats = [
    get_stats(strength_no_music, "Strength (Silence)"),
    get_stats(strength_music, "Strength (Music)"),
    get_stats(endurance_no_music, "Endurance (Silence)"),
    get_stats(endurance_music, "Endurance (Music)"),
]
for s in all_stats:
    print(
        f"{s['Name']}: Mean={s['Mean']:.2f}, Median={s['Median']:.2f}, "
        f"SD={s['SD']:.2f}, Var={s['Var']:.2f}, Range=[{s['Min']}, {s['Max']}]"
    )

print("\n--- Inferential Statistics (Paired T-Tests) ---")
res_strength = stats.ttest_rel(strength_music, strength_no_music)
print(f"Strength (Music vs Silence): t={res_strength.statistic:.4f}, p={res_strength.pvalue:.4f}")

res_endurance = stats.ttest_rel(endurance_music, endurance_no_music)
print(f"Endurance (Music vs Silence): t={res_endurance.statistic:.4f}, p={res_endurance.pvalue:.4f}")

print("\n--- Correlation Analysis (Strength vs Endurance) ---")
corr_silence, p_silence = stats.pearsonr(strength_no_music, endurance_no_music)
corr_music, p_music = stats.pearsonr(strength_music, endurance_music)

print(f"Silence: r={corr_silence:.4f}, p-value={p_silence:.4f}")
print(f"Music: r={corr_music:.4f}, p-value={p_music:.4f}")

z_silence = 0.5 * np.log((1 + corr_silence) / (1 - corr_silence))
z_music = 0.5 * np.log((1 + corr_music) / (1 - corr_music))
n = len(strength_no_music)
z_score = (z_music - z_silence) / np.sqrt(2 / (n - 3))
p_comp = 2 * (1 - stats.norm.cdf(np.abs(z_score)))
print(f"Fisher Z Comparison: z={z_score:.4f}, p-value={p_comp:.4f}")

print("\n--- Manual Calculation Example Data (Subject 1) ---")
print("Silence: 1RM=160, Endurance=12")
print("Music: 1RM=165, Endurance=14")


def create_scatter(x, y, label, color_hex, filename):
    apply_plot_style()
    fig, ax = plt.subplots(figsize=(7.8, 5.8))
    ax.scatter(
        x,
        y,
        color=color_hex,
        alpha=0.78,
        s=52,
        edgecolors="white",
        linewidths=0.45,
        label=f"Subjects ({label})",
    )
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    xsort = np.sort(np.array(x))
    ax.plot(xsort, p(xsort), color=MUTED, linestyle="--", linewidth=1.35, label=f"OLS line (r = {stats.pearsonr(x, y)[0]:.2f})")
    ax.set_title(f"1RM vs reps @70% — {label}")
    subtitle(ax, "Classroom dataset; trendline is descriptive, not causal")
    ax.set_xlabel("1RM (lb)")
    ax.set_ylabel("Reps at 70% 1RM")
    ax.legend(loc="best", fontsize=9)
    finish_figure(fig)
    fig.savefig(filename)
    plt.close()


create_scatter(strength_no_music, endurance_no_music, "silence", FRONTIER, "strength_endurance_silence.png")
create_scatter(strength_music, endurance_music, "music", MVP, "strength_endurance_music.png")

print("\nPlots saved: strength_endurance_silence.png, strength_endurance_music.png")
