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

**I. Le décor, par pixel, sur toute la durée.** Chaque pixel est lu avec ses
huit voisins, moyennés par un petit noyau gaussien renormalisé sur les bords :
le signal qu'on analyse est celui de ce disque, pas celui d'un capteur isolé.
On en tire la **médiane** (le décor, partout où la danseuse occupe le pixel
moins de la moitié du temps), les **enveloppes** basse et haute (k-ièmes valeurs
extrêmes jamais vues, donc à l'abri du grain), et la **MAD**, qui donne le
plancher de bruit local — un z-score robuste dont la fenêtre est la durée
entière. Puis l'**arbitrage**, là où ces trois-là se contredisent : la danseuse
stationne, son ombre aussi, et chacune s'imprime dans la médiane à sa manière.

**II. La métrique.** `s = max_canaux |I − P| / plancher`, avec tolérance au
décalage d'un pixel ou deux et rejet des ombres portées. Sous le seuil bas,
α = 0 ; au-dessus du seuil haut, α = 1 ; entre les deux, une rampe.

**III. La frontière, globalement.** Le score est moyenné sur un bloc espace-temps
x·y·t, puis : **hystérésis** — une composante ne survit que si elle contient un
noyau franc, et s'étend ensuite de proche en proche ; **continent** — une
danseuse n'est pas un archipel ; **trous** bouchés avec discernement ;
**topographie** — α descend du plateau vers la plaine sans jamais remonter, des
courbes de niveau qui ne se croisent pas.

**IV. Le bord**, recalé sur les arêtes de l'image par filtre guidé.

**V. En option (`--rvm`)**, tout cela se fusionne avec RobustVideoMatting, qui
sait ce qu'est une personne là où nous ne savons que ce qui a changé — et qu'on
rejoue à rebrousse-temps, puisque nous n'avons pas sa contrainte de causalité.

**VI. Composition.** `sortie = α × image`. Ce qui reste manqué dans les zones
sombres de la danseuse est peu visible : le fond de sortie est noir aussi.

Usage :

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 [-o SORTIE.mp4]
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --planche   # 6 vignettes, pas de vidéo
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --rvm       # fusion avec le matteur
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --rvm-seul  # le matteur seul, étalon

Sans ffmpeg sur cette machine : la sortie est muette (la piste audio de
l'entrée n'est pas recopiée).
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

# ── Réglages ───────────────────────────────────────────────────────────────────
# I. Lecture du signal — le voisinage immédiat de chaque pixel, pondéré en
# gaussienne. Ce qu'on analyse ensuite est le signal temporel de ce petit disque,
# pas celui d'un capteur isolé : le grain tombe d'un facteur ~2,5, et la décision
# porte sur quelque chose de spatialement réel.
NOYAU = np.array([[0.07021169894, 0.1198588674, 0.07021169894],
                  [0.1198588674,  0.2397177347, 0.1198588674],
                  [0.07021169894, 0.1198588674, 0.07021169894]], np.float32)
N_ECHANTILLONS = 120      # images tirées pour la médiane temporelle
K_ENVELOPPE = 4           # rang de l'extrême retenu pour les enveloppes
PLANCHER_MIN = 3.0        # plancher de bruit minimal (niveaux 0-255)
PLANCHER_MAX = 22.0       # au-delà, la zone deviendrait aveugle

# I bis. Arbitrage — les deux endroits où la médiane ment.
CONTAMINE_ECART = 60      # écart de luminance à partir duquel on soupçonne
CONTAMINE_RATIO = 0.30    # ... et effondrement de l'enveloppe basse exigé
CONTAMINE_OUVERTURE = 15  # ouverture morphologique de la carte des contaminés
CONTAMINE_COMBLE = 0.055  # voisinage du minimum comblant, en fraction du grand côté
OMBRE_ECART = 10          # écart à partir duquel on rend au décor sa lumière
OMBRE_RATIO_HAUT = 0.45   # une ombre assombrit ; un voile éclatant, non

# Ombres portées — le même fait physique lu deux fois, RGB puis HSV.
FOND_CLAIR = 15           # au-delà, le décor n'est plus noir : il porte des ombres,
                          # et le découvrir se verrait — deux conséquences, un seuil
OMBRE_RATIO = (0.05, 0.94)  # une ombre assombrit sans changer la couleur
OMBRE_TOL = (6.0, 0.18)   # tolérance d'ombre : absolue, puis relative à la luminance
OMBRE_SATURATION = 20     # une ombre n'augmente pas la saturation (Cucchiara)
OMBRE_TEINTE = 40         # ... et ne déplace la teinte que peu (degrés)

# II. Métrique et seuils.
SEUIL_HAUT = 6.0          # α = 1 au-delà, en multiples du plancher de bruit
SEUIL_BAS = 2.5           # α = 0 en-deçà ; entre les deux, une rampe
TOL_DECALAGE = 5          # voisinage toléré si le décor glisse d'un pixel ou deux

# III. Frontière.
LISSAGE_XY = 5            # noyau spatial de la décision (bloc x·y·t)
LISSAGE_T = 3             # profondeur temporelle de la décision (images, impair)
AIRE_MIN_REL = 3e-4       # composante gardée si son aire dépasse ce ratio
ILOT_RELATIF = 0.25       # ... et si elle pèse au moins ce quart du continent
TROU_MAX_REL = 4e-3       # trou bouché en zone claire si son aire est sous ce ratio
BORD_LARGEUR = 6.0        # pixels sur lesquels α descend du plateau à la plaine

# IV. Bord.
FLOU_BORD = 5             # rayon du recalage de bord (0 = bord franc)
GUIDE_EPS = 1e-3          # tolérance du filtre guidé : petit = colle aux arêtes

# V. Matteur (option --rvm).
RVM_RATIO = 0.5           # sous-échantillonnage interne du réseau
RVM_PORTE = 0.10          # au-dessus, le réseau reconnaît la personne
RVM_DILATE = 11           # marge laissée autour d'elle, contre ses propres ratés

# VI. Rendu.
VIGNETTES = 6             # instants de la planche de contrôle
REDUCTION = 3             # facteur de réduction des vignettes


# ── Petits outils ──────────────────────────────────────────────────────────────
def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _luma(x: np.ndarray) -> np.ndarray:
    return x.mean(axis=2)


def _impair(x: float) -> int:
    return max(3, int(x) | 1)


def _ellipse(n: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))


def _hsv(x: np.ndarray) -> np.ndarray:
    """Teinte (0-360), saturation (0-255), valeur (0-255), en float32."""
    return cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV_FULL
                        ).astype(np.float32) * np.array([360 / 255, 1, 1], np.float32)


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


def est_ombre(img: np.ndarray, plaque: np.ndarray) -> np.ndarray:
    """Vrai si `img` est `plaque` simplement assombrie — même couleur, moins de lumière.

    Deux lectures du même fait physique, et il faut les deux :

    - **multiplicative, en RGB.** Une ombre, c'est I ≈ k·P avec 0 < k < 1, le même
      k sur les trois canaux. On estime k par le rapport des luminances, puis on
      vérifie canal par canal que k·P retombe sur I. Tester la couleur par simple
      différence absolue échouerait sur les ombres profondes, où tout s'écrase.
    - **en HSV, selon Cucchiara et al.** — une ombre fait chuter la *valeur*, ne
      bouge la *teinte* que très peu, et *abaisse* la saturation. Ce dernier point
      est le plus discriminant, et il est invisible au test multiplicatif : un
      objet sombre et coloré posé sur le décor a la même luminance qu'une ombre,
      mais pas la même saturation.

    Un pixel n'est déclaré ombre que si les deux lectures concordent.
    """
    k = _luma(img) / np.maximum(_luma(plaque), 1.0)
    tol = np.maximum(OMBRE_TOL[0], OMBRE_TOL[1] * _luma(img))
    ecart = np.max(np.abs(img - k[..., None] * plaque), axis=2)
    multiplicatif = (k > OMBRE_RATIO[0]) & (k < OMBRE_RATIO[1]) & (ecart < tol)

    hi, hp = _hsv(img), _hsv(plaque)
    dteinte = np.abs(hi[..., 0] - hp[..., 0])
    dteinte = np.minimum(dteinte, 360.0 - dteinte)          # la teinte est un cercle
    ratio_v = hi[..., 2] / np.maximum(hp[..., 2], 1.0)
    cucchiara = ((ratio_v > OMBRE_RATIO[0]) & (ratio_v < OMBRE_RATIO[1])
                 & (hi[..., 1] - hp[..., 1] < OMBRE_SATURATION)
                 & (dteinte < OMBRE_TEINTE))
    return multiplicatif & cucchiara


# ── I. Le décor ────────────────────────────────────────────────────────────────
@dataclass
class Decor:
    """Ce qu'on sait de la scène vide, et tout ce qui s'en déduit.

    `plaque` est le décor lui-même ; `plancher` le bruit qu'on lui tolère, par
    canal. `bas` et `haut` sont la plaque érodée et dilatée : l'*intervalle*
    qu'elle prend dans un petit voisinage, pour ne pas s'affoler si le décor
    glisse d'un pixel. `clair` marque les pixels dont le décor n'est pas noir —
    ceux qui peuvent porter une ombre, et qu'on verrait si on les découvrait.
    """

    plaque: np.ndarray
    plancher: np.ndarray
    contamine: np.ndarray
    bas: np.ndarray = field(init=False)
    haut: np.ndarray = field(init=False)
    clair: np.ndarray = field(init=False)
    sombre: np.ndarray = field(init=False)
    aire_min: int = field(init=False)
    trou_max: int = field(init=False)

    def __post_init__(self) -> None:
        self.bas = cv2.erode(self.plaque, _ellipse(TOL_DECALAGE))
        self.haut = cv2.dilate(self.plaque, _ellipse(TOL_DECALAGE))
        self.clair = _luma(self.plaque) > FOND_CLAIR
        self.sombre = (~self.clair).astype(np.uint8)
        pixels = self.plaque.shape[0] * self.plaque.shape[1]
        self.aire_min = int(AIRE_MIN_REL * pixels)
        self.trou_max = int(TROU_MAX_REL * pixels)


def enveloppes(chemin: Path, k: int = K_ENVELOPPE, pas: int = 1
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
            for tampon, dessus in ((bas, False), (haut, True)):
                reste = f                          # insertion dans une liste triée
                for j in range(k):
                    remplace = reste > tampon[j] if dessus else reste < tampon[j]
                    suivant = np.where(remplace, tampon[j], reste)
                    tampon[j] = np.where(remplace, reste, tampon[j])
                    reste = suivant
        i += 1
    cap.release()
    if bas is None:
        raise RuntimeError(f"aucune image lisible : {chemin}")
    return bas[k - 1], haut[k - 1]


def _empile(cap: cv2.VideoCapture, indices: np.ndarray) -> np.ndarray:
    pile = []
    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, img = cap.read()
        if ok:
            pile.append(_lisse(img))
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


def bati_le_decor(chemin: Path, n_echantillons: int = N_ECHANTILLONS,
                  pas: int = 1) -> Decor:
    """Médiane, enveloppes, MAD — puis l'arbitrage entre elles."""
    cap = cv2.VideoCapture(str(chemin))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = min(n_echantillons, max(total, 1))
    _log(f"  médiane temporelle : {n} images sur {total}")
    pile = _empile(cap, np.linspace(0, max(total - 1, 0), n).astype(int))
    cap.release()
    med, mad = _mediane_et_mad(pile)
    del pile

    _log("  enveloppes basse et haute : balayage de toute la durée")
    bas, haut = enveloppes(chemin, pas=pas)
    lb, lm, lh = _luma(bas), _luma(med), _luma(haut)

    # Premier mensonge de la médiane : la danseuse stationne, donc c'est *elle*
    # qui s'y imprime. On le voit à ce que l'enveloppe basse s'effondre — une
    # ombre, elle, garde une part de la lumière du décor. L'ouverture achève le
    # tri : la contamination est une tache compacte, l'ombre profonde un mouchetis.
    contamine = ((lm - lb > CONTAMINE_ECART)
                 & (lb / np.maximum(lm, 1.0) < CONTAMINE_RATIO)).astype(np.uint8)
    contamine = cv2.morphologyEx(contamine, cv2.MORPH_OPEN, _ellipse(CONTAMINE_OUVERTURE))
    contamine = cv2.morphologyEx(contamine, cv2.MORPH_CLOSE, _ellipse(CONTAMINE_OUVERTURE))
    # Un îlot qu'elle ne quitte *jamais* n'a même pas d'enveloppe basse effondrée :
    # il n'est pas détecté, et se présente comme un trou au milieu des contaminés.
    # On bouche donc la carte, puis on comble l'îlot par un minimum sur large
    # voisinage — sans risque là-dedans, où le décor est par construction la toile.
    contamine = np.maximum(contamine, _trous(contamine)).astype(bool)
    comble = cv2.erode(bas, _ellipse(_impair(CONTAMINE_COMBLE * max(bas.shape[:2]))))

    # Second mensonge, symétrique : c'est l'*ombre portée* qui stationne, et le
    # décor se retrouve plus clair que sa propre plaque — chaque fois qu'elle s'en
    # va, la toile nue passerait pour un objet. Si la médiane n'est qu'une version
    # assombrie de l'enveloppe haute, on rend au décor sa lumière.
    sous_ombre = (~contamine & (lh - lm > OMBRE_ECART)
                  & (lm / np.maximum(lh, 1.0) > OMBRE_RATIO_HAUT)
                  & est_ombre(med, haut))

    plaque = np.where(contamine[..., None], comble,
                      np.where(sous_ombre[..., None], haut, med))
    plancher = np.clip(1.4826 * mad, PLANCHER_MIN, PLANCHER_MAX)
    plancher[contamine] = PLANCHER_MIN          # une MAD contaminée ne dit rien
    _log(f"  contaminés : {100 * contamine.mean():.2f} %"
         f" · sous l'ombre : {100 * sous_ombre.mean():.2f} %")
    return Decor(plaque, plancher, contamine)


# ── II. La métrique ────────────────────────────────────────────────────────────
def score(img: np.ndarray, decor: Decor) -> np.ndarray:
    """`max_c` de l'écart normalisé au décor, avec tolérance au décalage d'un pixel.

    Comparer un pixel au seul pixel de même adresse rend un tapis explosif : qu'il
    glisse d'un pixel ou deux sous le pied, et sa texture chargée s'allume toute
    entière. On compare donc à l'*intervalle* que la plaque prend dans un petit
    voisinage. Sur une toile noire et lisse, l'intervalle est plat : on n'y perd
    aucune finesse.
    """
    f = _lisse(img)                                # même espace que les statistiques
    ecart = np.maximum(np.maximum(decor.bas - f, f - decor.haut), 0.0) / decor.plancher
    s = np.max(ecart, axis=2)                      # trois canaux, puis une métrique
    if decor.clair.any():   # une ombre portée sur le décor clair n'est pas la danseuse
        s = np.where(decor.clair & est_ombre(f, decor.plaque), 0.0, s)
    return s


def _seuille(s: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rend (α brut, graine, pousse) : la rampe continue et ses deux seuillages."""
    alpha = np.clip((s - SEUIL_BAS) / max(SEUIL_HAUT - SEUIL_BAS, 1e-6), 0.0, 1.0)
    return alpha, (s > SEUIL_HAUT).astype(np.uint8), (s > SEUIL_BAS).astype(np.uint8)


# ── III. La frontière ──────────────────────────────────────────────────────────
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


def _garde(masque: np.ndarray, gardes: np.ndarray, n: int, labels: np.ndarray) -> np.ndarray:
    table = np.zeros(n, np.uint8)
    table[gardes] = 1
    return table[labels]


def discipline(graine: np.ndarray, pousse: np.ndarray, decor: Decor
               ) -> tuple[np.ndarray, np.ndarray]:
    """Rend (masque net, trous bouchés) — le domaine où α a le droit de vivre."""
    m = _hysteresis(graine, pousse)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, _ellipse(3))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, _ellipse(9))

    # Une danseuse est un continent, pas un archipel : les îlots qui flottent au
    # large sont du décor mal lu. On ne tolère, à côté de la plus grande
    # composante, que des compagnons d'un poids comparable — au cas où un bras se
    # détacherait sur un fond peu contrasté.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 1:
        aires = stats[1:, cv2.CC_STAT_AREA]
        seuil = max(decor.aire_min, ILOT_RELATIF * float(aires.max()))
        gardes = np.nonzero(aires >= seuil)[0] + 1
        if gardes.size == 0:
            gardes = np.array([1 + int(np.argmax(aires))])
        m = _garde(m, gardes, n, labels)

    # Un trou dont le décor est noir se bouche sans risque : ce qu'on y laisse
    # voir est déjà noir. Ailleurs — un tapis, un sol, une toile grise — on ne
    # bouche que les petits, sous peine d'y ramener du décor.
    trous = _trous(m)
    if trous.any():
        garde = (trous & decor.sombre).astype(np.uint8)
        nt, tl, ts, _ = cv2.connectedComponentsWithStats(trous, connectivity=8)
        if nt > 1:
            petits = np.nonzero(ts[1:, cv2.CC_STAT_AREA] < decor.trou_max)[0] + 1
            garde |= _garde(trous, petits, nt, tl)
        trous = garde
        m = np.maximum(m, trous)
    return m, trous


def alpha_du_bloc(scores: list[np.ndarray], decor: Decor) -> np.ndarray:
    """α de l'image du milieu, décidé sur le bloc espace-temps qui l'entoure."""
    # La décision se prend sur le score moyenné dans le temps puis lissé dans
    # l'espace — une convolution sur le bloc x·y·t. Ce qui scintille sans durer
    # ni s'étendre s'y éteint ; la danseuse, large et persistante, non.
    milieu = len(scores) // 2
    bloc = scores[milieu] if len(scores) == 1 else np.mean(scores, axis=0)
    if LISSAGE_XY >= 3:
        bloc = cv2.blur(bloc, (LISSAGE_XY, LISSAGE_XY))
    _, graine, pousse = _seuille(bloc)
    m, trous = discipline(graine, pousse, decor)

    # ... mais la *valeur* de α vient du score net de l'image, pour garder le
    # tranchant du bord, les voiles et le flou de mouvement.
    brut, _, _ = _seuille(scores[milieu])

    # Une carte topographique : le plateau à 1, la plaine à 0, et entre les deux
    # des courbes de niveau qui ne se croisent pas. On l'impose par la distance au
    # plateau — α ne peut que descendre en s'en éloignant, jamais remonter. Ce que
    # la mesure propose au-delà de la pente est écrêté.
    plateau = np.maximum(graine * m, trous)
    if plateau.any():
        loin = cv2.distanceTransform(1 - plateau, cv2.DIST_L2, 3)
        descente = np.clip(1.0 - loin / max(BORD_LARGEUR, 1e-6), 0.0, 1.0)
    else:
        descente = np.zeros_like(brut)
    return np.maximum(np.minimum(brut, descente) * m, plateau).astype(np.float32)


# ── IV. Le bord ────────────────────────────────────────────────────────────────
def affine_bord(alpha: np.ndarray, img: np.ndarray, rayon: int) -> np.ndarray:
    """Recale le bord de α sur les arêtes de l'image, par filtre guidé.

    Un flou gaussien adoucit le bord sans rien savoir de l'image : il déborde
    autant sur la danseuse que sur le décor. Le filtre guidé (He, Sun & Tang)
    modélise α comme une transformation linéaire locale de l'image elle-même —
    la pente suit donc les vraies arêtes. Là où l'image est plate, il lisse ; là
    où elle tranche, il tranche aussi. C'est ce qui récupère les mèches et les
    franges de voile que la statistique ne voit qu'à moitié.

    Sans `opencv-contrib`, on retombe sur le flou gaussien — moins fin, jamais faux.
    """
    if rayon < 3:
        return alpha
    if hasattr(cv2, "ximgproc"):
        return np.clip(cv2.ximgproc.guidedFilter(img, alpha.astype(np.float32),
                                                 radius=rayon, eps=GUIDE_EPS), 0.0, 1.0)
    return cv2.GaussianBlur(alpha, (_impair(rayon), _impair(rayon)), 0)


# ── V. L'a priori « humain », en option ────────────────────────────────────────
class Matteur:
    """RobustVideoMatting (Lin et al., WACV 2022) — ce que la statistique ignore.

    Notre construction ne sait qu'une chose : ce pixel a changé. Elle ne sait pas
    *ce qu'est* une danseuse, et c'est pourquoi une ombre portée la trompe — une
    ombre est un vrai changement. Un réseau de matting, lui, ne sait rien du décor
    (il ne l'a jamais vu vide) mais sait reconnaître une personne, et rend un α
    fin jusqu'à la mèche. Les deux angles morts sont exactement complémentaires.

    Modèle et poids téléchargés une fois dans `~/.cache/torch/hub`. Sans torch,
    l'option n'existe pas et le reste marche pareil.
    """

    def __init__(self, variante: str = "mobilenetv3") -> None:
        import torch                                # importé seulement si demandé
        self.torch = torch
        self.appareil = ("mps" if torch.backends.mps.is_available()
                         else "cuda" if torch.cuda.is_available() else "cpu")
        self.modele = torch.hub.load("PeterL1n/RobustVideoMatting", variante,
                                     trust_repo=True).eval().to(self.appareil)
        self.etat: list = [None] * 4
        self.arriere: np.ndarray | None = None
        _log(f"  matteur {variante} sur {self.appareil}")

    def oublie(self) -> None:
        """Coupe la mémoire récurrente — pour des images non consécutives."""
        self.etat = [None] * 4

    def alpha(self, img: np.ndarray, ratio: float = RVM_RATIO) -> np.ndarray:
        torch = self.torch
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        t = (torch.from_numpy(rgb).permute(2, 0, 1)[None].float().div(255)
             .to(self.appareil))
        with torch.no_grad():
            _, pha, *self.etat = self.modele(t, *self.etat, downsample_ratio=ratio)
        return pha[0, 0].float().cpu().numpy()

    def remonte_le_temps(self, chemin: Path, total: int) -> None:
        """Calcule et retient α pour toute la vidéo, jouée à l'envers.

        RobustVideoMatting est *causal* : sa mémoire récurrente ne contient que le
        passé, parce qu'il est fait pour le direct. Nous n'avons pas cette
        contrainte. Rejouer la séquence à l'envers lui donne accès au futur — et
        les deux passes ne se trompent pas aux mêmes endroits : celle qui vient de
        l'avant hésite quand un bras surgit, celle qui vient de l'arrière hésite
        quand il disparaît. Leur moyenne est plus stable que l'une ou l'autre, et
        la première image cesse d'être une image froide.
        """
        cap = cv2.VideoCapture(str(chemin))
        self.oublie()
        self.arriere = None
        for i in range(total - 1, -1, -1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ok, img = cap.read()
            if not ok:
                continue
            a = self.alpha(img)
            if self.arriere is None:
                self.arriere = np.zeros((total,) + a.shape, np.uint8)
            self.arriere[i] = np.clip(a * 255, 0, 255).astype(np.uint8)
        cap.release()
        self.oublie()

    def alpha_deux_sens(self, img: np.ndarray, i: int) -> np.ndarray:
        """α de la passe avant, moyenné avec celui de la passe arrière s'il existe."""
        pha = self.alpha(img)
        if self.arriere is not None and 0 <= i < len(self.arriere):
            pha = 0.5 * (pha + self.arriere[i].astype(np.float32) / 255.0)
        return pha


def fusionne(stat: np.ndarray, pha: np.ndarray, decor: Decor) -> np.ndarray:
    """Porte par le réseau, générosité à l'intérieur, puis contrainte de continent.

    Hors de la personne que le réseau reconnaît, rien ne passe : l'ombre tombe.
    À l'intérieur, on prend le plus généreux des deux α — la statistique rattrape
    ce que le réseau ampute, le réseau rattrape les mèches et les voiles.
    """
    porte = (pha > RVM_PORTE).astype(np.uint8)
    if porte.any():
        n, labels, stats, _ = cv2.connectedComponentsWithStats(porte, connectivity=8)
        if n > 1:                                  # la personne, pas les miettes
            plus_grande = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            porte = (labels == plus_grande).astype(np.uint8)
        porte = cv2.dilate(porte, _ellipse(_impair(RVM_DILATE)))
    fusion = np.maximum(stat, pha) * porte

    # Le continent vaut aussi pour le résultat fusionné : le réseau a ses propres
    # miettes, et l'union de deux α n'hérite d'aucune des deux disciplines.
    vif = (fusion > RVM_PORTE).astype(np.uint8)
    m, trous = discipline(vif, vif, decor)
    return np.maximum(fusion * m, trous.astype(np.float32))


# ── VI. Le rendu ───────────────────────────────────────────────────────────────
@dataclass
class Source:
    """Une vidéo ouverte, et ce qu'elle sait d'elle-même."""

    cap: cv2.VideoCapture
    fps: float
    taille: tuple[int, int]
    total: int

    @classmethod
    def ouvre(cls, chemin: Path, max_images: int | None = None) -> "Source":
        cap = cv2.VideoCapture(str(chemin))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return cls(cap, cap.get(cv2.CAP_PROP_FPS) or 30.0,
                   (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
                   min(total, max_images) if max_images else total)

    @property
    def jalons(self) -> list[int]:
        """Les instants de la planche de contrôle, répartis sur toute la durée."""
        return sorted(set(np.linspace(0, max(self.total - 1, 0), VIGNETTES)
                          .astype(int).tolist()))


class Rendu:
    """Là où α devient une image : la vidéo, la planche de vignettes, ou les deux."""

    def __init__(self, sortie: Path, src: Source, *, video: bool, vignettes: bool):
        self.sortie = sortie
        self.jalons = set(src.jalons)
        self.veut_vignettes = vignettes
        self.vignettes: list[np.ndarray] = []
        self.reduit = (src.taille[0] // REDUCTION, src.taille[1] // REDUCTION)
        self.ecrites = 0
        self.ecrivain = None
        if video:
            sortie.parent.mkdir(parents=True, exist_ok=True)
            self.ecrivain = cv2.VideoWriter(str(sortie), cv2.VideoWriter_fourcc(*"mp4v"),
                                            src.fps, src.taille)
            if not self.ecrivain.isOpened():
                raise RuntimeError(f"écriture impossible : {sortie}")

    def pose(self, img: np.ndarray, alpha: np.ndarray, i: int) -> None:
        out = (img.astype(np.float32) * alpha[..., None]).astype(np.uint8)
        if self.ecrivain is not None:
            self.ecrivain.write(out)
            self.ecrites += 1
        if self.veut_vignettes and i in self.jalons:
            self.vignettes.append(cv2.resize(out, self.reduit))

    def ferme(self) -> None:
        if self.ecrivain is not None:
            self.ecrivain.release()
        if not self.vignettes:
            return
        if len(self.vignettes) >= 6:
            planche = np.vstack([np.hstack(self.vignettes[:3]),
                                 np.hstack(self.vignettes[3:6])])
        else:
            planche = np.hstack(self.vignettes)
        chemin = self.sortie.with_suffix(".planche.jpg")
        chemin.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(chemin), planche, [cv2.IMWRITE_JPEG_QUALITY, 88])
        _log(f"  planche : {chemin}")


def detoure(entree: Path, sortie: Path, *, n_echantillons: int = N_ECHANTILLONS,
            max_images: int | None = None, flou_bord: int = FLOU_BORD,
            apercu: bool = False, planche_seule: bool = False,
            pas: int = 1, matteur: Matteur | None = None) -> None:
    """La chaîne complète : décor, métrique, frontière, bord, composition."""
    t0 = time.time()
    _log(f"» {entree.name}")
    decor = bati_le_decor(entree, n_echantillons, pas)

    src = Source.ouvre(entree, max_images)
    rendu = Rendu(sortie, src, video=not planche_seule,
                  vignettes=apercu or planche_seule)

    if matteur is not None and not planche_seule:
        _log("  matteur : passe arrière, à rebrousse-temps")
        matteur.remonte_le_temps(entree, src.total)

    def pose(img: np.ndarray, a: np.ndarray, i: int) -> None:
        if matteur is not None:
            a = fusionne(a, matteur.alpha_deux_sens(img, i), decor)
        rendu.pose(img, affine_bord(a, img, flou_bord), i)

    if planche_seule:                              # quelques instants, rien d'autre
        for i in src.jalons:
            if matteur is not None:
                matteur.oublie()                   # instants non consécutifs
            fenetre = []
            for j in range(i - LISSAGE_T // 2, i + LISSAGE_T // 2 + 1):
                src.cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(j, src.total - 1)))
                ok, im = src.cap.read()
                if ok:
                    fenetre.append((im, score(im, decor)))
            if fenetre:
                milieu = len(fenetre) // 2
                pose(fenetre[milieu][0], alpha_du_bloc([s for _, s in fenetre], decor), i)
    else:
        tampon: deque[tuple[np.ndarray, np.ndarray]] = deque(maxlen=LISSAGE_T)
        milieu = LISSAGE_T // 2
        for i in range(src.total):
            ok, img = src.cap.read()
            if not ok:
                break
            tampon.append((img, score(img, decor)))
            if len(tampon) == LISSAGE_T:
                pose(tampon[milieu][0], alpha_du_bloc([s for _, s in tampon], decor),
                     i - milieu)
            elif len(tampon) == 1:                 # la toute première
                pose(tampon[0][0], alpha_du_bloc([tampon[0][1]], decor), 0)
            if i % 100 == 0:
                _log(f"  image {i}/{src.total}  ({time.time() - t0:.0f} s)")
        for j in range(milieu + 1, len(tampon)):   # les dernières, fenêtre incomplète
            pose(tampon[j][0], alpha_du_bloc([tampon[j][1]], decor),
                 src.total - len(tampon) + j)

    src.cap.release()
    rendu.ferme()
    _log(f"  fini : {sortie}  ({rendu.ecrites} images, {time.time() - t0:.0f} s)")


def detoure_sans_decor(entree: Path, sortie: Path, matteur: Matteur, *,
                       max_images: int | None = None, flou_bord: int = FLOU_BORD,
                       apercu: bool = False, planche_seule: bool = False) -> None:
    """Le réseau seul, sans aucune statistique de fond — l'étalon de comparaison.

    Il ne sait rien du décor : il n'a jamais vu la scène vide, et ne s'en sert
    pas. Ce qu'il rend ici est ce qu'on obtiendrait sans exploiter l'immobilité
    du décor, c'est-à-dire sans l'atout principal de ces prises de vue.
    """
    t0 = time.time()
    _log(f"» {entree.name} — matteur seul")
    src = Source.ouvre(entree, max_images)
    rendu = Rendu(sortie, src, video=not planche_seule,
                  vignettes=apercu or planche_seule)

    for i in (src.jalons if planche_seule else range(src.total)):
        if planche_seule:
            src.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            matteur.oublie()                       # images non consécutives
        ok, img = src.cap.read()
        if not ok:
            break
        rendu.pose(img, affine_bord(matteur.alpha(img), img, flou_bord), i)
        if not planche_seule and i % 100 == 0:
            _log(f"  image {i}/{src.total}  ({time.time() - t0:.0f} s)")

    src.cap.release()
    rendu.ferme()
    _log(f"  fini : {sortie}  ({rendu.ecrites} images, {time.time() - t0:.0f} s)")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Détourage sur fond fixe, sortie sur noir.")
    p.add_argument("entrees", nargs="+", type=Path, help="vidéo(s) d'entrée")
    p.add_argument("-o", "--sortie", type=Path, default=None,
                   help="fichier .mp4 de sortie (une seule entrée) ou dossier de sortie")
    p.add_argument("--echantillons", type=int, default=N_ECHANTILLONS,
                   help=f"images pour la médiane temporelle (défaut {N_ECHANTILLONS})")
    p.add_argument("--pas-enveloppes", type=int, default=1, metavar="N",
                   help="ne lire qu'une image sur N pour les enveloppes (défaut 1)")
    p.add_argument("--max-images", type=int, default=None,
                   help="ne traiter que les N premières images (prototypage)")
    p.add_argument("--flou-bord", type=int, default=FLOU_BORD,
                   help=f"rayon du recalage de bord, 0 = franc (défaut {FLOU_BORD})")
    p.add_argument("--apercu", action="store_true",
                   help=f"écrire aussi une planche de {VIGNETTES} vignettes")
    p.add_argument("--planche", action="store_true",
                   help="n'écrire QUE la planche de vignettes, pas de vidéo")
    p.add_argument("--rvm", nargs="?", const="mobilenetv3", default=None,
                   choices=["mobilenetv3", "resnet50"],
                   help="fusionner avec RobustVideoMatting (requiert torch)")
    p.add_argument("--rvm-seul", nargs="?", const="mobilenetv3", default=None,
                   choices=["mobilenetv3", "resnet50"],
                   help="le réseau SEUL, sans statistique de fond — étalon de comparaison")
    a = p.parse_args(argv)

    manquantes = [e for e in a.entrees if not e.exists()]
    if manquantes:
        _log("introuvable : " + ", ".join(str(e) for e in manquantes))
        return 1

    matteur = None
    if a.rvm or a.rvm_seul:
        try:
            matteur = Matteur(a.rvm_seul or a.rvm)
        except ImportError:
            _log("torch absent : `./.venv/bin/pip install torch torchvision`")
            return 1

    for entree in a.entrees:
        if a.sortie is None:
            sortie = entree.with_name(f"{entree.stem}_nobg.mp4")
        elif a.sortie.suffix.lower() == ".mp4" and len(a.entrees) == 1:
            sortie = a.sortie
        else:
            sortie = a.sortie / f"{entree.stem}_nobg.mp4"
        if matteur is not None:
            matteur.oublie()                       # chaque vidéo repart à zéro
        if a.rvm_seul:
            detoure_sans_decor(entree, sortie, matteur, max_images=a.max_images,
                               flou_bord=a.flou_bord, apercu=a.apercu,
                               planche_seule=a.planche)
        else:
            detoure(entree, sortie, n_echantillons=a.echantillons,
                    max_images=a.max_images, flou_bord=a.flou_bord, apercu=a.apercu,
                    planche_seule=a.planche, pas=a.pas_enveloppes, matteur=matteur)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
