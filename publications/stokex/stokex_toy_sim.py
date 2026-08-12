#!/usr/bin/env python3
"""Petite simulation jouet du $tôkEx, et ses graphes.

Compagnon de `stokex_toy.py`, qui porte le mécanisme et ne dépend de rien. Ce
script-ci ajoute matplotlib, fait tourner un marché de quatre participants
pendant 120 unités de temps, et trace ce qui se passe.

Trois sortes d'événements sont mises en scène, toutes prévues par le
document (la simulation en produit cinq occurrences) :
  1. un participant se vide et sort du marché (§4.1, l'exclusion) ;
  2. un participant révise sa déclaration (§4, action 4), ce qui déplace le
     prix d'un coup ;
  3. le participant vidé est réintégré dès qu'il possède à nouveau l'actif
     qu'il veut vendre (§4.1, la réintégration triée).

Couleurs : palette Smoothop, `docs/Style.md`. Les nuances −1 du bleu et de
l'orange sont validées contraste/daltonismes ; le vert et le magenta ajoutés
ici pour tenir quatre séries ne le sont pas encore — c'est un item ouvert du
`TODO.md`.

Sortie : `stokex_toy_sim.png`, **non versionnée** — une illustration se
regénère, elle ne s'archive pas.

Exécution :
  ./.venv/bin/python publications/stokex/stokex_toy_sim.py           # écrit le PNG
  ./.venv/bin/python publications/stokex/stokex_toy_sim.py --show    # + une fenêtre
"""
import os
import sys

import matplotlib

# Par défaut le script est muet : il écrit un PNG et rend la main, ce qui le
# rend exécutable partout, y compris sans écran. Avec --show, on garde le
# backend natif de la machine et on ouvre une vraie fenêtre, zoomable.
SHOW = "--show" in sys.argv
if not SHOW:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

from stokex_toy import Market, Participant, weight_of_degree

OUT = os.path.dirname(os.path.abspath(__file__))

# Palette Smoothop (docs/Style.md) — teintes de marque, nuance 3
BLUE = "#0B85A6"     # S3, le bleu Smoothop
ORANGE = "#CC6318"   # O3
GREEN = "#1A7A27"    # G3
MAGENTA = "#9A23A3"  # M3
INK = "#404040"      # K5
GRID = "#CACACA"     # W5

SERIES = [BLUE, ORANGE, GREEN, MAGENTA]

plt.rcParams.update({
    "font.size": 9,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def simulate(market, duration, step, revision=None):
    """Échantillonne la trajectoire du marché, sans jamais fausser le pas exact.

    On avance par petits morceaux ; `Market.advance` traite en interne les
    événements qui tombent à l'intérieur d'un morceau, donc l'état reste exact.
    `revision` est un couple (instant, fonction) appliqué en cours de route.
    """
    hist = {"t": [], "price": [], "weight": [], "n_participants": [],
            "alpha": [[] for _ in market.participants],
            "beta": [[] for _ in market.participants],
            "estimate": [[] for _ in market.participants]}
    events = []

    t = 0.0
    market.inner()
    trading_before = {p.name for p in market.participants if p.trading}
    done_revision = revision is None

    while t <= duration + 1e-12:
        for key, val in (("t", t), ("price", market.price),
                         ("weight", market.total_weight)):
            hist[key].append(val)
        hist["n_participants"].append(sum(1 for p in market.participants if p.trading))
        for i, p in enumerate(market.participants):
            hist["alpha"][i].append(p.n_alpha)
            hist["beta"][i].append(p.n_beta)
            hist["estimate"][i].append(p.estimate)   # elle peut changer en route

        trading_now = {p.name for p in market.participants if p.trading}
        if trading_now != trading_before:
            for name in trading_before - trading_now:
                events.append((t, f"{name} sort", ORANGE))
            for name in trading_now - trading_before:
                events.append((t, f"{name} revient", GREEN))
            trading_before = trading_now

        if not done_revision and t >= revision[0]:
            revision[1](market)
            market.inner()
            events.append((t, "révision", MAGENTA))
            done_revision = True

        market.advance(step)
        t += step

    return hist, events


def _revise(market):
    """Bob change d'avis : il croit β bien plus cher, et le croit fermement.

    Assez fermement pour tirer le prix du marché **au-dessus** de l'estimation de
    Carol — qui, vidée de son α depuis longtemps, redevient alors vendeuse de β,
    l'actif qu'il lui reste. C'est la réintégration de §4.1.
    """
    bob = next(p for p in market.participants if p.name == "Bob")
    bob.estimate = 6.0
    bob.degree = 92.0
    bob.weight = weight_of_degree(92.0)


def main():
    market = Market([
        Participant("Alice", estimate=2.00, degree=75.0, n_alpha=100.0, n_beta=50.0),
        Participant("Bob",   estimate=1.00, degree=50.0, n_alpha=80.0,  n_beta=80.0),
        Participant("Carol", estimate=3.50, degree=90.0, n_alpha=10.0,  n_beta=200.0),
        Participant("Dan",   estimate=1.50, degree=30.0, n_alpha=60.0,  n_beta=60.0),
    ], reference_velocity=1.0)

    a0, b0 = market.totals()
    hist, events = simulate(market, duration=120.0, step=0.05, revision=(50.0, _revise))
    a1, b1 = market.totals()

    fig, axes = plt.subplots(4, 1, figsize=(7.2, 9.0), sharex=True)
    t = hist["t"]

    # 1 — le prix du marché, et les estimations qu'il agrège
    ax = axes[0]
    for i, p in enumerate(market.participants):
        # l'estimation déclarée, dans le temps : Bob change la sienne en route
        ax.plot(t, hist["estimate"][i], color=SERIES[i], lw=0.9,
                ls=(0, (4, 3)), alpha=0.8)
    ax.plot(t, hist["price"], color=INK, lw=2.0)
    ax.set_ylabel(r"$[\alpha/\beta]_\Omega$")
    ax.set_title("Le prix du marché, borné par les estimations des participants",
                 fontsize=10, loc="left")
    style(ax)

    # 2 — les soldes en α
    ax = axes[1]
    for i, p in enumerate(market.participants):
        ax.plot(t, hist["alpha"][i], color=SERIES[i], lw=1.6, label=p.name)
    ax.set_ylabel(r"$n_i^\alpha$")
    ax.legend(ncol=4, frameon=False, fontsize=8, loc="upper left")
    ax.set_ylim(top=ax.get_ylim()[1] * 1.18)
    style(ax)

    # 3 — les soldes en β
    ax = axes[2]
    for i, p in enumerate(market.participants):
        ax.plot(t, hist["beta"][i], color=SERIES[i], lw=1.6)
    ax.set_ylabel(r"$n_i^\beta$")
    style(ax)

    # 4 — la raideur du marché
    ax = axes[3]
    ax.plot(t, hist["weight"], color=BLUE, lw=1.8)
    ax.set_ylabel(r"$W_\Omega$")
    ax.set_xlabel("temps (unités de $\\dot{R}$)")
    style(ax)

    # les événements, sur les quatre panneaux
    for ax in axes:
        for t_e, label, color in events:
            ax.axvline(t_e, color=color, lw=1.0, ls=(0, (2, 2)), alpha=0.8)
    # étiquettes décalées en alternance : deux événements peuvent se suivre
    # de très près (la révision et la réintégration qu'elle provoque)
    for rank, (t_e, label, color) in enumerate(events):
        axes[0].annotate(label, (t_e, axes[0].get_ylim()[1]), fontsize=7.5,
                         color=color, rotation=90, va="top", ha="right",
                         xytext=(-2, -4 - 26 * (rank % 2)), textcoords="offset points")

    fig.tight_layout()
    path = os.path.join(OUT, "stokex_toy_sim.png")
    fig.savefig(path, dpi=170)

    print(f"figure écrite : {path}")
    print(f"prix final    : {market.price:.6f} α par β")
    print(f"événements    : " + ", ".join(f"{lab} à t={te:.2f}" for te, lab, _ in events))
    print(f"conservation  : Δ(Σn^α) = {a1 - a0:.3e}, Δ(Σn^β) = {b1 - b0:.3e}")
    assert abs(a1 - a0) < 1e-6 and abs(b1 - b0) < 1e-6, "le mécanisme ne conserve plus"
    print("conservation vérifiée sur toute la simulation.")

    if SHOW:
        print("fenêtre ouverte — ferme-la pour rendre la main.")
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    main()
