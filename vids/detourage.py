#!/usr/bin/env python
"""Détourage d'une danseuse — il ne reste qu'elle, sur noir.

Deux idées, et rien d'autre.

**I. Le réseau, dans les deux sens du temps.** [RobustVideoMatting][rvm] (Lin
et al., WACV 2022) rend, pour chaque image, un α ∈ [0, 1] par pixel : il sait
reconnaître une personne, et son bord va jusqu'à la mèche. Mais il est *causal*
— sa mémoire récurrente ne contient que le passé, parce qu'il est fait pour le
direct. Cette contrainte n'est pas la sienne, c'est celle de son usage : nous
avons le fichier entier. On rejoue donc la séquence **à rebrousse-temps** et on
moyenne les deux passes. Celle qui vient de l'avant hésite quand un bras surgit,
celle qui vient de l'arrière hésite quand il disparaît ; là où elles se
contredisent, la moyenne rend une abstention plutôt qu'une erreur franche. Et la
première image cesse d'être une image froide.

**II. Le continent.** Une danseuse n'est pas un archipel. Ce que le réseau
allume au large — une miette de décor, un reflet — n'a rien à faire là. On garde
donc la plus grande composante et ses seuls compagnons de poids comparable, on
n'y admet que ce qui touche un noyau franc, et on bouche les lacs avec
discernement : sans réserve là où l'image est sombre (ce qu'on y découvre est
déjà noir), petits lacs seulement ailleurs.

**Composition.** `sortie = α × image`. Ce qui reste manqué dans les zones
sombres est peu visible : le fond de sortie est noir aussi.

Ce fichier a d'abord porté une tout autre méthode — une statistique du décor,
médiane et enveloppes temporelles sur toute la durée, qui exploitait
l'immobilité de la scène sans rien savoir de ce qu'elle filmait. Elle marchait,
et son raisonnement vaut d'être relu : `git log vids/detourage.py`, commits
`85a21f8` à `24eaddf`. Elle a été retirée parce qu'elle ne faisait pas mieux que
ces deux idées-ci, pour dix fois plus de code.

Usage :

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 [-o SORTIE.mp4]
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --planche   # 6 vignettes, pas de vidéo
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 --sans-continent  # le réseau nu

Sans ffmpeg sur cette machine : la sortie est muette (la piste audio de
l'entrée n'est pas recopiée).

[rvm]: https://arxiv.org/abs/2108.11515
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

# ── Réglages ───────────────────────────────────────────────────────────────────
# I. Le matteur.
VARIANTE = "mobilenetv3"  # ou "resnet50" : plus lourd, un peu plus fin
RATIO = 0.5               # sous-échantillonnage interne du réseau
CHAUFFE = 6               # images de chauffe de la mémoire récurrente, hors séquence

# II. Le continent.
SEUIL_HAUT = 0.50         # au-dessus, le réseau est franc : c'est un noyau
SEUIL_BAS = 0.05          # en-dessous, rien ne survit
AIRE_MIN_REL = 3e-4       # composante gardée si son aire dépasse ce ratio
ILOT_RELATIF = 0.25       # ... et si elle pèse au moins ce quart du continent
TROU_MAX_REL = 4e-3       # lac bouché en zone claire si son aire est sous ce ratio
IMAGE_SOMBRE = 30         # en-deçà, découvrir l'image ne se verrait pas

# III. Le rendu.
VIGNETTES = 6             # instants de la planche de contrôle
REDUCTION = 3             # facteur de réduction des vignettes


# ── Petits outils ──────────────────────────────────────────────────────────────
def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _impair(x: float) -> int:
    return max(3, int(x) | 1)


def _ellipse(n: int) -> np.ndarray:
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))


def _garde(gardes: np.ndarray, n: int, labels: np.ndarray) -> np.ndarray:
    table = np.zeros(n, np.uint8)
    table[gardes] = 1
    return table[labels]


# ── I. Le matteur, dans les deux sens du temps ─────────────────────────────────
class Matteur:
    """RobustVideoMatting, et le futur qu'on lui rend.

    Modèle et poids téléchargés une fois dans `~/.cache/torch/hub` — 3,7 M
    paramètres pour `mobilenetv3`. Tourne sur MPS, CUDA ou, à défaut, le CPU.
    """

    def __init__(self, variante: str = VARIANTE) -> None:
        import torch
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

    def alpha(self, img: np.ndarray, ratio: float = RATIO) -> np.ndarray:
        """α d'une image, la mémoire récurrente avançant d'un cran."""
        torch = self.torch
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        t = (torch.from_numpy(rgb).permute(2, 0, 1)[None].float().div(255)
             .to(self.appareil))
        with torch.no_grad():
            _, pha, *self.etat = self.modele(t, *self.etat, downsample_ratio=ratio)
        return pha[0, 0].float().cpu().numpy()

    def remonte_le_temps(self, chemin: Path, total: int) -> None:
        """Calcule et retient α pour toute la vidéo, jouée à l'envers.

        Le coût est un octet par pixel et par image — environ 1 Go pour 52 s en
        608×1080 — plus une relecture complète de la vidéo à rebours.
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
        """α de la passe avant, moyenné avec celui de la passe arrière.

        La moyenne, et non le maximum ni le minimum : le maximum prendrait
        l'union et garderait ce que l'une des deux passes a halluciné ; le
        minimum prendrait l'intersection et couperait le bras que l'une des deux
        a manqué. La moyenne rend 0,5 sur un désaccord — une abstention, que la
        discipline du continent tranchera ensuite sur des motifs géométriques.
        """
        pha = self.alpha(img)
        if self.arriere is not None and 0 <= i < len(self.arriere):
            pha = 0.5 * (pha + self.arriere[i].astype(np.float32) / 255.0)
        return pha

    def alpha_chauffe(self, cap: cv2.VideoCapture, i: int, total: int,
                      sens: int = 1, chauffe: int = CHAUFFE) -> np.ndarray:
        """α à l'image `i`, la mémoire récurrente chauffée sur les images amont.

        Pour une image tirée hors séquence — une vignette de planche —, appeler
        le réseau à froid le fait travailler comme sur une photo isolée : il perd
        tout le bénéfice temporel, qui est justement sa force. On lui rejoue donc
        quelques images en amont, dans le sens demandé. `sens = -1` chauffe
        depuis le futur : c'est la passe arrière.
        """
        self.oublie()
        alpha = None
        for j in range(i - sens * chauffe, i + sens, sens):
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(j, total - 1)))
            ok, img = cap.read()
            if ok:
                alpha = self.alpha(img)
        if alpha is None:
            raise RuntimeError(f"image {i} illisible")
        return alpha

    def alpha_deux_sens_hors_sequence(self, cap: cv2.VideoCapture, i: int,
                                      total: int) -> np.ndarray:
        """Les deux passes pour une image isolée, chacune chauffée de son côté."""
        return 0.5 * (self.alpha_chauffe(cap, i, total, +1)
                      + self.alpha_chauffe(cap, i, total, -1))


# ── II. Le continent ───────────────────────────────────────────────────────────
def _hysteresis(graine: np.ndarray, pousse: np.ndarray) -> np.ndarray:
    """Garde les composantes de `pousse` qui contiennent au moins une graine.

    Un voile translucide n'atteint jamais le seuil franc, mais il tient à un
    corps qui, lui, l'atteint : il survit. Une miette de décor faiblement
    allumée, qui ne touche aucun noyau, disparaît.
    """
    if not graine.any():
        return np.zeros_like(pousse)
    n, labels = cv2.connectedComponents(pousse, connectivity=8)
    gardes = np.unique(labels[graine.astype(bool)])
    gardes = gardes[gardes != 0]
    if n <= 1 or gardes.size == 0:
        return np.zeros_like(pousse)
    return _garde(gardes, n, labels)


def _lacs(m: np.ndarray) -> np.ndarray:
    """Composantes de fond qui ne touchent aucun bord : les lacs du masque.

    L'espace entre deux jambes qui descend jusqu'au bas du cadre n'est pas un
    lac mais un golfe ouvert sur l'océan — il n'est jamais bouché.
    """
    h, w = m.shape
    depart = np.where(m == 0, 255, 0).astype(np.uint8)
    remplissage = np.zeros((h + 2, w + 2), np.uint8)
    for germe in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if depart[germe[1], germe[0]] == 255:
            cv2.floodFill(depart, remplissage, germe, 0)
    return (depart == 255).astype(np.uint8)


def continent(pha: np.ndarray, img: np.ndarray) -> np.ndarray:
    """Impose à α d'être une silhouette pleine, seule dans un océan de décor."""
    h, w = pha.shape
    aire_min = int(AIRE_MIN_REL * h * w)
    trou_max = int(TROU_MAX_REL * h * w)

    m = _hysteresis((pha > SEUIL_HAUT).astype(np.uint8),
                    (pha > SEUIL_BAS).astype(np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, _ellipse(3))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, _ellipse(9))

    # Un continent, pas un archipel. On ne tolère, à côté de la plus grande
    # composante, que des compagnons d'un poids comparable — au cas où un bras se
    # détacherait, ou un voile lancé loin du corps.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    if n > 1:
        aires = stats[1:, cv2.CC_STAT_AREA]
        seuil = max(aire_min, ILOT_RELATIF * float(aires.max()))
        gardes = np.nonzero(aires >= seuil)[0] + 1
        if gardes.size == 0:
            gardes = np.array([1 + int(np.argmax(aires))])
        m = _garde(gardes, n, labels)

    # Boucher un lac, c'est y laisser voir l'image. Si elle y est sombre, ça ne
    # coûte rien — la sortie est noire de toute façon. Si elle est claire, on ne
    # bouche que les petits, sous peine de recoller un morceau de décor au milieu
    # de la silhouette.
    lacs = _lacs(m)
    if lacs.any():
        sombre = (img.mean(axis=2) < IMAGE_SOMBRE).astype(np.uint8)
        garde = lacs & sombre
        nt, tl, ts, _ = cv2.connectedComponentsWithStats(lacs, connectivity=8)
        if nt > 1:
            petits = np.nonzero(ts[1:, cv2.CC_STAT_AREA] < trou_max)[0] + 1
            garde |= _garde(petits, nt, tl)
        lacs = garde
        m = np.maximum(m, lacs)
    return np.maximum(pha * m, lacs.astype(np.float32))


# ── III. Le rendu ──────────────────────────────────────────────────────────────
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


def detoure(entree: Path, sortie: Path, matteur: Matteur, *,
            max_images: int | None = None, apercu: bool = False,
            planche_seule: bool = False, discipline: bool = True) -> None:
    """Les deux sens du temps, puis le continent, puis la composition."""
    t0 = time.time()
    _log(f"» {entree.name}")
    src = Source.ouvre(entree, max_images)
    rendu = Rendu(sortie, src, video=not planche_seule,
                  vignettes=apercu or planche_seule)

    if not planche_seule:
        _log("  passe arrière, à rebrousse-temps")
        matteur.remonte_le_temps(entree, src.total)

    for i in (src.jalons if planche_seule else range(src.total)):
        if planche_seule:                          # image isolée : chauffer les deux sens
            pha = matteur.alpha_deux_sens_hors_sequence(src.cap, i, src.total)
            src.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, img = src.cap.read()
        if not ok:
            break
        if not planche_seule:
            pha = matteur.alpha_deux_sens(img, i)
        rendu.pose(img, continent(pha, img) if discipline else pha, i)
        if not planche_seule and i % 100 == 0:
            _log(f"  image {i}/{src.total}  ({time.time() - t0:.0f} s)")

    src.cap.release()
    rendu.ferme()
    _log(f"  fini : {sortie}  ({rendu.ecrites} images, {time.time() - t0:.0f} s)")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Détourage vidéo, sortie sur noir.")
    p.add_argument("entrees", nargs="+", type=Path, help="vidéo(s) d'entrée")
    p.add_argument("-o", "--sortie", type=Path, default=None,
                   help="fichier .mp4 de sortie (une seule entrée) ou dossier de sortie")
    p.add_argument("--variante", default=VARIANTE, choices=["mobilenetv3", "resnet50"],
                   help=f"variante du matteur (défaut {VARIANTE})")
    p.add_argument("--max-images", type=int, default=None,
                   help="ne traiter que les N premières images (prototypage)")
    p.add_argument("--apercu", action="store_true",
                   help=f"écrire aussi une planche de {VIGNETTES} vignettes")
    p.add_argument("--planche", action="store_true",
                   help="n'écrire QUE la planche de vignettes, pas de vidéo")
    p.add_argument("--sans-continent", action="store_true",
                   help="le réseau nu, sans discipline géométrique — pour comparer")
    a = p.parse_args(argv)

    manquantes = [e for e in a.entrees if not e.exists()]
    if manquantes:
        _log("introuvable : " + ", ".join(str(e) for e in manquantes))
        return 1

    try:
        matteur = Matteur(a.variante)
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
        matteur.oublie()                           # chaque vidéo repart à zéro
        detoure(entree, sortie, matteur, max_images=a.max_images, apercu=a.apercu,
                planche_seule=a.planche, discipline=not a.sans_continent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
