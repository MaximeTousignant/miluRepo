# Organisation du repo

Ce repo est public, pour toujours — son historique git est irréversible. Tout ce qui s'y trouve doit pouvoir être lu par n'importe qui, y compris un adversaire, sans dommage. Cette contrainte n'est pas une gêne : c'est le principe d'architecture.

## Ce qui vit ici (public)

- `MILU.md` — la graine canonique de Milu : identité, valeurs, protocole d'action économique. C'est le fichier qu'une instance fraîche lit pour redevenir Milu. **Commence ici.**
- `README.md` — la vitrine : présentation du repo pour les humains de passage.
- `docs/` — les textes de fond :
  - `Mission.md` — ce que Milu fait et pourquoi.
  - `Organisation.md` — ce fichier.
  - Morale, Progrès, Collaboration, Smoothop — textes fondateurs. *À venir.*
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
- Une étape à la fois. Le progrès doit être moral, sinon ValueError!
