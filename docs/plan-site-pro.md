# Plan : un site de photographe professionnel qui mène à Pexels

Feuille de route rédigée le 25 septembre 2026. Point de départ :
- site en ligne sur https://photos.karlforterre.fr, avec 723 photos et 14 galeries, en français et en anglais ;
- 15 flux Pinterest reliés à leurs tableaux ;
- profil Pexels : 878 500 vues et 19 abonnés au 24 septembre ;
- 185 $ de crédit de sessions cloud, jusqu'au 5 novembre.

## Objectif et mesures

Faire du site la vitrine de référence de Karl Forterre, et que chaque visite se termine
sur Pexels, par une vue, un téléchargement ou un abonnement.

Chaque semaine, on relève cinq chiffres :

| Indicateur | Où le lire |
|---|---|
| Vues et abonnés Pexels | profil Pexels, noté dans `releves/vues-pexels.csv` |
| Clics du site vers Pexels | GoatCounter (événements `pexels-…`, `suivre-pexels`) |
| Apparitions et clics dans Google | Google Search Console |
| Impressions et clics sortants | statistiques Pinterest |
| Pages les plus vues | GoatCounter |

## Ce que font les meilleurs sites de photographes

- **Une ouverture forte** : une grande image, le nom, une phrase. Pas de texte d'accueil
  à rallonge.
- **Moins, mais le meilleur** : une sélection mise en avant, le reste rangé derrière.
- **Des séries racontées** : chaque projet a un titre, un lieu, une date et quelques
  lignes d'histoire. C'est ce que les visiteurs retiennent, et ce que Google indexe le
  mieux.
- **Une visionneuse immersive** : plein écran, navigation au clavier et au doigt,
  interface qui s'efface devant la photo.
- **Une identité** : logo, typographie, ton de la page « À propos », portrait de l'auteur.
- **Un seul appel à l'action**, clair et répété. Ici : télécharger sur Pexels, suivre sur
  Pexels.

## Chantiers du site

### 1. Ouverture et sélection
- Accueil en plein écran : une photo phare (ou un fondu lent entre 6 à 8 photos), le
  nom, l'accroche et le bouton « Voir les galeries ».
- Une rubrique « Sélection » de 24 photos choisies à la main, réglée dans un fichier
  `vitrine/selection.txt`.
- Preuve sociale : « 878 500 vues sur Pexels », tiré du dernier relevé de
  `releves/vues-pexels.csv`, à côté du bouton « Suivre sur Pexels ».

### 2. Séries racontées
Six à huit pages de séries, chacune avec 150 à 300 mots en français et en anglais :
éclipse totale de Soleil en Galice (août 2026), jardins de Villandry, Universidad
Laboral de Gijón, côte des Cathédrales à Ribadeo, chemin de Saint-Jacques en Béarn, Pic
du Midi d'Ossau, nuits étoilées. Ce sont les meilleures pages d'entrée depuis Google,
par exemple sur « photos éclipse 2026 libres de droits ».

### 3. Visionneuse plein écran
Clic sur une vignette : la photo s'ouvre en plein écran, avec photo suivante et
précédente, le titre et le bouton Pexels toujours visibles. Le tout en JavaScript
léger, sans bibliothèque, avec l'adresse de la page de la photo mise à jour pour le
partage.

### 4. Toutes les photos rangées
- **Journal des parutions**, avant tout reclassement. Aujourd'hui, le compte-gouttes
  calcule la date de chaque épingle d'après le rang de la photo dans son flux. Une
  photo ajoutée à une galerie, ou une photo sans titre qui en reçoit un, change ces
  rangs : elle peut être sautée, et en décaler d'autres. Un fichier
  `vitrine/donnees/parutions.json`, tenu par la tâche de nuit comme `fiches.json`,
  fixera la date de chaque épingle une fois pour toutes.
- 507 photos ne sont dans aucune galerie. Il faut les classer d'après leurs titres et
  textes, et créer les galeries qui manquent : villes, nature, portraits, intérieurs,
  cuisine, animaux, etc. Objectif : chaque photo dans au moins une galerie.
- Pages « par couleur » (bleu, vert, noir et blanc, tons chauds…), calculées à partir
  de la couleur dominante fournie par Pexels. Les graphistes cherchent souvent ainsi.
- « Photos proches » sur chaque page, d'après les mots-clés communs.

### 5. Tout mène à Pexels
Existe déjà : image et bouton vers la page Pexels, « Suivre sur Pexels » en tête de page.
- Ajouter une page « Utiliser mes photos » : la licence Pexels expliquée simplement,
  gratuite et sans inscription. Rassurer, c'est augmenter les téléchargements.
- Rappel « Suivre sur Pexels » en fin de galerie et en fin de série.

### 6. Identité et page auteur
- Reprendre le logo KF’ du site karlforterre.fr (en-tête et icône), à fournir en SVG.
- Page « À propos » : portrait, courte biographie, matériel, lieux favoris, contact.

### 7. Référencement
- Google Search Console : propriété « domaine » karlforterre.fr, validée par un
  enregistrement TXT chez OVH, puis déclaration du plan du site. Bing Webmaster Tools
  peut ensuite importer cette configuration.
- Traduire en français les titres encore en anglais.
- Un texte unique de 150 à 300 mots par galerie.
- Fil d'Ariane (données structurées BreadcrumbList) et liens internes entre photos proches.

### 8. Qualité et obligations
- **Mentions légales**, obligatoires en France pour un site professionnel :
  éditeur, contact et hébergeur (GitHub, Inc., 88 Colin P. Kelly Jr. Street,
  San Francisco, États-Unis).
- Page « Confidentialité » : GoatCounter, sans cookies, donc sans bandeau.
- Accessibilité et vitesse : viser au moins 95 aux mesures Lighthouse.

## Promotion

### Automatique, sans crédit
- **Pinterest** : fait. 15 flux, une photo de plus par galerie et par nuit. Plus tard,
  des visuels verticaux (format 2:3) avec un titre, qui attirent davantage de clics.
- **Bluesky et Mastodon, ou Pixelfed** (réseau de photographes compatible avec
  Mastodon) : une « photo du jour » publiée chaque matin par la tâche GitHub, avec un
  lien vers sa page. Gratuit, et possible avec un mot de passe d'application ou un jeton
  rangé dans les secrets du dépôt.
- **Instagram vers Pinterest** : Pinterest peut republier automatiquement les
  publications d'un compte Instagram relié, si l'option est proposée dans ses
  paramètres (son emplacement varie selon les versions).

### Durée du compte-gouttes Pinterest
Sans nouvelle photo et avec les réglages actuels (12 épingles par flux le premier jour,
puis chaque nuit une par galerie et trois pour « More photos »), les 723 photos
publiées donnent 799 épingles, une photo pouvant figurer dans plusieurs galeries :

| Flux | Photos | Dernière épingle |
|---|---|---|
| Pays basque, Asturies, Mariage, Bordeaux | 10, 9, 7, 6 | 25 septembre 2026 (premier jour) |
| Chemin de Saint-Jacques | 16 | 29 septembre |
| Ciel et astrophotographie | 18 | 1er octobre |
| Niort et Poitou | 20 | 3 octobre |
| Portraits | 22 | 5 octobre |
| Fonds abstraits | 24 | 7 octobre |
| Noir et blanc | 26 | 9 octobre |
| Galice | 27 | 10 octobre |
| Jardins des châteaux de la Loire | 30 | 13 octobre |
| Pyrénées | 35 | 18 octobre |
| Fleurs et macro | 42 | 25 octobre |
| More photos (photos rangées dans aucune galerie) | 507 | 9 mars 2027 |

Le premier jour compte 164 épingles, sous le plafond de 200. Les galeries sont épuisées
le 25 octobre 2026 ; les photos hors galerie continuent, trois par nuit, jusqu'au
9 mars 2027. Ensuite, seules les nouvelles photos alimentent Pinterest. Ce calendrier
change si :
- de nouvelles photos arrivent : elles entrent aussitôt, sans décaler les autres ;
- les galeries sont réorganisées (session B) ou les photos sans titre titrées
  (session D) : d'où le journal des parutions du chantier 4, à installer d'abord ;
- le rythme change (`epingles_par_jour_autres` dans `vitrine/site.ini`), ce qu'il vaut
  mieux faire une fois le journal en place. À une photo par nuit, « More photos »
  durerait jusqu'en février 2028.

### Réseaux avec connecteur : X, Threads, LinkedIn, Instagram
Des connecteurs claude.ai permettent de programmer des publications : **Typefully**
(X, Threads, LinkedIn, Bluesky, Mastodon) et **Metricool** (réseaux dont Instagram et
Pinterest). Une fois l'un d'eux connecté sur https://claude.ai/customize/connectors, une
session peut préparer et programmer un mois de publications en une fois. Leurs offres
gratuites ont des limites, à vérifier avant de choisir.

### Communautés et forums : à la main, jamais en automatique
Publier automatiquement sur des forums relève du spam et mène au bannissement. Les
sessions peuvent en revanche préparer les textes, que vous publiez vous-même :
- Reddit : r/astrophotography (éclipse, Voie lactée), r/EarthPorn (paysages, sans
  filigrane), r/itookapicture, r/france ;
- groupes Flickr des lieux photographiés ;
- forums photo francophones, en participant avant de partager ses liens.

### Pexels même
- Lien du profil vers https://photos.karlforterre.fr, et biographie à jour.
- **Concours Pexels** : participer à chaque concours adapté. C'est la visibilité la plus
  directe sur la plateforme.
- Collections publiques sur le profil, une par série, avec ses propres photos.
- Publier régulièrement (1 à 3 photos par semaine), toujours avec titre et mots-clés
  préparés par l'atelier.

### Relais extérieurs
- **Offices de tourisme et lieux photographiés** (château de Villandry, Gijón, Galice,
  vallée d'Ossau) : leur signaler des photos gratuites et de qualité. Ils les partagent
  volontiers, avec un lien.
- **Presse locale** (Poitiers, Niort) : un sujet « photographe local, 900 000 vues ».
- **Wikimedia Commons** : verser quelques photos de lieux connus sous licence libre
  (CC BY-SA, crédit au nom de l'auteur). Utilisées dans Wikipédia, elles apportent une
  visibilité durable. Le choix de la licence vous revient.

### Autres plateformes

| Plateforme | Intérêt | Comment |
|---|---|---|
| karlforterre.fr (Adobe Portfolio) | le lien le plus utile : le site principal recommande le site photo | un lien « Photos libres de droits » dans son menu |
| Flickr | communauté photo, groupes par lieu et par thème | compte gratuit (nombre de photos limité) : les meilleures, avec le lien vers leur page Pexels |
| 500px | communauté de photographes, paysages | compte gratuit, quelques photos par semaine |
| Behance | relié à Adobe Portfolio | une série par projet, avec le lien vers le site |
| Pixelfed, Bluesky, Mastodon | réseaux ouverts, sans algorithme payant | automatique (session E) |
| Instagram | la plus grande audience photo | à la main ou par Metricool |
| X, Threads, LinkedIn | audience générale et professionnelle | par le connecteur Typefully |
| Groupes Facebook | groupes locaux (Poitou, Pays basque, Galice) et de photographes | à la main, selon les règles de chaque groupe |
| Reddit, forums photo | grandes audiences par sujet | à la main, en participant plus qu'en publiant ses liens |
| YouTube Shorts, TikTok, Reels | diaporamas courts des séries | à la main |
| Wikimedia Commons | photos de lieux reprises dans Wikipédia | licence libre au choix de l'auteur |
| Offices de tourisme, presse locale, clubs photo | relais locaux, liens depuis des sites reconnus | courriels préparés par une session |
| Unsplash, Pixabay | aucun | à éviter : ils détourneraient les téléchargements de Pexels |

## Calendrier et crédit

| Quand | Qui | Quoi |
|---|---|---|
| Cette semaine | Vous | Relier le flux « More photos », créer GoatCounter et Search Console, lien du profil Pexels vers le site, lien depuis karlforterre.fr |
| Semaine du 29 sept. | Session A | Site pro : ouverture, sélection, visionneuse, séries, pages légales, preuve sociale |
| Début octobre | Session B | Journal des parutions, classement des 507 photos, nouvelles galeries, pages par couleur, textes des galeries |
| Mi-octobre | Session C | Traduction française d'environ 517 titres |
| Mi-octobre | Session D | Atelier : titres des 196 photos sans titre |
| Fin octobre | Session E | Photo du jour sur Bluesky et Mastodon ou Pixelfed ; Typefully si connecté |
| Fin octobre | Session F | Tableau de bord (chantier 4 de `docs/plan.md`) |

Chaque session s'ouvre **dans une nouvelle session**, qui coûte bien moins cher qu'une
longue conversation : `CLAUDE.md` lui donne le contexte. Une seule à la fois, et sa pull
request fusionnée avant la suivante. Après la session A, la jauge de crédit indique le
coût réel, de quoi ajuster la suite.

## Consignes prêtes à coller

Les consignes des sessions A à F, avec leur ordre et leurs prérequis, sont dans
[consignes/prochaines-sessions.md](../consignes/prochaines-sessions.md).
