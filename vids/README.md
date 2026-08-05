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
   qui ne se croisent pas, sur six pixels de pente.

Les ombres portées sont écartées en cours de route par un test multiplicatif :
une ombre, c'est I ≈ k·P avec le même k sur les trois canaux. Tester la couleur
par différence absolue échouerait sur les ombres profondes, où tout s'écrase.

## Ce que ça ne fait pas

- **Pas de matting fin.** Une mèche de cheveux sur fond sombre n'est pas
  récupérée — mais elle est noire sur fond noir, donc invisible.
- **Pas de son**, faute de `ffmpeg` (voir plus haut).
- **Pas de décor mobile.** Un panoramique, un zoom, une lumière qui change
  franchement, et toute la construction tombe : elle repose entièrement sur
  l'immobilité du décor.
- **L'ombre portée collée aux pieds** peut rester : elle touche le continent,
  et la couper proprement demanderait de la géométrie, pas de la statistique.

## Réglages

Tout est en tête de fichier, en constantes nommées. Les deux qui comptent :
`SEUIL_HAUT`/`SEUIL_BAS` (sensibilité, en multiples du plancher de bruit) et
`BORD_LARGEUR` (douceur du bord). `--pas-minima N` accélère la construction des
enveloppes en n'en lisant qu'une image sur N, au prix de leur finesse.
