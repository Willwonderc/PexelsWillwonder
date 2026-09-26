# Plan : un site de photographe professionnel qui mène à Pexels

Feuille de route rédigée le 25 septembre 2026. Point de départ :
- site en ligne sur https://photos.karlforterre.fr, avec 723 photos et 14 galeries, en français et en anglais ;
- 15 flux Pinterest reliés à leurs tableaux ;
- profil Pexels : 878 500 vues et 19 abonnés au 24 septembre ;
- fiche de suivi du 24 septembre (`releves/suivi-pexels.csv`) : 3 950 téléchargements et
  89 photos retenues par la modération de Pexels, sur 919 ;
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
| Téléchargements, photos retenues, photos les plus vues | fiche de suivi, déposée dans `releves/` |

## Ce que montre la fiche de suivi

Relevé du 24 septembre 2026, photo par photo :
- **La modération fait les vues.** Les 89 photos retenues (10 %) totalisent 81 % des vues :
  7 962 vues en moyenne, contre 204 pour les 830 refusées, qui restent visibles dans la
  galerie du profil sans être mises en avant.
- **Sans titre, aucune chance.** Aucune des 351 photos importées sans vrai titre
  (« Free stock photo of… » ou rien) n'a été retenue, contre 89 des 568 photos titrées (16 %).
- **Ça progresse.** Part des photos retenues par année d'import : aucune en 2021, 2 à 3 %
  de 2022 à 2024, 9 % en 2025, 23 % en 2026.
- **Quelques photos portent le compte.** Les 10 plus vues font 44 % des vues.

D'où trois conséquences :
1. Le premier levier des vues Pexels est la modération : ne rien importer sans titre ni
   mots-clés préparés par l'atelier, et choisir les photos d'après ce qui est retenu
   (analyse confiée à la session D).
2. Pour les 830 photos refusées, le site et Pinterest sont la seule vitrine.
3. La sélection, l'ordre des épingles et la photo du jour partent des photos les plus vues.

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
- Une rubrique « Sélection » de 24 photos, choisies parmi les plus vues et les plus
  téléchargées de la fiche de suivi, réglée dans un fichier `vitrine/selection.txt`.
- Preuve sociale : « 878 500 vues et 3 950 téléchargements sur Pexels », tirés des
  derniers relevés de `releves/`, à côté du bouton « Suivre sur Pexels ».

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
Fait en session B (25 septembre 2026) : journal des parutions, 19 nouvelles galeries
(33 en tout), chaque photo publiée rangée dans au moins une, pages par couleur et photos
proches.
- **Journal des parutions**, avant tout reclassement. Aujourd'hui, le compte-gouttes
  calcule la date de chaque épingle d'après le rang de la photo dans son flux. Une
  photo ajoutée à une galerie, ou une photo sans titre qui en reçoit un, change ces
  rangs : elle peut être sautée, et en décaler d'autres. Un fichier
  `vitrine/donnees/parutions.json`, tenu par la tâche de nuit comme `fiches.json`,
  fixera la date de chaque épingle une fois pour toutes. La file passera alors les
  nouvelles photos en tête, puis le fonds par vues décroissantes.
- 507 photos ne sont dans aucune galerie ; 506 d'entre elles ont des mots-clés Pexels
  dans la fiche de suivi, qui serviront à les classer. Il faut les classer d'après leurs titres et
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
- Logo KF’ : `vitrine/statique/logo.svg`, vectorisé d'après l'original (couleur du texte,
  `currentColor`), pour l'en-tête et l'icône du site ; version texturée d'origine :
  `vitrine/statique/logo-kf.webp`.
- Page « À propos » : portrait, courte biographie, matériel, lieux favoris, contact.

### 7. Référencement
- Google Search Console : propriété « domaine » karlforterre.fr, validée par un
  enregistrement TXT chez OVH, puis déclaration du plan du site. Bing Webmaster Tools
  peut ensuite importer cette configuration.
- Traduire en français les titres encore en anglais.
- Un texte unique de 150 à 300 mots par galerie (fait en session B).
- Fil d'Ariane (données structurées BreadcrumbList) et liens internes entre photos proches
  (faits en session B).

### 8. Qualité et obligations
- **Mentions légales**, obligatoires en France pour un site professionnel :
  éditeur, contact et hébergeur (GitHub, Inc., 88 Colin P. Kelly Jr. Street,
  San Francisco, États-Unis).
- Page « Confidentialité » : GoatCounter, sans cookies, donc sans bandeau.
- Accessibilité et vitesse : viser au moins 95 aux mesures Lighthouse.

## Promotion

### Automatique, sans crédit
- **Pinterest** : fait. Un flux par galerie (34 avec « More photos »), une photo de plus
  par galerie et par nuit, d'après le journal des parutions. Plus tard,
  des visuels verticaux (format 2:3) avec un titre, qui attirent davantage de clics.
- **Bluesky et Mastodon, ou Pixelfed** (réseau de photographes compatible avec
  Mastodon) : fait (session E). Une « photo du jour » publiée chaque matin par la tâche
  GitHub, avec un lien vers sa page ; mode d'emploi : `reseaux/README.md`. Gratuit, et possible avec un mot de passe d'application ou un jeton
  rangé dans les secrets du dépôt.
- **Instagram vers Pinterest** : Pinterest peut republier automatiquement les
  publications d'un compte Instagram relié, si l'option est proposée dans ses
  paramètres (son emplacement varie selon les versions).

### Durée du compte-gouttes Pinterest
Depuis la session B, le journal `vitrine/donnees/parutions.json` fixe le jour de chaque
épingle (règles dans `pinterest/README.md`). Les 723 photos publiées, rangées dans
33 galeries, donnent 1 183 épingles (dont 164 parues le premier jour), une photo pouvant
figurer dans plusieurs galeries.
Prévision du 25 septembre 2026, sans nouvelle photo et avec les réglages actuels (une
épingle par galerie et par nuit, 6 le premier jour d'un nouveau flux) :

| Flux | Photos | Dernière épingle |
|---|---|---|
| Mariage, Bordeaux | 7, 6 | déjà toutes parues le 25 septembre |
| Asturies, Pays basque, Chemin de Saint-Jacques, Transports | 11, 13, 15, 11 | 27 septembre au 1er octobre |
| Paris, Normandie et Bretagne, Vosges, Ciel et astrophotographie | 12, 13, 15, 21 | 2 au 5 octobre |
| Jardins de la Loire, Charente, Cuisine, Galice, Mer et littoral | 24, 17, 20, 29, 25 | 7 au 14 octobre |
| Nuages, Objets, Niort et Poitou, Val de Loire, Paysages, Pyrénées | 28 à 47 | 17 au 30 octobre |
| Portraits, Églises, Fonds abstraits, Scènes de vie, Rivières | 43 à 55 | 1er au 13 novembre |
| Villes, Animaux, Noir et blanc, Fleurs et macro | 62 à 71 | 21 au 28 novembre |
| Arbres et forêts, Architecture et patrimoine | 79, 96 | 7 et 24 décembre |

Environ 30 épingles par jour, 96 le lendemain de la bascule, jamais plus de 200. Les
nouvelles photos entrent aussitôt dans leurs flux ; les photos titrées par la session D
entrent dans les files sans décaler les parutions passées. Calendrier à jour :
`python3 pinterest/epingles.py --calendrier`.

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
| karlforterre.fr (site d'auteur) | le lien le plus utile : le site principal recommande le site photo | fait : sa section Photographie montre la sélection, les séries et les galeries du site photo (apercu.json), chaque photo ouvrant sa page |
| Flickr | communauté photo, groupes par lieu et par thème | compte gratuit (nombre de photos limité) : les meilleures, avec le lien vers leur page Pexels |
| 500px | communauté de photographes, paysages | compte gratuit, quelques photos par semaine |
| Behance | relié à Adobe Portfolio | une série par projet, avec le lien vers le site |
| Pixelfed, Bluesky, Mastodon | réseaux ouverts, sans algorithme payant | automatique : photo du jour ([reseaux/](../reseaux/README.md)) |
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
| Cette semaine | Vous | Créer GoatCounter et Search Console, lien du profil Pexels vers le site, lien depuis karlforterre.fr |
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
