# publications/toksys_1 — workflow

**Le système des tôks, partie 1 : le temps, les humains, les tôks et les flots**
(`toksys_1.tex`), premier article de la série arrêtée le 2026-08-04 — voir `TODO.md`,
section « Recherche ».

La série, pour situer ce dossier :

1. le \$tôkEx (`publications/stokex/`) — publication défensive TDCommons ;
2. **partie 1 — le temps, les humains, les tôks et les flots** *(ici)* ;
3. partie 2 — la taxe démocratique et le \$tôkEx ;
4. partie 3 — la bourse du carbone citoyenne et la transition énergétique.

Cible : revues à comité de lecture spécialisées en économie, sur les sujets qui touchent
le revenu universel. Le choix des revues est ouvert — c'est la première tâche de la
section « Recherche » du `TODO.md`, et il détermine format, longueur et politique de
déclaration de contribution IA.

## Ce qui n'est pas encore décidé

- **Signature.** La `LICENSE` de ce dossier porte `À CONFIRMER` à la ligne du copyright.
  Le \$tôkEx a tranché pour un auteur unique nommé, avec déclaration de contribution IA ;
  ici, le mandat confie au **comité Milu** le développement des équations, ce qui n'est
  pas la même chose qu'une signature. À régler avant toute soumission, et à reporter dans
  la `LICENSE` **et** dans la page titre du `.tex`.
- **Langue.** Le squelette est en anglais, par cohérence avec le \$tôkEx et avec les
  revues visées. À confirmer si une revue francophone entre dans la liste.
- **Contenu mathématique.** Les équations sont en cours d'écriture par l'Opératrice. Ce
  dossier n'en contient aucune qui ne soit déjà publique et vérifiée dans `docs/Toks.md` ;
  le corps du document est en `\placeholder`.

## Environnement Python

Même établi que le reste du repo : un seul `.venv/` à la racine, gitignoré,
reconstructible depuis `requirements.txt`. C'est l'organe E du câblage — spécification
dans `docs/Cablage.md`.

```sh
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

Prérequis système : une installation LaTeX (`latex`, `dvipng`), fournie par
MacTeX / TeX Live. Non reconstructible depuis ce repo — s'il manque, on le dit.

## Compiler le document

```sh
cd publications/toksys_1 && latexmk -pdf -interaction=nonstopmode -halt-on-error toksys_1.tex
```

Compilation continue (recompile à chaque sauvegarde) :

```sh
cd publications/toksys_1 && latexmk -pvc -pdf -interaction=nonstopmode -view=none toksys_1.tex
```

Les artefacts (`.aux`, `.log`, `.fls`, `.fdb_latexmk`, …) sont gitignorés.

## Une source de vérité pour les constantes

Les constantes du système ne se recopient pas de mémoire : elles se lisent en direct.

```sh
curl -s https://tok-backend-v2-640177943705.northamerica-northeast1.run.app/api/tok-constants
```

`k_des`, `r_umg` ($\dot\Lambda$), `a_inf`, `tax`, `time`, `flows_limits`. Toute valeur
numérique du document doit s'y rapporter, ou dire explicitement d'où elle vient.

**Piège de lecture** — l'API renvoie un `amount` extrapolé linéairement sur le délai non
résolu du solve paresseux : différencier deux relevés d'`amount` mesure $k/(1-k\,dt)$ et
non $k$. Prendre `net_revenue` tel quel. Détail dans `docs/Cablage.md`, section
« La carte de l'API du tok-backend ».

## Placeholders

Comme dans `stokex/`, la macro `\placeholder{...}` (boîte jaune) marque ce qui reste à
écrire. Avant toute soumission :

```sh
grep -n "placeholder" toksys_1.tex
```

ne doit plus rien retourner dans le corps du texte.
