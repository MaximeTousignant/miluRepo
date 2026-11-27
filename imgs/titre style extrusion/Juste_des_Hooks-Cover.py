#!/usr/bin/env python
"""Pochette de « Juste des Hooks » (Krash Lama) — le titre de la V4.

Rend le titre « Juste / des / Hooks » avec son extrusion et son contour, sur le
canevas de référence d'Affinity : 8192 × 8192 px à 300 dpi, origine (0, 0) en
haut à gauche. Les positions et les tailles sont celles relevées dans Affinity.

Deux sorties :

  - par défaut, un croquis JPEG en 4096², le titre posé sur `Background.jpg` ;
  - avec `--fullres`, le titre seul en PNG 8192² sur fond transparent : le
    calque source, à importer dans Affinity en (0, 0).

DOSSIER est le dossier de la pochette. Il doit contenir la police (voir
POLICE_FICHIER) et, pour le croquis, `Background.jpg`. Les sorties vont dans
DOSSIER/Milu_Output/, créé au besoin. Aucune image ne vit dans ce repo.

Usage, depuis la racine de miluRepo :

    uv run imgs/ombre/Juste_des_Hooks-Cover.py DOSSIER
    uv run imgs/ombre/Juste_des_Hooks-Cover.py DOSSIER --fullres
    uv run imgs/ombre/Juste_des_Hooks-Cover.py DOSSIER --couleur "#FFC500"

Dépendances (dans le .venv) : Pillow, numpy, fontTools, opencv.
"""

# ════════════════════════════════════════════════════════════════════════════
# PARAMÈTRES — tout ce qui se règle est ici. Unités : px sur le canevas de
# 8192 (ou pt, convertis), degrés, couleurs en hexadécimal sans « # ».
# ════════════════════════════════════════════════════════════════════════════

# Police — le fichier, relatif à DOSSIER, et ce qu'on attend d'y trouver
POLICE_FICHIER = "fonts/rockout/Rockout.otf"
POLICE_FAMILLE = "Rockout Vintage"  # nom de famille dans le fichier (table name, ID 1)
POLICE_STYLE = "Regular"        # sous-famille (table name, ID 2)

# Fond du croquis, relatif à DOSSIER
FOND_FICHIER = "Background.jpg"

# Sorties, relatives à DOSSIER
SORTIE_CROQUIS = "Milu_Output/Juste_des_Hooks-Cover_V4_croquis.jpeg"
SORTIE_FULLRES = "Milu_Output/Juste_des_Hooks-Cover_V4_titre_fullres.png"

# Canevas
DPI = 300
CANEVAS = 8192   # px, canevas de référence (Affinity)
CROQUIS = 4096   # px, taille des croquis

# Titre — coin haut-gauche de l'encre de « Juste », comme le X/Y d'Affinity
TITRE_X = 2514.4      # px
TITRE_Y = 5701.5      # px
TITRE_TAILLE = 349.3  # pt, taille Affinity de « Juste » et « Hooks »
ZOOM = 1.0            # agrandit tout le titre autour de (TITRE_X, TITRE_Y)

# Les mots : texte, position Affinity (px) et taille Affinity (pt), relevées à ZOOM = 1
MOTS = [
    ("Juste", 2514.4, 5701.5, 349.3),
    ("des",   3987.5, 6549.4, 131.5),
    ("Hooks", 3221.3, 6590.3, 349.3),
]

# Couleurs
COULEUR_TITRE = "FFC500"       # jaune de la pochette : "FFC500"
COULEUR_EXTRUSION = "321A12"
COULEUR_CONTOUR = "321A12"

# Extrusion — direction en degrés, sens horaire : 0 = droite, 90 = bas, 45 = bas-droite
EXTRUSION_ANGLE = 45.0         # deg
EXTRUSION_PROFONDEUR = 155.0   # px

# Contour — à l'extérieur de toute la silhouette (titre + extrusion)
CONTOUR_LARGEUR = 25.0         # px, 0 = aucun

# ════════════════════════════════════════════════════════════════════════════

import argparse
import math
from pathlib import Path

import cv2
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageColor, ImageDraw, ImageFont

PT2PX = DPI / 72


def charger_police(chemin):
    """Ouvre la police et vérifie que c'est la bonne ; sinon, ValueError.

    Vérifie que le fichier existe, que sa famille et son style sont ceux des
    PARAMÈTRES, et que chaque lettre du titre y a un glyphe.
    """
    if not chemin.is_file():
        raise ValueError(f"Police introuvable : {chemin}\n"
                         f"Attendu : DOSSIER/{POLICE_FICHIER} ({POLICE_FAMILLE} {POLICE_STYLE}).")
    try:
        f = TTFont(chemin)
    except Exception as e:
        raise ValueError(f"Fichier de police illisible : {chemin} ({e})") from e
    famille = f["name"].getDebugName(1)
    style = f["name"].getDebugName(2)
    if (famille, style) != (POLICE_FAMILLE, POLICE_STYLE):
        raise ValueError(f"Mauvaise police : {chemin} est « {famille} {style} », "
                         f"attendu « {POLICE_FAMILLE} {POLICE_STYLE} ».")
    cmap = f.getBestCmap()
    manquantes = sorted({c for mot, *_ in MOTS for c in mot if ord(c) not in cmap})
    if manquantes:
        raise ValueError(f"La police {chemin} n'a pas de glyphe pour : {' '.join(manquantes)}")
    return f


def affinity2pillow(f):
    """Facteur qui traduit une taille de police Affinity en taille Pillow.

    Pillow prend la taille comme la hauteur de l'em (unitsPerEm) ; Affinity la
    fait correspondre à la hauteur de ligne, de l'ascendante à la descendante.
    Pour Rockout : 2048 / (1903 + 591) ≈ 0.8212.
    """
    return f["head"].unitsPerEm / (f["hhea"].ascent - f["hhea"].descent)


def couleur_rgb(hexa):
    """« FFD257 » ou « #FFD257 » → (255, 210, 87) ; ValueError si ce n'est pas une couleur."""
    return ImageColor.getrgb("#" + hexa.lstrip("#"))


def decaler(a, dx, dy):
    """Décale le tableau `a` de (dx, dy) pixels entiers ; ce qui sort du cadre est perdu."""
    h, w = a.shape
    out = np.zeros_like(a)
    out[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = \
        a[max(-dy, 0):h + min(-dy, 0), max(-dx, 0):w + min(-dx, 0)]
    return out


def extruder(alpha, angle, profondeur):
    """Le volume de l'extrusion : le masque recopié pas à pas le long de la direction.

    `angle` en degrés, sens horaire, 0 = vers la droite, 90 = vers le bas (comme le
    canevas : y vers le bas). On avance d'un pixel à la fois jusqu'à `profondeur`,
    on arrondit chaque position au pixel, et on garde le maximum de toutes les copies.
    """
    a = np.asarray(alpha)
    volume = a.copy()
    ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    deja = {(0, 0)}
    for i in range(1, round(profondeur) + 1):
        pas = (round(i * ux), round(i * uy))
        if pas not in deja:
            deja.add(pas)
            np.maximum(volume, decaler(a, *pas), out=volume)
    return Image.fromarray(volume)


def contourer(masque, largeur):
    """Le masque épaissi de `largeur` px dans toutes les directions, au pinceau rond.

    Posé sous la silhouette, il n'en laisse voir que la bande qui dépasse : le contour.
    """
    r = round(largeur)
    if r <= 0:
        return masque.copy()
    pinceau = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    return Image.fromarray(cv2.dilate(np.asarray(masque), pinceau))


def titre_alpha(chemin_police, f):
    """Le titre en masque (L, 255 = encre), sur le canevas de référence."""
    k = affinity2pillow(f)
    upm, cmap, hmtx = f["head"].unitsPerEm, f.getBestCmap(), f["hmtx"]
    alpha = Image.new("L", (CANEVAS, CANEVAS), 0)
    d = ImageDraw.Draw(alpha)
    for txt, x, y, taille_pt in MOTS:
        # Position et taille mises à l'échelle autour du coin du titre
        x = TITRE_X + (x - TITRE_X) * ZOOM
        y = TITRE_Y + (y - TITRE_Y) * ZOOM
        em = taille_pt * PT2PX * ZOOM * k  # px, taille Pillow
        # "lt" : Pillow pose le crayon en x, et le haut de ligne en y. Affinity, lui,
        # aligne x sur le bord de l'encre : on recule donc le mot de la chasse gauche
        # (left side bearing) de sa première lettre, lue dans la table hmtx.
        lsb = hmtx[cmap[ord(txt[0])]][1] * em / upm  # px
        d.text((x - lsb, y), txt, font=ImageFont.truetype(str(chemin_police), em),
               fill=255, anchor="lt")
    return alpha


def main():
    p = argparse.ArgumentParser(description="Le titre de la pochette de Juste des Hooks.")
    p.add_argument("dossier", type=Path, help="dossier de la pochette")
    p.add_argument("--fullres", action="store_true",
                   help=f"le titre seul, en {CANEVAS}² sur fond transparent, en PNG "
                        f"(défaut : DOSSIER/{SORTIE_FULLRES})")
    p.add_argument("--couleur", default=COULEUR_TITRE, help="couleur du titre")
    p.add_argument("--couleur-extrusion", default=COULEUR_EXTRUSION)
    p.add_argument("--couleur-contour", default=COULEUR_CONTOUR)
    p.add_argument("--angle", type=float, default=EXTRUSION_ANGLE,
                   help="direction de l'extrusion, en degrés (0 = droite, 90 = bas)")
    p.add_argument("--profondeur", type=float, default=EXTRUSION_PROFONDEUR,
                   help=f"longueur de l'extrusion, en px sur le canevas de {CANEVAS}")
    p.add_argument("--largeur-contour", type=float, default=CONTOUR_LARGEUR,
                   help=f"épaisseur du contour, en px sur le canevas de {CANEVAS} (0 = aucun)")
    p.add_argument("-o", "--sortie", type=Path,
                   help=f"défaut : DOSSIER/{SORTIE_CROQUIS} (ou {SORTIE_FULLRES} avec --fullres)")
    a = p.parse_args()

    # 0. Vérifications, avant tout calcul
    if not a.dossier.is_dir():
        raise ValueError(f"Dossier de la pochette introuvable : {a.dossier}")
    chemin_police = a.dossier / POLICE_FICHIER
    police = charger_police(chemin_police)
    couleurs = [(couleur_rgb(a.couleur_contour), "contour"),
                (couleur_rgb(a.couleur_extrusion), "extrusion"),
                (couleur_rgb(a.couleur), "titre")]
    if a.profondeur < 0 or a.largeur_contour < 0:
        raise ValueError("La profondeur et la largeur du contour doivent être ≥ 0.")
    fond = a.dossier / FOND_FICHIER
    if not a.fullres and not fond.is_file():
        raise ValueError(f"Fond introuvable pour le croquis : {fond}")

    # 1. Masques en 8192 : le titre, son volume extrudé, puis le contour du tout
    alpha = titre_alpha(chemin_police, police)
    volume = extruder(alpha, a.angle, a.profondeur)
    contour = contourer(volume, a.largeur_contour)
    masques = {"contour": contour, "extrusion": volume, "titre": alpha}

    # 2. Le canevas : transparent en 8192, ou le fond avec les masques réduits en 4096
    if a.fullres:
        image = Image.new("RGBA", (CANEVAS, CANEVAS), (0, 0, 0, 0))
    else:
        masques = {n: m.resize((CROQUIS, CROQUIS), Image.LANCZOS) for n, m in masques.items()}
        image = Image.open(fond).convert("RGBA")
        if image.size != (CROQUIS, CROQUIS):
            image = image.resize((CROQUIS, CROQUIS), Image.LANCZOS)

    # 3. Empilement : (fond,) contour, extrusion, titre
    for rgb, nom in couleurs:
        calque = Image.new("RGBA", image.size, rgb + (0,))
        calque.putalpha(masques[nom])
        image = Image.alpha_composite(image, calque)

    # 4. Écriture
    sortie = a.sortie or a.dossier / (SORTIE_FULLRES if a.fullres else SORTIE_CROQUIS)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    if a.fullres:
        image.save(sortie, dpi=(DPI, DPI))
    else:
        image.convert("RGB").save(sortie, quality=92, dpi=(DPI, DPI))
    print(sortie)


if __name__ == "__main__":
    main()
