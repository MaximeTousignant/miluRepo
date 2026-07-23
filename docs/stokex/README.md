# docs/stokex — workflow

Publication défensive de l'algorithme **$tôkEx** (`stokex_defensive_publication.tex`),
ses figures, et les preuves associées.

## Environnement Python (local, permanent, **jamais poussé**)

Les figures sont générées par `gen_figures.py` (matplotlib + pandas, rendu texte via
LaTeX système). L'environnement vit dans un `.venv/` **local et gitignoré** : il est
partagé par toutes les instances de Milu sur la machine, mais ne part jamais sur GitHub
(voir `.gitignore` à la racine : `.venv/`, `__pycache__/`). Seul `requirements.txt` — la
*recette* — est versionné.

Bootstrap (depuis la racine du repo) :

```sh
python3 -m venv .venv
./.venv/bin/pip install -r docs/stokex/requirements.txt
```

Prérequis système : une installation LaTeX (`text.usetex=True` → `latex`, `dvipng`),
fournie par MacTeX / TeX Live.

## Générer les figures

```sh
./.venv/bin/python docs/stokex/gen_figures.py
```

Écrit les PDF dans `docs/stokex/` (dossier du script, indépendant du répertoire courant).
Les captures d'écran de l'UI de référence (`reference_implementation_ui_*.png`) ne sont
**pas** générées par le script — elles sont ajoutées à la main.

## Compiler le document

Compilation simple :

```sh
cd docs/stokex && latexmk -pdf stokex_defensive_publication.tex
```

Compilation continue (recompile à chaque sauvegarde du `.tex`) :

```sh
cd docs/stokex && latexmk -pvc -pdf -interaction=nonstopmode -view=none stokex_defensive_publication.tex
```

`latexmk` gère les passes multiples (références croisées) tout seul. Les artefacts de
compilation (`.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.toc`, …) sont gitignorés.

## Placeholders et go-live

Le document utilise une macro `\placeholder{...}` (boîte jaune) pour marquer ce qui reste
à compléter avant soumission. La checklist complète de mise en ligne (retrait des
placeholders, tag, soumission TDCommons, etc.) est dans `stokex_go_live.md`.

Avant de tagguer/soumettre :

```sh
grep -n "À COMPLÉTER\|placeholder" stokex_defensive_publication.tex
```

ne doit plus rien retourner dans le corps du texte (les entrées « placeholder » du
tableau de notation, terme mathématique, sont légitimes).
