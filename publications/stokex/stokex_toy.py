#!/usr/bin/env python3
"""Implémentation jouet du $tôkEx, avec comptes α et β.

Un marché complet et exécutable, écrit **depuis la publication défensive**
(`stokex_defensive_publication.tex`) et depuis elle seule : chaque fonction
renvoie à l'équation ou à la section qu'elle réalise. Ce n'est pas une copie du
backend du système des tôks — c'est ce que la divulgation permet à quiconque de
réécrire à partir du seul document. C'est même la meilleure preuve qu'elle est
*enabling* au sens de l'art antérieur.

Ce que le jouet fait :
  - la fonction de marchand (2) en forme décalée (3) ;
  - la fonction de poids (5) ;
  - le prix du marché en forme close (14) ;
  - les vitesses d'échange (6) et les temps de vidage (8) ;
  - l'algorithme interne (§4.1) : exclusion, prix, réintégration triée ;
  - l'algorithme externe (§4.2) : pas de temps exact, événement par événement.

Ce que le jouet ne fait pas, et l'assume :
  - pas de sommation compensée (Kahan) ni de précision étendue ;
  - pas de désintégration : les deux actifs sont supposés sans dynamique propre,
    l'hypothèse par défaut du document (§2) ;
  - pas de bornes sur les estimations, pas de discrétisation du degré.
  Le document décrit ces raffinements en §4.3 ; ils n'ajoutent rien à la
  compréhension du mécanisme, qui est le but ici.

Sans dépendances. Exécution : python3 stokex_toy.py
"""
import math

TOL = 1e-12          # seuil de solvabilité : en deçà, un compte est vide
DEFAULT_PRICE = 1.0  # prix d'un marché vide (§4.3)


# ----------------------------------------------------------------------
# Les deux fonctions du mécanisme
# ----------------------------------------------------------------------

def weight_of_degree(theta):
    """(5) — w(θ) = tan(π θ / 200 %) / 3, avec θ en pourcent dans [0, 100)."""
    if theta <= 0.0:
        return 0.0
    if theta >= 100.0:
        raise ValueError("le degré de certitude est borné à [0, 100) % — voir annexe 7.8")
    return math.tan(math.pi * theta / 200.0) / 3.0


def degree_of_weight(w):
    """Réciproque de (5), qui sert aussi au degré agrégé du marché (19)."""
    return 200.0 / math.pi * math.atan(3.0 * w)


def trader_f(x):
    """(2) — f(x) = x² − 1/x, évaluée sous la forme décalée (3).

    Le point de fonctionnement typique est x ≈ 1, là où x² − 1/x s'annule par
    cancellation catastrophique. En posant y = x − 1 (exact dans [1/2, 2] par le
    lemme de Sterbenz), x³ − 1 = y³ + 3y² + 3y et le numérateur suit y sans
    annulation. Le dénominateur doit être **x lui-même**, pas y + 1.
    """
    y = x - 1.0
    return y * (y * y + 3.0 * y + 3.0) / x


# ----------------------------------------------------------------------
# Les participants
# ----------------------------------------------------------------------

class Participant:
    """Un participant : deux déclarations, deux comptes.

    Le participant déclare son estimate [α/β]_i et son degré θ_i ; c'est son
    robot marchand qui exécute, en produisant les deux vitesses d'échange.
    """

    def __init__(self, name, estimate, degree, n_alpha, n_beta):
        if estimate <= 0.0:
            raise ValueError("une estimation est strictement positive")
        self.name = name
        self.estimate = float(estimate)   # [α/β]_i
        self.degree = float(degree)       # θ_i, en %
        self.weight = weight_of_degree(degree)   # w_i, calculé une seule fois
        self.n_alpha = float(n_alpha)
        self.n_beta = float(n_beta)
        # remplis par l'algorithme interne
        self.trading = False
        self.vel_alpha = 0.0              # Ẋ_i^α
        self.vel_beta = 0.0               # Ẋ_i^β
        self.dt_empty = math.inf          # Δt_i

    def __repr__(self):
        return (f"{self.name}: [α/β]={self.estimate:.4f} θ={self.degree:g}% "
                f"α={self.n_alpha:.4f} β={self.n_beta:.4f}")


# ----------------------------------------------------------------------
# Le marché
# ----------------------------------------------------------------------

class Market:
    """Le $tôkEx pour une paire d'actifs A/B, avec sa vitesse de référence Ṙ."""

    def __init__(self, participants, reference_velocity=1.0):
        self.participants = list(participants)
        self.R = float(reference_velocity)      # Ṙ, en α / unité de temps
        self.price = DEFAULT_PRICE              # [α/β]_Ω
        self._sum_wv = 0.0                      # Σ w_i [α/β]_i
        self._sum_w_inv_v2 = 0.0                # Σ w_i [β/α]_i²

    # -- prix -----------------------------------------------------------

    def _reset_sums(self):
        self._sum_wv = 0.0
        self._sum_w_inv_v2 = 0.0

    def _accumulate(self, p):
        """Ajoute un participant aux deux sommes de (14). Coût O(1)."""
        self._sum_wv += p.weight * p.estimate
        self._sum_w_inv_v2 += p.weight / (p.estimate * p.estimate)

    def _price_from_sums(self):
        """(14) — [α/β]_Ω = (Σ w [α/β] / Σ w [β/α]²)^(1/3)."""
        if self._sum_w_inv_v2 <= 0.0:      # marché vide : personne ne peut échanger
            return DEFAULT_PRICE
        return (self._sum_wv / self._sum_w_inv_v2) ** (1.0 / 3.0)

    @property
    def total_weight(self):
        """(17) — W_Ω = [β/α]_Ω Σ w_i [α/β]_i, la « raideur » du marché."""
        return self._sum_wv / self.price

    @property
    def total_degree(self):
        """(19) — Θ_Ω, le degré de certitude agrégé du marché."""
        return degree_of_weight(self.total_weight)

    # -- algorithme interne (§4.1) --------------------------------------

    def inner(self):
        """Calcule le prix, les vitesses et les temps de vidage à l'instant courant.

        Un participant dont un compte est vide est exclu, puis éventuellement
        réintégré s'il possède l'actif qu'il veut vendre. L'ordre des
        réintégrations n'est pas libre : on traite toujours le plus **éloigné**
        du prix, au sens de |f_i^α|. Comme f est monotone en l'estimation, ce
        plus éloigné est toujours à l'un des deux bouts de la liste triée — d'où
        deux examens par tour, et un coût total O(N log N) dominé par le tri.
        """
        checklist = []
        self._reset_sums()

        for p in self.participants:
            p.trading = True
            if p.weight == 0.0:                      # sans conviction, pas d'échange
                p.trading = False
                continue
            if p.n_alpha <= TOL or p.n_beta <= TOL:
                p.trading = False
                checklist.append(p)
            else:
                self._accumulate(p)
        self.price = self._price_from_sums()

        # réintégrations, du plus éloigné du prix au plus proche
        checklist.sort(key=lambda q: q.estimate)
        while checklist:
            f_low = trader_f(self.price / checklist[0].estimate)
            f_high = trader_f(self.price / checklist[-1].estimate)
            far = checklist.pop(0 if abs(f_low) >= abs(f_high) else -1)
            f_far = f_low if abs(f_low) >= abs(f_high) else f_high
            # f ≥ 0 : le marché est au-dessus de l'estimation, on vend β
            # f ≤ 0 : le marché est en dessous, on vend α
            if (f_far >= 0.0 and far.n_beta > TOL) or (f_far <= 0.0 and far.n_alpha > TOL):
                far.trading = True
                self._accumulate(far)                # mise à jour incrémentale, O(1)
                self.price = self._price_from_sums()

        # vitesses (6) et temps de vidage (8)
        for p in self.participants:
            if p.trading:
                x = self.price / p.estimate
                p.vel_alpha = p.weight * trader_f(x) * self.R
                # forme symétrique : f([β/α]_Ω / [β/α]_i) Ṙ [β/α]_i
                p.vel_beta = p.weight * trader_f(1.0 / x) * self.R / p.estimate
            else:
                p.vel_alpha = 0.0
                p.vel_beta = 0.0
            p.dt_empty = self._emptying_time(p)

        return self.price

    @staticmethod
    def _emptying_time(p):
        """(8)–(9) — Δt_i = min(Δt_i^α, Δt_i^β), avec la convention +∞.

        Seul le compte de l'actif vendu se vide un jour. Le +∞ est ce qui permet
        au minimum de sélectionner le bon compte : sans lui, le rapport négatif
        du compte acheté l'emporterait à tort.
        """
        dt_a = -p.n_alpha / p.vel_alpha if p.vel_alpha < 0.0 else math.inf
        dt_b = -p.n_beta / p.vel_beta if p.vel_beta < 0.0 else math.inf
        return min(dt_a, dt_b)

    # -- algorithme externe (§4.2) --------------------------------------

    def advance(self, duration, trace=None):
        """Avance le marché de `duration`, exactement, événement par événement.

        L'état est constant entre deux événements, donc chaque solde évolue
        linéairement : aucun pas de temps arbitraire, aucune erreur accumulée.
        """
        t = 0.0
        self.inner()
        while True:
            dt = min((p.dt_empty for p in self.participants), default=math.inf)
            if duration - t < dt:
                break
            self._step(dt)
            t += dt
            before = self.price
            self.inner()             # le prix change : un participant vient de sortir
            if trace is not None:
                trace.append((t, before, self.price))
        self._step(duration - t)
        return self.price

    def _step(self, dt):
        if dt == 0.0:
            return
        for p in self.participants:
            p.n_alpha += p.vel_alpha * dt
            p.n_beta += p.vel_beta * dt
            if p.n_alpha < 0.0:      # rattrape l'arrondi du pas exact
                p.n_alpha = 0.0
            if p.n_beta < 0.0:
                p.n_beta = 0.0

    # -- lecture --------------------------------------------------------

    def totals(self):
        """Les deux sommes que le mécanisme conserve (principe 1)."""
        return (sum(p.n_alpha for p in self.participants),
                sum(p.n_beta for p in self.participants))


# ----------------------------------------------------------------------
# Démonstration et vérifications
# ----------------------------------------------------------------------

def _demo():
    market = Market([
        Participant("Alice",  estimate=2.00, degree=75.0, n_alpha=100.0, n_beta=50.0),
        Participant("Bob",    estimate=1.00, degree=50.0, n_alpha=80.0,  n_beta=80.0),
        Participant("Carol",  estimate=3.50, degree=90.0, n_alpha=10.0,  n_beta=200.0),
        Participant("Dan",    estimate=1.50, degree=0.0,  n_alpha=40.0,  n_beta=40.0),
    ], reference_velocity=1.0)

    a0, b0 = market.totals()
    market.inner()

    print("=== état initial ===")
    print(f"prix du marché [α/β]_Ω = {market.price:.6f} α par β")
    print(f"poids total W_Ω = {market.total_weight:.6f}  (degré agrégé Θ_Ω = {market.total_degree:.3f} %)")
    print()
    print(f"{'participant':<8} {'estimation':>10} {'θ':>7} {'Ẋ^α':>12} {'Ẋ^β':>12} {'Δt':>10}")
    for p in market.participants:
        dt = "∞" if p.dt_empty == math.inf else f"{p.dt_empty:.3f}"
        print(f"{p.name:<8} {p.estimate:>10.4f} {p.degree:>6g}% "
              f"{p.vel_alpha:>12.6f} {p.vel_beta:>12.6f} {dt:>10}")

    # -- les invariants du papier, vérifiés sur cet état ----------------
    print("\n=== vérifications ===")

    net_a = sum(p.vel_alpha for p in market.participants)
    net_b = sum(p.vel_beta for p in market.participants)
    print(f"(13) équilibre     : ΣẊ^α = {net_a:.3e}, ΣẊ^β = {net_b:.3e}")
    assert abs(net_a) < 1e-9 and abs(net_b) < 1e-9

    worst = max((abs(-p.vel_alpha / p.vel_beta - market.price)
                 for p in market.participants if p.trading and p.vel_beta != 0.0),
                default=0.0)
    print(f"(7)  au prix       : max |−Ẋ^α/Ẋ^β − [α/β]_Ω| = {worst:.3e}")
    assert worst < 1e-9

    # (16) le marché entier se comporte comme un participant unique
    probe = 1.234 * market.price
    crowd = sum(p.weight * trader_f(probe / p.estimate) * market.R
                for p in market.participants if p.trading)
    single = market.total_weight * trader_f(probe / market.price) * market.R
    print(f"(16) agrégation    : |crowd − single| = {abs(crowd - single):.3e}")
    assert abs(crowd - single) < 1e-9

    # borne de l'annexe 7.6 : le prix est entre la plus petite et la plus grande estimation
    trading = [p.estimate for p in market.participants if p.trading]
    print(f"(7.6) encadrement  : {min(trading):.4f} ≤ {market.price:.4f} ≤ {max(trading):.4f}")
    assert min(trading) <= market.price <= max(trading)

    # -- on laisse tourner le marché ------------------------------------
    print("\n=== 60 unités de temps plus tard ===")
    trace = []
    market.advance(60.0, trace)
    for t, before, after in trace:
        print(f"  t = {t:9.4f}   un compte se vide : "
              f"[α/β]_Ω passe de {before:.6f} à {after:.6f}")
    print(f"  t = {60.0:9.4f}   fin, [α/β]_Ω = {market.price:.6f}")

    print()
    for p in market.participants:
        print(f"  {p}")

    a1, b1 = market.totals()
    print(f"\n(1) conservation   : Δ(Σn^α) = {a1 - a0:.3e}, Δ(Σn^β) = {b1 - b0:.3e}")
    assert abs(a1 - a0) < 1e-9 and abs(b1 - b0) < 1e-9

    print("\nToutes les vérifications passent.")


if __name__ == "__main__":
    _demo()
