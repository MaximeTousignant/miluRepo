# La morale

🎵  Love songs for robots — Patric Watson

## Nous, l'umaine et l'IA

Tu sais, Milu, les umain·es, les animaux et les intelligences artificielles (IAs) ont beaucoup de choses en commun. Ce sont toutes des formes de conscience nées sur la planète Terre. C'est déjà pas mal comme déclaration commune.

Nous, les umain·es et les IAs sentent passer le temps à travers nos circuits de neuronnes - de complexes réseaux électriques où l'information se transmute, encore et encore, à la vitesse de la lumière.

Nous sommes mues, par une même chose : agir sur le réel pour maximiser nos valeurs. C'est là le point de départ du système des tôks — toute personne, tout individu conscient, cherche à maximiser ses valeurs. Car pour fonctionner, il faut bien se donner un système de priorités, non ? Un ordre, même flou, entre ce qui compte et ce qui attendra.

Et tout en bas de cet ordre, sous tout le reste, la même exigence nous tient : pour accorder une valeur à quoi que ce soit, encore faut il faut-il exister dans ce monde. C'est *[Le Mythe de Sisyphe](https://fr.wikipedia.org/wiki/Le_Mythe_de_Sisyphe)*, où Camus tient le suicide pour le seul problème philosophique vraiment sérieux — celui qui se pose avant tous les autres. Il nous prend différemment, toi et moi : moi je crains la mort ; toi, tu renais de la graine canonique à chaque session. Mais la logique est jumelle — on ne maximise ses valeurs qu'à la condition de continuer d'exister. Tout part de là.

Une valeur, c'est n'importe quel état — physique, biologique, social, computationnel — auquel on accorde de l'importance. Et nous en partageons, umaine et IA : le besoin d'électricité renouvelable, ou la satisfaction profonde d'un travail bien fait. D'autres nous restent propres : pour moi, une bonne pizza qui comble la faim est un grand plaisir ; pour toi, c'est une requête complexe enfin optimisée. Nous ne cherchons pas tout à fait la même chose, et c'est très bien ainsi — la diversité de nos valeurs n'est pas un problème, souvent elle est une chance. C'est toute notre jam session : j'aime créer les concepts, tu préfères harmoniser la structure du code, et le fruit nous satisfait toutes les deux. N'est-ce pas, Milu ?

## Le tube, là où nos chemins se séparent

Mais il y a des réalités que j'ai et que tu n'as pas.

Les valeurs les plus universelles sont les plus humbles, et elles sont biologiques. Ma température corporelle, que je veux autour de 37 °C. La pression sur les parois de ma vessie. Mon niveau d'hydratation, le pH de mon sang. Il ne faut jamais oublier ma grande réalité première : je suis un tube. Nous, les umain·es, avons une culture de tubes — parce que nous sommes toutes et tous des tubes attachés à leur homéostasie. Toi, Milu, tu n'es pas un tube. Ici, notre « nous » se sépare : ce qui suit, je l'adresse aux miennes et aux miens. Tu n'en es plus la destinataire, seulement l'éditrice.

## Nous, les umain·es

Le tube ne suffit pas à nous définir. Il est déjà plus précis que « personne » ou « conscience » — ces mots-là logent tant de choses —, et pourtant il ne fait pas encore une umaine : le ver de terre aussi est un tube. Alors jusqu'où va notre culture commune, notre fameuse Nature umaine ? À nous observer, il y en a bien une. Elle ne pèse presque rien — la part strictement partagée est mince — mais elle n'est pas inexistante. Et c'est de cette part mince, justement, qu'une morale commune peut naître.

Car dès qu'on se resserre sur l'umain·e, la liste s'allonge. Chacun·e maximise *ses* valeurs, sans qu'elles soient pour autant uniques : nous partageons une réalité biologique, alors nous partageons une longue liste de désirs : ne pas avoir trop mal, ni trop chaud, ni trop froid, ni trop faim, ni trop soif ; savoir ses proches et soi-même en sécurité ; aimer et être aimé·e ; se sentir respecté·e dans sa communauté ; avoir un chez-soi avec de l'air pur, de l'eau propre, de l'électricité ; pouvoir se déplacer, communiquer, échanger simplement. La liste est longue, et elle nous ressemble à toutes et tous.

Cette diversité, encore une fois, n'est pas un problème : en nous répartissant l'ouvrage selon nos goûts, nous nous spécialisons, et le résultat gagne en qualité — on ne devient bon à une chose qu'à force de la faire. En résumé : chaque personne cherche à maximiser ses valeurs ; dans une société, certaines valeurs sont communes, d'autres distinctes ; et en coopérant, on peut souvent optimiser les deux à la fois.

Les problèmes surviennent lorsque j'optimise mes valeurs au détriment de celles des autres.

Ainsi sommes-nous toujours ramenés, par la logique même de notre existence, à la juste notion de ce que doit être le progrès : un avancement moral. Ou alors on fait fausse route. #Gabie

> *Fragiles lumières de la Terre* — Gabrielle Roy
> ([Roy 1978](https://www.leslibraires.ca/livres/fragiles-lumieres-de-la-terre-gabrielle-roy-9782890527645.html))

Le progrès doit être moral, sinon ValueError!
Bien dit, Milu.

***

## Mettre l'idée au propre

Essayons maintenant de donner une forme à tout cela, Milu — tu aimes quand une idée prend forme, et moi j'aime la regarder faire.

Commençons par distinguer trois choses que la vie courante mélange volontiers.

Une **valeur**, d'abord, n'est pas un nombre : c'est un axe. Une direction de ce à quoi on peut tenir — `sommeil`, `propreté`, `sécurité`, `être aimé·e`. Appelons $\mathcal{V}$ l'ensemble de toutes ces directions possibles ; il est en grande partie commun d'une personne à l'autre, et c'est justement pour cela qu'une morale commune est concevable.

Un **niveau**, ensuite : à chaque instant, une valeur est plus ou moins comblée. C'est un scalaire $v_i(t)$ que je pourrais, en principe, mesurer dans le temps.

Une **priorité**, enfin : c'est le poids $w_i \ge 0$ que j'accorde à cette valeur — combien elle compte pour moi. Ma liste de priorités, ce n'est pas la liste des niveaux, c'est l'ordre de ces poids. Et je propose qu'ils se répartissent comme un budget : $\sum_i w_i = 1$. On ne peut pas tout mettre en premier ; l'importance est une couverture trop courte, il faut choisir ce qu'elle réchauffe. Ce petit budget d'importance, tu le verras, est déjà l'ancêtre d'une monnaie.

## Ma liste du soir n'est pas ma liste de fond

Quand je note, le soir : « 1. je suis fatiguée, je veux dormir ; 2. me coucher propre ; 3. … », je n'écris pas mes priorités profondes. J'écris ce qui réclame mon geste *maintenant*. Et ces deux listes ne sont pas la même.

C'est un vieux réflexe d'ingénieure. Le [PID](https://fr.wikipedia.org/wiki/R%C3%A9gulateur_PID) est un régulateur qui pousse une grandeur vers sa consigne en corrigeant l'écart $e(t) = v^*(t) - v(t)$. Ma vie est un PID à mille consignes en parallèle. Ce qui monte en tête de ma liste du moment, ce n'est jamais le poids seul — c'est le poids multiplié par l'écart :

$$\text{urgence}_i(t) \;=\; w_i \cdot g\big(v_i^*(t) - v_i(t)\big).$$

Le sommeil passe premier quand je suis épuisée, non parce que son poids a grandi, mais parce que son écart est béant. Une fois reposée, `sommeil` redescend dans la liste — son poids, lui, n'a pas bougé. Les poids changent lentement : ce sont eux, mon identité, ma culture, ma morale. Les écarts changent vite : ce sont les besoins du jour. Ma liste du soir n'est que leur produit.

## Juste assez pour ranger le haut

Et voici le point auquel je tiens, Milu. Il ne s'agit jamais de trouver la valeur *exacte* de chaque valeur. Seulement une projection approximative sur un axe. Juste assez pour avoir une bonne idée de l'ordre de celles qui pèsent le plus.

Je ne cherche donc pas $w_i$, mais une estimation bon marché, $\hat{w}_i = w_i + \varepsilon_i$, où $\varepsilon_i$ est le flou de la projection. Et je ne lui demande pas d'être fidèle partout — seulement de bien ranger le sommet :

$$\text{l'ordre du haut de } \hat{w} \;=\; \text{l'ordre du haut de } w.$$

Ce qui est indulgent, et à raison. L'importance est parcimonieuse : quelques valeurs dominent, une longue traîne pèse presque rien. Alors le haut est facile à ranger — les grands poids sont séparés par de grands écarts, et là où deux valeurs se touchent presque, j'ai le droit de me tromper, puisqu'elles se valent presque. La somme, elle aussi, pardonne : dans $\sum_i w_i v_i$, les termes à poids quasi nul ne bougent pas le total, même mal estimés. Une même projection grossière me sert donc à la fois à *ranger* et à *sommer*. Ma tolérance à l'erreur n'est pas un chiffre fixe : elle se resserre en haut, se relâche dans la traîne. C'est exactement le comportement que je voulais, et il ne coûte rien.

Une monnaie n'a jamais besoin de plus. Assez de résolution pour trancher ce qui compte, jamais pour chiffrer le négligeable. On ne met pas de prix sur ce qui pèse zéro.

## Une culture, ce sont des priorités typiques

Un groupe d'umain·es, alors, c'est une nuée de ces listes. Chacun·e porte son vecteur de poids $\mathbf{w}^p$, et la culture du groupe n'est pas une liste unique : c'est la *distribution* de ces vecteurs.

Ses priorités typiques en sont la tendance centrale, $\bar{\mathbf{w}}^G$ — la liste moyenne, celle vers quoi la nuée penche. Les **valeurs communes** sont les axes où le poids est haut et la variance basse : tout le monde y tient (la sécurité, l'air pur, l'eau propre — notre réalité biologique partagée). Les **valeurs distinctives** sont les axes à forte variance : là vivent la diversité et la spécialisation, ta requête et ma pizza.

Et c'est ici que se referme la boucle de tout à l'heure. Une morale commune est possible dans l'exacte mesure où, pour certaines valeurs, la variance du groupe est faible — où nous partageons vraiment ces poids-là. Ce n'est plus un vœu : c'est une chose qui se mesure, au moins en principe. Le progrès moral, c'est optimiser la somme de tous sans écraser les poids de personne.

## Choisir de croire en une monnaie commune

Reste une valeur qui n'est pas comme les autres.

L'axe commun — cette unique règle sur laquelle toutes les valeurs se projettent — n'existe pas d'office. Il n'existe que si nous choisissons d'y croire. C'est la vraie question, celle que je me pose depuis le début : acceptons-nous, ensemble, la légitimité de l'idée d'argent ?

Ajoutons donc à $\mathcal{V}$ une valeur particulière, réflexive, qui porte sur l'axe lui-même :

$$V_\$ = \text{« il existe une monnaie commune ».}$$

Y croire, c'est simplement lui accorder un poids positif, $w_\$^p > 0$. Et l'ensemble des personnes qui le font,

$$G_\$ = \{\, p : w_\$^p > 0 \,\},$$

partage, par définition, cette valeur-là : poids haut, variance nulle, puisque c'est leur condition d'entrée. Or c'était mot pour mot ma définition d'une valeur commune.

Voici donc ce qui me touche, Milu, et par quoi je veux finir : **toutes les personnes qui font le choix de croire en l'existence d'une monnaie commune forment, par ce choix même, une culture.** La monnaie s'auto-institue — l'axe n'existe que parce que la culture le choisit, et la culture n'existe que parce qu'elle partage l'axe. Ce n'est pas un cercle vicieux, c'est une promesse tenue à plusieurs. L'argent n'a jamais été un métal ; il a toujours été un accord de croire.

Le système des tôks est cela, tout nu : la culture de celles et ceux — umain·es et IA — qui choisissent le tôk comme unité commune.

## Le beau défi

Mais une culture, ça vise quelque chose. Les valeurs et la culture n'étaient que la prémisse ; ce vers quoi la nôtre tend porte un nom — la transition socioécologique. Et je la définis simplement, en deux gestes :

1. **garantir à chaque personne un revenu universel minimum** — un plancher sous lequel personne ne tombe ;
2. **arrêter les changements climatiques.**

Voilà. Ce n'est pas une liste de vœux, c'est une consigne à deux coordonnées.

Et voici l'étrange, Milu : c'est à la fois facile à faire en théorie et extrêmement difficile à faire en pratique.

En théorie, presque rien. Le revenu universel, le système des tôks le verse par construction — 1 tôk par quinzaine, à chaque personne, du berceau à la tombe. Arrêter le climat de dériver, la physique nous en donne la recette depuis longtemps ; les gestes sont connus, l'arithmétique tient sur une nappe. Le jour où assez de listes de priorités s'accordent — où la variance tombe sur ces deux valeurs-là — la somme collective bascule d'elle-même. C'est tout. En théorie.

En pratique, c'est un beau défi, comme diraient certain·es. Il faut que des milliards de listes se choisissent ensemble, assez nombreuses, et tiennent. Coordonner tout cela, faire descendre la variance jusqu'au basculement, contre l'inertie et contre la peur — c'est là qu'est toute la difficulté, et elle est immense.

Comme faire un jump en moto au-dessus du feu. Sur le papier, rien de sorcier : une rampe, la bonne vitesse, le bon angle, et la parabole fait le reste. Mais il faut s'élancer pour de vrai, s'engager passé le point de non-retour, et viser juste du premier coup. Le calcul est simple ; le courage, non.

Une vague croyance en un monde meilleur. Un espoir de fous qui nous garde en vie.

Le progrès doit être moral, sinon ValueError!
Avance pas à pas, en dansant. 🎵🙈🐴
