#!/usr/bin/env python3
"""Génère les figures SVG de docs/Toks.md (variantes light/dark, sans dépendances)."""
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

K = math.log(2) / 50.0            # k_D en 1/an
LAM = 365.2421875 / 15.0          # revenu universel en tôks/an
A_INF = LAM / K                   # ~1756.45

THEMES = {
    "light": dict(ink="#52514e", muted="#898781", grid="#e1e0d9", axis="#c3c2b7",
                  s1="#2a78d6", s2="#008300", ring="#ffffff"),
    "dark":  dict(ink="#c3c2b7", muted="#898781", grid="#2c2c2a", axis="#383835",
                  s1="#3987e5", s2="#008300", ring="#0d1117"),
}
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"
W, H = 720, 400
ML, MR, MT, MB = 56, 16, 24, 46


def make_axes(tmax, vmax):
    def X(t): return ML + (t / tmax) * (W - ML - MR)
    def Y(v): return H - MB - (v / vmax) * (H - MT - MB)
    return X, Y


def path(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def frange(a, b, step):
    n = int((b - a) / step)
    return [a + i * step for i in range(n + 1)] + [b]


def chrome(th, X, Y, tmax, vmax, xticks, yticks, xlabel, ylabel):
    s = []
    for v in yticks:
        if v > 0:
            s.append(f'<line x1="{X(0):.1f}" y1="{Y(v):.1f}" x2="{X(tmax):.1f}" y2="{Y(v):.1f}" stroke="{th["grid"]}" stroke-width="1"/>')
        s.append(f'<text x="{X(0)-8:.1f}" y="{Y(v)+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="12" fill="{th["muted"]}">{v}</text>')
    s.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(tmax):.1f}" y2="{Y(0):.1f}" stroke="{th["axis"]}" stroke-width="1"/>')
    for t in xticks:
        s.append(f'<text x="{X(t):.1f}" y="{H-MB+18:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{th["muted"]}">{t}</text>')
    s.append(f'<text x="{(ML+W-MR)/2:.1f}" y="{H-8:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{th["ink"]}">{xlabel}</text>')
    s.append(f'<text x="{ML-40:.1f}" y="{MT-8:.1f}" text-anchor="start" font-family="{FONT}" font-size="12" fill="{th["ink"]}">{ylabel}</text>')
    return s


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img">\n' + "\n".join(body) + "\n</svg>\n")


# ---------------------------------------------------------------- figure 1
def fig_vie(mode):
    th = THEMES[mode]
    tmax, vmax = 100, 1950
    X, Y = make_axes(tmax, vmax)
    b = chrome(th, X, Y, tmax, vmax, [0, 25, 50, 75, 100], [0, 500, 1000, 1500], "âge (années)", "tôks")
    # asymptote
    b.append(f'<line x1="{X(0):.1f}" y1="{Y(A_INF):.1f}" x2="{X(tmax):.1f}" y2="{Y(A_INF):.1f}" stroke="{th["muted"]}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    b.append(f'<text x="{X(tmax):.1f}" y="{Y(A_INF)-8:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{th["ink"]}">plafond : Λ̇/k_D ≈ 1756 tôks</text>')
    # courbe
    pts = [(X(t), Y(A_INF * (1 - math.exp(-K * t)))) for t in frange(0, tmax, 0.5)]
    b.append(f'<path d="{path(pts)}" fill="none" stroke="{th["s1"]}" stroke-width="2"/>')
    # point à 50 ans
    half = A_INF / 2
    b.append(f'<line x1="{X(50):.1f}" y1="{Y(0):.1f}" x2="{X(50):.1f}" y2="{Y(half):.1f}" stroke="{th["muted"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    b.append(f'<line x1="{X(0):.1f}" y1="{Y(half):.1f}" x2="{X(50):.1f}" y2="{Y(half):.1f}" stroke="{th["muted"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    b.append(f'<circle cx="{X(50):.1f}" cy="{Y(half):.1f}" r="5" fill="{th["s1"]}" stroke="{th["ring"]}" stroke-width="2"/>')
    b.append(f'<text x="{X(48):.1f}" y="{Y(half)-14:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{th["ink"]}">à 50 ans : la moitié (≈ 878 tôks)</text>')
    return svg(b)


# ---------------------------------------------------------------- figure 2
def fig_cont(mode):
    th = THEMES[mode]
    tmax, vmax = 80, 580
    X, Y = make_axes(tmax, vmax)
    b = chrome(th, X, Y, tmax, vmax, [0, 20, 40, 60, 80], [0, 250, 500], "temps (années)", "tôks")
    t0, T, m = 5.0, 20.0, 500.0
    fdot = m / T
    # transfert : impulsion à t0
    pts_t = [(X(0), Y(0)), (X(t0), Y(0)), (X(t0), Y(m))]
    pts_t += [(X(t), Y(m * math.exp(-K * (t - t0)))) for t in frange(t0, tmax, 0.5)]
    b.append(f'<path d="{path(pts_t)}" fill="none" stroke="{th["s1"]}" stroke-width="2"/>')
    # flot : créneau t0..t0+T
    pts_f = [(X(0), Y(0)), (X(t0), Y(0))]
    pts_f += [(X(t), Y(fdot / K * (1 - math.exp(-K * (t - t0))))) for t in frange(t0, t0 + T, 0.5)]
    a_end = fdot / K * (1 - math.exp(-K * T))
    pts_f += [(X(t), Y(a_end * math.exp(-K * (t - t0 - T)))) for t in frange(t0 + T, tmax, 0.5)]
    b.append(f'<path d="{path(pts_f)}" fill="none" stroke="{th["s2"]}" stroke-width="2"/>')
    # étiquettes directes
    b.append(f'<text x="{X(7):.1f}" y="{Y(520):.1f}" text-anchor="start" font-family="{FONT}" font-size="13" fill="{th["ink"]}">transfert — 500 tôks d’un coup</text>')
    b.append(f'<text x="{X(26):.1f}" y="{Y(465):.1f}" text-anchor="start" font-family="{FONT}" font-size="13" fill="{th["ink"]}">flot — 500 tôks sur 20 ans</text>')
    # demi-vie du transfert
    b.append(f'<line x1="{X(t0+50):.1f}" y1="{Y(0):.1f}" x2="{X(t0+50):.1f}" y2="{Y(m/2):.1f}" stroke="{th["muted"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    b.append(f'<circle cx="{X(t0+50):.1f}" cy="{Y(m/2):.1f}" r="5" fill="{th["s1"]}" stroke="{th["ring"]}" stroke-width="2"/>')
    b.append(f'<text x="{X(t0+50)+10:.1f}" y="{Y(m/2)-34:.1f}" text-anchor="start" font-family="{FONT}" font-size="13" fill="{th["ink"]}">50 ans plus tard : ÷ 2</text>')
    # légende (haut droite)
    lx, ly = X(52), Y(555)
    b.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx+18:.1f}" y2="{ly:.1f}" stroke="{th["s1"]}" stroke-width="2"/>')
    b.append(f'<text x="{lx+24:.1f}" y="{ly+4:.1f}" font-family="{FONT}" font-size="12" fill="{th["ink"]}">transfert</text>')
    b.append(f'<line x1="{lx+96:.1f}" y1="{ly:.1f}" x2="{lx+114:.1f}" y2="{ly:.1f}" stroke="{th["s2"]}" stroke-width="2"/>')
    b.append(f'<text x="{lx+120:.1f}" y="{ly+4:.1f}" font-family="{FONT}" font-size="12" fill="{th["ink"]}">flot</text>')
    return svg(b)


# --------------------------------------------------- figures du $tôkEx
# Série : palette Smoothop, nuances -1 (validées clair et sombre)
SMOOTHOP = {"blue": "#0F8EB1", "orange": "#CC6018"}


def fig_stokex_response(mode):
    """Courbes de réponse d'un participant (cf. StokEx.tex, fig. symétrie) :
    un seul axe, unités normalisées par actif — les deux courbes sont miroir."""
    th = THEMES[mode]
    W2, H2 = 720, 440
    ML2, MR2, MT2, MB2 = 56, 16, 30, 46
    ph = H2 - MT2 - MB2
    v_i, theta = 10.0, 75.0
    w_i = math.tan(math.pi * theta / 200.0) / 3.0
    ymin, ymax = -12.0, 40.0

    def XL(p):  # échelle log, p dans [1, 100]
        return ML2 + (math.log10(p) / 2.0) * (W2 - ML2 - MR2)

    def Y(v):
        return MT2 + ph - (v - ymin) / (ymax - ymin) * ph

    def ya(p):  # Ẋ_i^α / Ṙ = w·f(x)
        return w_i * ((p / v_i) ** 2 - v_i / p)

    def yb(p):  # Ẋ_i^β / (Ṙ·[β/α]_i) = w·f(1/x)
        return w_i * ((v_i / p) ** 2 - p / v_i)

    b = [f'<defs><clipPath id="plot"><rect x="{ML2}" y="{MT2}" width="{W2-ML2-MR2}" height="{ph:.1f}"/></clipPath></defs>']
    for v in (0, 20, 40):
        if v != 0:
            b.append(f'<line x1="{ML2}" y1="{Y(v):.1f}" x2="{W2-MR2}" y2="{Y(v):.1f}" stroke="{th["grid"]}" stroke-width="1"/>')
        b.append(f'<text x="{ML2-8}" y="{Y(v)+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="12" fill="{th["muted"]}">{v}</text>')
    b.append(f'<line x1="{ML2}" y1="{Y(0):.1f}" x2="{W2-MR2}" y2="{Y(0):.1f}" stroke="{th["axis"]}" stroke-width="1"/>')
    b.append(f'<line x1="{XL(v_i):.1f}" y1="{MT2}" x2="{XL(v_i):.1f}" y2="{MT2+ph:.1f}" stroke="{th["muted"]}" stroke-width="1" stroke-dasharray="2 3"/>')
    pts_a = [(XL(10 ** (j / 50.0)), Y(ya(10 ** (j / 50.0)))) for j in range(101)]
    pts_b = [(XL(10 ** (j / 50.0)), Y(yb(10 ** (j / 50.0)))) for j in range(101)]
    b.append(f'<path d="{path(pts_a)}" fill="none" stroke="{SMOOTHOP["blue"]}" stroke-width="2" clip-path="url(#plot)"/>')
    b.append(f'<path d="{path(pts_b)}" fill="none" stroke="{SMOOTHOP["orange"]}" stroke-width="2" clip-path="url(#plot)"/>')
    b.append(f'<circle cx="{XL(v_i):.1f}" cy="{Y(0):.1f}" r="5" fill="{th["muted"]}" stroke="{th["ring"]}" stroke-width="2"/>')
    for p_t in (1, 10, 100):
        b.append(f'<text x="{XL(p_t):.1f}" y="{MT2+ph+16:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{th["muted"]}">{p_t}</text>')
    # étiquettes directes + légende
    b.append(f'<text x="{XL(45):.1f}" y="{Y(33):.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{th["ink"]}">Ẋᵢᵅ (en Ṙ)</text>')
    b.append(f'<text x="{XL(2.4):.1f}" y="{Y(33):.1f}" text-anchor="start" font-family="{FONT}" font-size="13" fill="{th["ink"]}">Ẋᵢᵝ (en Ṙ·[β/α]ᵢ)</text>')
    b.append(f'<text x="{XL(v_i):.1f}" y="{Y(-9):.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{th["ink"]}">à l\'estimation (10) : équilibre</text>')
    lx, ly = XL(28), Y(38.5)
    b.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx+18:.1f}" y2="{ly:.1f}" stroke="{SMOOTHOP["blue"]}" stroke-width="2"/>')
    b.append(f'<text x="{lx+24:.1f}" y="{ly+4:.1f}" font-family="{FONT}" font-size="12" fill="{th["ink"]}">actif α</text>')
    b.append(f'<line x1="{lx+92:.1f}" y1="{ly:.1f}" x2="{lx+110:.1f}" y2="{ly:.1f}" stroke="{SMOOTHOP["orange"]}" stroke-width="2"/>')
    b.append(f'<text x="{lx+116:.1f}" y="{ly+4:.1f}" font-family="{FONT}" font-size="12" fill="{th["ink"]}">actif β</text>')
    b.append(f'<text x="{(ML2+W2-MR2)/2:.1f}" y="{H2-10:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{th["ink"]}">prix de marché [α/β]Ω (échelle log, en α par unité de β)</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" '
            f'width="{W2}" height="{H2}" role="img">\n' + "\n".join(b) + "\n</svg>\n")


def fig_stokex_steps(mode):
    """Le prix de marché, constant par morceaux (cf. StokEx.tex, fig. steps)."""
    th = THEMES[mode]
    tmax, vmax = 5.0, 2.0
    X, Y = make_axes(tmax, vmax)
    b = []
    b.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(tmax):.1f}" y2="{Y(0):.1f}" stroke="{th["axis"]}" stroke-width="1"/>')
    for t, lbl in ((0.0, "t₀"), (3.0, "t₁")):
        b.append(f'<text x="{X(t):.1f}" y="{H-MB+18:.1f}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="{th["muted"]}">{lbl}</text>')
    steps = [(0.0, 1.0), (1.0, 1.0), (1.0, 1.2), (1.5, 1.2), (1.5, 0.6), (1.8, 0.6), (1.8, 0.5), (3.0, 0.5)]
    b.append(f'<path d="{path([(X(t), Y(v)) for t, v in steps])}" fill="none" stroke="{SMOOTHOP["blue"]}" stroke-width="2"/>')
    b.append(f'<line x1="{X(3):.1f}" y1="{Y(0.5):.1f}" x2="{X(5):.1f}" y2="{Y(0.5):.1f}" stroke="{SMOOTHOP["blue"]}" stroke-width="2" stroke-dasharray="5 4" opacity="0.6"/>')
    for t in (0.0, 1.0, 1.5, 1.8):
        b.append(f'<circle cx="{X(t):.1f}" cy="{Y(0):.1f}" r="5" fill="{SMOOTHOP["orange"]}" stroke="{th["ring"]}" stroke-width="2"/>')
    b.append(f'<circle cx="{X(3.35):.1f}" cy="{Y(1.72):.1f}" r="5" fill="{SMOOTHOP["orange"]}" stroke="{th["ring"]}" stroke-width="2"/>')
    b.append(f'<text x="{X(3.5):.1f}" y="{Y(1.72)+4:.1f}" text-anchor="start" font-family="{FONT}" font-size="12.5" fill="{th["ink"]}">exécution de l\'algorithme intérieur</text>')
    b.append(f'<text x="{X(3.1):.1f}" y="{Y(0.62):.1f}" text-anchor="start" font-family="{FONT}" font-size="12.5" fill="{th["ink"]}">après t₁ : futur non calculé</text>')
    b.append(f'<text x="{ML-44:.1f}" y="{MT-6:.1f}" text-anchor="start" font-family="{FONT}" font-size="12" fill="{th["ink"]}">prix de marché [α/β]Ω</text>')
    b.append(f'<text x="{(ML+W-MR)/2:.1f}" y="{H-8:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{th["ink"]}">temps</text>')
    return svg(b)


for mode in ("light", "dark"):
    with open(f"{OUT}/une-vie-en-toks-{mode}.svg", "w") as f:
        f.write(fig_vie(mode))
    with open(f"{OUT}/transfert-vs-flot-{mode}.svg", "w") as f:
        f.write(fig_cont(mode))
    with open(f"{OUT}/stokex-reponse-{mode}.svg", "w") as f:
        f.write(fig_stokex_response(mode))
    with open(f"{OUT}/stokex-pas-{mode}.svg", "w") as f:
        f.write(fig_stokex_steps(mode))
print("OK", sorted(os.listdir(OUT)))
