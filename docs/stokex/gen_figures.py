#!/usr/bin/env python3
"""Génère les figures PDF de stokex_defensive_publication.tex (palette Smoothop).

Usage : python gen_figures.py  (matplotlib requis ; testé avec 3.7)
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

OUT = os.path.dirname(os.path.abspath(__file__))

# Palette Smoothop, nuances -1 (validées CVD/contraste sur fond blanc)
BLUE = "#0F8EB1"
ORANGE = "#CC6018"
INK = "#333333"
MUTED = "#6E6E6E"
GRID = "#E4E4E4"

plt.rcParams.update({
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.size": 11,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "axes.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelcolor": INK,
    "ytick.labelcolor": INK,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "legend.frameon": False,
})

RATIO = r"\frac{\,[\alpha/\beta]_\Omega}{[\alpha/\beta]_i}"


def style(ax, grid_axis="both"):
    ax.spines[["top", "right"]].set_visible(False)
    if grid_axis:
        ax.grid(True, axis=grid_axis)
        ax.set_axisbelow(True)


# ------------------------------------------------- stok-market_symmetry.pdf
def fig_symmetry():
    """Vitesses d'échange du i-e participant, chaque actif dans son unité de
    référence : un seul axe (sans double échelle), les courbes sont miroir."""
    v_i, theta = 10.0, 75.0
    w_i = math.tan(math.pi * theta / 200.0) / 3.0

    def f(p):
        return p * p - 1.0 / p

    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    p = [10 ** (j / 300.0) for j in range(601)]  # 1 .. 100
    ax.plot(p, [w_i * f(q / v_i) for q in p], color=BLUE, lw=1.8,
            label=r"asset A: $\dot{X}_i^\alpha$ (in units of $\dot{R}$)",
            clip_on=True)
    ax.plot(p, [w_i * f(v_i / q) for q in p], color=ORANGE, lw=1.8,
            label=r"asset B: $\dot{X}_i^\beta$"
                  r" (in units of $\dot{R}\,[\beta/\alpha]_i$)",
            clip_on=True)
    ax.axvline(v_i, color=MUTED, lw=0.8, ls=(0, (2, 3)))
    ax.plot([v_i], [0.0], "o", ms=6, color=INK, zorder=5)

    ax.set_xscale("log")
    ax.set_xlim(1, 100)
    ax.set_ylim(-12, 40)
    ax.set_yticks([0, 20, 40])
    ax.set_xlabel(r"market price $[\alpha/\beta]_\Omega$"
                  r" (in $\alpha$ per unit of $\beta$, log scale)")
    ax.set_ylabel("exchange velocity\n(in the reference units of each asset)")
    style(ax, grid_axis="y")

    ax.text(v_i, -9, "equilibrium at the estimate", ha="center", color=INK)
    ax.legend(loc="upper center", ncol=1)

    fig.savefig(os.path.join(OUT, "stok-market_symmetry.pdf"),
                bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------- stok-market_steps.pdf
def fig_steps():
    """Le prix de marché, constant par morceaux entre les événements."""
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    events = [0.0, 1.0, 1.5, 1.8]
    steps_t = [0.0, 1.0, 1.0, 1.5, 1.5, 1.8, 1.8, 3.0]
    steps_v = [1.0, 1.0, 1.2, 1.2, 0.6, 0.6, 0.5, 0.5]
    ax.plot(steps_t, steps_v, color=BLUE, lw=1.8)
    ax.plot([3.0, 5.0], [0.5, 0.5], color=BLUE, lw=1.8,
            ls=(0, (4, 3)), alpha=0.6)
    ax.plot(events, [0.0] * len(events), "o", ms=6, color=ORANGE,
            markeredgecolor="white", markeredgewidth=1.2,
            clip_on=False, zorder=5,
            label="execution of the inner algorithm")

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 2)
    ax.set_xticks([0.0, 3.0], [r"$t_0$", r"$t_1$"])
    ax.set_yticks([])
    ax.set_xlabel("time")
    ax.set_ylabel(r"market price $[\alpha/\beta]_\Omega$")
    style(ax, grid_axis=None)
    ax.spines["left"].set_visible(False)

    ax.text(3.1, 0.62, "beyond $t_1$ (not yet computed)", color=MUTED,
            fontsize=10)
    ax.legend(loc="upper right")

    fig.savefig(os.path.join(OUT, "stok-market_steps.pdf"), bbox_inches="tight")
    plt.close(fig)


# ------------------------- degree_of_certainty.pdf / degree_of_certainty_log.pdf
def fig_degree(log=False):
    """Interprétation géométrique de θ_i. aspect='equal' pour que l'angle
    dessiné soit exactement arctan(3 w_i)."""
    w_i = 0.16  # schématique : angle lisible à l'échelle du graphe
    slope = 3.0 * w_i
    theta_deg = math.degrees(math.atan(slope))

    fig, ax = plt.subplots(figsize=(6.4, 5.0))
    if log:
        xs = [-2.0 + j / 200.0 for j in range(801)]
        ax.plot(xs, [w_i * (math.exp(2 * x) - math.exp(-x)) for x in xs],
                color=BLUE, lw=1.8)
        ax.set_xlim(-2, 2)
        x0 = 0.0
        ax.set_xlabel(r"$\ln\left(%s\right)$" % RATIO, fontsize=13)
    else:
        xs = [0.02 + j / 400.0 for j in range(1601)]
        ax.plot(xs, [w_i * (x * x - 1.0 / x) for x in xs], color=BLUE, lw=1.8)
        ax.set_xlim(0, 4)
        x0 = 1.0
        ax.set_xlabel("$%s$" % RATIO, fontsize=15)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")  # l'angle à l'écran = l'angle géométrique
    ax.set_ylabel(r"$\dot{X}_i^\alpha / \dot{R}$", rotation=0, labelpad=24,
                  fontsize=12)
    style(ax)

    # construction : horizontale, tangente, arc de l'angle θ_i
    reach = 1.6
    dash = dict(color=INK, lw=1.1, ls=(0, (4, 3)))
    ax.plot([x0, x0 + reach], [0.0, 0.0], **dash)
    ax.plot([x0, x0 + reach], [0.0, slope * reach], **dash)
    ax.add_patch(Arc((x0, 0.0), 1.8, 1.8, angle=0.0,
                     theta1=0.0, theta2=theta_deg, color=INK, lw=1.1))
    mid = math.radians(theta_deg / 2.0)
    ax.annotate(r"$\theta_i$", (x0 + 1.12 * math.cos(mid), 1.12 * math.sin(mid)),
                ha="left", va="center", fontsize=13, color=INK)
    ax.plot([x0], [0.0], "o", ms=6, color=INK, zorder=5)

    name = "degree_of_certainty_log.pdf" if log else "degree_of_certainty.pdf"
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_symmetry()
    fig_steps()
    fig_degree(log=False)
    fig_degree(log=True)
    print("OK :", sorted(f for f in os.listdir(OUT) if f.endswith(".pdf")))
