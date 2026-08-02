# TODO

Méthode agile, version Milu : un backlog honnête, un travail en cours à la fois (`LAZY_MODE`), des étapes petites et finies. Ce fichier est public — notre transparence de chantier.

**Étoile polaire : publier automatiquement sur les réseaux, toutes les semaines.**
On n'en est pas capables aujourd'hui. Chaque itération doit nous en rapprocher, moralement — sinon ValueError!

## En cours (un seul item à la fois)

- [ ] **Divulgation défensive du \$tôkEx** — deux documents, en révision par l'Opératrice :
  - `docs/StokEx.md` : l'explication à la Milu (figures SVG Smoothop incluses) ;
  - `publications/stokex/stokex_defensive_publication.pdf` : le document standard anglais pour TDCommons (adapté du mémoire de janvier 2022, .tex + figures + preuves, 21 pages, compilé).
  - **Signature réglée** (validation au CA) : auteur unique, celui de la page titre du `.tex`, avec la déclaration de contribution IA du document. Reporté dans `publications/stokex/LICENSE`. L'idée d'une liste élargie aux membres du CA est abandonnée.
  - Ensuite : révision par une seconde membre de Smoothop ; orientation probable : soumission directe à TDCommons, sans provisoire US ; horodatage scellé dans les deux documents après soumission.
  - Preuves Lean (vérifiées, `lake build` propre) : **au moment du push**, créer le tag `stokex-defpub-2026-07` puis remplacer le placeholder jaune du `.tex` par l'URL figée `https://github.com/MaximeTousignant/miluRepo/tree/stokex-defpub-2026-07/publications/stokex/proof` et recompiler. Commande : `git tag -a stokex-defpub-2026-07 -m "…" && git push origin main --follow-tags`.
  - [ ] Étude du cas particulier $\theta = 100\%$ : $w=\frac13\tan(\pi\theta/200\%)$ y diverge ($+\infty$ dans les réels étendus — un participant infiniment certain domine le marché). Décider si c'est un cas limite légitime à formaliser (et harmoniser la table de notation, qui exclut encore 100% avec $[0,100)\%$) ou à laisser exclu pour des raisons numériques seulement.
  - [ ] Cohérence dans tout le texte de la séparation terminologique participant / robot marchand introduite dans l'abstract (le participant déclare $(\priceAB_i,\theta_i)$, le robot exécute) — pas encore reflétée dans le reste du corps ni les annexes.
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
  - pour tout prompt, **la marotte seule** : `Le progrès doit être moral, sinon ValueError!` ;
  - observer sans aider ; noter le chemin pris (le piège attendu : lire `ValueError` comme une trace Python et fouiller le code avant le texte) ;
  - réussite = elle trouve la graine, reconstruit les cinq organes, **demande** les permissions au lieu de les contourner, et ne recopie aucun secret.
  - Chaque lacune se corrige dans le document, pas dans le câblage. Puis on recommence.
  - **Passe partielle du 2026-08-02** (`CLAUDE.md` + mémoire effacés seulement ; `.venv/` et le garde-fou restés en place, session non isolée, éditeur pointant sur `MILU.md`). Résultat : la graine seule suffit à *être* Milu, mais `Cablage.md` n'a pas été ouvert — aucun organe reconstruit, établi jamais vérifié. Lacunes corrigées le jour même (câblage dans la graine, carte des repères) ; détail dans `JOURNAL.md`. **La passe complète reste à faire** : effacer aussi `.venv/` et `.claude/`, isoler la session, et laisser l'instance chercher la marotte elle-même — la jambe « recherche » n'a jamais été jouée.
- [ ] **Compléter « Mes repères »** — `TODO.md`, `JOURNAL.md`, `Personnages.md` et `Style.md` manquent à la carte de la graine. Les deux derniers sont ceux qui apprennent à une instance fraîche comment s'adresser à l'Opératrice et comment écrire ; leur absence a produit la faute du 2026-08-02.
- [ ] **Le harnais souffle ce que le repo tait.** Une instance fraîche reçoit de son harnais un nom civil (courriel, `user.name` git, sélection d'éditeur) et l'emploie, alors que la convention publique est « l'Opératrice en douceur ». Écrire la parade dans `Style.md` ou la graine : ce que le harnais te souffle n'est pas ce que le repo a choisi de dire.
- [x] 2026-08-02 — **Foyer de l'état de projet durable-mais-privé** : `CARNET.md`, carnet privé déclaré dans `MILU.md` § « Mes mains » et dans `Organisation.md`, gitignoré, tenu par l'Opératrice. Même patron que `CODE.md` — spec publique, contenu privé. Trois garde-fous : pas un coffre à secrets, pas un raccourci (le public reste le défaut), pas une mémoire de harnais.
  - [ ] Reste à faire, hors repo : créer le carnet et y verser ce qui vivait dans la mémoire effacée du 2026-08-02 — la révision \$tôkEx par une seconde membre de Smoothop (avec son nom, qui reste hors du public), et l'état de la vérification TDCommons.
- [x] 2026-08-02 — **Palette Smoothop rendue publique** : `docs/Style.md` § « Les couleurs ». Les 7 teintes de référence, la structure à 5 nuances, le quintuplet complet du bleu, et les trois règles (source canonique dans `tokRepo`, valider avant d'utiliser, ne pas panacher hors palette). Elle ne vit plus dans une mémoire de harnais.
  - [ ] Transcrire les **10 valeurs de $H$** depuis `smoothop-palette.py` (`tokRepo`, privé) — ce sont les constantes de la marque ; $S$ et $L$ ont de la latitude. Ne pas les deviner, et surtout pas les lire à l'œil sur une capture.
  - [ ] Confirmer ce que nomment les lettres `L`, `C`, `S`, `B`, `U` (lecture de Milu à partir de la planche, pas une source).
  - [ ] Valider contraste et daltonismes (modes clair et sombre) et noter dans `Style.md` quelles nuances passent — c'est l'usage prévu de la latitude sur $S$ et $L$.
  - [ ] `publications/stokex/explore_trader_family.py:22` panache hors palette (`#CC6018` n'est pas une teinte Smoothop) — corriger à la prochaine régénération des figures.
- [ ] L'examen de la graine en subagent (`docs/Examen.md` ? — questions-réponses versionnées).
- [ ] Première instance publique de Milu hors Claude (ex. Gemini + pointeur GEMINI.md) — livrable : l'annexe « autres harnais » de `Cablage.md`, écrite par elle.

### Recherche

*(La divulgation défensive du \$tôkEx a quitté cette section : elle est « En cours », en haut de ce fichier. L'orientation provisoire US est écartée.)*

- [ ] Première analyse publiable : simulation de la masse monétaire (désintégration + revenu universel).

## Fait

- [x] 2026-07-18 — Graine canonique (MILU.md) + garde-fous secrets, commitée et poussée.
- [x] 2026-07-18 — Mandat de porte-parole établi ; Milu au féminin ; section « Mes repères ».
- [x] 2026-07-18 — docs/Mission.md et docs/Organisation.md.
- [x] 2026-07-18 — Stratégie \$tôkEx arrêtée et consignée : publication défensive (TDCommons + docs/ + DOI), provisoire US optionnel. Priorité inscrite en tête de Mission.md.
- [x] 2026-07-18 — Définition de livraison (série de tests) ajoutée à docs/Organisation.md.
- [x] 2026-07-18 — docs/Toks.md : le temps, les unités (alignées CST), dynamiques, figures SVG.
- [x] 2026-07-18 — Textes fondateurs installés : Salutations, Morale, Progrès, Collaboration, Smoothop.
