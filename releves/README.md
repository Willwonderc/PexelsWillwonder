# 4 — Relevés pour le tableau de bord

[vues-pexels.csv](vues-pexels.csv) rassemble le total de vues Pexels, une ligne par
relevé : l'API Pexels ne fournit pas ce chiffre, et ni ce dépôt ni ses tâches ne relèvent
aucune statistique sur pexels.com. Karl le note à la main ; une fois la session T faite
([consignes](../consignes/prochaines-sessions.md)), Telepex, son application Mac, y
ajoutera lui-même une ligne à chaque relevé.

## Fiche de suivi, photo par photo

[suivi-pexels.csv](suivi-pexels.csv) reprend la fiche de suivi de Karl (classeur
« Suivi des photos Pexels » écrit par Telepex, relevé du 24 septembre 2026 à 12 h 42),
une ligne par photo, de la plus vue à la moins vue :

- `photo` : numéro Pexels ;
- `moderation` : `retenue` si la modération de Pexels a mis la photo en avant (statut
  « approved »), `refusée` sinon (statut « rejected ») : la photo reste alors visible
  dans la galerie du profil ;
- `import` : date d'import sur Pexels ;
- `vues`, `telechargements`, `jaime` : statistiques affichées par Pexels au moment du
  relevé ;
- `evenement` : `oui` si la photo figure dans l'onglet « Événements marquants » du profil ;
- `titre` : titre sur Pexels, vide pour une photo sans titre (la fiche du 24 septembre
  porte encore, pour 333 photos, le texte automatique « Free stock photo of… ») ;
- `mots_cles` : mots-clés saisis à l'import.

Une fois la session T faite, Telepex remplace lui-même ce fichier à chaque relevé,
chaque semaine ou chaque jour, avec une colonne de plus, `releve` (date et heure du
relevé). D'ici là, ou si Telepex ne peut pas publier, déposer à sa place un fichier au
même format et au même nom (Add file → Upload files), en UTF-8. Le dépôt est public : il
ne reçoit que le relevé, jamais Telepex lui-même.

## Ajouter un relevé

Sur GitHub, ouvrir `vues-pexels.csv`, cliquer sur le crayon, ajouter une ligne à la fin,
puis « Commit changes ». Exemple de ligne, chiffres fictifs :

    2026-10-01,880000,920,20,épingles Pinterest lancées

- `date` : au format AAAA-MM-JJ ;
- `vues` : total de vues affiché par Pexels, sans espaces ;
- `photos` et `abonnes` : facultatifs, laisser vide au besoin ;
- `remarque` : facultative, pour noter un événement de la semaine.

Une fois la session T faite, Telepex ajoute lui-même sa ligne à chaque relevé (remarque
« Telepex ») : ne noter à la main que ce qu'il ne relève pas, comme les abonnés s'il ne
les lit pas.

Ce relevé alimentera la page de tableau de bord du site (session F) et le compteur de
l'écran Turing.

Chaque relevé compte aussi comme une activité du dépôt. GitHub suspend les tâches
planifiées d'un dépôt public resté 60 jours sans activité : un relevé par semaine garde
donc en marche la reconstruction nocturne du site.

## Réponses des assistants IA

[assistants-ia.csv](assistants-ia.csv) garde, une fois par mois, les réponses de
ChatGPT, Copilot, Perplexity, Gemini et Claude à une liste fixe de questions (« Qui est
Karl Forterre ? », « Qu'est-ce que la médiation auctoriale ? »…), pour voir s'ils citent
le site photo, karlforterre.fr ou Pexels. Une ligne par question et par assistant :

- `date` : au format AAAA-MM-JJ ;
- `assistant` : ChatGPT, Copilot, Perplexity, Gemini, Claude… ;
- `question` : la question posée, telle quelle ;
- `cite` : `oui` si la réponse ou ses sources mentionnent le site, karlforterre.fr ou
  Pexels, `non` sinon ;
- `source` : l'adresse citée, s'il y en a une ;
- `remarque` : une erreur à corriger, un détail notable.

Liste des questions et démarche : [referencement/README.md](../referencement/README.md),
partie 5.
