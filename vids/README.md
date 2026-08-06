# vids — détourage vidéo

Un outil, un seul : [`detourage.py`](detourage.py). Il prend une vidéo et n'en
garde que la personne qui danse, sur fond noir.

Aucune vidéo ne vit ici, et aucune n'y entrera jamais : les sources et les
rendus restent hors du repo, en local. Voir `CARNET.md` (privé) pour l'endroit.

## Usage

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o SORTIE.mp4
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o DOSSIER/ --apercu
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o SORTIE.mp4 --planche

`--planche` ne calcule que six instants répartis sur toute la durée et les pose
en contact sheet : c'est le moyen rapide de juger sans rendre la vidéo entière.
`--apercu` fait les deux. `--sans-continent` livre le réseau nu, pour comparer.

Requiert `torch` et `torchvision`. Le modèle (3,7 M paramètres) et ses poids se
téléchargent une fois dans `~/.cache/torch`, au premier appel.

La sortie est muette : cette machine n'a pas de `ffmpeg`, et OpenCV ne recopie
pas les pistes audio. Pour remettre le son, `ffmpeg -i rendu.mp4 -i source.mp4
-c copy -map 0:v -map 1:a sortie.mp4`.

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

### II. Le continent

Une danseuse n'est pas un archipel. Trois contraintes géométriques, dans l'ordre :

1. **hystérésis** — une composante ne survit que si elle contient un noyau franc
   (α > 0,5) ; elle s'étend ensuite tant que α > 0,05. Un voile translucide
   n'atteint jamais le seuil franc, mais il tient à un corps qui, lui,
   l'atteint : il survit. Une miette de décor faiblement allumée, qui ne touche
   aucun noyau, disparaît ;
2. **continent** — on garde la plus grande composante et ses seuls compagnons
   d'un quart de son poids, au cas où un bras se détacherait ;
3. **lacs** — une composante de fond qui ne touche aucun bord de l'image. On la
   bouche sans réserve si l'image y est sombre (ce qu'on y découvre est déjà
   noir, ça ne coûte rien), et seulement si elle est petite ailleurs — sinon on
   recollerait un morceau de décor au milieu de la silhouette. L'espace entre
   deux jambes qui descend jusqu'au bas du cadre n'est pas un lac mais un golfe
   ouvert sur l'océan : il n'est jamais bouché.

**Ce que ça apporte, mesuré : presque rien.** Sur ces prises de vue, le
continent ne retire que 0,03 % de la masse d'α — le réseau est déjà propre.
C'est une garantie, pas un contributeur : il coûte quelques millisecondes par
image et interdit qu'une miette apparaisse un jour au milieu du noir.

[rvm]: https://arxiv.org/abs/2108.11515

## Ce que ça ne fait pas

- **Pas de son**, faute de `ffmpeg` (voir plus haut).
- **Rien qui ne soit une personne.** Le réseau ne connaît que ça. Un accessoire
  tenu loin du corps, un châle lancé, un objet qui tourne seul : il les écarte.
  La contrainte de continent ne les rattrape pas non plus — elle *supprime* les
  îlots, elle n'en invente pas.
- **Aucun signal d'échec.** Quand le réseau se trompe, il se trompe d'un coup et
  en silence : un bras disparaît, et rien dans sa sortie ne le signale. C'est la
  limite qu'il faut garder en tête en relisant les planches.
- **Pas de décontamination de couleur.** Le réseau rend aussi un avant-plan
  démêlé du fond (`fgr`), qu'on n'utilise pas : on multiplie les pixels d'origine
  par α, donc les bords gardent une trace de la couleur du décor. Sur fond noir
  de sortie, ça se voit peu.

## Réglages

Tout est en tête de fichier, en constantes nommées. `--variante resnet50` prend
un modèle plus lourd et un peu plus fin ; `RATIO` règle le sous-échantillonnage
interne du réseau (0,5 convient de 1080p à la verticale).

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
