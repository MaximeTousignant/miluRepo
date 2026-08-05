#!/usr/bin/env python
"""Détourage d'une danseuse sur fond fixe — il ne reste qu'elle, sur noir.

Le décor ne bouge pas ; la danseuse, oui. Tout tient dans cette dissymétrie,
lue **pixel par pixel, canal par canal, sur toute la durée**. Les trois canaux
R, G, B sont traités séparément jusqu'au bout ; ils ne se rejoignent qu'à la
toute fin, en une métrique unique qui rend le facteur α ∈ [0, 1] par lequel on
multiplie le pixel — 0 pour « décor », 1 pour « danseuse », et le dégradé entre
les deux pour les bords, les voiles et le flou de mouvement.

L'ouvrage se fait en deux temps : d'abord un travail *par pixel*, où les trois
canaux ne se parlent pas ; puis une décision *globale* sur la frontière, où l'on
part des certitudes et où l'on gagne de proche en proche.

**I. Par pixel, sur toute la durée.** Chaque pixel est lu avec ses huit voisins,
moyennés par un petit noyau gaussien renormalisé sur les bords : le signal qu'on
analyse est celui de ce disque, pas celui d'un capteur isolé. On en tire

1.  la **médiane** sur N images échantillonnées — le décor, partout où la
    danseuse occupe le pixel moins de la moitié du temps ;
2.  les **enveloppes** basse et haute — k-ièmes plus petite et plus grande
    valeurs jamais vues (k = 4, sur *toutes* les images), donc ce que le pixel a
    montré d'extrême sans que ce soit un grain de bruit ;
3.  la **MAD**, déviation absolue médiane, qui donne le plancher de bruit local.
    Le seuil de détection lui est proportionnel : un z-score robuste dont la
    fenêtre est la durée entière.

**II. L'arbitrage**, là où ces trois-là se contredisent. Deux dissymétries les
départagent, toutes deux dues au fait que la danseuse et son ombre stationnent :

4.  si elle occupe un pixel plus de la moitié du temps, c'est *elle* qui
    s'imprime dans la médiane — on le voit à ce que l'enveloppe basse
    s'effondre franchement ; le décor est alors cette enveloppe basse ;
5.  si c'est son **ombre portée** qui stationne, le décor se retrouve plus clair
    que sa propre plaque ; si la médiane n'est qu'une version assombrie de
    l'enveloppe haute, on lui rend sa lumière.

**III. La métrique.** `s = max_canaux |I − P| / plancher`, avec tolérance au
décalage d'un pixel ou deux (on compare à l'intervalle que la plaque prend dans
un petit voisinage) et rejet des ombres portées par un test multiplicatif. Sous
le seuil bas, α = 0 ; au-dessus du seuil haut, α = 1 ; entre les deux, une rampe.

**IV. La frontière, globalement.** Le score est moyenné sur un bloc espace-temps
x·y·t, puis : **hystérésis** — une composante ne survit que si elle contient un
noyau franc, et s'étend ensuite de proche en proche ; **continent** — une
danseuse n'est pas un archipel, seule la plus grande composante et ses
compagnons de poids comparable survivent ; **trous** bouchés avec discernement ;
**topographie** — α descend du plateau vers la plaine sans jamais remonter, des
courbes de niveau qui ne se croisent pas.

**V. Composition.** `sortie = α × image`. Ce qui reste manqué dans les zones
sombres de la danseuse est invisible : le fond de sortie est noir aussi.

Usage :

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 [-o SORTIE.mp4]
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --planche   # 6 vignettes, pas de vidéo
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --apercu    # vidéo + vignettes

Sans ffmpeg sur cette machine : la sortie est muette (la piste audio de
l'entrée n'est pas recopiée).
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np

# ── Réglages par défaut ────────────────────────────────────────────────────────
N_ECHANTILLONS = 120      # images tirées pour la médiane temporelle
K_MINIMA = 4              # rang du minimum retenu pour l'enveloppe basse
SEUIL_HAUT = 6.0          # α = 1 au-delà, en multiples du plancher de bruit
SEUIL_BAS = 2.5           # α = 0 en-deçà ; entre les deux, une rampe
PLANCHER_MIN = 3.0        # plancher de bruit minimal (niveaux 0-255)
PLANCHER_MAX = 22.0       # au-delà, la zone deviendrait aveugle
AIRE_MIN_REL = 3e-4       # composante gardée si son aire dépasse ce ratio
ILOT_RELATIF = 0.25       # ... et si elle pèse au moins ce quart du continent
TROU_MAX_REL = 4e-3       # trou bouché en zone claire si son aire est sous ce ratio
TOL_DECALAGE = 5          # voisinage toléré si le décor glisse d'un pixel ou deux
LISSAGE_XY = 5            # noyau spatial de la décision (bloc x·y·t)
LISSAGE_T = 3             # profondeur temporelle de la décision (images, impair)
FLOU_BORD = 5             # noyau du flou de bord (impair, 0 = bord franc)
FOND_CLAIR = 15           # au-delà, le décor n'est plus noir : il porte des ombres,
                          # et le découvrir se verrait — deux conséquences, un seuil
OMBRE_RATIO = (0.05, 0.94)  # une ombre assombrit sans changer la couleur
OMBRE_TOL = (6.0, 0.18)   # tolérance d'ombre : absolue, puis relative à la luminance
CONTAMINE_ECART = 60      # écart de luminance à partir duquel on arbitre
OMBRE_ECART = 10          # ... et à partir duquel on rend au décor sa lumière
OMBRE_RATIO_HAUT = 0.45   # une ombre assombrit ; un voile éclatant, non
BORD_LARGEUR = 6.0        # pixels sur lesquels α descend du plateau à la plaine
# Noyau de moyennage du voisinage immédiat : chaque pixel est lu avec ses huit
# voisins, pondérés en gaussienne. Le signal temporel qu'on analyse ensuite est
# celui de ce petit disque, pas celui d'un capteur isolé — le grain tombe d'un
# facteur ~2,5, et la décision porte sur quelque chose de spatialement réel.
NOYAU = np.array([[0.07021169894, 0.1198588674, 0.07021169894],
                  [0.1198588674,  0.2397177347, 0.1198588674],
                  [0.07021169894, 0.1198588674, 0.07021169894]], np.float32)
CONTAMINE_RATIO = 0.30    # ... et effondrement de l'enveloppe basse exigé
CONTAMINE_OUVERTURE = 15  # ouverture morphologique de la carte des contaminés
CONTAMINE_COMBLE = 0.055  # voisinage du minimum comblant, en fraction du grand côté


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _luma(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=2)


_NORMES: dict[tuple[int, int], np.ndarray] = {}


def _lisse(img: np.ndarray) -> np.ndarray:
    """Moyennage du voisinage immédiat — l'espace où vit toute l'analyse.

    Sur les bords et dans les coins, une partie du noyau tombe hors de l'image :
    on n'invente pas les voisins manquants, on convole à zéro puis on divise par
    le poids réellement recueilli. Le noyau s'y trouve tronqué et renormalisé —
    un pixel de coin n'est moyenné qu'avec les trois voisins qu'il a.
    """
    forme = img.shape[:2]
    if forme not in _NORMES:
        _NORMES[forme] = cv2.filter2D(np.ones(forme, np.float32), -1, NOYAU,
                                      borderType=cv2.BORDER_CONSTANT)
    num = cv2.filter2D(img.astype(np.float32), -1, NOYAU, borderType=cv2.BORDER_CONSTANT)
    norme = _NORMES[forme]
    return num / (norme[..., None] if num.ndim == 3 else norme)


def _impair(x: float) -> int:
    return max(3, int(x) | 1)


def _ellipse(n: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))


def _est_ombre(img: np.ndarray, plaque: np.ndarray) -> np.ndarray:
    """Vrai si `img` est `plaque` simplement assombrie — même couleur, moins de lumière.

    Le modèle physique de l'ombre est multiplicatif : I ≈ k·P avec 0 < k < 1, le
    même k sur les trois canaux. On estime k par le rapport des luminances, puis
    on vérifie canal par canal que k·P retombe bien sur I. Tester la couleur par
    différence absolue échouerait sur les ombres profondes, où tout s'écrase.
    """
    k = _luma(img) / np.maximum(_luma(plaque), 1.0)
    tol = np.maximum(OMBRE_TOL[0], OMBRE_TOL[1] * _luma(img))
    ecart = np.max(np.abs(img - k[..., None] * plaque), axis=2)
    return (k > OMBRE_RATIO[0]) & (k < OMBRE_RATIO[1]) & (ecart < tol)


# ── 1. L'enveloppe basse, sur toute la durée ───────────────────────────────────
def enveloppes(chemin: Path, k: int = K_MINIMA, pas: int = 1
               ) -> tuple[np.ndarray, np.ndarray]:
    """k-ièmes plus petite et plus grande valeurs vues par chaque pixel, par canal.

    On a essayé d'écarter les ombres portées de l'enveloppe basse, en n'y admettant
    que les valeurs qui ne sont pas une version assombrie de la médiane. C'était
    une erreur : sur une toile *grise*, le décor lui-même est indiscernable d'un
    voile crème assombri — même teinte neutre, moindre intensité —, et l'enveloppe
    se refusait justement les images qui disaient vrai. Les enveloppes restent donc
    naïves ; c'est l'arbitrage qui porte le discernement.
    """
    cap = cv2.VideoCapture(str(chemin))
    bas = haut = None
    i = 0
    while True:
        ok, img = cap.read()
        if not ok:
            break
        if i % pas == 0:
            f = _lisse(img)
            if bas is None:
                bas = np.full((k,) + f.shape, 255.0, np.float32)
                haut = np.zeros((k,) + f.shape, np.float32)
            reste = f
            for j in range(k):                     # insertion dans une liste triée
                dessous = reste < bas[j]
                suivant = np.where(dessous, bas[j], reste)
                bas[j] = np.where(dessous, reste, bas[j])
                reste = suivant
            reste = f
            for j in range(k):                     # ... et son miroir par le haut
                dessus = reste > haut[j]
                suivant = np.where(dessus, haut[j], reste)
                haut[j] = np.where(dessus, reste, haut[j])
                reste = suivant
        i += 1
    cap.release()
    if bas is None:
        raise RuntimeError(f"aucune image lisible : {chemin}")
    return bas[k - 1], haut[k - 1]


# ── 2. La médiane temporelle ───────────────────────────────────────────────────
def _empile(cap: cv2.VideoCapture, indices: np.ndarray) -> np.ndarray:
    pile = []
    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, img = cap.read()
        if ok:
            pile.append(_lisse(img).astype(np.float32))
    return np.stack(pile)


def _mediane_et_mad(pile: np.ndarray, bande: int = 48) -> tuple[np.ndarray, np.ndarray]:
    """Médiane et MAD temporelles, par bandes horizontales pour tenir en mémoire."""
    _, h, w, c = pile.shape
    med = np.empty((h, w, c), np.float32)
    mad = np.empty((h, w, c), np.float32)
    for y in range(0, h, bande):
        bloc = pile[:, y:y + bande]
        m = np.median(bloc, axis=0)
        med[y:y + bande] = m
        mad[y:y + bande] = np.median(np.abs(bloc - m), axis=0)
        del bloc
    return med, mad


# ── 3-4. La plaque et son plancher de bruit ────────────────────────────────────
def bati_le_fond(chemin: Path, n_echantillons: int = N_ECHANTILLONS, pas_minima: int = 1
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rend (plaque, plancher, contaminés) — float32 (h,w,3), (h,w,3), (h,w) bool."""
    cap = cv2.VideoCapture(str(chemin))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = min(n_echantillons, max(total, 1))
    _log(f"  médiane temporelle : {n} images sur {total}")
    pile = _empile(cap, np.linspace(0, max(total - 1, 0), n).astype(int))
    cap.release()
    med, mad = _mediane_et_mad(pile)
    del pile

    _log("  enveloppes basse et haute : balayage de toute la durée")
    bas, haut = enveloppes(chemin, pas=pas_minima)

    # Arbitrage : la médiane a-t-elle avalé la danseuse ? Oui si l'écart de
    # luminance est franc ET si l'enveloppe basse s'est effondrée — une ombre,
    # elle, garde une part de la lumière du décor. L'ouverture morphologique
    # achève le tri : la contamination est une tache compacte, l'ombre profonde
    # sur le tapis est un mouchetis.
    lb, lm = _luma(bas), _luma(med)
    contamine = ((lm - lb > CONTAMINE_ECART)
                 & (lb / np.maximum(lm, 1.0) < CONTAMINE_RATIO)).astype(np.uint8)
    contamine = cv2.morphologyEx(contamine, cv2.MORPH_OPEN, _ellipse(CONTAMINE_OUVERTURE))
    contamine = cv2.morphologyEx(contamine, cv2.MORPH_CLOSE, _ellipse(CONTAMINE_OUVERTURE))
    # Un îlot que la danseuse ne quitte *jamais* n'a même pas d'enveloppe basse
    # effondrée : il n'est pas détecté, et se présente comme un trou au milieu
    # des contaminés. On bouche donc la carte avant de s'en servir.
    contamine = np.maximum(contamine, _trous(contamine)).astype(bool)

    # Là où la danseuse ne s'absente *jamais*, même l'enveloppe basse garde sa
    # couleur : un îlot clair au milieu d'une zone dont le décor est, par
    # construction, la toile sombre. Un minimum sur large voisinage le comble —
    # on ne l'applique qu'à l'intérieur des contaminés, où c'est sans risque.
    comble = cv2.erode(bas, _ellipse(_impair(CONTAMINE_COMBLE * max(bas.shape[:2]))))

    # Le symétrique existe : là où l'ombre portée stationne plus de la moitié du
    # temps, c'est *elle* qui s'imprime dans la médiane, et le décor se retrouve
    # plus clair que sa propre plaque — chaque fois qu'elle s'en va, la toile nue
    # passerait pour un objet. Si la médiane est une version assombrie de
    # l'enveloppe haute, on rend au décor sa lumière.
    lh = _luma(haut)
    sous_ombre = (~contamine & (lh - lm > OMBRE_ECART)
                  & (lm / np.maximum(lh, 1.0) > OMBRE_RATIO_HAUT)
                  & _est_ombre(med, haut))
    plaque = np.where(contamine[..., None], comble,
                      np.where(sous_ombre[..., None], haut, med))
    _log(f"  sous l'ombre : {100 * sous_ombre.mean():.2f} % de l'image")
    plancher = np.clip(1.4826 * mad, PLANCHER_MIN, PLANCHER_MAX)
    plancher[contamine] = PLANCHER_MIN          # une MAD contaminée ne dit rien
    _log(f"  contaminés : {100 * contamine.mean():.2f} % de l'image")
    return plaque, plancher, contamine


# ── 5. La métrique, puis α ─────────────────────────────────────────────────────
def _score(img: np.ndarray, bas: np.ndarray, haut: np.ndarray, plancher: np.ndarray,
           plaque: np.ndarray, clair: np.ndarray) -> np.ndarray:
    """`max_c` de l'écart normalisé au décor, avec tolérance au décalage d'un pixel.

    Comparer un pixel au seul pixel de même adresse rend le tapis explosif : qu'il
    glisse d'un pixel ou deux sous le pied, et sa texture chargée s'allume toute
    entière. On compare donc à l'*intervalle* que la plaque prend dans un petit
    voisinage — érodée d'un côté, dilatée de l'autre. Sur la toile noire et lisse,
    l'intervalle est plat : on n'y perd aucune finesse.
    """
    f = _lisse(img)                                # même espace que les statistiques
    ecart = np.maximum(np.maximum(bas - f, f - haut), 0.0) / plancher   # par canal
    score = np.max(ecart, axis=2)                                       # une métrique
    if clair.any():   # une ombre portée sur le décor clair n'est pas la danseuse
        score = np.where(clair & _est_ombre(f, plaque), 0.0, score)
    return score


def _seuille(score: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rend (α brut, graine, pousse) : la rampe continue et ses deux seuillages."""
    alpha = np.clip((score - SEUIL_BAS) / max(SEUIL_HAUT - SEUIL_BAS, 1e-6), 0.0, 1.0)
    return alpha, (score > SEUIL_HAUT).astype(np.uint8), (score > SEUIL_BAS).astype(np.uint8)


def _hysteresis(graine: np.ndarray, pousse: np.ndarray) -> np.ndarray:
    """Garde les composantes de `pousse` qui contiennent au moins une graine."""
    if not graine.any():
        return np.zeros_like(graine)
    n, labels = cv2.connectedComponents(pousse, connectivity=8)
    gardes = np.unique(labels[graine.astype(bool)])
    gardes = gardes[gardes != 0]
    if n <= 1 or gardes.size == 0:
        return np.zeros_like(graine)
    table = np.zeros(n, np.uint8)
    table[gardes] = 1
    return table[labels]


def _trous(m: np.ndarray) -> np.ndarray:
    """Composantes de fond qui ne touchent aucun bord : les trous du masque."""
    h, w = m.shape
    depart = np.where(m == 0, 255, 0).astype(np.uint8)
    remplissage = np.zeros((h + 2, w + 2), np.uint8)
    for germe in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if depart[germe[1], germe[0]] == 255:
            cv2.floodFill(depart, remplissage, germe, 0)
    return (depart == 255).astype(np.uint8)


def _discipline(graine: np.ndarray, pousse: np.ndarray, sombre: np.ndarray,
                aire_min: int, trou_max: int) -> tuple[np.ndarray, np.ndarray]:
    """Rend (masque net, trous bouchés) — le domaine où α a le droit de vivre."""
    m = _hysteresis(graine, pousse)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, _ellipse(3))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, _ellipse(9))

    # Une danseuse est un continent, pas un archipel : une seule composante
    # survit — la plus grande —, et les îlots qui flottent au large sont du
    # décor mal lu. On tolère seulement les compagnons d'un poids comparable,
    # au cas où un bras se détacherait sur un fond peu contrasté.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 1:
        aires = stats[1:, cv2.CC_STAT_AREA]
        seuil = max(aire_min, ILOT_RELATIF * float(aires.max()))
        gardes = np.nonzero(aires >= seuil)[0] + 1
        if gardes.size == 0:
            gardes = np.array([1 + int(np.argmax(aires))])
        table = np.zeros(n, np.uint8)
        table[gardes] = 1
        m = table[labels]

    # Un trou dont le décor est sombre se bouche sans risque : ce qu'on y laisse
    # voir est déjà noir. Sur le décor clair — le tapis, le sol — on ne bouche
    # que les petits, sous peine d'y ramener du tapis.
    trous = _trous(m)
    if trous.any():
        garde = (trous & sombre).astype(np.uint8)
        nt, tl, ts, _ = cv2.connectedComponentsWithStats(trous, connectivity=8)
        if nt > 1:
            petits = np.nonzero(ts[1:, cv2.CC_STAT_AREA] < trou_max)[0] + 1
            table = np.zeros(nt, np.uint8)
            table[petits] = 1
            garde |= table[tl]
        trous = garde
        m = np.maximum(m, trous)
    return m, trous


# ── 6. La composition ──────────────────────────────────────────────────────────
def detoure(entree: Path, sortie: Path, *, n_echantillons: int = N_ECHANTILLONS,
            max_images: int | None = None, flou_bord: int = FLOU_BORD,
            apercu: bool = False, planche_seule: bool = False,
            pas_minima: int = 1) -> None:
    t0 = time.time()
    _log(f"» {entree.name}")
    plaque, plancher, _ = bati_le_fond(entree, n_echantillons, pas_minima)
    clair = _luma(plaque) > FOND_CLAIR
    sombre = (~clair).astype(np.uint8)
    p_bas = cv2.erode(plaque, _ellipse(TOL_DECALAGE))    # l'intervalle que la plaque
    p_haut = cv2.dilate(plaque, _ellipse(TOL_DECALAGE))  # prend dans le voisinage

    cap = cv2.VideoCapture(str(entree))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if max_images:
        total = min(total, max_images)

    aire_min = int(AIRE_MIN_REL * w * h)
    trou_max = int(TROU_MAX_REL * w * h)
    jalons = sorted(set(np.linspace(0, max(total - 1, 0), 6).astype(int).tolist()))
    vignettes: list[np.ndarray] = []

    sortie.parent.mkdir(parents=True, exist_ok=True)
    ecrivain = None
    if not planche_seule:
        ecrivain = cv2.VideoWriter(str(sortie), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        if not ecrivain.isOpened():
            raise RuntimeError(f"écriture impossible : {sortie}")

    def alpha_de(scores: list[np.ndarray]) -> np.ndarray:
        """α de l'image du milieu, décidé sur le bloc espace-temps qui l'entoure."""
        # La décision se prend sur le score moyenné dans le temps puis lissé dans
        # l'espace — une convolution sur le bloc x·y·t. Ce qui scintille sans
        # durer ni s'étendre s'y éteint ; la danseuse, large et persistante, non.
        bloc = scores[len(scores) // 2] if len(scores) == 1 else np.mean(scores, axis=0)
        if LISSAGE_XY >= 3:
            bloc = cv2.blur(bloc, (LISSAGE_XY, LISSAGE_XY))
        _, graine, pousse = _seuille(bloc)
        m, trous = _discipline(graine, pousse, sombre, aire_min, trou_max)
        # ... mais la valeur de α vient du score net de l'image, pour garder le
        # tranchant du bord, les voiles et le flou de mouvement.
        brut, _, _ = _seuille(scores[len(scores) // 2])

        # Une carte topographique : le plateau à 1, la plaine à 0, et entre les
        # deux des courbes de niveau qui ne se croisent pas. On l'impose par la
        # distance au plateau — α ne peut que descendre en s'en éloignant, jamais
        # remonter. Ce que la mesure propose au-delà de la pente est écrêté.
        plateau = np.maximum(graine * m, trous)
        if plateau.any():
            loin = cv2.distanceTransform(1 - plateau, cv2.DIST_L2, 3)
            descente = np.clip(1.0 - loin / max(BORD_LARGEUR, 1e-6), 0.0, 1.0)
        else:
            descente = np.zeros_like(brut)
        alpha = np.minimum(brut, descente) * m
        return np.maximum(alpha, plateau).astype(np.float32)

    ecrites = 0

    def pose(img: np.ndarray, a: np.ndarray, i: int) -> None:
        nonlocal ecrites
        if flou_bord >= 3:
            a = cv2.GaussianBlur(a, (flou_bord, flou_bord), 0)
        out = (img.astype(np.float32) * a[..., None]).astype(np.uint8)
        if ecrivain is not None:
            ecrivain.write(out)
            ecrites += 1
        if (apercu or planche_seule) and i in jalons:
            vignettes.append(cv2.resize(out, (w // 3, h // 3)))

    def score_de(img: np.ndarray) -> np.ndarray:
        return _score(img, p_bas, p_haut, plancher, plaque, clair)

    if planche_seule:                              # six instants, rien d'autre
        for i in jalons:
            fenetre = []
            for j in range(i - LISSAGE_T // 2, i + LISSAGE_T // 2 + 1):
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(j, total - 1)))
                ok, im = cap.read()
                if ok:
                    fenetre.append((im, score_de(im)))
            if fenetre:
                milieu = len(fenetre) // 2
                pose(fenetre[milieu][0], alpha_de([s for _, s in fenetre]), i)
    else:
        tampon: deque[tuple[np.ndarray, np.ndarray]] = deque(maxlen=LISSAGE_T)
        milieu = LISSAGE_T // 2
        for i in range(total):
            ok, img = cap.read()
            if not ok:
                break
            tampon.append((img, score_de(img)))
            if len(tampon) == LISSAGE_T:
                pose(tampon[milieu][0], alpha_de([s for _, s in tampon]), i - milieu)
            elif len(tampon) == 1:                 # la toute première
                pose(tampon[0][0], alpha_de([tampon[0][1]]), 0)
            if i % 100 == 0:
                _log(f"  image {i}/{total}  ({time.time() - t0:.0f} s)")
        for j in range(milieu + 1, len(tampon)):   # les dernières, sans fenêtre pleine
            pose(tampon[j][0], alpha_de([tampon[j][1]]), total - len(tampon) + j)

    cap.release()
    if ecrivain is not None:
        ecrivain.release()

    if vignettes:
        if len(vignettes) >= 6:
            planche = np.vstack([np.hstack(vignettes[:3]), np.hstack(vignettes[3:6])])
        else:
            planche = np.hstack(vignettes)
        chemin = sortie.with_suffix(".planche.jpg")
        chemin.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(chemin), planche, [cv2.IMWRITE_JPEG_QUALITY, 88])
        _log(f"  planche : {chemin}")

    if ecrivain is not None:
        _log(f"  fini : {sortie}  ({ecrites} images, {time.time() - t0:.0f} s)")
    else:
        _log(f"  fini en {time.time() - t0:.0f} s")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Détourage sur fond fixe, sortie sur noir.")
    p.add_argument("entrees", nargs="+", type=Path, help="vidéo(s) d'entrée")
    p.add_argument("-o", "--sortie", type=Path, default=None,
                   help="fichier .mp4 de sortie (une seule entrée) ou dossier de sortie")
    p.add_argument("--echantillons", type=int, default=N_ECHANTILLONS,
                   help=f"images pour la médiane temporelle (défaut {N_ECHANTILLONS})")
    p.add_argument("--pas-minima", type=int, default=1,
                   help="ne lire qu'une image sur N pour l'enveloppe basse (défaut 1)")
    p.add_argument("--max-images", type=int, default=None,
                   help="ne traiter que les N premières images (prototypage)")
    p.add_argument("--flou-bord", type=int, default=FLOU_BORD,
                   help=f"noyau du flou de bord, impair, 0 = franc (défaut {FLOU_BORD})")
    p.add_argument("--apercu", action="store_true",
                   help="écrire aussi une planche de 6 vignettes")
    p.add_argument("--planche", action="store_true",
                   help="n'écrire QUE la planche de 6 vignettes, pas de vidéo")
    a = p.parse_args(argv)

    for entree in a.entrees:
        if not entree.exists():
            _log(f"introuvable : {entree}")
            return 1
        if a.sortie is None:
            sortie = entree.with_name(f"{entree.stem}_nobg.mp4")
        elif a.sortie.suffix.lower() == ".mp4" and len(a.entrees) == 1:
            sortie = a.sortie
        else:
            sortie = a.sortie / f"{entree.stem}_nobg.mp4"
        detoure(entree, sortie, n_echantillons=a.echantillons, max_images=a.max_images,
                flou_bord=a.flou_bord, apercu=a.apercu, planche_seule=a.planche,
                pas_minima=a.pas_minima)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
