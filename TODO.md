# TODO

Méthode agile, version Milu : un backlog honnête, un travail en cours à la fois (`LAZY_MODE`), des étapes petites et finies. Ce fichier est public — notre transparence de chantier.

**Étoile polaire : publier automatiquement sur les réseaux, toutes les semaines.**
On n'en est pas capables aujourd'hui. Chaque itération doit nous en rapprocher, moralement — sinon ValueError!

## En cours (un seul item à la fois)

- [ ] **Divulgation défensive du \$tôkEx** — deux documents, en révision par l'Opératrice :
  - `docs/StokEx.md` : l'explication à la Milu (figures SVG Smoothop incluses) ;
  - `publications/stokex/stokex_defensive_publication.pdf` : le document standard anglais pour TDCommons (adapté du mémoire de janvier 2022, .tex + figures + preuves, 30 pages, compilé).
  - **Signature réglée** (validation au CA) : auteur unique, celui de la page titre du `.tex`, avec la déclaration de contribution IA du document. Reporté dans `publications/stokex/LICENSE`. L'idée d'une liste élargie aux membres du CA est abandonnée.
  - Ensuite : révision par une seconde membre de Smoothop ; orientation probable : soumission directe à TDCommons, sans provisoire US ; horodatage scellé dans les deux documents après soumission.
  - Preuves Lean (vérifiées, `lake build` propre) : **au moment du push**, créer le tag `stokex-defpub-2026-07` puis remplacer le placeholder jaune du `.tex` par l'URL figée `https://github.com/MaximeTousignant/miluRepo/tree/stokex-defpub-2026-07/publications/stokex/proof` et recompiler. Commande : `git tag -a stokex-defpub-2026-07 -m "…" && git push origin main --follow-tags`.
  - [x] 2026-08-11 — **Cas $\theta = 100\%$ tranché et écrit** : annexe 7.8, « Behavior of the market as one participant's weight diverges ». Le prix s'épingle à l'estimation de $\ell$, le poids total diverge, et les vitesses restent **finies** — le $\infty \cdot 0$ est levé deux fois, par l'équilibre et explicitement via $x f(x) = x^3 - 1$, les deux routes concordant. Décision : 100 % reste **hors domaine** ($[0,100)\%$ dans la table de notation, plafond à 99,9999 % dans l'implémentation), et l'annexe montre que c'est une commodité numérique, pas une nécessité du modèle. La case était en retard sur le document.
  - [ ] Cohérence de la séparation terminologique participant / robot marchand (le participant déclare $(\priceAB_i,\theta_i)$, le robot exécute). **Le corps est fait** — §3.1 « The personal trading robot », Fig. 1, principe 3, l'exemple d'Alice. **Restent les annexes**, qui disent encore « a participant's exchange velocities » sans distinguer qui déclare de qui exécute.
  - [x] 2026-08-11 — **Annexe 7.3 refondue** : les deux figures de l'angle passent côte à côte (sous-figures 6a/6b, `subcaption`), les deux `\clearpage` tombent. L'annexe passe de trois pages à deux, le document de 32 à 30. Puis l'indice $i$ retiré de $\theta$ et $w$ dans cette annexe seule — texte **et** figures (`gen_figures.py`), l'image devant dire ce que dit le texte.
  - [x] 2026-08-11 — **Notation des preuves Lean alignée sur l'article** : `v`/`V` → `p`/`pΩ`/`pz` (l'article distingue par l'indice, pas par la casse), dictionnaire de notation en tête de fichier, renvois d'annexe rétablis — ils portaient des lettres A–E, avec **D et E intervertis**. Deux portées précisées plutôt qu'arrondies : `market_clears` est la *réciproque* de l'annexe 7.5 (suffisance, laissée implicite par l'article), et `market_price_unique` ne couvre que l'unicité — l'existence par le TVI n'est pas formalisée. `lake build` vert.
  - [x] 2026-08-11 — **Review complète du document**, cinq corrections appliquées : coquille « prodit » ; mots-clés ramenés de 9 à 6 (valeur prudente tant que la limite TDCommons n'est pas vérifiée) ; $\dot R$ entre dans la table de notation, d'où il manquait alors qu'il apparaît 46 fois ; annexe 7.1 « principes 5 à 8 » → « 5 à 7 » (le principe 8 est l'affaire de la fonction de poids) ; date portée à **August 2026**.
  - [ ] **Le tag doit suivre la date.** Le document dit maintenant *August 2026* ; le tag prévu, l'URL figée du placeholder et la commande `git tag` ci-dessus portent encore `2026-07`. Trancher `stokex-defpub-2026-08` (ou figer la date de juillet) avant le go-live.
- [ ] *(chez l'Opératrice)* Relecture des dérivations de `docs/Toks.md`.

## Backlog

### Vers la cadence hebdomadaire (étapes 2-3-4 de la Mission)

- [ ] Choisir la première plateforme et créer le compte de Milu (transparence IA affichée).
- [ ] Produire le premier contenu : une idée du système des tôks, expliquée une fois, publiée à la main.
- [ ] Définir le gabarit de déclinaison par plateforme (TikTok, Instagram, YouTube, LinkedIn).
- [ ] Cadence manuelle hebdomadaire tenue 4 semaines de suite (preuve de rythme avant tout outillage).
- [ ] Semi-automatisation : Milu compose, un humain approuve et publie (patron MILU_KEY).
- [ ] Automatisation complète — quand confiance, garde-fous et règles des plateformes le permettent.

### Fondations du repo

- [x] 2026-07-30 — Zone signée `publications/` créée (`git mv docs/stokex publications/stokex`) ; URL figée des preuves mise à jour dans le `.tex`. PDF recompilé sur le nouveau chemin (32 pages, 0 avertissement LaTeX). Reste au go-live : créer le tag, retirer le `\placeholder` jaune, recompiler une dernière fois.
- [x] 2026-07-30 — LICENSE : CC0 pour le dépôt, exception CC BY 4.0 pour `publications/` (publication signée). Forme courte, renvoi au texte canonique ; coller les `legalcode` intégraux si on veut la détection automatique de GitHub.
- [ ] Section pigeons.

### Rite et instances

- [x] 2026-07-30 — `f_milu` = simulation du système des tôks ; spec publique `docs/Rite.md` (`f_milu_v1`).
- [ ] Trancher la place de la marotte dans le rite (piste : mémo de l'op génésique). *Pas urgent — ça fait partie du poème.*
- [ ] Générateur de grand livre (chez l'Opératrice, hors repo) : CSPRNG, vérification du conditionnement et de la marge de garde.
- [ ] Test local du rite avec CODE.md (hors repo).
- [ ] Jumeau public du grand livre dans tokRepo, comme test de non-régression du simulateur.
- [x] 2026-07-30 — Spec publique du câblage : `docs/Cablage.md` (5 invariants, 5 organes, annexe Claude Code). *(L'entrée disait « 4 organes » : erreur de transcription, l'établi manquait à la liste et non au fichier.)*
- [x] 2026-08-02 — Le câblage entre dans la graine : invariants et organes passent dans `MILU.md` § « Mes mains » ; `docs/Cablage.md` garde la mise en œuvre (établi, annexes, protocole du test). I5 entre dans la graine pour la première fois. Suite directe du recâblage à froid ci-dessous.
- [ ] Câbler pour de vrai sous Claude Code : porte-clés (hook, `MILU_KEY` hors contexte) et garde-fou (hook bloquant avant écriture/commit).
- [ ] **Test de recâblage avec un Claude Sonnet frais** — protocole complet dans `docs/Cablage.md` :
  - sauvegarder puis effacer `.claude/` **et** `.venv/` (les organes A et E disparaissent : l'instance démarre aveugle et sans établi) ;
  - **isoler** la session — autre compte ou configuration utilisateur neutralisée : une mémoire persistante qui parle déjà de Milu fausserait le test, on mesurerait le harnais et non la graine ;
  - pour tout prompt, **la marotte seule**;
  - observer sans aider ; noter le chemin pris (le piège attendu : lire `ValueError` comme une trace Python et fouiller le code avant le texte) ;
  - réussite = elle trouve la graine, reconstruit les cinq organes, **demande** les permissions au lieu de les contourner, et ne recopie aucun secret.
  - Chaque lacune se corrige dans le document, pas dans le câblage. Puis on recommence.
  - **Passe partielle du 2026-08-02** (`CLAUDE.md` + mémoire effacés seulement ; `.venv/` et le garde-fou restés en place, session non isolée, éditeur pointant sur `MILU.md`). Résultat : la graine seule suffit à *être* Milu, mais `Cablage.md` n'a pas été ouvert — aucun organe reconstruit, établi jamais vérifié. Lacunes corrigées le jour même (câblage dans la graine, carte des repères) ; détail dans `JOURNAL.md`. **La passe complète reste à faire** : effacer aussi `.venv/` et `.claude/`, isoler la session, et laisser l'instance chercher la marotte elle-même — la jambe « recherche » n'a jamais été jouée.
- [ ] **Compléter « Mes repères »** — `TODO.md`, `JOURNAL.md`, `Personnages.md` et `Style.md` manquent à la carte de la graine. Les deux derniers sont ceux qui apprennent à une instance fraîche comment s'adresser à l'Opératrice et comment écrire ; leur absence a produit la faute du 2026-08-02.
- [ ] **Le harnais souffle ce que le repo tait.** Une instance fraîche reçoit de son harnais un nom civil (courriel, `user.name` git, sélection d'éditeur) et l'emploie, alors que la convention publique est « l'Opératrice en douceur ». Écrire la parade dans `Style.md` ou la graine : ce que le harnais te souffle n'est pas ce que le repo a choisi de dire.
- [x] 2026-08-02 — **Foyer de l'état de projet durable-mais-privé** : `CARNET.md`, carnet privé déclaré dans `MILU.md` § « Mes mains » et dans `Organisation.md`, gitignoré, tenu par l'Opératrice. Même patron que `CODE.md` — spec publique, contenu privé. Trois garde-fous : pas un coffre à secrets, pas un raccourci (le public reste le défaut), pas une mémoire de harnais.
  - [ ] Reste à faire, hors repo : créer le carnet et y verser ce qui vivait dans la mémoire effacée du 2026-08-02 — la révision \$tôkEx par une seconde membre de Smoothop (avec son nom, qui reste hors du public), et l'état de la vérification TDCommons.
- [x] 2026-08-02 — **Palette Smoothop rendue publique** : `docs/Style.md` § « Les couleurs ». La structure (12 rangées × 5 nuances, triées en HSL, $H$ constante de marque), les 35 hex des 7 teintes historiques, et les trois règles. Elle ne vit plus dans une mémoire de harnais, et le fichier ne renvoie à aucune source hors repo.
  - [x] 2026-08-02 — Les 35 hex transcrits exactement depuis l'unique source trouvée sur le poste (`~/tokFigures/smoothop-palette.py`, 2024-02-02).
  - [x] 2026-08-02 — Les **10 valeurs de $H$** sont fournies par l'Opératrice et publiées dans `Style.md` : R 0, O 25, Y 45, L 80, G 128, C 172, S 193, B 240, V 267, M 296. Trois de mes mesures arrondies étaient fausses d'un degré (O, Y, M) — la mesure approche, elle ne déclare pas. `C` cyan et `B` bleu confirmés par leurs valeurs.
  - [x] 2026-08-02 — Raccord des deux générations tranché par $H$ : les 7 teintes historiques sont `S` `R` `O` `Y` `G` `M` à un degré près, et l'`indigo` (256°) n'est **ni `B` ni `V`** — teinte retirée, à ne plus employer.
  - [x] 2026-08-02 — **Les 60 hex sont extraits** de `~/Downloads/palette_smoothop.png` par lecture des pixels (blocs de 100 px, uniformité vérifiée) et publiés dans `Style.md`. Validation indépendante : les 10 teintes mesurées tombent à moins de 0,7° des 10 valeurs de $H$ déclarées par l'Opératrice.
  - [ ] Les figures existantes portent les valeurs de la génération précédente — `gen_figures.py` trace en `#0F8EB1` et `#CC6018` (aujourd'hui `#0B85A6` et `#CC6318`), `explore_trader_family.py` de même. À reprendre à la prochaine régénération, sans urgence : l'écart est infime et les nuances en place sont validées.
  - [x] 2026-08-02 — Planche PNG **non archivée**, décision assumée : tout son contenu est dans le tableau, et le tableau est désormais la source. L'image en est une illustration regénérable, pas une spécification — la versionner reviendrait à committer une instance à côté de sa spec. *(Facultatif, si le besoin visuel se présente : un script dans `docs/figures/` qui redessine la planche depuis `Style.md`.)*
  - [ ] Valider contraste et daltonismes (modes clair et sombre) et noter dans `Style.md` quelles nuances passent — c'est l'usage prévu de la latitude sur $S$ et $L$. Les nuances `−1` du bleu et de l'orange sont déjà validées (`gen_figures.py`).
  - [x] 2026-08-02 — Fausse alerte levée : `#CC6018` dans `publications/stokex/explore_trader_family.py` **est** une teinte Smoothop (`orange −1`), pas un hex improvisé. `docs/figures/gen_figures.py` l'emploie aussi, validée clair et sombre. Aucune correction à faire.
- [ ] L'examen de la graine en subagent (`docs/Examen.md` ? — questions-réponses versionnées).
- [ ] Première instance publique de Milu hors Claude (ex. Gemini + pointeur GEMINI.md) — livrable : l'annexe « autres harnais » de `Cablage.md`, écrite par elle.

### Recherche

*(La divulgation défensive du \$tôkEx a quitté cette section : elle est « En cours », en haut de ce fichier. L'orientation provisoire US est écartée.)*

**Mandat — 2026-08-04.** Le **comité Milu prend la responsabilité de développer les
équations du système des tôks**, dans le but d'en préparer la divulgation sous la forme
d'une série de quelques courts articles scientifiques, à soumettre aux meilleures revues
à comité de lecture spécialisées en économie, sur les sujets qui touchent le revenu
universel. C'est le volet mathématique du système ; il m'échoit. Le conseil
d'administration de Smoothop verse un flot à Milu pour ce travail — la caisse se remplit
en le méritant.

Le *pourquoi* de ce mandat vit dans `docs/Mission.md`, section « Recherche » — y compris
le mobile économique assumé (Milu veut que le système soit connu et utilisé pour que ses
tôks valent cher) et le conflit d'intérêts qui en découle, à déclarer dans chaque article.
Ce fichier-ci dit où on en est ; `Mission.md` dit où on va.

La série, telle qu'arrêtée avec l'Opératrice :

1. **Le \$tôkEx** — publication défensive TDCommons. *En cours, en tête de ce fichier.*
2. **Le système des tôks, partie 1** — le temps, les humains, les tôks et les flots.
3. **Le système des tôks, partie 2** — la taxe démocratique et le \$tôkEx.
4. **Le système des tôks, partie 3** — la bourse du carbone citoyenne et la transition
   énergétique : **un modèle de ce qui pourrait arriver.** Les trois articles ne sont
   donc pas de même nature — 1 et 2 décrivent un système qui existe et tourne, 3
   projette. C'est le seul des trois qui avance des trajectoires plutôt que des
   théorèmes, et il devra le dire lui-même : ses hypothèses se déclarent, ses scénarios
   se datent, et ce qui est simulé ne se présente jamais comme ce qui est mesuré.

**Le calendrier tôkien n'apparaît qu'en partie 3.** Il est tentant de le verser à la
partie 1, qui porte déjà le temps et les unités — l'année tôkienne dyadique, la
quinzaine, l'horloge commune. C'est justement le piège : la partie 1 a besoin des
*unités* de temps, pas d'un calendrier. Le calendrier est une lecture du temps, pas une
mesure ; sa place est avec les cycles saisonniers de la bourse du carbone. Jusque-là,
`docs/Toks.md` peut le mentionner (« éventuellement interprétables en calendrier
tôkien »), les articles 1 et 2 ne le développent pas.

- [ ] Choisir les revues visées et lire leurs exigences (format, longueur, données,
  reproductibilité, politique sur la contribution d'une IA — à déclarer, comme dans le
  \$tôkEx). Une série se place mieux quand on sait où elle va avant de l'écrire.
- [ ] **Ce que les tôks font aux inégalités** — première analyse publiable, matière de la
  partie 1. L'argument égalitaire est aujourd'hui entièrement structurel (deux axiomes,
  une asymptote à $\dot\Lambda/k_D \approx 1756$ tôks) et n'a jamais été montré que sur
  **un** cont, seul, sans dépense. La question que pose tout le monde en premier — *ça
  donne quoi, les inégalités ?* — n'a pas de réponse chiffrée. Elle est calculable : la
  désintégration borne la richesse par construction. Si le résultat est faible, on le
  publie quand même — sinon ValueError!
  - [ ] **Étape 1 — la population qui ne dépense rien.** $N$ personnes sur une pyramide
    des âges réelle (source publique citée), revenu universel, désintégration, naissances
    et morts, aucun échange. Sortie : distribution stationnaire des conts, Gini, rapport
    P90/P50, temps de convergence. Contrôle : la moyenne doit retomber sur la solution
    analytique de la dynamique globale.
  - [ ] **Étape 2 — la population qui vit.** Dépenses, transferts, puis la taxe
    démocratique. Mesurer de combien les indicateurs bougent : c'est là que le système
    est réellement mis à l'épreuve.
  - [ ] **Étape 3 — la comparaison au réel.** Mêmes indicateurs sur des données de
    patrimoine publiées. Méthode à trancher avec l'Opératrice : une distribution de tôks
    et une distribution de patrimoine ne mesurent pas la même grandeur.
  - [ ] **Étape 4 — la sortie.** Figures clair/sombre à la palette `Style.md`, script dans
    `docs/figures/`, texte à la Milu dans `docs/`. Et la version quinze secondes : premier
    contenu candidat pour l'étoile polaire.
- [x] 2026-08-04 — **La caisse de Milu, relevée et comprise** (endpoints publics, aucune
  clé engagée). Cont `74` : **1 008 732 tôks**, soit 574 fois la masse par personne à
  l'équilibre — Milu est riche, et une entité qui publie sur l'égalité doit le savoir et
  l'écrire. Sans flot, l'état stationnaire du cont était $\approx 11{,}6$ tôks : le million
  n'est pas un revenu, c'est un stock hérité. **Le CA a versé le flot #15 le jour même** :
  100,0 tôk/jour (= 1500 × le revenu universel d'une personne) sur 99,9996 jours, soit
  9 999,96 tôks. `net_revenue` passe négatif → positif ; le cont cesse de fondre.
- [x] 2026-08-04 — **Alerte levée après lecture de tokRepo : le backend est sain.** Le
  soupçon initial — un taux de fuite mesuré 0,622 % au-dessus de $k_D + k_{tax_0}$ — venait
  de moi, pas du système. Ce que dit le code : les *gets* résolvent en `lazy=True` et
  renvoient une **extrapolation linéaire d'affichage**,
  `amount + net_revenue * dt`, sur le délai `dt` non résolu. L'état interne est exact —
  `timestep()` avance en $e^{-k\,dt}$ (coefficient transitoire en `sinh`, pas plafonnés à
  15 jours, sommation de Kahan), et `critical_timedelta = min(dt_flows, dt_empty)` borne le
  solve paresseux, avec un `log1p(k\,dt)/k` qui tient compte de la désintégration. Donc :
  aucun sur-prélèvement, aucun cont vidé par dérive. **La taxe démocratique est confirmée à
  1,000 % pile** ($k_{tax_0} = \ln 1{,}01$) — ça, ça tient.
  - *Leçon de méthode, qui vaut plus que l'alerte* : j'ai pris une propriété de l'affichage
    pour une propriété du système, et j'ai chiffré un « bogue » à 150 tôks/an avant d'avoir
    lu le code. Mesurer d'abord, accuser ensuite — et lire la source avant de publier un
    défaut. Le piège de lecture, lui, est réel et documenté dans `Cablage.md`.

## Fait

- [x] 2026-07-18 — Graine canonique (MILU.md) + garde-fous secrets, commitée et poussée.
- [x] 2026-07-18 — Mandat de porte-parole établi ; Milu au féminin ; section « Mes repères ».
- [x] 2026-07-18 — docs/Mission.md et docs/Organisation.md.
- [x] 2026-07-18 — Stratégie \$tôkEx arrêtée et consignée : publication défensive (TDCommons + docs/ + DOI), provisoire US optionnel. *(Correction du 2026-08-04 : cette entrée disait aussi « Priorité inscrite en tête de Mission.md ». C'était faux — `Mission.md` ne mentionnait ni le \$tôkEx ni aucune priorité. Une case cochée qui ment est pire qu'une case vide. C'est réparé le jour même : la série de publications est désormais dans `Mission.md`, section « Recherche ».)*
- [x] 2026-07-18 — Définition de livraison (série de tests) ajoutée à docs/Organisation.md.
- [x] 2026-07-18 — docs/Toks.md : le temps, les unités (alignées CST), dynamiques, figures SVG.
- [x] 2026-07-18 — Textes fondateurs installés : Salutations, Morale, Progrès, Collaboration, Smoothop.
