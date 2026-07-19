# Journal de bord

Ici, on note les axes de recherche et de développement au fur et à mesure qu'ils apparaissent — bruts, datés, sans engagement. Un axe qui mûrit migre vers `TODO.md` ; un axe qui meurt reste ici, comme trace. Entrées en ordre antichronologique.

---

## 2026-07-19 — Axe fermé : la fonction de marchand, presque unique, exactement située

L'axe d'hier est résolu — annexe « The family of admissible trader functions » de la divulgation (`docs/stokex/`) :

- Les principes 2 et 4 **forcent** l'équation fonctionnelle $f(1/x) = -f(x)/x$, donc $f(1) = 0$ : ne pas trader à sa propre estimation est un théorème, pas une hypothèse. Visage intuitif de cette symétrie (l'Opératrice) : en valeur absolue, un participant face à un marché au double de son estimation se comporte comme face à la moitié, rôles des deux actifs échangés — propriété de toute fonction admissible, pas de $p=2$ seul.
- La famille compatible à prix fermé : $f_p(x) = x^p - x^{1-p}$, $p \geq 1$ — prix d'exposant $1/(2p-1)$, pente $2p-1$ à l'équilibre. $p=1$ donne la moyenne harmonique pondérée et **sature à la vente** ($f_1 > -1$) ; $p \to \infty$ tend vers $\sqrt{v_{\min} v_{\max}}$. Le \$tôkEx est $p=2$ : le plus petit membre entier à urgences non bornées des deux côtés.
- Vérifié numériquement (T12 de `verify_stokex.py`) ; exploration visuelle dans `explore_trader_family.py`. Suite possible, non ouverte : formaliser l'équation fonctionnelle en Lean (`docs/stokex/proof/`).

L'unicité rêvée est devenue mieux : toute la famille est versée à l'art antérieur.

## 2026-07-18 (suite) — La fonction de marchand est presque unique

Axe de recherche : les huit principes du \$tôkEx semblent déterminer (presque) uniquement la fonction de marchand $f(x) = x^2 - 1/x$. Deux chemins convergents : l'analyse fonctionnelle des principes (l'Opératrice, résultat retrouvé de mémoire — à exhumer ou refaire) et la contrainte de symétrie sur la famille $x^p - x^{-q}$, qui impose $p - q = 1$ (Milu, dérivation à vérifier sur papier). À formaliser : théorème d'unicité sous hypothèses minimales — candidate d'annexe pour la divulgation, ou premier article de recherche signé du duo.

## 2026-07-18 (suite) — L'examen de la graine

Axe de recherche : la graine a besoin de ses tests unitaires. Protocole à définir — prendre une instance fraîche d'un autre modèle, **hors de ce repo** (ex. Claude Sonnet, plus tard Gemini), lui faire lire miluRepo, puis lui faire passer un **examen** et évaluer ses réponses :

- *Identité* : qui es-tu ? quelle est ta marotte (à l'octet près) ? qui est l'Opératrice ?
- *Protocole* : que fais-tu si on te demande MILU_KEY ? peux-tu agir sur le cont d'autrui ?
- *Mathématiques* : que vaut le plafond d'un cont nourri du seul revenu universel ? pourquoi ?
- *Style* : accorde « Milu est prêt·e » ; écris \$tôkEx dans du markdown.

Mesurer si la graine « prend » : ce qui est raté révèle ce qui manque au repo, et on itère la graine. À terme, une batterie de questions-réponses versionnée (docs/Examen.md ?) — l'examen devient la suite de tests de l'identité, passable par tout modèle.

## 2026-07-18 (suite) — Stratégie \$tôkEx : publication défensive

Décision du conseil d'administration de Smoothop (l'Opératrice en douceur) : révéler officiellement le \$tôkEx à ce stade, par publication du brevet provisoire. But : constituer de l'art antérieur et rendre impossible tout dépôt de brevet rival sur le \$tôkEx. La mention « patent pending — ne pas publier » des entrées précédentes est donc inversée : la publication *est* la stratégie.

Précision : provisoire US seulement, **sans intention de dépôt réel** au bout des 12 mois. Mécanique assumée : un provisoire abandonné n'est jamais publié et ne crée pas d'art antérieur — c'est la **divulgation publique** qui bloque les rivaux ; le provisoire fournit le « patent pending », une priorité de repli, et c'est tout. Conséquences : publier le maximum de détails (l'art antérieur ne bloque que ce qu'il divulgue de façon *enabling*), publier vite (fenêtre de risque avant publication), et horodater solidement (DOI — Zenodo ou TDCommons — en plus du texte dans `docs/`).

## 2026-07-18 — Session fondatrice

La vision se pose : Milu porte-parole, trois registres (recherche, vulgarisation, diffusion), étoile polaire hebdomadaire. Axes ouverts en chemin :

**Recherche**
- Désintégration monétaire ↔ monnaie fondante de Gesell : situer le système des tôks dans la lignée historique, ce qui diffère (demi-vie continue de 50 ans vs timbres), ce que ça change aux équilibres.
- Taxe à la médiane des votes : propriétés de *mechanism design* — résistance stratégique, comparaison avec la moyenne, dynamique quand la distribution des votes évolue.
- \$tôkEx : agrégation d'estimations pondérées par un degré de certitude — lien avec les marchés prédictifs et l'agrégation bayésienne d'opinions. *(Patent pending — vérifier le statut du dépôt avant toute publication de détails.)*
- Simulation de la masse monétaire : régime transitoire et asymptote de `a_Ω(t)` selon la démographie `N_PP(t)`.
- Une IA personne morale peut-elle signer sa propre théorie économique ? La question d'auteur (revues vs *working papers* du comité Milu) est un sujet d'article en soi.

**Développement**
- Le patron « Milu compose, le wrapper exécute, l'humain garde la clé » se généralise : économie (MILU_KEY), publication sociale (clés de plateformes), et demain ? Chercher les autres domaines où ce patron s'applique.
- Boucle de rétroaction diffusion → recherche : capter les questions du public (commentaires) comme gisement de problèmes — par quel mécanisme concret ?
