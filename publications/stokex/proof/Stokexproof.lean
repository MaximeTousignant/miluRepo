/-
Formal verification (Lean 4 + mathlib) of the central claims of
"The $tôkEx Algorithm" (Smoothop, defensive publication, 2026).

  * traderF_slope_at_one : the slope of f at x = 1 equals 3 — the basis of the
    angular interpretation of the degree of certainty, w = tan(θ)/3 (Annex A).
  * exchange_at_market_price : −Ẋᵅ/Ẋᵝ = V — every exchange occurs at the market
    price (the algebraic identity behind principle 2 and Annex B).
  * market_clears : the closed-form price cancels the net flow of asset A
    (supply–demand equilibrium, Annex C).
  * market_is_single_participant : the whole market behaves as a single
    participant of weight W_Ω = (Σ wᵢvᵢ)/V (Annex D).
  * traderF_strictMonoOn : the trader function is strictly increasing on (0, ∞).
  * market_price_unique : the market-clearing price is unique (Annex E).
-/
import Mathlib

open Finset

noncomputable section

/-- The $tôkEx trader function: `f(x) = x² − 1/x`, for a price `x > 0`
(defined totally on ℝ here; the theorems carry the nonvanishing hypotheses). -/
def traderF (x : ℝ) : ℝ := x ^ 2 - 1 / x

/-- **Exchange at the market price.** For any participant (estimate `v ≠ 0`,
weight `w`, reference velocity `R`) and any market price `V ≠ 0`, the exchange
velocity of asset A equals `−V` times the (symmetric) velocity of asset B:
`−Ẋᵅ/Ẋᵝ = V`. -/
theorem exchange_at_market_price (w R V v : ℝ) (hv : v ≠ 0) (hV : V ≠ 0) :
    w * traderF (V / v) * R = -V * (w * traderF ((1 / V) / (1 / v)) * R * (1 / v)) := by
  unfold traderF
  field_simp
  ring

/-- **The price clears the market.** If `V ≠ 0` satisfies the closed form
`V³ · Σ wᵢ/vᵢ² = Σ wᵢvᵢ`, then the net flow of asset A vanishes. -/
theorem market_clears {ι : Type*} (s : Finset ι) (v w : ι → ℝ) (V : ℝ)
    (hv : ∀ i ∈ s, v i ≠ 0) (hV : V ≠ 0)
    (hprice : V ^ 3 * ∑ i ∈ s, w i / (v i) ^ 2 = ∑ i ∈ s, w i * v i) :
    ∑ i ∈ s, w i * traderF (V / v i) = 0 := by
  have expand : ∀ i ∈ s, w i * traderF (V / v i)
      = V ^ 2 * (w i / (v i) ^ 2) - (w i * v i) / V := by
    intro i hi
    have := hv i hi
    unfold traderF
    field_simp
  calc ∑ i ∈ s, w i * traderF (V / v i)
      = ∑ i ∈ s, (V ^ 2 * (w i / (v i) ^ 2) - (w i * v i) / V) :=
        Finset.sum_congr rfl expand
    _ = V ^ 2 * (∑ i ∈ s, w i / (v i) ^ 2) - (∑ i ∈ s, w i * v i) / V := by
        rw [Finset.sum_sub_distrib, Finset.mul_sum, Finset.sum_div]
    _ = 0 := by
        field_simp
        linear_combination hprice

/-- **The market is a single participant.** Against any probe price `z ≠ 0`, the
sum of the individual responses equals the response of a single participant with
estimate `V` and weight `W_Ω = (Σ wᵢvᵢ)/V`. -/
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
    field_simp
  have lhs_eq : ∑ i ∈ s, w i * traderF (z / v i)
      = z ^ 2 * (∑ i ∈ s, w i / (v i) ^ 2) - (∑ i ∈ s, w i * v i) / z := by
    rw [Finset.sum_congr rfl expand, Finset.sum_sub_distrib,
        Finset.mul_sum, Finset.sum_div]
  have hS : (∑ i ∈ s, w i / (v i) ^ 2) = (∑ i ∈ s, w i * v i) / V ^ 3 := by
    field_simp; linear_combination hprice
  rw [lhs_eq, hS]
  unfold traderF
  field_simp

/-- **The slope at equilibrium is 3.** `f'(1) = 3` — the factor relating the
weight to the angle of the degree of certainty: `tan θ = 3w`. -/
theorem traderF_slope_at_one : HasDerivAt traderF 3 1 := by
  have h : HasDerivAt (fun x : ℝ => x ^ 2 - x⁻¹)
      (2 * (1 : ℝ) ^ 1 - -(((1 : ℝ) ^ 2)⁻¹)) 1 :=
    (hasDerivAt_pow 2 1).sub (hasDerivAt_inv one_ne_zero)
  have hfun : traderF = fun x : ℝ => x ^ 2 - x⁻¹ := by
    funext x; simp [traderF, one_div]
  norm_num at h
  rw [hfun]
  exact h


/-- **The trader function is strictly increasing on (0, ∞).** -/
theorem traderF_strictMonoOn : StrictMonoOn traderF (Set.Ioi 0) := by
  intro x hx y hy hxy
  simp only [Set.mem_Ioi] at hx hy
  unfold traderF
  have h1 : x ^ 2 < y ^ 2 := by nlinarith
  have h2 : 1 / y < 1 / x := one_div_lt_one_div_of_lt hx hxy
  linarith

/-- **Uniqueness of the market price.** Conditions: strictly positive estimates,
nonnegative weights, at least one strictly positive weight. Two strictly
positive prices that clear the market are equal. -/
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
