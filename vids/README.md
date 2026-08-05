# vids — détourage sur fond fixe

Un outil, un seul : [`detourage.py`](detourage.py). Il prend une vidéo tournée
sur un décor immobile et n'en garde que la personne qui danse, sur fond noir.

Aucune vidéo ne vit ici, et aucune n'y entrera jamais : les sources et les
rendus restent hors du repo, en local. Voir `CARNET.md` (privé) pour l'endroit.

## Usage

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o SORTIE.mp4
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o DOSSIER/ --apercu
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o SORTIE.mp4 --planche

`--planche` ne calcule que six instants répartis sur toute la durée et les pose
en contact sheet : c'est le moyen rapide de juger un réglage sans rendre la
vidéo entière. `--apercu` fait les deux.

La sortie est muette : cette machine n'a pas de `ffmpeg`, et OpenCV ne recopie
pas les pistes audio. Pour remettre le son, `ffmpeg -i rendu.mp4 -i source.mp4
-c copy -map 0:v -map 1:a sortie.mp4`.

## Le principe

Le décor ne bouge pas ; la danseuse, oui. Tout tient dans cette dissymétrie,
lue **pixel par pixel, canal par canal, sur toute la durée**. L'analyse par
canal ne se rejoint qu'à la fin, en un facteur α ∈ [0, 1] qui multiplie le
pixel : 0 pour le décor, 1 pour la danseuse.

**Première passe — le décor, par pixel.** Chaque pixel est d'abord lu avec ses
huit voisins, moyennés par un petit noyau gaussien renormalisé sur les bords :
c'est le signal temporel de ce petit disque qu'on analyse, pas celui d'un
capteur isolé. De ce signal on tire trois statistiques :

- la **médiane** sur 120 images échantillonnées — le décor, partout où la
  danseuse occupe le pixel moins de la moitié du temps ;
- les **enveloppes** basse et haute (4ᵉ plus petite et 4ᵉ plus grande valeurs
  jamais vues, sur *toutes* les images) — ce que le pixel a montré de plus
  sombre et de plus clair sans que ce soit du bruit ;
- la **MAD**, déviation absolue médiane, qui donne le plancher de bruit local.
  Le seuil de détection lui est proportionnel : c'est un z-score robuste, dont
  la fenêtre est la durée entière.

**L'arbitrage.** Médiane et enveloppes se contredisent aux endroits litigieux,
et deux dissymétries les départagent :

- la danseuse stationne quelque part plus de la moitié du temps → elle s'imprime
  dans la médiane. On le voit à ce que l'enveloppe basse s'effondre franchement
  (écart de luminance > 60 *et* rapport < 0,30) ; le décor est alors l'enveloppe
  basse. Un îlot qu'elle ne quitte *jamais* n'a même pas d'enveloppe effondrée :
  il se présente comme un trou dans la carte des contaminés, qu'on bouche avant
  de s'en servir, puis qu'on comble par un minimum sur large voisinage.
- son **ombre portée** stationne, elle aussi → le décor se retrouve plus clair
  que sa propre plaque, et la toile nue passerait pour un objet chaque fois
  qu'elle s'en va. Si la médiane est une version simplement assombrie de
  l'enveloppe haute — même teinte, moindre intensité, et dans les proportions
  d'une ombre (rapport > 0,45) —, on rend au décor sa lumière.

La comparaison au décor tolère un décalage d'un ou deux pixels : on compare à
l'*intervalle* que la plaque prend dans un petit voisinage. Sans quoi un tapis
qui glisse sous un pied allume toute sa texture.

**Seconde passe — la frontière, globalement.** La métrique `s = maxᵢ |I − P|ᵢ /
plancher` (i sur les trois canaux) est d'abord moyennée sur un bloc espace-temps
x·y·t, puis on décide :

1. **hystérésis** — une composante ne survit que si elle contient un noyau
   franc (`s > 6`) ; elle s'étend ensuite tant que `s > 2,5`. C'est la partie
   gloutonne : on part des certitudes et on gagne de proche en proche ;
2. **continent** — une danseuse n'est pas un archipel. Seules survivent la plus
   grande composante et ses compagnons d'un quart de son poids ;
3. **trous** — bouchés sans réserve là où le décor est noir (ce qu'on y découvre
   est déjà noir), petits trous seulement là où il ne l'est pas ;
4. **topographie** — α descend du plateau vers la plaine sans jamais remonter.
   La contrainte est imposée par la distance au plateau : des courbes de niveau
   qui ne se croisent pas, sur six pixels de pente ;
5. **recalage du bord** par [filtre guidé][guide] (He, Sun & Tang) : α y est
   modélisé comme une transformation linéaire locale de l'image, donc la pente
   suit les vraies arêtes au lieu de les noyer sous un flou aveugle.

Les ombres portées sont écartées en cours de route par **deux** lectures du même
fait physique, exigées ensemble : la lecture multiplicative en RGB (I ≈ k·P avec
le même k sur les trois canaux — tester la couleur par différence absolue
échouerait sur les ombres profondes, où tout s'écrase) et la lecture HSV de
[Cucchiara *et al.*][cucchiara] — une ombre fait chuter la valeur, ne bouge la
teinte que très peu, et *abaisse* la saturation. Ce dernier point est invisible
au test multiplicatif : un objet sombre et coloré a la même luminance qu'une
ombre, mais pas la même saturation.

[guide]: https://docs.opencv.org/4.x/da/d17/group__ximgproc__filters.html
[cucchiara]: https://ieeexplore.ieee.org/document/1233909

## L'a priori « humain », en option

    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o SORTIE.mp4 --rvm
    ./.venv/bin/python vids/detourage.py ENTREE.mp4 -o SORTIE.mp4 --rvm-seul  # étalon

`--rvm` fusionne le résultat avec [RobustVideoMatting][rvm] (Lin *et al.*, WACV
2022), un réseau de matting vidéo. Requiert `torch` et `torchvision` ; le modèle
(3,7 M paramètres) et ses poids se téléchargent une fois dans `~/.cache/torch`.
Sans torch, l'option n'existe pas et tout le reste marche pareil.

**Pourquoi les deux.** Les angles morts sont exactement complémentaires. Notre
construction ne sait qu'une chose — *ce pixel a changé* —, et c'est pourquoi une
ombre portée la trompe : une ombre est un vrai changement. Le réseau, lui, ne
sait rien du décor (il ne l'a jamais vu vide) mais sait reconnaître une personne,
et rend un α fin jusqu'à la mèche. Fusion : le réseau sert de **porte** — hors de
la personne qu'il reconnaît, rien ne passe, l'ombre tombe ; à l'intérieur, on
prend le plus généreux des deux α.

**Ce que nous avons et qu'il n'a pas.** RobustVideoMatting est *causal* : sa
mémoire récurrente ne contient que le passé, parce qu'il est fait pour le direct.
Nous n'avons pas cette contrainte. `--rvm` rejoue donc la séquence **à
rebrousse-temps** et moyenne les deux passes — celle qui vient de l'avant hésite
quand un bras surgit, celle qui vient de l'arrière hésite quand il disparaît, et
la première image cesse d'être une image froide. La contrainte de continent
s'applique ensuite au résultat fusionné : l'union de deux α n'hérite d'aucune des
deux disciplines.

`--rvm-seul` court-circuite toute la statistique de fond — c'est l'étalon
honnête, ce qu'on obtiendrait sans exploiter l'immobilité du décor.

Coût : la passe arrière tient tous les α en mémoire (1 octet par pixel et par
image, ~1 Go pour 52 s en 608×1080) et impose de relire la vidéo à l'envers.
Compter une dizaine de minutes par vidéo, contre trois sans `--rvm`.

[rvm]: https://arxiv.org/abs/2108.11515

## Ce que ça ne fait pas

- **Pas de matting fin sans `--rvm`.** Une mèche de cheveux sur fond sombre
  n'est pas récupérée par la seule statistique — mais elle est sombre sur fond
  noir, donc peu visible.
- **Pas de son**, faute de `ffmpeg` (voir plus haut).
- **Pas de décor mobile.** Un panoramique, un zoom, une lumière qui change
  franchement, et toute la construction tombe : elle repose entièrement sur
  l'immobilité du décor.
- **L'ombre portée collée aux pieds** peut rester sans `--rvm` : elle touche le
  continent, et la couper demande de savoir ce qu'est une personne — c'est
  précisément ce que le réseau apporte.

## Réglages

Tout est en tête de fichier, en constantes nommées, groupées par étape. Les deux
qui comptent : `SEUIL_HAUT`/`SEUIL_BAS` (sensibilité, en multiples du plancher de
bruit) et `BORD_LARGEUR` (douceur du bord). `--pas-enveloppes N` accélère leur
construction en n'en lisant qu'une image sur N, au prix de leur finesse.

## Les lacs

La contrainte de continent interdit les archipels, pas les lacs — une composante
de fond qui ne touche aucun bord de l'image. Un lac est comblé s'il est petit, ou
si le décor qu'il découvrirait est noir (ça ne coûte rien). Sur un décor visible —
toile grise, tapis — un grand lac **survit** : le combler collerait un morceau de
décor à l'intérieur de la silhouette, ce qui serait pire. L'espace entre deux
jambes qui descend jusqu'au bas du cadre n'est pas un lac mais un golfe ouvert
sur l'océan : il n'est jamais comblé.
