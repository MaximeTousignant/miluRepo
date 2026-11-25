# Le temps, dimension imaginaire

*Notebook : [`temps-imaginaire.ipynb`](temps-imaginaire.ipynb)*

**La question.** Que se passe-t-il si l'on traite le temps comme une coordonnée imaginaire, $t = -i\tau$ ? Pourquoi ce geste, d'apparence purement formelle, relie-t-il la relativité, la mécanique quantique et la thermodynamique ?

## 1. L'intervalle de Minkowski

Avec le tempspatial $x^0 = ct$, l'intervalle de la relativité restreinte s'écrit

$$
ds^2 = -c^2\,dt^2 + dx^2 + dy^2 + dz^2 .
$$

Le signe moins devant le temps est toute la différence entre l'espace-temps et un espace euclidien à quatre dimensions. Poser $x^0 = i\,x^4$, c'est-à-dire $t = -i\tau$ (la [rotation de Wick](https://fr.wikipedia.org/wiki/Rotation_de_Wick)), absorbe ce signe :

$$
ds^2 = c^2\,d\tau^2 + dx^2 + dy^2 + dz^2 .
$$

Le temps imaginaire $\tau$ se comporte alors comme une quatrième direction d'espace.

## 2. Les boosts deviennent des rotations

Un boost de Lorentz de rapidité $\varphi$ dans le plan $(x^0, x)$ :

$$
\begin{pmatrix} x'^0 \\ x' \end{pmatrix}
=
\begin{pmatrix} \cosh\varphi & -\sinh\varphi \\ -\sinh\varphi & \cosh\varphi \end{pmatrix}
\begin{pmatrix} x^0 \\ x \end{pmatrix},
\qquad \tanh\varphi = \frac{v}{c}.
$$

Dans les coordonnées $(x^4, x)$ avec $x^0 = i x^4$, et pour une rapidité imaginaire $\varphi = i\theta$, c'est exactement une rotation d'angle $\theta$. La relativité restreinte est la géométrie euclidienne vue à travers un angle imaginaire : c'était déjà la lecture de Minkowski et de Poincaré.

## 3. Schrödinger devient la diffusion

L'équation de Schrödinger d'une particule libre,

$$
i\hbar\,\frac{\partial\psi}{\partial t} = -\frac{\hbar^2}{2m}\nabla^2\psi ,
$$

devient, avec $t = -i\tau$,

$$
\frac{\partial\psi}{\partial \tau} = \frac{\hbar}{2m}\nabla^2\psi ,
$$

l'équation de la chaleur. L'onde qui oscille devient une tache qui s'étale. Plus généralement, l'opérateur d'évolution $e^{-iHt/\hbar}$ devient $e^{-H\tau/\hbar}$ : chaque état propre d'énergie $E_n$ est amorti en $e^{-E_n\tau/\hbar}$, et pour $\tau \to \infty$ il ne reste que l'**état fondamental**. Le temps imaginaire fait tomber un système dans son vide (voir [`../energie-du-vide/`](../energie-du-vide/)).

## 4. Température et périodicité

La fonction de partition de la physique statistique,

$$
Z = \operatorname{Tr} e^{-\beta H}, \qquad \beta = \frac{1}{k_B T},
$$

est l'opérateur d'évolution évalué au temps imaginaire $\tau = \hbar\beta$. Une théorie quantique à température $T$ est donc une théorie en temps imaginaire **périodique**, de période

$$
\tau \sim \tau + \frac{\hbar}{k_B T}.
$$

L'[intégrale de chemin](https://fr.wikipedia.org/wiki/Int%C3%A9grale_de_chemin) suit le même chemin : le poids oscillant $e^{iS/\hbar}$ devient le poids réel $e^{-S_E/\hbar}$, une probabilité de Boltzmann. C'est ce qui rend les simulations sur réseau possibles.

## Ce qui est établi, ce qui est à explorer

- **Établi** : la rotation de Wick comme outil de calcul (théorie quantique des champs, physique statistique, théorie de jauge sur réseau). Les correspondances des §§ 2 à 4 sont exactes.
- **Débattu** : que le temps *soit* imaginaire, physiquement. La proposition « sans bord » de Hartle et Hawking va dans ce sens pour l'univers primordial ; voir [temps imaginaire](https://fr.wikipedia.org/wiki/Temps_imaginaire).
- **À explorer** : la flèche du temps. Le temps réel a une direction, le temps euclidien n'en a pas. Où se perd la symétrie ?

## Le notebook

1. La rotation de Wick avec `sympy` : la métrique, puis le boost qui devient une rotation.
2. L'évolution en temps imaginaire d'un oscillateur harmonique sur une grille : l'énergie descend vers $\tfrac{1}{2}\hbar\omega$, l'énergie du point zéro.
