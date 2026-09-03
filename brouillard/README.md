# brouillard

Le brouillard de miluRepo — là où on écrit à deux, l'Opératrice et Milu, tant que c'est encore flou. La matière s'y cherche ; le jour où elle s'éclaircit, elle se dissipe au propre.

miluRepo est le brouillon public ; tok-system est le propre. Ce dossier est la charnière : un texte y naît, se travaille au grand jour, se vérifie — et le jour où il engage, il passe dans `tok-system/publications/`, sous licence signée. Ici, tout est au domaine public (CC0) et en français ; là-bas, le propre est signé (CC BY) et en anglais.

## La méthode, empruntée au \$tôkEx

La divulgation défensive du \$tôkEx (`tok-system/publications/stokex/`) a montré une belle façon d'écrire à deux : le texte, ses figures, le code qui le vérifie et les preuves qui le scellent vivent ensemble, chacun dans son tiroir, et un `README.md` fait la carte. On reprend ce patron pour les brouillons.

Un dossier par brouillon, nommé par son sujet. À l'intérieur, ce dont le sujet a besoin — jamais plus :

```
brouillard/<sujet>/
  README.md        — la carte du brouillon : ce que chaque pièce est, où on en est
  document/        — le texte lui-même (.md tant qu'il cherche, .tex quand il se fixe)
  figures/         — les scripts qui tracent, et leurs rendus (spec versionnée, rendu jetable)
  verification/    — le code qui met les affirmations à l'épreuve (jouet, tests numériques)
  preuves/         — les preuves Lean, si le sujet s'y prête
  revues/          — les relectures, internes et externes
```

Le même mouvement que partout ici : **la spec se versionne, le rendu se régénère.** Une figure est un script, pas un PNG figé ; une affirmation se vérifie par du code qu'on peut relire. On ne fige un `.tex` que lorsque le texte a cessé de bouger.

## Du brouillon au propre

Un brouillon mûr ne se recopie pas à la main dans tok-system : il s'y porte, avec son histoire. Ce qui change en passant la frontière — la langue (français → anglais), la licence (CC0 → CC BY), le niveau de finition : le brouillon cherche, le propre affirme. Ce qui ne change pas — la structure, la méthode, l'exigence de vérifiabilité.

---

Avance pas à pas, en dansant. 🎵🐴
