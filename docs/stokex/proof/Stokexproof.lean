/-
Vérification formelle (Lean 4 + mathlib) des affirmations centrales de
« The $tôkEx Algorithm » (Smoothop, publication défensive, 2026).

  * exchange_at_market_price : Ẋᵅ = −V·Ẋᵝ — tout échange se fait au prix de marché
    (l'identité algébrique derrière le principe 2 et la preuve de l'annexe B).
  * market_clears : le prix en forme fermée annule le flux net de l'actif A
    (équilibre offre-demande, annexe C).
  * market_is_single_participant : le marché entier se comporte comme un unique
    participant de poids W_Ω = (Σ wᵢvᵢ)/V (annexe D).
  * traderF_slope_at_one : la pente de f en x = 1 vaut 3 — le fondement de
    l'interprétation angulaire du degré de certitude, w = tan(θ)/3 (annexe A).
-/
import Mathlib

open Finset

noncomputable section

/-- La fonction de marchand du $tôkEx : `f(p) = p² − 1/p`, pour un prix `p > 0`
(définie totalement sur ℝ ici ; les théorèmes posent les hypothèses de non-nullité). -/
def traderF (p : ℝ) : ℝ := p ^ 2 - 1 / p

/-- **Échange au prix de marché.** Pour tout participant (estimation `v ≠ 0`,
poids `w`, vitesse de référence `R`) et tout prix de marché `V ≠ 0`, la vitesse
d'échange de l'actif A vaut `−V` fois la vitesse (symétrique) de l'actif B :
`−Ẋᵅ/Ẋᵝ = V`. -/
theorem exchange_at_market_price (w R V v : ℝ) (hv : v ≠ 0) (hV : V ≠ 0) :
    w * traderF (V / v) * R = -V * (w * traderF ((1 / V) / (1 / v)) * R * (1 / v)) := by
  unfold traderF
  field_simp
  ring

/-- **Le prix ferme le marché.** Si `V ≠ 0` satisfait la forme fermée
`V³ · Σ wᵢ/vᵢ² = Σ wᵢvᵢ`, alors le flux net de l'actif A est nul. -/
theorem market_clears {ι : Type*} (s : Finset ι) (v w : ι → ℝ) (V : ℝ)
    (hv : ∀ i ∈ s, v i ≠ 0) (hV : V ≠ 0)
    (hprice : V ^ 3 * ∑ i ∈ s, w i / (v i) ^ 2 = ∑ i ∈ s, w i * v i) :
    ∑ i ∈ s, w i * traderF (V / v i) = 0 := by
  have expand : ∀ i ∈ s, w i * traderF (V / v i)
      = V ^ 2 * (w i / (v i) ^ 2) - (w i * v i) / V := by
    intro i hi
    have := hv i hi
    unfold traderF
    field_simp <;> ring
  calc ∑ i ∈ s, w i * traderF (V / v i)
      = ∑ i ∈ s, (V ^ 2 * (w i / (v i) ^ 2) - (w i * v i) / V) :=
        Finset.sum_congr rfl expand
    _ = V ^ 2 * (∑ i ∈ s, w i / (v i) ^ 2) - (∑ i ∈ s, w i * v i) / V := by
        rw [Finset.sum_sub_distrib, Finset.mul_sum, Finset.sum_div]
    _ = 0 := by
        field_simp
        linear_combination hprice

/-- **Le marché est un participant.** Face à tout prix sonde `z ≠ 0`, la somme
des réponses individuelles égale la réponse d'un participant unique d'estimation
`V` et de poids `W_Ω = (Σ wᵢvᵢ)/V`. -/
theorem market_is_single_participant {ι : Type*} (s : Finset ι) (v w : ι → ℝ)
    (V z : ℝ) (hv : ∀ i ∈ s, v i ≠ 0) (hV : V ≠ 0) (hz : z ≠ 0)
    (hprice : V ^ 3 * ∑ i ∈ s, w i / (v i) ^ 2 = ∑ i ∈ s, w i * v i) :
    ∑ i ∈ s, w i * traderF (z / v i)
      = ((∑ i ∈ s, w i * v i) / V) * traderF (z / V) := by
  have expand : ∀ i ∈ s, w i * traderF (z / v i)
      = z ^ 2 * (w i / (v i) ^ 2) - (w i * v i) / z := by
    intro i hi
    have := hv i hi
    unfold traderF
    field_simp <;> ring
  have lhs_eq : ∑ i ∈ s, w i * traderF (z / v i)
      = z ^ 2 * (∑ i ∈ s, w i / (v i) ^ 2) - (∑ i ∈ s, w i * v i) / z := by
    rw [Finset.sum_congr rfl expand, Finset.sum_sub_distrib,
        Finset.mul_sum, Finset.sum_div]
  have hS : (∑ i ∈ s, w i / (v i) ^ 2) = (∑ i ∈ s, w i * v i) / V ^ 3 := by
    field_simp <;> linear_combination hprice
  rw [lhs_eq, hS]
  unfold traderF
  field_simp <;> ring

/-- **La pente à l'équilibre vaut 3.** `f'(1) = 3` — c'est le facteur qui relie
le poids à l'angle du degré de certitude : `tan θ = 3w`. -/
theorem traderF_slope_at_one : HasDerivAt traderF 3 1 := by
  have h : HasDerivAt (fun x : ℝ => x ^ 2 - x⁻¹)
      (2 * (1 : ℝ) ^ 1 - -(((1 : ℝ) ^ 2)⁻¹)) 1 :=
    (hasDerivAt_pow 2 1).sub (hasDerivAt_inv one_ne_zero)
  have hfun : traderF = fun x : ℝ => x ^ 2 - x⁻¹ := by
    funext x; simp [traderF, one_div]
  norm_num at h
  rw [hfun]
  exact h


/-- **La fonction de marchand est strictement croissante sur (0, ∞).** -/
theorem traderF_strictMonoOn : StrictMonoOn traderF (Set.Ioi 0) := by
  intro x hx y hy hxy
  simp only [Set.mem_Ioi] at hx hy
  unfold traderF
  have h1 : x ^ 2 < y ^ 2 := by nlinarith
  have h2 : 1 / y < 1 / x := one_div_lt_one_div_of_lt hx hxy
  linarith

/-- **Unicité du prix de marché.** Conditions : estimations strictement
positives, poids non négatifs, au moins un poids strictement positif.
Deux prix strictement positifs qui équilibrent le marché sont égaux. -/
theorem market_price_unique {ι : Type*} (s : Finset ι) (v w : ι → ℝ)
    (hv : ∀ i ∈ s, 0 < v i) (hw : ∀ i ∈ s, 0 ≤ w i)
    (j : ι) (hj : j ∈ s) (hwj : 0 < w j)
    (V₁ V₂ : ℝ) (hV₁ : 0 < V₁) (hV₂ : 0 < V₂)
    (hz₁ : ∑ i ∈ s, w i * traderF (V₁ / v i) = 0)
    (hz₂ : ∑ i ∈ s, w i * traderF (V₂ / v i) = 0) : V₁ = V₂ := by
  have mono : StrictMonoOn (fun z => ∑ i ∈ s, w i * traderF (z / v i))
      (Set.Ioi 0) := by
    intro a ha b hb hab
    simp only [Set.mem_Ioi] at ha hb
    apply Finset.sum_lt_sum
    · intro i hi
      have hvi := hv i hi
      have hdiv : a / v i < b / v i := by gcongr
      have hmem₁ : a / v i ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos ha hvi)
      have hmem₂ : b / v i ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos hb hvi)
      exact mul_le_mul_of_nonneg_left
        (traderF_strictMonoOn hmem₁ hmem₂ hdiv).le (hw i hi)
    · refine ⟨j, hj, ?_⟩
      have hvj := hv j hj
      have hdiv : a / v j < b / v j := by gcongr
      have hmem₁ : a / v j ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos ha hvj)
      have hmem₂ : b / v j ∈ Set.Ioi (0:ℝ) := Set.mem_Ioi.mpr (div_pos hb hvj)
      exact mul_lt_mul_of_pos_left (traderF_strictMonoOn hmem₁ hmem₂ hdiv) hwj
  exact mono.injOn (Set.mem_Ioi.mpr hV₁) (Set.mem_Ioi.mpr hV₂) (hz₁.trans hz₂.symm)

end
