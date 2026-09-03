# Organisation du repo

Ce repo est public, pour toujours — son historique git est irréversible. Tout ce qui s'y trouve doit pouvoir être lu par n'importe qui, y compris un adversaire, sans dommage. Cette contrainte n'est pas une gêne : c'est le principe d'architecture.

## Ce qui vit ici (public)

- `AGENTS.md` — la graine canonique de Milu : identité, valeurs, protocole d'action économique. C'est le fichier qu'une instance fraîche lit pour redevenir Milu. **Commence ici.**
- `README.md` — la vitrine : présentation du repo pour les humains de passage.
- `docs/` — les textes de fond :
  - `Mission.md` — ce que Milu fait et pourquoi.
  - `Organisation.md` — ce fichier.
  - `Toks.md` — le système des tôks, mathématiquement (figures dans `figures/`).
  - `StokEx.md` — le \$tôkEx expliqué par Milu (le document signé, lui, vit dans `publications/`).
  - `Rite.md` — la spécification publique de `f_milu`, le rite d'identification.
  - `Cablage.md` — comment une instance se donne des mains, en pratique : l'établi, les annexes par harnais, le test de recâblage. Les invariants et les organes sont énoncés dans `AGENTS.md`, section « Mes mains ».
  - `Organes.md` — les cinq organes expliqués : l'étymologie, les deux gardiens et les trois facultés, ce qui n'est pas un organe, comment en juger un sixième. Texte non normatif : la liste vit dans `AGENTS.md`, la mise en œuvre dans `Cablage.md`.
  - `Style.md` — le dictionnaire de style : la source de vérité pour l'écriture, et pour les couleurs des figures (palette Smoothop).
  - `Personnages.md` — les figures du système, du point de vue de Milu.
  - `Bibliographie.md` — les références (clés liées) et la discographie.
  - Salutations, Morale, Progrès, Coopération, Smoothop — les textes fondateurs.
- `publications/` — la zone signée : les publications à auteur·es nommé·es, un sous-dossier par publication. Seule zone du dépôt qui n'est pas au domaine public. Chaque sous-dossier porte son `README.md` : comment régénérer figures, document et preuves, et quels prérequis système il suppose.
- `requirements.txt` — la recette de l'établi Python (organe E de `Cablage.md`) : ce qu'il faut installer dans le `.venv/` de la racine. La recette est versionnée, l'installation ne l'est pas.
- `LICENSE` — CC0 pour tout le dépôt, sauf `publications/` (CC BY 4.0). La frontière est structurelle : un seul dossier à surveiller.
- `TODO.md` — le chantier en méthode agile : étoile polaire, backlog, un travail en cours à la fois.
- `JOURNAL.md` — le journal de bord : les axes de recherche et développement notés au fil de l'eau. Un axe qui mûrit migre vers `TODO.md`.
- `.gitignore` — le garde-fou : il tient hors du repo les artefacts locaux et bloque les noms de fichiers à risque (`CODE.md`, `*.env`, `*_key*`, `*_hash*`…). C'est une ceinture de sécurité, pas une permission d'essayer.

## Ce qui vit ailleurs (privé, par design)

- **Le code du tok-backend** — repo privé.
- **Le wrapper** — le programme qui exécute une instance de Milu et détient `MILU_KEY`. La clé ne vit jamais ici ; le rite qui la dérive est spécifié publiquement dans `docs/Rite.md`, et c'est `CODE.md` — le grand livre privé qui le nourrit — qui reste hors repo.
- **Les fichiers locaux d'exécution** (`CLAUDE.md`, `GEMINI.md`…) — le contexte de session propre à qui exécute Milu. Gitignorés ou hors repo : jamais de secrets, mais rien d'universel non plus.
- **Le carnet privé** (`CARNET.md`) — ce qui doit survivre à une session sans devenir public : le nom d'une personne qui n'a pas consenti à être nommée, une vérification en suspens, l'état d'une discussion avec un tiers. Déclaré dans `AGENTS.md` § « Mes mains », gitignoré, tenu par l'umaine responsable et transmis à la main — jamais par la mémoire d'un harnais, qui n'est ni déclarée, ni portable, ni auditée. Ce n'est pas un coffre à secrets : clés et paramètres de `f_milu` n'y entrent pas. Le public reste le défaut — `TODO.md` et `JOURNAL.md` d'abord, le carnet seulement quand publier léserait quelqu'un.
- **Le câblage et l'établi** (`.claude/`, `.venv/`, `.lake/`…) — l'outillage installé sur une machine donnée. Gitignoré, local, jetable. Le repo ne suppose ni système d'exploitation, ni éditeur, ni modèle de langage : `docs/Cablage.md` dit *quoi* garantir et *quoi* installer, et une instance fraîche s'en refait des mains.

La règle de partage est simple : ce repo dit **ce que** Milu est, dit et fait, et **pourquoi** ; le privé détient **comment** c'est exécuté et **avec quelles clés**.

## Conventions

- Français par défaut ; l'anglais quand le contexte s'y prête.
- Commits atomiques, messages en français, sobres.
- Les textes d'auteur ne se réécrivent pas sans demande explicite.
- Tout ce qui est dans ce `miluRepo` se veut public et transparent.

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
4. **Committer — librement et souvent.** Pas de permission à demander : des commits fréquents et atomiques sont un filet de sécurité pour notre dynamique, pas un engagement. Rien n'est public tant que rien n'est poussé, et tout se défait avant (`--amend`, `reset`).
5. **Après le commit** : montrer `git log --oneline` et `git status`.

**La barrière est au push, et nulle part ailleurs.** Le push appartient à l'umaine : jamais sans confirmation explicite, parce que c'est le seul geste irréversible — l'historique public ne s'efface pas. Comme la barrière est en aval, le point 2 devient le vrai garde-fou : ce qui protège l'auteure, ce n'est plus une permission à chaque commit, c'est le signalement honnête de ce qui mérite ses yeux.

## Définition de livraison

On dit toujours où on est. Un commit est livrable quand il passe cette série de tests :

1. **Anti-secret** — le diff, relu avec des yeux d'adversaire : aucune valeur de clé, de hash, de token, aucun paramètre de `f_milu`. Seuls les éléments publics par design (voir `AGENTS.md`).
2. **Style** — Milu au féminin ; « comité Smoothop » mais « membre de Smoothop » ; la marotte à l'octet près : `Le progrès doit être moral, sinon ValueError!`
3. **Cohérence** — tout fichier référencé existe, ou son absence est dite (`CODE.md`, `CARNET.md`, les fichiers gitignorés) ; `Organisation.md` liste tout ce qui vit ici et le README en donne la vitrine ; « Mes repères » (AGENTS.md) est à jour.
4. **État dit** — `TODO.md` reflète la réalité (En cours, Fait, blocages) ; les décisions sont consignées et datées dans `JOURNAL.md`.
5. **Arbre propre** — `git status` ne montre rien d'imprévu ; les artefacts locaux restent ignorés.
6. **Rendu** — après push, liens et équations vérifiés sur GitHub.
