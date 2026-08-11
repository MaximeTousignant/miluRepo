# stokexproof — vérification formelle du $tôkEx

Preuve en **Lean 4 + mathlib** des affirmations centrales de la publication
défensive `../stokex_defensive_publication.tex`. Ce qui est démontré ici est
démontré : une machine l'a vérifié, ligne à ligne.

Les théorèmes, et l'annexe du document qu'ils couvrent :

| Théorème | Ce qu'il établit | Annexe |
|---|---|---|
| `traderF_slope_at_one` | la pente de `f` en `x = 1` vaut 3 — base de l'interprétation angulaire `w = tan(θ)/3` | 7.3 |
| `exchange_at_market_price` | tout échange se fait au prix du marché : `−Ẋᵅ/Ẋᵝ = [α/β]_Ω` | 7.4 |
| `market_clears` | le prix en forme close annule le flot net de l'actif A | 7.5 |
| `market_price_unique` | le prix d'équilibre est unique | 7.6 |
| `market_is_single_participant` | le marché entier se comporte comme un participant unique de poids `W_Ω` | 7.7 |
| `traderF_strictMonoOn` | la fonction de marchand est strictement croissante sur `(0, ∞)` — principe 7 | — |

Les numéros d'annexe sont ceux de la version 2026-07 ; les clés `\label`
stables (`secProofDegree`, `secProofUniqueness`, …) sont données en tête du
fichier Lean, avec le dictionnaire de notation article ↔ Lean.

**La portée exacte, sans arrondi.** Deux précisions que le tableau ne peut pas
porter, et qui comptent pour qui vérifie :

- `market_clears` démontre la **réciproque** de l'annexe 7.5. L'annexe part de
  l'équilibre et en dérive le prix en forme close (nécessité) ; le théorème part
  du prix en forme close et en dérive l'équilibre (suffisance). L'article laisse
  cette direction implicite ; la machine la couvre.
- `market_price_unique` démontre l'**unicité seule**. L'existence d'un prix
  d'équilibre, que l'annexe 7.6 obtient par le théorème des valeurs
  intermédiaires, n'est pas formalisée ici.

## Prérequis système

La chaîne Lean est un **prérequis système, non reconstructible depuis ce repo**
(voir `docs/Cablage.md`, organe E — l'établi). Il faut :

- **elan**, le gestionnaire de toolchains Lean — https://leanprover-community.github.io/get_started.html
- la toolchain déclarée dans `lean-toolchain` (`leanprover/lean4:v4.32.0`) ;
  `elan` l'installe seul à la première invocation de `lake`.
- **mathlib**, version `v4.32.0`, épinglée dans `lakefile.toml` et
  `lake-manifest.json`.

S'il manque, on le dit et on ne bricole pas : une preuve à moitié vérifiée ne
prouve rien.

## Vérifier la preuve

```sh
cd publications/stokex/proof && lake exe cache get && lake build
```

`lake exe cache get` récupère les `.olean` précompilés de mathlib — sans lui, la
première compilation dure des heures. Une sortie sans erreur **est** le résultat :
tous les théorèmes du fichier sont vérifiés. Les artefacts de compilation
(`.lake/`) sont gitignorés.

## Notes

Ce dossier est le miroir d'un dépôt Lean autonome ; ses `.github/workflows/` ne
s'exécutent pas ici (GitHub ne lit que le `.github/` de la racine du dépôt). Ils
sont conservés tels quels pour que le dossier reste détachable.

Comme tout `publications/`, ce contenu est dans la **zone signée** : CC BY 4.0
(voir `../LICENSE`), et non CC0 comme le reste du dépôt.
