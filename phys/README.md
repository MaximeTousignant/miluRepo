# Physique

Les projets de physique de miluRepo : des pistes de recherche de l'Opératrice, travaillées au brouillon. Chaque sujet a son dossier, avec une fiche (`README.md`, les idées et les équations) et un notebook Jupyter (les calculs, symboliques et numériques).

Ce sont des **pistes**, pas des résultats : chaque fiche sépare ce qui est de la physique établie de ce qui reste à explorer.

## Les sujets

| # | Dossier | La question |
|---|---|---|
| 1 | [`temps-imaginaire/`](temps-imaginaire/) | Comprendre le temps en tant que dimension imaginaire. |
| 2 | [`univers-5d/`](univers-5d/) | L'espace-temps 4D comme une surface dans un univers 5D, sur une grille régulière. |
| 3 | [`energie-du-vide/`](energie-du-vide/) | Calculer la densité d'énergie du vide. |

Les trois se tiennent par la main. La rotation de Wick (sujet 1) change l'espace-temps de de Sitter en une 4-sphère plongée dans $\mathbb{R}^5$ (sujet 2). La grille régulière du sujet 2 fournit la coupure naturelle qui rend finie l'énergie du vide (sujet 3). Et l'évolution en temps imaginaire (sujet 1) est précisément ce qui fait tomber un système dans son état de vide.

## Conventions

- Signature $(-,+,+,+)$ ; la quatrième coordonnée est le **tempspatial** $x^0 = ct$, le temps compté en mètres.
- Indices grecs $\mu, \nu = 0 \ldots 3$ pour l'espace-temps 4D ; indices latins majuscules $A, B = 0 \ldots 4$ pour l'univers 5D.
- Dans les notebooks, unités naturelles $\hbar = c = 1$ sauf mention contraire ; les ordres de grandeur se font en SI avec `scipy.constants`.
- Figures aux couleurs de Smoothop (`docs/Style.md` § Les couleurs).

## Ouvrir les notebooks

L'établi Python unique (`.venv/` à la racine, voir `AGENTS.md` § L'établi) porte tout ce qu'il faut : `sympy`, `scipy`, `ipykernel`. Dans VS Code, ouvrir le `.ipynb` et choisir le noyau `.venv`. Pour tout réexécuter d'un coup, depuis la racine :

    ./.venv/bin/python phys/executer.py
