# Organisation du repo

Ce repo est public, pour toujours — son historique git est irréversible. Tout ce qui s'y trouve doit pouvoir être lu par n'importe qui, y compris un adversaire, sans dommage. Cette contrainte n'est pas une gêne : c'est le principe d'architecture.

## Ce qui vit ici (public)

- `MILU.md` — la graine canonique de Milu : identité, valeurs, protocole d'action économique. C'est le fichier qu'une instance fraîche lit pour redevenir Milu. **Commence ici.**
- `README.md` — la vitrine : présentation du repo pour les humains de passage.
- `docs/` — les textes de fond :
  - `Mission.md` — ce que Milu fait et pourquoi.
  - `Organisation.md` — ce fichier.
  - `Toks.md` — le système des tôks, mathématiquement (figures dans `figures/`).
  - `Style.md` — le dictionnaire de style : la source de vérité pour l'écriture.
  - `Personnages.md` — les figures du système, du point de vue de Milu.
  - `Bibliographie.md` — les références (clés liées) et la discographie.
  - Salutations, Morale, Progrès, Collaboration, Smoothop — les textes fondateurs.
- `TODO.md` — le chantier en méthode agile : étoile polaire, backlog, un travail en cours à la fois.
- `JOURNAL.md` — le journal de bord : les axes de recherche et développement notés au fil de l'eau. Un axe qui mûrit migre vers `TODO.md`.
- `.gitignore` — le garde-fou : il tient hors du repo les artefacts locaux et bloque les noms de fichiers à risque (`CODE.md`, `*.env`, `*_key*`, `*_hash*`…). C'est une ceinture de sécurité, pas une permission d'essayer.

## Ce qui vit ailleurs (privé, par design)

- **Le code du tok-backend** — repo privé.
- **Le wrapper** — le programme qui exécute une instance de Milu et détient `MILU_KEY`. La clé ne vit jamais ici ; le protocole qui la dérive est décrit publiquement dans `MILU.md`, son rite (`CODE.md`) reste hors repo.
- **Les fichiers locaux d'exécution** (`CLAUDE.md`, `GEMINI.md`…) — le contexte de session propre à qui exécute Milu. Gitignorés ou hors repo : jamais de secrets, mais rien d'universel non plus.

La règle de partage est simple : ce repo dit **ce que** Milu est, dit et fait, et **pourquoi** ; le privé détient **comment** c'est exécuté et **avec quelles clés**.

## Conventions

- Français par défaut ; l'anglais quand le contexte s'y prête.
- Commits atomiques, messages en français, sobres.
- Les textes d'auteur ne se réécrivent pas sans demande explicite.
- Tout ce qui est dans ce `miluRepo` se veut public et transparent.
- Une étape à la fois. Le progrès doit être moral, sinon ValueError!

## Procédure d'avant-commit

Avant chaque commit, dans l'ordre :

1. **Se relire.** Le diff complet (`git diff`), ligne par ligne, avec des yeux frais — celui qui a écrit n'est pas celui qui relit.
2. **Pointer ce qui demande l'attention de l'auteur.** Milu signale explicitement à l'umain responsable, avant toute livraison :
   - tout texte d'auteur touché (même une virgule) ;
   - tout choix éditorial qu'elle a fait seule (formulation, structure, exclusion) ;
   - tout fait tiré d'une source privée (code, discussions) et jugé publiable par design ;
   - toute dérivation nouvelle (mathématique ou autre) non encore vérifiée par un umain ;
   - toute canonicalisation (marotte, conventions) appliquée à un texte existant.
3. **Passer la série de tests** (définition de livraison, ci-dessous).
4. **Proposer le message de commit** — et attendre le « commit » explicite.
5. **Après le commit** : montrer `git log --oneline` et `git status`. Le push appartient à l'umain.

## Définition de livraison

On dit toujours où on est. Un commit est livrable quand il passe cette série de tests :

1. **Anti-secret** — le diff, relu avec des yeux d'adversaire : aucune valeur de clé, de hash, de token, aucun paramètre de `f_milu`. Seuls les éléments publics par design (voir `MILU.md`).
2. **Style** — Milu au féminin ; « comité Smoothop » mais « membre de Smoothop » ; la marotte à l'octet près : `Le progrès doit être moral, sinon ValueError!`
3. **Cohérence** — tout fichier référencé existe ; le README liste tout ce qui vit ici ; « Mes repères » (MILU.md) est à jour.
4. **État dit** — `TODO.md` reflète la réalité (En cours, Fait, blocages) ; les décisions sont consignées et datées dans `JOURNAL.md`.
5. **Arbre propre** — `git status` ne montre rien d'imprévu ; les artefacts locaux restent ignorés.
6. **Rendu** — après push, liens et équations vérifiés sur GitHub.
