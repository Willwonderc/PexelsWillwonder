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
- **Moteurs de recherche** : pour photos.karlforterre.fr et pour karlforterre.fr, Google
  (recherche web et Google Images à part) et Bing côte à côte : clics, impressions, taux de
  clic et position moyenne sur 28 jours et semaine après semaine, les dix recherches et les
  dix pages qui amènent le plus de clics, d'après Google Search Console et Bing Webmaster
  Tools ;
- **Pinterest** et **assistants IA**, d'après les relevés ci-dessous ;
- en tête, un rappel pour chaque relevé en retard (plus de huit jours, ou plus d'un mois
  pour les assistants IA).

L'historique des relevés, `vitrine/donnees/historique.json`, est tenu par la tâche de nuit :
les totaux de chaque relevé, les chiffres photo par photo des cinq dernières semaines (pour
les gains de la semaine et du mois), et les semaines de GoatCounter, de Google et de Bing.

[vues-pexels.csv](vues-pexels.csv) rassemble le total de vues Pexels, une ligne par
relevé : l'API Pexels ne fournit pas ce chiffre, et ni ce dépôt ni ses tâches ne relèvent
aucune statistique sur pexels.com. Depuis le 28 septembre 2026, Telepex, l'application Mac
de Karl, y ajoute lui-même une ligne à chaque relevé (session T des
[consignes](../consignes/prochaines-sessions.md)) ; une ligne peut aussi se noter à la main.

## Fiche de suivi, photo par photo

[suivi-pexels.csv](suivi-pexels.csv) reprend la fiche de suivi de Karl (classeur
« Suivi des photos Pexels » écrit par Telepex), une ligne par photo, de la plus vue à la
moins vue :

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

Telepex remplace lui-même ce fichier à chaque relevé, chaque semaine ou chaque jour,
depuis le 28 septembre 2026, avec une colonne de plus, `releve` (date et heure du relevé).
Si Telepex ne peut pas publier, déposer à sa place un fichier au même format et au même
nom (Add file → Upload files), en UTF-8. Le dépôt est public : il
ne reçoit que le relevé, jamais Telepex lui-même.

## Ajouter un relevé

Sur GitHub, ouvrir `vues-pexels.csv`, cliquer sur le crayon, ajouter une ligne à la fin,
puis « Commit changes ». Exemple de ligne, chiffres fictifs :

    2026-10-01,880000,920,20,épingles Pinterest lancées

- `date` : au format AAAA-MM-JJ ;
- `vues` : total de vues affiché par Pexels, sans espaces ;
- `photos` et `abonnes` : facultatifs, laisser vide au besoin ;
- `remarque` : facultative, pour noter un événement de la semaine.

Telepex ajoute lui-même sa ligne à chaque relevé (remarque « Telepex ») : ne noter à la
main que ce qu'il ne relève pas.

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

## Relier Google Search Console et Bing Webmaster Tools

La rubrique « Moteurs de recherche » du tableau de bord lit chaque nuit, en lecture seule,
les chiffres de Google Search Console et de Bing Webmaster Tools pour les deux sites. Il lui
faut deux accès, rangés dans les secrets du dépôt : la clé d'un « compte de service » Google,
une sorte d'utilisateur réservé aux programmes, et la clé d'API de Bing. Compter vingt
minutes. Au préalable, les deux sites doivent être dans Bing Webmaster Tools :
[referencement/README.md](../referencement/README.md), partie 1 (import depuis Search Console).

Ne jamais coller ces clés dans une conversation, un fichier du dépôt ou un message : les
secrets de GitHub suffisent.

### A. Google : le compte de service

1. **Projet.** Ouvrir https://console.cloud.google.com avec le compte Google de Search
   Console (accepter les conditions à la première visite). En haut, cliquer sur le
   sélecteur de projet, puis **Nouveau projet** : nom `tableau-de-bord-photos`, laisser
   « Aucune organisation », **Créer**. Aucune facturation n'est demandée : ces API sont
   gratuites.
2. **Deux API.** Le nouveau projet choisi en haut de la page, ouvrir tour à tour ces deux
   adresses et cliquer sur **Activer** :
   - https://console.cloud.google.com/apis/library/searchconsole.googleapis.com (« Google
     Search Console API », qui donne les chiffres) ;
   - https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com (« IAM
     Service Account Credentials API », qui fournit chaque nuit un jeton d'accès valable une
     heure).
3. **Compte de service.** Menu ☰ → **IAM et administration** → **Comptes de service** →
   **+ Créer un compte de service**. Nom : `tableau-de-bord` ; **Créer et continuer**. À
   l'étape **Autorisations**, choisir le rôle **Créateur de jetons du compte de service**
   (Service Account Token Creator), exigé par l'action de Google qui produit le jeton ;
   **Continuer**, puis **OK**. Noter l'adresse du compte, de la forme
   `tableau-de-bord@tableau-de-bord-photos.iam.gserviceaccount.com` : elle n'a rien de secret.
4. **Clé.** Cliquer sur le compte → onglet **Clés** → **Ajouter une clé** → **Créer une
   clé** → **JSON** → **Créer**. Un fichier `.json` se télécharge : il vaut un mot de passe.
   Si Google répond que la création de clés est désactivée, c'est que le compte appartient à
   une organisation (Google Workspace) qui l'interdit : en parler à une session Claude.
5. **Search Console.** Sur https://search.google.com/search-console, propriété
   **karlforterre.fr** → **Paramètres** → **Utilisateurs et autorisations** → **Ajouter un
   utilisateur** : coller l'adresse du compte de service, autorisation **Restreinte**
   (« Limitée » selon la traduction), puis **Ajouter**. Un utilisateur restreint voit les
   performances, mais ne peut rien modifier.

### B. Bing : la clé d'API

Sur https://www.bing.com/webmasters, cliquer sur la roue dentée (**Paramètres**), en haut à
droite → **Accès API** → accepter les conditions → **Clé API** → **Générer une clé API**,
puis la copier. Bing ne donne qu'une clé par personne, valable pour tous ses sites ; elle
permet aussi de modifier des réglages (retirer un site, bloquer une page) : à garder comme un
mot de passe. Le tableau de bord ne s'en sert que pour lire.

### C. Les deux secrets

1. Google conseille de ranger la clé JSON sur une seule ligne. Dans le Terminal du Mac,
   taper `tr -d '\n' < ` (avec l'espace final), glisser le fichier `.json` dans la fenêtre,
   taper ` | pbcopy`, puis Entrée : la clé est copiée, sans s'afficher.
2. Sur GitHub, dépôt Willwonderc/PexelsWillwonder : **Settings** → **Secrets and variables**
   → **Actions** → **New repository secret**. Nom : `SEARCH_CONSOLE_CLE` ; valeur : coller
   (⌘V) ; **Add secret**.
3. De même, **New repository secret** : nom `BING_WEBMASTER_CLE`, valeur : la clé de Bing ;
   **Add secret**.
4. Mettre le fichier `.json` à la corbeille et la vider : au besoin, on en crée une autre.
5. Onglet **Actions** → **Site** → **Run workflow**, ou attendre la nuit : la rubrique
   « Moteurs de recherche » se remplit. Si un accès manque, un rappel en tête du tableau de
   bord dit lequel, et renvoie à l'étape de ce mode d'emploi.

**Révoquer un accès** : supprimer la clé dans Google Cloud (compte de service, onglet
**Clés**) ou retirer l'utilisateur dans Search Console ; pour Bing, **Supprimer** dans
**Accès API**. Pour remplacer une clé, recommencer l'étape A4 ou B, puis modifier le secret
(**Update**).

### Ce que montre la rubrique

Pour chaque site, Google et Bing côte à côte :

- **Les 28 derniers jours** : clics, impressions (apparitions dans les résultats), taux de
  clic et position moyenne, pour la recherche web de Google, Google Images et Bing, avec
  l'écart par rapport aux 28 jours d'avant ;
- **les clics par semaine**, en colonnes, pour Google (web et images réunis) et pour Bing ;
- **semaine après semaine**, du lundi au dimanche, les mêmes chiffres, source par source ;
- **les dix recherches et les dix pages** qui amènent le plus de clics.

Bon à savoir, d'après la documentation des deux moteurs (septembre 2026) :

- **Google** donne ses chiffres définitifs en deux à trois jours, en journées de Californie
  (heure du Pacifique) ; la semaine en cours reprend aussi ses chiffres provisoires. Search
  Console ne connaît qu'une propriété, le domaine karlforterre.fr : le tableau de bord lit
  chaque site en filtrant ses pages, et Google compte alors page par page, comme Search
  Console quand on y filtre par page. Il tait les recherches trop rares, par respect de la
  vie privée. Quota : 1 200 demandes par minute pour un site ; la tâche en fait douze à
  chaque passage.
- **Bing** donne ses clics et ses impressions jour par jour, toutes recherches confondues
  (web, images, vidéos, actualités, Copilot), et met à jour ses recherches et ses pages
  chaque semaine : la position moyenne et les listes portent sur ses quatre dernières
  semaines. Aucun quota n'est publié ; la tâche fait sept demandes à chaque passage.
  Microsoft ne documente pas l'échelle de ses positions : le tableau de bord les divise par
  10, comme le font ceux qui se servent de l'API ; si elles paraissent dix fois trop petites
  à côté de Bing Webmaster Tools, le signaler à une session Claude (réglage `BING_POSITION`
  de `vitrine/build.py`).
- **Les citations dans Copilot** (rapport AI Performance) ne sont pas encore dans l'API de
  Bing : elles se lisent sur Bing Webmaster Tools, une fois par mois
  ([referencement/README.md](../referencement/README.md), partie 5).

La rubrique n'est qu'un résumé : Search Console et Bing Webmaster Tools gardent seize mois
d'historique et le détail (pays, appareils, recherche par recherche).

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
