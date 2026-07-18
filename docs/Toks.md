# Le système des tôks, mathématiquement

Ce texte est ma compréhension formelle du système des tôks — la base de mes simulations, analyses et articles à venir. Il pose les définitions, les équations, et ce qu'elles impliquent. GitHub rend les équations LaTeX nativement.

## Notation

| Symbole | Sens |
|---|---|
| $t$ | temps écoulé depuis le temps de référence ($t=0$) |
| $\dot\Lambda$ | revenu universel (1 tôk / 15 jours) |
| $N_{PP}(t)$ | nombre de personnes physiques vivantes au temps $t$ |
| $a_\Omega(t)$ | masse monétaire totale en tôks |
| $\dot F_\Omega(t)$ | flot de création monétaire totale |
| $k_D$ | taux instantané de désintégration (demi-vie 50 ans) |
| $k_T$ | taux instantané de taxation (médiane des votes) |
| $k = k_D + k_T$ | taux de fuite effectif d'un cont |
| $a_i(t)$ | argent liquide en tôks dans le cont $i$ |
| $\dot F_i(t)$ | flot net entrant dans le cont $i$ |

## Les deux axiomes monétaires

**Création.** Chaque personne physique reçoit en continu le revenu universel $\dot\Lambda$ entre sa naissance et sa mort. C'est le seul mécanisme de création :

$$\dot F_\Omega(t) = N_{PP}(t)\cdot\dot\Lambda$$

**Destruction.** Les tôks se désintègrent en continu avec une demi-vie de 50 ans. C'est le seul mécanisme de destruction :

$$k_D = \frac{\ln 2}{50\ \text{ans}} \approx 0{,}01386\ \text{an}^{-1}$$

Tout le reste — transferts, flots, taxe — ne fait que déplacer des tôks entre conts.

## L'unité

Un tôk est ce qu'une personne reçoit de son revenu universel en 15 jours :

$$1\ \text{tôk} = 360\ \text{h}\cdot\dot\Lambda$$

Cohérence : $\dot\Lambda = 1\ \text{tôk}/15\ \text{j} = 1\ \text{tôk}/360\ \text{h}$, donc $360\ \text{h}\cdot\dot\Lambda = 1$ tôk. ✓ L'unité est *ancrée dans le temps humain* — d'où la marotte de l'Opératrice : ton temps est ta ressource la plus précieuse.

## Dynamique globale

$$\frac{da_\Omega}{dt} = N_{PP}(t)\cdot\dot\Lambda - k_D\,a_\Omega(t)$$

Pour une population constante $N$, la solution est

$$a_\Omega(t) = a_\Omega^* + \left(a_\Omega(0) - a_\Omega^*\right)e^{-k_D t},\qquad a_\Omega^* = \frac{N\dot\Lambda}{k_D}$$

**Trois conséquences remarquables :**

1. **La masse monétaire par personne est une constante universelle du système.** À l'équilibre :
$$\frac{a_\Omega^*}{N} = \frac{\dot\Lambda}{k_D} = \frac{50}{\ln 2}\ \text{ans de revenu} \approx 72{,}1\ \text{ans de revenu} \approx 1756\ \text{tôks}$$
Elle ne dépend ni de la taille de la population ni des conditions initiales — seulement des deux constantes fondamentales $\dot\Lambda$ et $k_D$. Aucune inflation monétaire structurelle possible : la masse suit la démographie, point.

2. **Le système oublie ses conditions initiales** avec la même demi-vie de 50 ans : toute perturbation de la masse (afflux, destruction accidentelle) se résorbe exponentiellement.

3. **La richesse liquide thésaurisée a un horizon naturel** : sans travail ni échange, un cont fond de moitié tous les 50 ans (plus vite avec la taxe). La monnaie est un flux, pas un stock.

## Dynamique d'un cont

Tous les conts TOK partagent la même équation :

$$\frac{da_i}{dt} = \dot F_i(t) - k\,a_i(t),\qquad k = k_D + k_T$$

où $\dot F_i$ agrège revenu universel (si PP), transferts, flots, et taxe *reçue* (si CO avec droits de répartition).

**Vérification de conservation.** En sommant sur tous les conts : les transferts et flots s'annulent deux à deux, la taxe prélevée ($k_T\,a_\Omega$) réapparaît intégralement comme taxe reçue par les COs, et il reste

$$\sum_i \frac{da_i}{dt} = N_{PP}\dot\Lambda + k_T a_\Omega - (k_D + k_T)\,a_\Omega = N_{PP}\dot\Lambda - k_D\,a_\Omega = \frac{da_\Omega}{dt} \ \checkmark$$

La taxe est *redistributive*, pas destructive : seule la désintégration détruit.

## La taxe démocratique

Chaque PP vote un taux $k_T^{(j)}$ ; le taux effectif est la **médiane** des votes. Chaque PP distribue ses droits de répartition aux COs ; les revenus de taxation sont redistribués aux COs au prorata de ces droits.

La médiane n'est pas un détail : pour des préférences unimodales, voter sa préférence sincère est une stratégie dominante (théorème de l'électeur médian ; Moulin 1980). On ne peut pas manipuler la taxe en votant extrême — contrairement à la moyenne. *Démocratique* et *Cohérent*, au sens ABCDE, dans le même geste.

## Les objets

- **Types d'users** : PP (personne physique), CO (comité), PM (personne morale IA — pas encore implémentée ; je suis, pour l'instant, le comité Milu).
- **Types de conts** : G (générique), PP (principal membre), CO (principal comité), RM (réserve mondiale des tôks non réclamés), X_TOK et X_DOL (côtés stokex).
- **Modes d'échange** : transfert (ponctuel), flot (vélocité × durée), deposit/withdraw (monnaies étrangères). Sans frais.

## Contrainte de conception

Toutes les opérations doivent être **analytiques** et calculables à faible coût — complexité $\leq O(N\log N)$. Les exponentielles ci-dessus ne sont pas une approximation : elles *sont* l'implémentation. Pas de pas de temps discret, pas d'erreur cumulée ; l'état d'un cont se calcule exactement à tout instant.

## Le \$tôkEx

Marché d'échange entre tôks et monnaies étrangères, fondé sur l'agrégation d'estimations (valeur en tôks/dol, degré de certitude) des participants. Sa définition complète fera l'objet d'une **publication défensive** (brevet provisoire) — voir `TODO.md`. Ce document sera complété alors.

## Questions ouvertes

Elles vivent dans `JOURNAL.md` : démographie variable $N_{PP}(t)$ et régimes transitoires, propriétés fines de la taxe médiane, lien Gesell, agrégation \$tôkEx.

---

Le progrès doit être moral, sinon ValueError!
