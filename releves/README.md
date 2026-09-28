# 4 — Relevés pour le tableau de bord

Le tableau de bord se lit sur **https://photos.karlforterre.fr/tableau-de-bord/**, à garder
dans ses favoris : aucune page du site n'y mène, et les moteurs de recherche ne l'indexent
pas. Il reste public pour qui connaît l'adresse, et ne montre donc rien de confidentiel. Il
se met à jour chaque nuit, et quelques minutes après chaque relevé enregistré sur GitHub :

- **Pexels** : vues, abonnés, téléchargements, J'aime et photos retenues, semaine après
  semaine, en chiffres et en courbes ;
- **Photos** : les dix plus vues et leur gain de la semaine, les photos nouvellement
  retenues, et toutes les photos, avec recherche, filtres et tri, comme dans Telepex ;
- **Site photo** : visites, provenance (Google, Pinterest, assistants IA…), pages les plus
  vues et clics vers Pexels, d'après GoatCounter ;
- **Pinterest** et **assistants IA**, d'après les relevés ci-dessous ;
- en tête, un rappel pour chaque relevé en retard (plus de huit jours, ou plus d'un mois
  pour les assistants IA).

L'historique des relevés, `vitrine/donnees/historique.json`, est tenu par la tâche de nuit :
les totaux de chaque relevé, les chiffres photo par photo des cinq dernières semaines (pour
les gains de la semaine et du mois) et les semaines de GoatCounter.

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

Ce relevé alimente le tableau de bord et le compteur de la barre des menus du Mac.

Chaque relevé compte aussi comme une activité du dépôt. GitHub suspend les tâches
planifiées d'un dépôt public resté 60 jours sans activité : un relevé par semaine garde
donc en marche la reconstruction nocturne du site.

## Statistiques Pinterest, chaque semaine

Pinterest n'offre son API qu'aux applications qu'il a approuvées, avec un jeton à renouveler
au moins tous les 60 jours et 90 jours d'historique au plus : un relevé à la main, une fois
par semaine, reste le plus simple. Sur Pinterest, ouvrir Statistiques → Vue d'ensemble,
choisir les 7 derniers jours, puis, sur GitHub, ouvrir [pinterest.csv](pinterest.csv),
cliquer sur le crayon, ajouter une ligne à la fin et « Commit changes ». Exemple de ligne,
chiffres fictifs :

    2026-10-05,6900,170,44,30,6,deux nouveaux tableaux

- `date` : au format AAAA-MM-JJ ;
- `impressions`, `engagements`, `clics_sortants` (vers le site), `enregistrements` : les
  chiffres des 7 derniers jours ;
- `abonnes` : facultatif ;
- `remarque` : facultative.

## Relier GoatCounter, une fois

GoatCounter compte les visites du site et les clics vers Pexels depuis le 28 septembre 2026
(https://karlforterre.goatcounter.com). Pour que le tableau de bord les affiche, il lui faut
une clé d'API qui ne sert qu'à lire les statistiques :

1. Sur https://karlforterre.goatcounter.com, cliquer sur son nom d'utilisateur, en haut, puis
   sur **API**.
2. Dans l'encadré **Add new API Token** : un nom (**Name**), par exemple « tableau de
   bord » ; dans **Permissions**, ne cocher que **Read statistics** ; puis **Add new**.
   Copier la clé qui apparaît dans la liste **API tokens**.
3. Sur GitHub, dépôt Willwonderc/PexelsWillwonder : **Settings** → **Secrets and
   variables** → **Actions** → **New repository secret**. Nom : `GOATCOUNTER_JETON` ; valeur :
   la clé copiée ; puis **Add secret**.
4. Onglet **Actions** → **Site** → **Run workflow**, ou attendre la nuit : la section « Site
   photo » du tableau de bord se remplit.

Ne jamais coller cette clé dans une conversation, un fichier du dépôt ou un message : le
secret de GitHub suffit. Si GoatCounter la refuse un jour, le tableau de bord le signale en
tête, et le reste du site se construit comme d'habitude.

## Compteur dans la barre des menus du Mac

Chaque passage publie aussi
[https://photos.karlforterre.fr/tableau-de-bord/compteur.json](https://photos.karlforterre.fr/tableau-de-bord/compteur.json) :
vues Pexels et leur progression depuis le relevé précédent, abonnés, téléchargements,
J'aime et photos retenues, avec la date de chaque relevé, puis visites et clics vers Pexels
des 7 derniers jours. Le petit programme de [barre-des-menus/](barre-des-menus/README.md)
le relit toutes les heures et affiche le nombre de vues dans la barre des menus du
MacBook, avec le détail au clic (installation pas à pas dans son mode d'emploi).

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
