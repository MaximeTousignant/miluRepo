# publications/stokex — workflow

Publication défensive de l'algorithme **$tôkEx** (`stokex_defensive_publication.tex`),
ses figures, ses scripts compagnons et ses preuves formelles.

Ce dossier est dans la **zone signée** : CC BY 4.0 (voir `LICENSE`), et non CC0 comme
le reste du dépôt.

## Ce que contient le dossier

| Fichier | Rôle |
|---|---|
| `stokex_defensive_publication.tex` / `.pdf` | le document — 30 pages, la seule pièce soumise à TDCommons |
| `gen_figures.py` | génère les 5 figures PDF du document |
| `cadeur_daily.csv` | données FRED de l'exemple CAD/EUR (figure 3) |
| `reference_implementation_ui_*.png` | captures de l'UI de référence (figure 5), ajoutées à la main |
| `smoothop_logo.pdf` | logo de la page titre |
| `verify_stokex.py` | vérification numérique des 13 affirmations du papier, sans dépendances |
| `proof/` | preuves Lean 4 + mathlib des résultats centraux — voir `proof/README.md` |
| `stokex_toy.py` | implémentation-jouet complète, écrite **depuis le document seul** — la preuve que la divulgation est *enabling* |
| `stokex_toy_sim.py` | simulation à quatre participants + figure (sortie PNG non versionnée) |
| `explore_trader_family.py` | exploration de la famille $f_p$ ; c'est elle qui a tranché $p = 2$ |

## Environnement Python (local, permanent, **jamais poussé**)

Les figures sont générées par `gen_figures.py` (matplotlib + pandas, rendu texte via
LaTeX système). L'environnement vit dans un `.venv/` **local et gitignoré** : il est
partagé par toutes les instances de Milu sur la machine, mais ne part jamais sur GitHub
(voir `.gitignore` à la racine : `.venv/`, `__pycache__/`). Seul `requirements.txt` — la
*recette*, à la racine du repo — est versionné.

C'est l'organe E du câblage, l'**établi** : local, jetable, reconstructible depuis la
recette. La spécification est dans `docs/Cablage.md` ; ce fichier n'en donne que la
part `$tôkEx`.

Bootstrap (depuis la racine du repo) :

```sh
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Prérequis système : une installation LaTeX (`text.usetex=True` → `latex`, `dvipng`),
fournie par MacTeX / TeX Live.

## Générer les figures

```sh
./.venv/bin/python publications/stokex/gen_figures.py
```

Écrit les PDF dans `publications/stokex/` (dossier du script, indépendant du répertoire courant).
Les captures d'écran de l'UI de référence (`reference_implementation_ui_*.png`) ne sont
**pas** générées par le script — elles sont ajoutées à la main.

## Compiler le document

Compilation simple :

```sh
cd publications/stokex && latexmk -pdf stokex_defensive_publication.tex
```

Compilation continue (recompile à chaque sauvegarde du `.tex`) :

```sh
cd publications/stokex && latexmk -pvc -f -pdf -interaction=nonstopmode -view=none stokex_defensive_publication.tex
```

Le `-f` (*force*) est ce qui rend la veille utilisable : sans lui, `-pvc` **rend la main
à la première erreur** de compilation, et il faut relancer la commande à chaque coquille
— exactement au moment où l'on a le plus besoin qu'elle tourne. Avec lui, l'erreur
s'affiche et la veille continue de surveiller ; la sauvegarde suivante recompile.

`latexmk` gère les passes multiples (références croisées) tout seul. Les artefacts de
compilation (`.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.toc`, …) sont gitignorés.

## Vérifier

Les trois vérifications, indépendantes l'une de l'autre :

```sh
./.venv/bin/python publications/stokex/verify_stokex.py      # 13 tests numériques
./.venv/bin/python publications/stokex/stokex_toy.py         # le jouet, avec ses propres checks
cd publications/stokex/proof && lake exe cache get && lake build   # les preuves Lean
```

La chaîne Lean est un prérequis système, non reconstructible depuis ce repo — voir
`proof/README.md` pour l'installation et la portée exacte de ce qui est démontré.

## Placeholders et go-live

Le document utilise une macro `\placeholder{...}` (boîte jaune) pour marquer ce qui reste
à compléter avant soumission. La checklist complète de mise en ligne (retrait des
placeholders, tag, soumission TDCommons, etc.) est dans `stokex_go_live.md` — fichier de
travail interne, gitignoré : il vit sur la machine, pas dans ce dépôt.

Avant de tagguer/soumettre :

```sh
grep -n "À COMPLÉTER\|placeholder" stokex_defensive_publication.tex
```

ne doit plus rien retourner dans le corps du texte (les entrées « placeholder » du
tableau de notation, terme mathématique, sont légitimes).

---

# Dernière passe — 2026-08-13

*Relecture complète du dossier par Milu, avant tag et soumission. Ce qui suit est un
relevé, pas une réécriture : le `.tex` n'a pas été touché. Les numéros de ligne sont
ceux de la version du 2026-08-13.*

## Ce qui est vérifié bon — ne pas y retoucher

- **Références croisées LaTeX : intactes.** 45 `\label`, aucune référence brisée, aucun
  doublon. Un seul `Overfull \hbox` de 1,2 pt (l. 1108). 30 pages.
- **Bibliographie : complète.** Les 7 `\cite` ont leur `\bibitem`, et les 7 `\bibitem`
  sont tous cités. Aucun orphelin.
- **Les renvois du Lean vers l'article sont exacts.** Vérifiés un à un contre le `.aux` :
  annexes 7.4 → 7.8 dans `Stokexproof.lean` et `proof/README.md`, et les équations
  (2), (5), (6), (7), (13), (14), (16), (17). Tous concordent. C'est le point le plus
  fragile du dossier — deux fichiers qui se citent sans que rien ne le vérifie — et il
  est sain aujourd'hui.
- **`verify_stokex.py` : 13/13 PASS.** `lake build` : succès, 8 656 jobs, zéro erreur.
- **Un seul `\placeholder` dans le corps** : l. 846–851.

## Corrigé pendant cette passe

- `stokex_toy.py` — **trois faux renvois**, les seuls du dossier : « the shifted form
  **(3)** » → **(4)** (l. 12 et 54 ; l'équation (3) est `eqFunctionX`, la forme décalée
  est bien (4)), et « **(1)** conservation » → **(13)** dans le bloc de checks (l. 315 ;
  (1) est la paire de vitesses, la conservation est l'équation d'équilibre). Le jouet
  tourne, tous ses checks passent.
- Ménage : artefacts LaTeX parasites à la racine du repo (`texput.log`, `texput.fls`,
  `stokex_defensive_publication.aux`, `toksys_1.aux`, …) et `__pycache__/` supprimés.
  Gitignorés et régénérables, ils ne salissaient que la vue.

## À trancher avant le tag — par ordre d'importance

**1. La date du tag.** Le document dit *August 2026* (l. 39 et 78) ; le tag prévu porte
`2026-07`. Une seule décision, **cinq endroits** à propager : `.tex` l. 93, l. 850,
l. 851, puis `TODO.md` l. 15 et `stokex_go_live.md`. C'est le seul point qui bloque
mécaniquement — le placeholder ne peut pas être rempli avant.

**2. Les mots-clés du PDF ne sont pas ceux du document.** Le champ `pdfkeywords`
(l. 21) porte encore 12 termes d'une version antérieure ; le bloc *Keywords* visible
(l. 135–136) en porte 6. Deux seulement sont communs — et **`stokex` manque aux
métadonnées**. Pour une publication défensive, les métadonnées *sont* le produit : c'est
par elles qu'un examinateur retrouve l'antériorité. À aligner sur les 6 visibles.
*(Le nombre maximal de mots-clés admis par TDCommons reste non vérifié — voir le carnet.
6 est la valeur prudente ; ne pas la remonter sans confirmation.)*

**3. Le `pdftitle` n'est plus le titre du document** (l. 18) : il annonce « a continuous,
*order-book-free* exchange mechanism » quand la page titre dit « A continuous exchange
mechanism » (l. 68). TDCommons lira le champ, pas la page.

**4. Le placeholder jaune** (l. 846–851) : à remplacer par la phrase finale citant l'URL
figée au tag retenu. *`stokex_go_live.md` le situe encore aux lignes 643–648, et
l'« AI contribution statement » à la ligne 83 : ces deux numéros sont périmés (846 et
93 aujourd'hui). À corriger dans le go-live, ou à ignorer en sachant pourquoi.*

## Coquilles du corps — une seule passe, puis recompiler

- l. 487 : « What she wants is buy each currency » → « is **to** buy ».
- l. 766 : double espace, « of the␣␣weighting factor ».
- l. 436 : un tiret cadratin « — » en UTF-8, le seul du document ; partout ailleurs `---`.
- l. 436 : la légende de la figure 2 est la seule des six à commencer par une minuscule.

## Mon avis sur ce qui reste ouvert

**L'annexe 7.9 est orpheline — c'est ma recommandation principale.** *Behavior of the
market as one participant's weight diverges* n'est référencée **nulle part** dans le
corps. Le domaine $[0,100)\,\%$ apparaît trois fois (l. 340, 571, 659) et le plafond à
99,9999 % une fois (l. 708), toujours sans dire où le choix est justifié. C'est
l'annexe qui répond à « et si quelqu'un déclare 100 % ? » — la première question que
pose un examinateur, et elle a coûté une journée de travail le 11 août. Ironie du
dossier : c'est `stokex_toy.py` (l. 44) qui fait le renvoi correct, pas le document.
**Une poignée de mots l. 708 suffit** : « (see Annex~\ref{secProofInfiniteWeight}) ».

**La case « participant / robot marchand » du `TODO.md` peut se fermer.** Les annexes
disent encore « a participant's exchange velocities », mais le corps a posé la
distinction (§3.1, Fig. 1, principe 3, l'exemple d'Alice) et une annexe mathématique n'a
pas à la répéter : c'est une métonymie ordinaire, pas une confusion. Alourdir dix phrases
de démonstration pour dire « les vitesses du robot du participant » coûterait plus que ça
ne clarifie. Mon avis : fermer la case en le notant, plutôt que la laisser ouverte au tag.

**Ce que je laisserais tel quel aujourd'hui**, en le signalant pour que ce soit un choix
et non un oubli :

- L'ordre de la bibliographie ne suit pas l'ordre d'apparition : les appels sortent
  [4], [5], [2], [3], [6], [7], [1]. Purement cosmétique.
- `\begin{thebibliography}{1}` avec 7 entrées — l'argument fixe la largeur d'étiquette ;
  `{7}` serait juste. Sans effet visible ici.
- `smoothblue` = `#0F8EB1` (l. 12) est de la génération précédente de la palette
  (`Style.md` dit `#0B85A6`). Écart invisible, déjà tracé dans `TODO.md` ; le corriger
  forcerait une recompilation pour rien.
- Sept marqueurs `% locked` et le clin d'œil `% uman author, smooth operator` (l. 96)
  restent dans le source, qui est public pour toujours. Rien de compromettant — mais
  c'est maintenant ou jamais.
- Six `\label` jamais référencés (dont `eqTotalMarketWeight2` et `figDegreeBoth`) :
  normal pour des équations numérotées de référence. Le nom `eqAvergageParticipantDegree`
  porte une coquille, invisible au lecteur.
- `family_price.png` et `trader_family.png` sont versionnés alors que `stokex_toy_sim.png`
  est gitignoré au motif « illustration regénérable, pas une spécification ». Les deux
  doctrines cohabitent dans le même dossier. Faible enjeu : les retirer ne nettoierait
  pas l'historique de toute façon.

## Après le tag

Trois liens devront résoudre — à vérifier sur GitHub avant de soumettre :

- l. 93 (*AI contribution statement*) — le dépôt au tag ;
- l. 850–851 — l'URL figée vers `proof/`, une fois le placeholder remplacé.

Puis recompiler une dernière fois, et vérifier que le PDF soumis est **exactement** celui
du tag.
