# La densité d'énergie du vide

*Notebook : [`energie-du-vide.ipynb`](energie-du-vide.ipynb)*

**La question.** Combien d'énergie contient un mètre cube de vide ? Le calcul naïf de la théorie quantique donne un nombre infini ; avec une coupure raisonnable, il donne un nombre fini, mais environ $10^{120}$ fois plus grand que ce que mesure la cosmologie. C'est le pire désaccord entre théorie et observation de toute la physique.

## 1. Le vide est un ensemble d'oscillateurs

Un champ libre se décompose en modes de vecteur d'onde $\mathbf{k}$, chacun un oscillateur harmonique de pulsation $\omega_k = c|\mathbf{k}|$. Même dans son état fondamental, un oscillateur garde l'**énergie du point zéro** $\tfrac{1}{2}\hbar\omega$. L'[énergie du vide](https://fr.wikipedia.org/wiki/%C3%89nergie_du_vide) par unité de volume est la somme sur tous les modes :

$$
\rho_{\text{vide}} = \frac{1}{V}\sum_{\mathbf{k}} \frac{1}{2}\hbar\omega_k
\;\longrightarrow\;
\int \frac{d^3k}{(2\pi)^3}\,\frac{1}{2}\hbar c\,k .
$$

L'intégrale diverge comme $k^4$ : il y a toujours plus de modes de plus haute énergie.

## 2. Avec une coupure

Si l'on ne garde que les modes $|\mathbf{k}| < k_{\max}$ :

$$
\rho_{\text{vide}} = \frac{\hbar c}{2\pi^2}\int_0^{k_{\max}} k^3\,dk = \frac{\hbar c\,k_{\max}^4}{16\pi^2}
$$

par degré de liberté (le photon en a deux, ses deux polarisations). La coupure naturelle est l'échelle de Planck, $k_{\max} = 1/\ell_P$ avec $\ell_P = \sqrt{\hbar G/c^3} \approx 1{,}6 \times 10^{-35}$ m :

$$
\rho_{\text{Planck}} \sim \frac{\hbar c}{16\pi^2\,\ell_P^4} \approx 3 \times 10^{111}\ \text{J/m}^3 .
$$

## 3. Ce que mesure la cosmologie

L'expansion accélérée de l'univers révèle une énergie du vide (la [constante cosmologique](https://fr.wikipedia.org/wiki/Constante_cosmologique)) :

$$
\rho_\Lambda = \Omega_\Lambda\,\frac{3H_0^2}{8\pi G}\,c^2 \approx 5 \times 10^{-10}\ \text{J/m}^3 ,
$$

avec $H_0 \approx 68$ km/s/Mpc et $\Omega_\Lambda \approx 0{,}69$. Le rapport $\rho_{\text{Planck}}/\rho_\Lambda$ est de l'ordre de $10^{120}$ : c'est le **problème de la constante cosmologique**, toujours ouvert.

## 4. Sur une grille régulière

Si l'espace est une grille cubique de pas $a$ (voir [`../univers-5d/`](../univers-5d/)), la coupure n'est plus une hypothèse ajoutée, elle est dans la géométrie. Les vecteurs d'onde vivent dans la zone de Brillouin $[-\pi/a, \pi/a]^3$ et la relation de dispersion devient

$$
\omega(\mathbf{k}) = \frac{2c}{a}\sqrt{\sum_{i=1}^{3}\sin^2\frac{k_i a}{2}} .
$$

La densité d'énergie du vide est alors finie :

$$
\rho_{\text{vide}} = \int_{\text{ZB}} \frac{d^3k}{(2\pi)^3}\,\frac{1}{2}\hbar\,\omega(\mathbf{k}) = C\,\frac{\hbar c}{a^4},
$$

où $C$ est un nombre pur, calculé dans le notebook ($C \approx 1{,}19$). Le vide d'une grille a une énergie fixée par son pas : c'est une prédiction, et c'est aussi le problème, car il faudrait $a \sim 0{,}1$ mm pour retrouver $\rho_\Lambda$, une grille qu'on aurait vue depuis longtemps.

## 5. Ce qui se mesure vraiment

L'énergie absolue du vide n'est pas mesurable en laboratoire ; ses *différences* le sont. Entre deux plaques conductrices parallèles séparées de $d$, certains modes sont exclus, et le vide pousse les plaques l'une vers l'autre ([effet Casimir](https://fr.wikipedia.org/wiki/Effet_Casimir)) :

$$
\frac{F}{A} = -\frac{\pi^2\hbar c}{240\,d^4} ,
$$

environ $1{,}3$ mPa pour $d = 1\ \mu$m. Mesuré, confirmé.

## Ce qui est établi, ce qui est à explorer

- **Établi** : l'énergie du point zéro, la divergence en $k^4$, l'effet Casimir, la valeur observée de $\rho_\Lambda$.
- **Ouvert** : pourquoi l'énergie du vide gravite si peu. Les contributions des différents champs (bosons positives, fermions négatives) se compensent-elles ? La supersymétrie le ferait, si elle n'était pas brisée.
- **À explorer** : dans le cadre de l'univers 5D sur grille, l'énergie du vide de la surface 4D dépend-elle de son orientation par rapport à la grille ? Peut-elle s'annuler pour certaines orientations ?

## Le notebook

1. L'intégrale avec coupure, en `sympy`.
2. Les ordres de grandeur en SI avec `scipy.constants` : $\rho_{\text{Planck}}$, $\rho_\Lambda$, leur rapport.
3. La constante $C$ de la grille, par intégration numérique sur la zone de Brillouin, et la dispersion de la grille comparée au continu.
4. La pression de Casimir en fonction de la distance.
