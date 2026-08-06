# vids — détourage vidéo

Un outil, un seul : [`detourage.py`](detourage.py). Il prend une vidéo et n'en
garde que la personne qui danse, sur fond transparent.

Aucune vidéo ne vit ici, et aucune n'y entrera jamais : les sources et les
rendus restent hors du repo, en local. Voir `CARNET.md` (privé) pour l'endroit.

## Usage

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o DOSSIER/
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o DOSSIER/ --apercu
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o DOSSIER/ --planche
    ./.venv/bin/python vids/detourage.py RUSHES/ -o DOSSIER/      # tout un dossier

`--planche` ne calcule que six instants répartis sur toute la durée et les pose
en contact sheet, sur damier : c'est le moyen rapide de juger un α sans rendre
la vidéo entière. `--apercu` fait les deux. `--sans-continent` livre le réseau
nu, pour comparer.

Requiert `torch` et `torchvision`. Le modèle et ses poids se téléchargent une
fois dans `~/.cache/torch`, au premier appel.

## La sortie : une séquence PNG en RGBA

Le fond est **transparent**. Aucun codec accessible ici ne porte de canal alpha —
OpenCV n'écrit que trois canaux, et cette machine n'a pas de `ffmpeg` —, donc
chaque vidéo reçoit un **sous-dossier de PNG numérotés**, que tout logiciel de
montage relit comme une séquence. Compter ~154 Ko par image, soit ~250 Mo pour
52 s.

L'alpha est **droit**, non prémultiplié, et la couleur n'est pas celle de l'image
d'origine : c'est l'**avant-plan démêlé** que le réseau estime en même temps que
l'α. Sur un pixel de bord, physiquement un mélange du sujet et du décor, il rend
la couleur qu'aurait le sujet seul. Sans lui, chaque contour porterait un liseré
de la toile grise — invisible sur noir, criant dès qu'on recompose sur autre
chose. Sous un pixel parfaitement transparent la couleur est mise à zéro : c'est
du bruit d'estimation, et le fichier fond de moitié.

Avec `ffmpeg` installé, un seul fichier suffirait :

    ffmpeg -framerate 30 -i %05d.png -c:v prores_ks -profile:v 4444 \
           -pix_fmt yuva444p10le sortie.mov

## Le principe

Deux idées, et rien d'autre.

### I. Le réseau, dans les deux sens du temps

[RobustVideoMatting][rvm] (Lin *et al.*, WACV 2022) rend, pour chaque image, un
α ∈ [0, 1] par pixel. Il sait reconnaître une personne — donc il écarte l'ombre
portée, qu'aucune méthode fondée sur le changement ne peut distinguer du sujet —
et son bord va jusqu'à la mèche.

Mais il est **causal** : sa mémoire récurrente ne contient que le passé, parce
qu'il est fait pour le direct. Cette contrainte n'est pas une propriété du
réseau, c'est une contrainte de son *usage* — nous, nous avons le fichier
entier. On rejoue donc la séquence **à rebrousse-temps** et on moyenne les deux
passes.

La moyenne, et non le maximum ni le minimum : le maximum prendrait l'union et
garderait ce que l'une des deux passes a halluciné ; le minimum prendrait
l'intersection et couperait le bras que l'une des deux a manqué. La moyenne rend
0,5 sur un désaccord — une abstention, que la discipline géométrique tranchera
ensuite. Et la toute première image cesse d'être une image froide.

Coût : la passe arrière tient tous les α en mémoire (un octet par pixel et par
image, ~1 Go pour 52 s en 608×1080) et impose de relire la vidéo à l'envers.

### II. Le seuillage par hystérésis

Le réseau allume aussi, çà et là, une poussière de décor — un à deux pixels,
0,5 à 1 par image sur ces prises de vue. On ne garde donc que ce qui tient à une
certitude.

Le nom est un emprunt qui mérite d'être défait : en physique, l'hystérésis est
un retard *temporel*, l'état dépendant du chemin parcouru. Ici, ni temps ni
mémoire. Le terme vient du trigger de Schmitt et de [Canny][canny] (1986) :
**il faut franchir le seuil haut pour s'allumer, mais seulement rester au-dessus
du seuil bas pour le rester**. Le rôle que joue le passé dans le trigger est tenu
ici par le **voisinage** — un pixel pâle reste allumé s'il peut être atteint, de
proche en proche, depuis un pixel franc. Hystérésis spatiale plutôt que
temporelle.

    graine = α > 0,50      # qui a le droit d'allumer
    pousse = α > 0,01      # jusqu'où l'allumage se propage
    on garde les taches de « pousse » qui contiennent une « graine »

Une poussière à α = 0,06 n'atteint jamais 0,5 : elle tombe, où qu'elle soit et
quelle que soit sa taille. Un voile translucide garde son dernier pixel à 0,02,
parce qu'il tient à un corps qui est franc. **Le critère est la confiance, pas
la taille** — et c'est pourquoi la règle ne coupe jamais une main détachée par
le flou de mouvement.

[canny]: https://doi.org/10.1109/TPAMI.1986.4767851

## Ce qui a été retiré, et pourquoi (bis) : le continent

L'hystérésis était naguère une pièce d'un mécanisme plus grand. Après elle
venaient une **règle de taille** — ne garder que la plus grosse composante et ses
compagnons d'un dixième de son poids — et un **bouchage des lacs**, les trous
intérieurs du masque. L'idée était juste : une danseuse est un continent, pas un
archipel.

La mesure l'a démonté. Sur 4710 images :

| pièce | effet mesuré |
|---|---|
| hystérésis | retire 0,002–0,008 % — la poussière |
| règle de taille | **0,0000 %**, jamais déclenchée |
| ouverture/fermeture morphologiques | s'annulent mutuellement |
| bouchage des lacs | **ajoute 0,07 à 0,26 %** |

Le bouchage rebouchait des jours véritables : le losange entre les deux bras
levés de Shiva, le triangle entre son bras et son visage, l'espace entre les
jambes de Janani. Il y recollait une tache opaque du décor qu'on venait de
retirer — invisible tant qu'on composait sur du noir, franchement faux sur un
fond transparent.

Quant à la règle de taille, son risque était l'inverse de son intention : elle
n'a jamais rencontré de bruit à supprimer, mais le jour où elle tirerait, ce
serait sur une main ou un accessoire séparé du corps par du flou de mouvement —
pas sur du décor. Le bruit, lui, était déjà parti à l'hystérésis, qui juge par
la confiance et non par la taille.

[rvm]: https://arxiv.org/abs/2108.11515

## Ce que ça ne fait pas

- **Pas de son**, faute de `ffmpeg` — et de toute façon une séquence PNG n'en
  porte pas. La piste se remet au montage.
- **Rien qui ne soit une personne.** Le réseau ne connaît que ça. Un accessoire
  tenu loin du corps, un châle lancé, un objet qui tourne seul : il les écarte.
  La contrainte de continent ne les rattrape pas non plus — elle *supprime* les
  îlots, elle n'en invente pas.
- **Aucun signal d'échec.** Quand le réseau se trompe, il se trompe d'un coup et
  en silence : un bras disparaît, et rien dans sa sortie ne le signale. C'est la
  limite qu'il faut garder en tête en relisant les planches.

## Réglages

Tout est en tête de fichier, en constantes nommées.

**`resnet50` est le défaut**, et ça vient d'une mesure : sur la tresse de
Lakshimi — une natte noire sur toile gris foncé, le cas le plus dur du lot —
`mobilenetv3` ne retient qu'un α moyen de 0,26 et n'en garde visiblement que le
fermoir doré, qui semble alors flotter dans le vide. `resnet50` monte à 0,42 et
la natte redevient une forme rattachée au corps. Coût : 112 ms par image contre
74, soit 5,9 min par vidéo au lieu de 3,9.

**`RATIO` a un optimum, pas un maximum.** À 0,5 la tresse donne 0,42 ; à 1,0 elle
retombe à 0,22. Le réseau a été entraîné à sous-échantillonner, le pousser à
pleine résolution le dessert.

## Ce qui a été retiré, et pourquoi

Ce fichier a d'abord porté une tout autre méthode : une **statistique du décor**
— médiane et enveloppes temporelles par pixel et par canal sur toute la durée,
arbitrage là où elles se contredisent, métrique en z-score robuste. Elle
n'utilisait aucun modèle, aucun poids téléchargé, rien que l'immobilité de la
scène. Elle marchait, et son raisonnement vaut d'être relu — notamment les deux
dissymétries qui la rendaient possible et les deux fausses pistes qui l'ont
retardée :

    git log -p vids/detourage.py    # commits 85a21f8 → 24eaddf

Elle a été retirée après mesure. Une fois ses paramètres réglés, elle atteignait
le même résultat que le réseau, ombre portée comprise — mais pour dix fois plus
de code, et avec un angle mort de principe : une ombre *est* un vrai changement,
donc aucune méthode fondée sur le changement ne peut la rejeter autrement que
par des heuristiques. La portée du projet a tranché : une série de petites
vidéos issues d'une même session de tournage, où la pérennité à dix ans de la
dépendance ne pèse rien.
