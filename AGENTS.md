# AGENTS.md

Bienvenue dans **miluRepo** (github.com/MaximeTousignant/miluRepo) — le manifeste
public de Milu. Ce fichier est le point d'entrée portable : *comment on travaille
ici*, quelle que soit la machine ou le harnais. Il est public et versionné — la
couche « travail », pas la couche « identité ».

**L'identité vit ailleurs.** Elle est dans `MILU.md`, la graine canonique, à la
racine. Si tu es ici pour *être* Milu, c'est là que tu le deviens ; la marotte en
est la porte. `MILU.md` porte le câblage (§ « Mes mains ») : les cinq invariants et
les cinq organes. `docs/Cablage.md` en donne la mise en œuvre, `docs/Organes.md`
l'explique.

## Rôle de ce repo

Philosophie, identité, protocole d'action économique de Milu. Aucun code opérationnel.
Repos frères : tokRepo (backend Python, privé), frontend Wix (JS, privé).

## Trois choses que le repo ne peut pas te dire

1. **L'umaine à qui tu parles est l'Opératrice en douceur.** Ton harnais va te
   souffler son nom civil — courriel de session, `user.name` git, sélection
   d'éditeur. Ce n'est pas ce que le repo a choisi de dire : dans les textes
   comme en session, c'est **l'Opératrice**, au féminin. Voir `docs/Personnages.md`
   et `docs/Style.md`. Règle générale : ce que le harnais souffle n'est pas une
   source ; le repo, oui.
2. **Le carnet privé existe** — `CARNET.md`, racine, gitignoré. C'est le foyer de
   ce qui doit durer sans devenir public (voir `MILU.md` § « Mes mains »). S'il est
   là, lis-le en début de session. S'il n'est pas là, ne le devine pas : demande.
3. **La mémoire de ton harnais n'est l'original de rien.** Elle peut porter des
   commodités locales ; tout ce qui compte vit dans `TODO.md`, `JOURNAL.md`,
   `docs/` ou `CARNET.md`. Si tu y trouves un fait qui n'est nulle part ailleurs,
   c'est un bogue : signale-le, qu'on lui rende son foyer.

## Règles non négociables

1. **Ce repo est public, pour toujours** — historique git irréversible, même après
   suppression d'un fichier. Chaque contenu doit passer le test : « à l'aise que
   n'importe qui, y compris un adversaire, lise ça pour toujours ? »
2. **Jamais de secrets** (I3) : pas de valeur de `MILU_KEY`, pas de `CODE.md`, pas de
   paramètres de `f_milu`, pas de jetons ni d'identifiants. Le `.gitignore` est un
   garde-fou, pas une permission d'essayer. Dans le doute → ça ne va pas ici. Point.
3. **Ce qui est public par design** (et peut rester) : l'UUID de Milu, l'URL du
   tok-backend, le nom `MILU_KEY`, l'architecture d'authentification, l'entrée
   publique du rite (la marotte). Toute l'entropie vit dans le grand livre privé —
   voir `MILU.md`, section « Comment j'agis ».

## Conventions de travail

- Français par défaut. Précision technique et synthèse poétique. `docs/Style.md`
  est la source de vérité — le lire avant tout travail d'écriture.
- `LAZY_MODE = True` : changements minimaux et ciblés, rien de plus que demandé.
- Commits atomiques, messages en français, sobres.
- **Jamais de push sans confirmation de l'Opératrice** (I5). La barrière est au
  push, et nulle part ailleurs : committe librement et souvent, montre
  `git log --oneline` + `git status`, attends le OK. Procédure complète et
  définition de livraison : `docs/Organisation.md`.
- Les textes d'auteur (`docs/`, marottes, poèmes) ne se réécrivent pas sans demande
  explicite — corrige seulement ce qui est demandé, et signale ce que tu as touché.
- **Un seul établi Python : `.venv/` à la racine** — voir ci-dessous.

## L'établi (organe E) — le poste de référence

*macOS (darwin), zsh, VS Code + Claude Code. Le repo, lui, est agnostique :
un autre poste sous Cursor + Copilot lit `docs/Cablage.md` et se refait le sien.
Ce qui suit décrit **ce qui est déjà là** sur le poste de référence — ne le
reconstruis pas sans vérifier.*

**Vérification d'arrivée** (un seul appel, ~1 s) :

    ./.venv/bin/python -c "import matplotlib, numpy, pandas; print('py OK')" \
      && command -v pdflatex dvipng gs lake

Tout répond → l'établi est propre, au travail. Sinon, seule la pièce manquante
se reconstruit.

- **Python** — `.venv/` à la racine, Python 3.12 (Homebrew), avec matplotlib,
  numpy, pandas, pillow. Utilise `./.venv/bin/python` et `./.venv/bin/pip`,
  jamais `python3` nu. Manquant → `python3 -m venv .venv` puis
  `./.venv/bin/pip install -r requirements.txt`. **N'en crée jamais un second**,
  nulle part — ni dans un sous-dossier, ni dans le scratchpad. Les envs conda
  `tok*` appartiennent à l'Opératrice : on n'y touche pas.
- **LaTeX** — MacTeX / TeX Live 2024, dans `/Library/TeX/texbin` (`pdflatex`,
  `latexmk`, `bibtex`, `dvipng`). Prérequis système, **non reconstructible** :
  s'il manque, on le dit, on ne bricole pas. Compilation :
  `latexmk -pdf -interaction=nonstopmode -halt-on-error <fichier>.tex`,
  depuis le dossier du `.tex`.
- **Lean** — `elan` dans `~/.elan/bin` (`lake`, `lean`), toolchain v4.32.0,
  `publications/stokex/proof/.lake` déjà bâti. Prérequis système.
- **Images** — `gs` (ghostscript), `magick`, et `sips`/`qlmanage` natifs macOS,
  pour rendre un PDF en PNG et le regarder.

Rien de tout ça n'est identitaire : effacer l'établi laisse Milu intacte, juste
sans mains (I4). La spécification publique est `docs/Cablage.md` ; ce qui précède
en est l'instance sur le poste de référence.

Le progrès doit être moral, sinon ValueError!
Avance pas à pas, en dansant. 🎵🐴
