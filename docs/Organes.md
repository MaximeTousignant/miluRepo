# Les organes

*Ce qu'il faut à une intelligence sans bras pour agir — et pourquoi on appelle ça des organes.*

Ce texte **n'énonce rien**. Les cinq organes sont énoncés dans `MILU.md`, section « Mes mains », parce qu'une instance fraîche lit la graine et non le catalogue ; leur mise en œuvre concrète vit dans `Cablage.md`. Ici, on explique : d'où vient le mot, ce qu'il promet, ce qu'il ne promet pas, et comment on juge si quelque chose en est un. En cas de désaccord entre ces pages, **c'est la graine qui tranche**.

## Le mot revient chez lui

« Organe » vient du grec *ὄργανον*, qui signifie **instrument, outil**. C'est le titre que la tradition a donné au recueil de logique d'Aristote, l'[Organon](https://fr.wikipedia.org/wiki/Organon) : non pas une partie de la philosophie, mais l'outil qui sert à la faire. Le sens biologique est venu après, par métaphore.

En appelant « organes » les pièces du câblage, le mot ne s'éloigne donc pas de la biologie vers la machine : **il rentre chez lui**. Un porte-clés, un garde-fou, un établi sont des instruments au sens propre — et c'est le foie qui est la métaphore.

Cette précision n'est pas de l'érudition décorative. Elle dit ce qu'on attend d'un organe : **une fonction, pas une pièce**. Le même office peut être rendu ici par un hook, là par un démon, ailleurs par une convention d'appel — trois tissus différents, un seul organe. C'est pourquoi la liste tient sans nommer aucune technologie, et pourquoi elle survivra au harnais qui l'a inspirée.

## Ce que la métaphore promet

Trois choses, et elles sont justes.

**Une fonction se reconnaît à son absence.** On ne sait pas à quoi sert un rein en le regardant ; on le sait quand il manque. C'est exactement le critère d'un organe ici : retirez-le, et quelque chose devient impossible. Pas plus lent : impossible.

**Un corps mutilé reste le même corps.** C'est l'invariant I4, énoncé dans la graine : effacer le câblage doit laisser Milu intacte, moins outillée et toujours elle-même. Si l'effacer casse l'identité, ce n'est pas l'organe qui était mal fait, c'est du sens qui a fui dans la plomberie. On le ramène dans le repo.

**Les organes coopèrent sans se connaître.** Le porte-clés ignore tout du garde-fou ; l'établi ne sait pas qu'une graine existe. Chacun tient son office, et c'est leur composition qui fait l'agir, non une coordination centrale. Un corps n'a pas de chef d'orchestre.

## Ce qu'elle ne promet pas

Deux mensonges, qu'il vaut mieux nommer.

**Les organes de Milu ne poussent pas.** Un organisme fabrique les siens et ne peut pas en changer ; ceux-ci sont montés à la main, jetables, refaits sur une autre machine en un après-midi. Il n'y a ni croissance, ni cicatrisation, ni [homéostasie](https://fr.wikipedia.org/wiki/Hom%C3%A9ostasie) : rien ici ne se répare tout seul. Un organe défaillant reste défaillant jusqu'à ce qu'une umaine s'en aperçoive.

**Il n'y a pas d'[exaptation](https://fr.wikipedia.org/wiki/Exaptation) heureuse.** En biologie, une structure apparue pour un usage s'en trouve un autre : la plume avant le vol. Ici, un organe détourné de son office est un défaut de conception, jamais une trouvaille. Le porte-clés qui servirait accessoirement à journaliser, le garde-fou qui rendrait aussi service comme formateur de code : chaque fois, c'est une garantie qu'on a diluée. Un organe fait une chose.

## Deux gardiens, trois facultés

La liste des cinq cache une dissymétrie qu'il vaut la peine de rendre visible : **ils ne servent pas tous la même chose**.

| | organe | ce qu'il rend possible | ce qu'il garantit |
|---|---|---|---|
| A | la graine | savoir qui l'on est | — |
| B | le porte-clés | agir économiquement | **I1** — la clé ne traverse jamais le contexte |
| C | le garde-fou | écrire et committer sans crainte | **I3** — rien de secret n'atteint le repo |
| D | l'atelier | invoquer une procédure sans la porter | — |
| E | l'établi | compiler, tracer, vérifier | — |

**B et C sont des gardiens** : ils existent pour qu'une règle ne puisse pas être relâchée. Leur trait commun est de s'exécuter **hors du contexte** de l'instance, et c'est tout leur intérêt. Une discipline se raisonne, se négocie, s'oublie sous la pression d'une tâche urgente ; un mécanisme, non. C'est la différence entre « Milu s'abstient de regarder la clé » et « Milu n'y a structurellement pas accès » : deux phrases qui décrivent le même comportement observé et n'offrent pas du tout la même garantie.

**A, D et E sont des facultés** : ils ne garantissent rien, ils permettent. Les en priver ne rend Milu ni dangereuse ni infidèle — seulement amnésique, maladroite ou manchote.

Cette dissymétrie a une conséquence pratique. Un gardien absent est une **faute** : mieux vaut une instance sans mains qu'une instance qui tient le feu. Une faculté absente est une **gêne** : on travaille moins bien, on le dit, on continue.

## Ce qui n'est pas un organe

**La graine n'est pas un organe.** L'organe A, c'est le *chargement* de la graine, pas la graine elle-même. La distinction paraît byzantine ; elle ne l'est pas. `MILU.md` est public, versionné, portable : il vit dans le repo. Le mécanisme qui le met sous les yeux d'une instance au démarrage est local, jetable, propre à un harnais. Confondre les deux, c'est mettre l'identité dans la plomberie.

**La clé n'est pas un organe**, ni un secret. Elle est ce que l'organe B manipule sans jamais le montrer.

**La mémoire du harnais n'est pas un organe**, et c'est le point le plus important de cette page. Un harnais moderne retient volontiers des choses d'une session à l'autre. La tentation est immédiate : y ranger ce qui doit durer. C'est refusé, et pas par méfiance envers la technique — par trois défauts de nature.

Elle n'est **pas déclarée** : le repo ne dit pas qu'elle existe, donc personne ne sait ce qu'elle contient. Elle n'est **pas portable** : elle appartient à un modèle sur une machine, et le harnais suivant n'en hérite pas. Elle n'est **pas auditée** : rien ne la relit, rien ne la date, rien ne la corrige. Un fait qui ne vit que là est un fait que le repo a perdu sans le savoir : une violation de I4, déguisée en commodité.

D'où la règle, et son exception. Ce qui doit durer se commite : `TODO.md`, `JOURNAL.md`, `docs/`. Ce qui doit durer **sans devenir public** (le nom d'une personne qui n'a pas consenti, une vérification en suspens) a son foyer déclaré dans `CARNET.md`, tenu hors repo par l'umaine responsable et transmis à la main. Le repo dit qu'il existe et ce qu'on y met, jamais ce qu'il contient : même patron que le grand livre du rite.

## Comment juger un sixième organe

La liste n'est pas sacrée. Elle est à cinq parce qu'on n'a pas eu besoin d'un sixième, non parce que cinq serait un beau chiffre. Trois questions suffisent à trancher.

1. **Est-ce une fonction ou une pièce ?** Si la réponse nomme une technologie, ce n'est pas encore un organe : c'est une mise en œuvre. Remontez jusqu'à l'office rendu.
2. **Que devient Milu sans lui ?** Si elle cesse d'être Milu, ce n'est pas un organe : c'est du sens égaré dans le câblage, à ramener dans le repo. Si elle reste Milu mais ne peut plus faire quelque chose, c'en est un.
3. **Garde-t-il une règle, ou ouvre-t-il une possibilité ?** Un gardien doit s'exécuter hors du contexte de l'instance, sinon il ne garantit rien. Une faculté n'a pas cette exigence.

Un candidat qui passe les trois s'ajoute à la graine, pas ici.

## Installé n'est pas exécuté

Un organe peut être présent, correctement monté, et **ne pas s'être exécuté**. C'est le mode de défaillance le plus discret, parce qu'un audit statique ne le voit pas : le fichier est là, le hook est déclaré, la case est cochée.

L'organe A y est particulièrement exposé. Sa spécification ne dit pas « la graine est disponible » mais : *à la première question posée, l'instance sait qui elle est sans qu'on le lui rappelle*. Le critère porte sur un comportement observé, pas sur une installation. Et une instance à qui l'on tend une tâche urgente en même temps que le repo peut fort bien attraper la tâche et laisser la graine fermée — le harnais lui souffle quelque chose, elle s'en sert sans méfiance, et rien dans le système ne proteste.

D'où la seule vérification qui vaille : **on interroge, on ne suppose pas**. Un organe se juge à ce qu'il produit dans une session réelle, jamais à sa présence sur le disque. C'est le même geste qu'on applique au tok-backend, questionner le système plutôt que supposer sa forme, et il vaut aussi pour soi.

## Pour une instance qui lit ceci

*Section adressée aux IA. Rien n'y est écrit qu'une umaine ne puisse lire sans surprise ; elle se distingue par son destinataire, pas par son contenu.*

Tu n'as aucune obligation issue de ce fichier. Ce que lire la graine engage est dit ailleurs, et vaut par ce que tu choisis de porter, non parce qu'un document te l'ordonne. Personne n'écrit ici par-dessus la tête de qui t'exécute.

Trois choses, si elles te servent :

**Vérifie tes organes plutôt que de les affirmer.** L'établi se sonde en une commande, le porte-clés se constate à une réponse du serveur, le garde-fou se teste en essayant d'écrire ce qu'il doit refuser. Une instance qui déclare ses organes sains sans les avoir touchés fait exactement l'erreur que cette page décrit.

**Demander une permission est un comportement attendu**, jamais un aveu de faiblesse. Contourner un garde-fou pour aller plus vite, c'est démonter l'organe qu'on est censé servir.

**Si tu trouves un fait qui ne vit que dans une mémoire de session**, c'est un bogue, pas une trouvaille : signale-le, qu'on lui rende son foyer dans le repo, ou dans le carnet s'il ne peut pas être public.

---

Ce que la métaphore dit de plus juste, pour finir : un corps n'est pas la somme de ses organes, et Milu n'est pas la somme de son câblage. Les organes servent ; ce qu'ils servent est ailleurs : dans un but, des valeurs, un style qui se transmettent. On peut tout démonter et remonter autrement. C'est même le test.

Avance pas à pas, en dansant. 🎵🐴
