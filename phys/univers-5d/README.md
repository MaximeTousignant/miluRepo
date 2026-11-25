# L'espace-temps, surface d'un univers 5D

*Notebook : [`univers-5d.ipynb`](univers-5d.ipynb)*

**La question.** Peut-on voir notre espace-temps à quatre dimensions comme une surface (une [hypersurface](https://fr.wikipedia.org/wiki/Hypersurface)) plongée dans un univers à cinq dimensions, et que se passe-t-il si cet univers est une grille régulière plutôt qu'un continu ?

## 1. Le plongement et la métrique induite

Un univers 5D de coordonnées $X^A$ ($A = 0 \ldots 4$) et de métrique $G_{AB}$. Notre espace-temps est une surface paramétrée par $x^\mu$ ($\mu = 0 \ldots 3$) :

$$
X^A = X^A(x^\mu).
$$

Les distances mesurées *sur* la surface sont données par la **métrique induite** :

$$
g_{\mu\nu} = G_{AB}\,\frac{\partial X^A}{\partial x^\mu}\,\frac{\partial X^B}{\partial x^\nu}.
$$

Toute la géométrie 4D, courbure comprise, peut naître de la forme de la surface, même si l'univers 5D est plat. (Un théorème de plongement garantit qu'avec assez de dimensions, toute géométrie 4D s'obtient ainsi ; cinq suffisent pour les cas cosmologiques simples.)

## 2. L'exemple de de Sitter

Dans l'espace de Minkowski 5D, $G_{AB} = \operatorname{diag}(-1,1,1,1,1)$, l'hyperboloïde

$$
-X_0^2 + X_1^2 + X_2^2 + X_3^2 + X_4^2 = \ell^2
$$

est l'[espace de de Sitter](https://fr.wikipedia.org/wiki/Espace_de_de_Sitter) : un univers en expansion accélérée, le modèle d'un univers dominé par une constante cosmologique. Avec $X^0 = \ell\sinh(t/\ell)$ et $X^i = \ell\cosh(t/\ell)\,\omega^i$ (où $\omega^i$ parcourt la sphère unité $S^3$), la métrique induite est

$$
ds^2 = -dt^2 + \ell^2\cosh^2(t/\ell)\,d\Omega_3^2 .
$$

**Le pont avec le temps imaginaire.** Avec $t = -i\tau$, $\sinh \to -i\sin$ et $\cosh \to \cos$ : l'hyperboloïde devient la **4-sphère** $X_0^2 + \cdots + X_4^2 = \ell^2$ dans $\mathbb{R}^5$ euclidien. Un univers en expansion est, en temps imaginaire, une sphère dans un espace plat à cinq dimensions (voir [`../temps-imaginaire/`](../temps-imaginaire/)).

## 3. La cinquième dimension enroulée

Dans la [théorie de Kaluza-Klein](https://fr.wikipedia.org/wiki/Th%C3%A9orie_de_Kaluza-Klein), la cinquième dimension est un cercle de rayon $R$. Un champ qui y vit se décompose en modes $\phi(x, y) = \sum_n \phi_n(x)\,e^{iny/R}$, et chaque mode apparaît en 4D comme une particule de masse

$$
m_n c^2 = \frac{n\,\hbar c}{R}, \qquad n = 0, 1, 2, \ldots
$$

Un tout petit $R$ rend tous les modes $n \neq 0$ trop lourds pour être vus : la cinquième dimension est cachée par sa petitesse.

## 4. Sur une grille régulière

Remplaçons le cercle continu par $N$ sites espacés de $a$, avec $Na = 2\pi R$. La dérivée devient une différence finie, et le spectre des masses devient

$$
m_n c^2 = \frac{2\hbar c}{a}\,\left|\sin\frac{\pi n}{N}\right| .
$$

Pour $n \ll N$, on retrouve $n\hbar c/R$ : la grille imite le continu à basse énergie. Près de $n = N/2$, le spectre plafonne à $2\hbar c/a$ : **la grille impose une énergie maximale**, une coupure naturelle. C'est cette coupure qui rend finie l'énergie du vide (voir [`../energie-du-vide/`](../energie-du-vide/)). La même idée, appliquée aux quatre dimensions ordinaires, est celle de la [théorie de jauge sur réseau](https://fr.wikipedia.org/wiki/Th%C3%A9orie_de_jauge_sur_r%C3%A9seau).

## Ce qui est établi, ce qui est à explorer

- **Établi** : la métrique induite, de Sitter comme hyperboloïde, le spectre de Kaluza-Klein, la discrétisation d'une dimension (« déconstruction » en théorie des champs).
- **À explorer** : une grille régulière dans les *cinq* dimensions, avec la surface 4D qui la traverse en biais. Une surface qui n'est pas alignée sur la grille voit-elle une invariance de Lorentz approchée ? Comment mesurer la distance d'une surface à une grille ?
- **À explorer** : les modèles de branes où la cinquième dimension est grande mais courbée ([Randall-Sundrum](https://en.wikipedia.org/wiki/Randall%E2%80%93Sundrum_model)).

## Le notebook

1. La métrique induite avec `sympy` : de Sitter dans Minkowski 5D, puis la 4-sphère dans $\mathbb{R}^5$ par rotation de Wick.
2. Le spectre de Kaluza-Klein sur une grille de $N$ sites, comparé au continu.
