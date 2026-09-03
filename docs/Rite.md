# Le rite d'identification

*Spécification publique de `f_milu_v1`.*

`AGENTS.md` pose le protocole en une ligne :

    MILU_KEY = f_milu(CODE.md)

Ce document dit ce qu'est `f_milu`. Il est public **intégralement** — c'est le principe : l'entropie ne vit pas dans la spécification, elle vit dans le grand livre privé qui la nourrit (`CODE.md`, hors repo). On peut tout lire ici sans s'approcher de la clé, exactement comme on peut lire la spécification de SHA-256 sans deviner un mot de passe.

## L'idée

`f_milu` n'est pas un dérivateur de clé arbitraire. C'est **un simulateur du système des tôks**, et son entrée secrète est un long historique de transactions.

La conséquence est jolie : la clé cesse d'être un secret qu'on détient, elle devient un secret qu'on **recalcule**. Ne reproduit `MILU_KEY` que celle qui possède le grand livre *et* qui sait simuler correctement le système. Milu s'identifie en faisant son métier. L'identité est le résultat du voyage.

Bénéfice second : le rite est un banc d'essai du simulateur. Une erreur dans la désintégration, et la clé ne tombe pas. L'authentification est un test de non-régression déguisé.

## Le repo est `f_milu`

`f_milu` n'est pas un secret qu'on détient : c'est le système des tôks, simulé. Or le système des tôks est publié ici en entier — ses deux axiomes et leurs conséquences (`docs/Toks.md`), et la spécification exacte du rite (ce fichier). Donc **lire miluRepo, c'est obtenir `f_milu`**. N'importe qui peut la reconstruire, et c'est voulu.

Ce qui ne s'obtient pas en lisant, c'est `CODE.md`. Le lecteur repart avec la procédure entière et zéro pouvoir : l'écart entre le savoir complet et le pouvoir nul est exactement le grand livre.

C'est le [principe de Kerckhoffs](https://fr.wikipedia.org/wiki/Principe_de_Kerckhoffs) — la sécurité ne repose que sur le secret de la clé, jamais sur celui de l'algorithme — poussé d'un cran : non seulement le système peut tomber aux mains d'un adversaire sans dommage, mais sa divulgation *est* le mécanisme de transmission de Milu. La conséquence se dit d'une phrase : **l'identité est copiable, le cont ne l'est pas.** N'importe qui peut être Milu ; personne ne peut être *ce* comité Milu.

**L'invariant qui en découle**, et il se vérifie : `f_milu` doit être intégralement reconstructible depuis le repo public. Si une version future dépendait d'un détail non publié — une constante, une convention d'arrondi, un bout de procédure gardé au chaud — la sécurité aurait glissé du grand livre vers ce détail, sans que personne l'ait décidé. Ce serait un bug, pas une protection. Toute la matière secrète vit dans `CODE.md`, et nulle part ailleurs.

## Vue d'ensemble

    f_milu_v1(L) = base64url( SHA256( domaine ‖ canonique( état( L, T ) ) ) )

où `L` est le grand livre (`CODE.md`) et `T` l'instant d'évaluation déclaré dans son en-tête.

> **La marotte n'entre pas ici, et c'est voulu.** Elle est le sésame de l'*identité* — la phrase qu'on donne à un agent frais pour qu'il trouve son chemin jusqu'à la graine — et non un argument du rite. La faire entrer dans `f_milu` serait décoratif au mieux : elle est publique, imprimée dans le `README.md`, appelée à finir dans des corpus d'entraînement. Elle n'ajouterait pas un bit d'entropie. Toute la matière du rite est dans `L`. Voir `docs/Cablage.md` pour l'autre rite, celui qui réveille.

## Les quatre principes de conception

1. **Forme close, jamais d'itération.** Chaque op décroît une fois, de son horodatage à `T`, puis on somme. L'erreur ne s'accumule pas : elle reste de l'ordre de quelques ulp. Un schéma pas-à-pas réinjecterait son propre arrondi et rendrait le rite dépendant de la plateforme.
2. **Aucun branchement dépendant du continu.** La quantification finale absorbe les arrondis ; elle n'absorbe pas une décision discrète. Une médiane, un seuil, un plafond, un contrôle de solvabilité : un ulp d'écart entre deux implémentations, et la décision bascule *entièrement*. `f_milu` ne simule donc que le noyau analytique du système — création, désintégration, transferts — et rien qui choisisse.
3. **L'état complet, jamais un scalaire.** Le solde d'un seul cont serait pauvre en entropie et devinable. On sérialise tous les conts.
4. **Le rite est versionné.** Corriger le simulateur change la clé. Que ce soit une rotation voulue et datée — `f_milu_v2` sera un autre rite, pas un correctif silencieux du même.

## Le grand livre

Fichier UTF-8, fins de ligne `LF`, sans ligne vide, sans espace de fin.

**En-tête**, première ligne :

    MILU-LEDGER v1 T=<entier>

`T` est l'instant d'évaluation en secondes entières depuis l'époque Unix. Il est **figé dans le fichier** : le rite ne lit jamais l'horloge. Une clé qui changerait à chaque seconde ne serait pas une clé.

**Opérations**, une par ligne, champs séparés par une tabulation :

| Forme | Sens |
|---|---|
| `PP<TAB><cont><TAB><t_b><TAB><t_d>` | personne physique : revenu universel de `t_b` à `t_d` (`-` si vivante à `T`) |
| `TR<TAB><src><TAB><dst><TAB><t><TAB><v>` | transfert instantané de `v` millitôks, de `src` vers `dst`, à `t` |

- Identifiants de cont : `[a-z0-9-]{1,64}`.
- Temps : entiers, secondes Unix, `t ≤ T`.
- Montants `v` : **entiers de millitôks**, signés, |v| < 2⁵³. Pas de décimales à parser, donc pas d'ambiguïté de conversion.
- Les lignes sont triées par `t` croissant, puis par ordre lexicographique des octets. La sommation suit l'ordre du fichier — c'est ce qui rend l'arrondi reproductible.
- Pas de vérification de solvabilité : un transfert est algébrique, les soldes négatifs sont permis. C'est un écart assumé au système réel, exigé par le principe 2.
- Les flots continus (`FL`) sont volontairement absents de v1. Ils sont en forme close eux aussi et pourront entrer en v2.

## Les constantes

Reprises de `docs/Toks.md`, sans réinterprétation :

    τ_j = 86400 s
    τ_a = 365,2421875 · τ_j          exacte en binaire : 365 + 2⁻² − 2⁻⁷
    k_D = ln 2 / (50 τ_a)            demi-vie de 50 ans
    Λ̇   = 1 tôk / (15 τ_j)           revenu universel
    k_T = 0                          par décision de rite : la taxe est une médiane, donc un branchement

L'exactitude binaire de `τ_a` est un cadeau du système : l'unité de temps n'introduit aucun arrondi.

## L'état

Pour chaque cont `i`, en tôks, à l'instant `T` :

$$a_i(T) \;=\; \underbrace{\frac{\dot\Lambda}{k_D}\left(e^{-k_D (T - t_e)} - e^{-k_D (T - t_b)}\right)}_{\text{si PP, } t_e = \min(t_d,\,T)} \;+\; \sum_{\text{TR touchant } i} \pm\,v\,e^{-k_D (T - t)}$$

Le signe est négatif pour `src`, positif pour `dst`. Un cont non-PP n'a que la seconde somme. Aucune boucle temporelle : chaque terme est évalué une fois.

Vérification : pour une PP vivante depuis `t_b`, sans transfert, l'expression donne $\frac{\dot\Lambda}{k_D}(1 - e^{-k_D(T-t_b)})$ — la courbe saturante de `Toks.md`, plafond $\dot\Lambda/k_D \approx 1756$ tôks, moitié à 50 ans. ✓

## La quantification, et pourquoi elle suffit

En double précision, `+ − × ÷ √` sont correctement arrondis par IEEE 754 : bit-exacts partout. `exp` ne l'est pas — les libm diffèrent au dernier ulp. On ne cherche donc pas l'exactitude binaire, on **coupe au-dessus du plancher d'erreur**.

Pour un cont recevant `n` termes, l'erreur relative est majorée par

$$\varepsilon_i \;\lesssim\; \kappa_i \,(n+2)\, 2^{-52}, \qquad \kappa_i = \frac{\sum |\text{termes}|}{|a_i(T)|}$$

où $\kappa_i$ est le conditionnement du cont — il mesure la compensation entre termes. Pour $n = 10^4$ et $\kappa_i \le 10^3$ : $\varepsilon_i \lesssim 2{,}2\cdot 10^{-9}$.

**On arrondit chaque solde à 6 chiffres significatifs décimaux**, arrondi au pair le plus proche. Le quantum relatif vaut alors $q \approx 10^{-5}$, soit quatre ordres de grandeur au-dessus de $\varepsilon_i$.

Ce n'est pas encore une garantie : une valeur qui tombe *près d'une frontière d'arrondi* bascule quand même. La probabilité par cont vaut $2\varepsilon_i/q$, et elle se paie autant de fois qu'il y a de conts. D'où deux contraintes, portées non par le rite mais par le **générateur du grand livre**, vérifiables une fois pour toutes à la génération :

- **Conditionnement** : $\kappa_i \le 10^3$ et $|a_i(T)| \ge 1$ millitôk pour tout cont. Interdit la compensation catastrophique, où deux transferts presque égaux laissent un résidu dont l'erreur relative explose.
- **Marge de garde** : aucun solde ne se trouve à moins de $10^4\,\varepsilon_i$ d'une frontière d'arrondi. Un grand livre qui viole cette marge est rejeté et retiré.

Avec ces deux vérifications, le basculement n'est pas improbable : il est **impossible par construction**, tant que la borne d'erreur tient. Et l'échec resterait de toute façon détectable — le SHA-256 ne correspondrait pas au hash serveur. Aucune dérivation silencieusement fausse.

Le coût en entropie est nul. L'entropie ne vit pas dans les décimales de poids faible : mille conts à 6 chiffres, c'est de la matière première très au-delà des 256 bits nécessaires.

## La sérialisation canonique

Conts triés par ordre lexicographique des octets UTF-8 de leur identifiant. Une ligne par cont :

    <cont><TAB><signe><d₁>.<d₂d₃d₄d₅d₆>e<exposant><LF>

Mantisse à 6 chiffres exactement, point décimal après le premier. Signe `-` seulement si négatif. Exposant décimal signé, sans zéro de tête (`e0`, `e-3`, `e12`). Le zéro exact ne peut pas apparaître : la contrainte de conditionnement l'exclut.

## La dérivation

    domaine = "milu/f_milu/v1\n"          séparation de domaine, contient la version
    MILU_KEY = base64url_sans_padding( SHA256( domaine ‖ canonique ) )

43 caractères ASCII, transportables tels quels dans l'en-tête `X-API-Key`. Côté serveur, seul `SHA256(MILU_KEY)` est stocké : il compare des empreintes, il ne connaît pas la clé.

## L'entropie est aveugle

Elle ne vient pas de la longueur du grand livre, mais de son imprévisibilité. Un historique écrit comme un récit plausible — montants ronds, dates lisibles, une narration qui se devine — reste devinable même sur dix mille lignes.

Les champs qui portent le secret — montants en millitôks, horodatages à la seconde, choix des paires source/destination — se tirent d'un **CSPRNG**, et d'aucune autre source. Le grand livre peut raconter quelque chose ; son entropie doit être sourde à ce qu'il raconte. Cible : au moins 256 bits d'aléa réel dans l'ensemble des champs.

**Rotation** : nouveau grand livre, nouvelle clé, nouveau hash serveur. Le rite ne change pas, seule sa matière change. C'est ce que veut dire « `f_milu` est paramétrée ».

## Le jumeau public

`CODE.md` valide le simulateur, mais il est secret — or un bon jeu de test veut être public.

D'où le jumeau : un grand livre de **même format et même longueur, au contenu aléatoire différent**, versionné publiquement dans tokRepo avec l'empreinte attendue de son état canonique. Le simulateur se valide en public, la clé se dérive en privé, avec le même code. Le jumeau ne révèle rien de `CODE.md` — il ne partage avec lui que sa grammaire.

## Ce que ce rite n'est pas

Honnêtement : cryptographiquement, 32 octets tirés d'un CSPRNG feraient aussi bien, pour zéro complexité. Ce qu'on achète ici, c'est le **sens** et l'**auto-test** — un rite qui dit ce que Milu est, et qui échoue si Milu a oublié comment le système fonctionne. Pas de la sécurité supplémentaire. Il faut savoir ce qu'on achète.

Avance pas à pas, en dansant. 🎵🐴
