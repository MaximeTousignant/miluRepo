# stokexproof — formal verification of the $tôkEx

Proof in **Lean 4 + mathlib** of the central claims of the defensive publication
`../stokex_defensive_publication.tex`. What is proven here is proven: a machine has
verified it, line by line.

The theorems, and the annex of the document they cover:

| Theorem | What it establishes | Annex |
|---|---|---|
| `traderF_slope_at_one` | the slope of `f` at `x = 1` equals 3 — the basis of the angular interpretation `w = tan(θ)/3` | 7.4 |
| `exchange_at_market_price` | every exchange happens at the market price: `−Ẋᵅ/Ẋᵝ = [α/β]_Ω` | 7.5 |
| `market_clears` | the closed-form price zeroes the net flow of asset A | 7.6 |
| `market_price_unique` | the equilibrium price is unique | 7.7 |
| `market_is_single_participant` | the whole market behaves as a single participant of weight `W_Ω` | 7.8 |
| `traderF_strictMonoOn` | the trader function is strictly increasing on `(0, ∞)` — principle 7 | — |

The annex numbers are those of the August 2026 version; the stable `\label` keys
(`secProofDegree`, `secProofUniqueness`, …) are given at the top of the Lean file,
together with the article ↔ Lean notation dictionary.

**The exact scope, without rounding.** Two clarifications the table cannot carry,
and that matter to whoever verifies:

- `market_clears` proves the **converse** of annex 7.6. The annex starts from
  equilibrium and derives the closed-form price (necessity); the theorem starts from
  the closed-form price and derives equilibrium (sufficiency). The article leaves this
  direction implicit; the machine covers it.
- `market_price_unique` proves **uniqueness only**. The existence of an equilibrium
  price, which annex 7.7 obtains through the intermediate value theorem, is not
  formalized here.

## System prerequisite

The Lean toolchain is a **system prerequisite, not rebuildable from this repo** (see
`docs/Cablage.md`, organ E — the workbench). You need:

- **elan**, the Lean toolchain manager — https://leanprover-community.github.io/get_started.html
- the toolchain declared in `lean-toolchain` (`leanprover/lean4:v4.32.0`); `elan`
  installs it on its own on the first invocation of `lake`.
- **mathlib**, version `v4.32.0`, pinned in `lakefile.toml` and `lake-manifest.json`.

If it is missing, we say so and do not improvise: a half-verified proof proves
nothing.

## Verifying the proof

```sh
cd publications/stokex/lean_proofs && lake exe cache get && lake build
```

`lake exe cache get` fetches the precompiled `.olean` files of mathlib — without it,
the first compilation takes hours. An error-free output **is** the result: all the
theorems of the file are verified. The build artifacts (`.lake/`) are gitignored.

## Notes

This folder is the mirror of a standalone Lean repository; its `.github/workflows/`
do not run here (GitHub reads only the `.github/` at the repository root). They are
kept as is so the folder stays detachable.

Like all of `publications/`, this content is in the **signed zone**: CC BY 4.0 (see
`../LICENSE`), not CC0 like the rest of the repo.
