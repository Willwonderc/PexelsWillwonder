# Contexte pour les sessions Claude

Ce fichier est chargé automatiquement au début de chaque session : il évite de
réexpliquer le projet dans les consignes.

## Projet

Promotion des photos de Karl Forterre publiées sur Pexels
(https://www.pexels.com/@karl-forterre-28489473). Point de départ, septembre 2026 :
919 photos, environ 878 500 vues, 19 abonnés. Des sessions Claude Code construisent,
avant le 5 novembre 2026, quatre outils qui tournent ensuite seuls et gratuitement sur
GitHub. Plan complet : `docs/plan.md` ; feuille de route du site et de la promotion :
`docs/plan-site-pro.md` ; consignes des sessions : `consignes/`.

1. Site de photographe (`vitrine/`) : site statique en français, anglais et chinois
   (`/zh/`) sur GitHub Pages, pensé pour le référencement, avec une page par photo,
   des galeries par thème et par lieu (chaque photo publiée dans au moins une) et des
   pages par couleur. `vitrine/build.py`
   (Python sans dépendance) lit `vitrine/photos.txt`, complète le cache
   `vitrine/donnees/fiches.json` par l'API et écrit `_site/` ; la tâche
   `.github/workflows/site.yml` le relance chaque nuit. Mode d'emploi : `vitrine/README.md`.
2. Pinterest (`pinterest/`) : un flux RSS par galerie, relié à son tableau, et « Photos by
   Karl Forterre » pour les photos hors galeries. Le journal `vitrine/donnees/parutions.json`,
   tenu par la tâche de nuit, fixe le jour de chaque épingle : nouvelles photos en tête,
   fonds par vues décroissantes, une seule parution par tableau, 200 par jour au plus
   (réglages dans `vitrine/site.ini`). Calendrier et fichiers d'import : `pinterest/epingles.py`.
3. Atelier titres et mots-clés (`atelier/`) : photos reçues par lien SwissTransfer (ou
   déposées dans `atelier/a-traiter/`), tableaux rendus dans `atelier/resultats/`.
4. Tableau de bord (`releves/` et une page non référencée du site) : clics vers Pexels,
   statistiques Pinterest, vues et téléchargements Pexels tirés des relevés de Karl.

## Façon de travailler

- Échanger en français, même quand les contenus sont en chinois ou en anglais. Textes
  du site en français, en anglais et en chinois.
- Documentation en français. Les « LISEZMOI » demandés sont des `README.md`.
- Tout doit rester simple à utiliser et à maintenir sans compétences de développement :
  peu de dépendances, aucun service payant, modes d'emploi pas à pas.
- S'en tenir à la consigne de la session : le crédit est un budget compté.

## Ligne éditoriale des textes

- **Politique** : Karl est communiste. Aucun texte (carrousels, vidéos, séries, galeries,
  titres) ne doit laisser croire à une sympathie monarchiste, conservatrice ou de droite.
  Un monument ou un lieu chargé d'histoire se présente par ce qu'il célèbre de
  républicain, de populaire ou d'ouvrier, avec le contexte utile, sans jamais célébrer
  rois, Girondins ou dictatures. Ainsi le monument dit « aux Girondins », à Bordeaux,
  figure le Triomphe de la République et de la Concorde (ses bronzes, déposés en 1943
  pour être fondus au profit de l'occupant, n'ont été remis en place qu'en 1983) ; et
  l'Universidad Laboral de Gijón a été bâtie par le régime franquiste.
- **Public français** (vidéos, Facebook personnel) : ne pas mettre en avant le
  « photographe français » ni les « en France, on… », que Karl trouve peu sérieux ; dire
  « Maëlle », pas « ma fiancée ».
- **Instagram** : toutes les publications en français, dans un style proche de
  l'expression de Karl (guide `reseaux/style-karl.md`, tiré de ses propres textes) ; les
  règles du public français s'y appliquent.
- **Musique des vidéos** : libre de droits (CC0 de préférence ; CC BY ou CC BY-SA avec le
  crédit exigé), en privilégiant les morceaux les plus employés dans la publicité et les
  médias (grands classiques, pop instrumentale connue).
- `main` est la branche publiée ; chaque session travaille sur sa branche et propose
  une pull request vers `main`.

## Règles impératives

- **Secret** : la clé Pexels n'apparaît jamais dans le code, les journaux ni
  l'historique. En session : variable d'environnement `PEXELS_API_KEY` ; dans GitHub
  Actions : secret du dépôt `PEXELS_API_KEY`. Le dépôt est public : tout ce qui est
  poussé est visible de tous.
- **API Pexels** : lire la fiche de chaque photo par le point d'accès « Photo »
  (`GET https://api.pexels.com/v1/photos/:id`), à partir de la liste
  `vitrine/photos.txt`. Respecter les limites de débit, afficher « Photos provided
  by Pexels » avec un lien, et vérifier la documentation officielle avant d'implémenter.
- **Conditions Pexels** : chaque photo renvoie vers sa page Pexels, sans téléchargement
  direct ; ne pas reproduire les fonctions de base de Pexels ; aucune collecte
  automatique sur pexels.com hors de l'API officielle, ni par les outils du dépôt, ni par
  ses tâches GitHub, ni en session. Les vues et les téléchargements, que l'API ne fournit pas, viennent des
  relevés de Karl, `releves/vues-pexels.csv` et `releves/suivi-pexels.csv` : notés à la
  main, ou publiés par Telepex, son application Mac, qui reste hors du dépôt (session T
  de `consignes/prochaines-sessions.md`).
- **Vues Pexels** : Pexels compte une vue quand la photo apparaît dans ses résultats
  de recherche ou chez ses partenaires de l'API. Le site et Pinterest renvoient donc
  chaque photo vers sa page Pexels. Aucun procédé artificiel : ni appels répétés à
  l'API, ni ouverture automatique de pages.
- **Filigranes** : aucune signature ni filigrane sur un fichier destiné à Pexels ; ils
  sont permis sur les visuels Pinterest.

## Repères techniques

- Adresse du site : https://photos.karlforterre.fr (enregistrement CNAME chez OVH vers
  willwonderc.github.io, domaine personnalisé déclaré dans Settings → Pages). Le
  réglage `adresse` de `vitrine/site.ini` fixe les liens ; zone DNS de karlforterre.fr
  chez OVH.
- Site d'auteur : https://karlforterre.fr, dépôt Willwonderc/karlforterre.fr (site
  statique sur GitHub Pages, qui remplace Adobe Portfolio ; mode d'emploi et bascule du
  domaine dans son README). Sa section Photographie lit chaque visite
  `https://photos.karlforterre.fr/apercu.json`, écrit par `build.py` (sélection avec ses
  titres courts de `selection.txt`, séries, galeries, chiffres) : garder ce fichier et
  son format.
- Publication : GitHub Pages, source « GitHub Actions », depuis `main`.
- Tâches planifiées : cron en UTC ; éviter la minute 0, souvent retardée. GitHub
  désactive les tâches planifiées d'un dépôt public après 60 jours sans activité ; les
  relevés hebdomadaires de `releves/` suffisent à l'éviter s'ils sont tenus.
- Identifiant de photographe Pexels : `28489473` (champ `photographer_id` de l'API).
- Limites constatées de l'API : environ 200 appels par heure (erreur 429 au-delà) et
  20 000 par mois. Garder les fiches des photos en cache et n'interroger que les
  nouvelles.
- Collections (constat du 24 septembre 2026) : les collections existantes sont des
  planches d'inspiration faites de photos d'autres photographes, et l'API n'y a
  renvoyé aucune photo du propriétaire. Le site s'appuie donc sur la liste des photos,
  pas sur les collections.
- Photo du jour : `reseaux/photo_du_jour.py`, lancé chaque matin par
  `.github/workflows/photo-du-jour.yml`, publie sur Bluesky, Mastodon (ou Pixelfed) et
  Instagram la photo la plus vue pas encore publiée ; journal `reseaux/photo-du-jour.json`,
  tenu par cette seule tâche ; langue réglée dans `vitrine/site.ini`, rubrique
  `[photo_du_jour]`. Essai sans publier : `--essai`. Instagram (@karl_forterre, compte
  « Créateur ») : API de Meta avec connexion Instagram, sans Page Facebook ; image
  téléchargée par Instagram à l'adresse images.pexels.com, `fm=jpg` imposant le JPEG
  (sinon AVIF ou WebP selon le client), recadrée au centre entre 4:5 et 1,91:1 ;
  5 hashtags au plus ; légende en français, sans lien (« lien dans la bio »), écrite à
  l'avance dans le style de Karl (`reseaux/legendes-instagram.csv`, ligne
  `langue_instagram` de `site.ini`), sinon le titre français. Jeton de 60 jours renouvelé
  chaque lundi par `.github/workflows/jeton-instagram.yml`, qui réécrit le secret
  `INSTAGRAM_JETON` grâce au jeton GitHub du secret `JETON_GITHUB` ; ne jamais lancer
  `--renouveler-jeton` en session.
- RedNote (小红书) : carrousels préparés en session et envoyés par courriel (avec leur
  paquet de publication pour Telepex, voir plus bas), publiés à la main par Karl sur le
  compte « Soviet Croissant » (rednote ID 26225410141) ; récit de photographe français,
  au ton léger, version française à côté. Règles et souvenirs de
  Karl : `reseaux/README.md`, rubrique « RedNote ». Chaque carrousel rejoint aussi la
  série de son sujet (`vitrine/series.ini`) : le récit dans les trois langues
  (`recit_*`), le petit cours de français sur les pages anglaises et chinoises
  seulement (`francais_en`, `francais_zh`) ; un nouveau sujet reçoit sa série.
- Publications à la main, préparées en session : RedNote et le profil Facebook personnel
  de Karl (carrousels en français, sans mettre en avant le côté français). Chaque
  carrousel peut aussi devenir une vidéo diaporama en chinois, français et anglais, avec
  musique libre de droits : classique en chinois et en anglais, pop en français
  (`reseaux/README.md`, « Vidéos diaporama des carrousels ») ; programme de session
  `reseaux/videos/`, plan pour atteindre le niveau d'une agence `docs/plan-videos.md`.
  Instagram reçoit, lui, la photo du jour automatiquement (voir plus haut). Chaque
  publication à faire à la main part aussi en paquet de publication (`reseaux/paquet.py`,
  format dans `reseaux/README.md`), envoyé comme fichier de la session, jamais dans le
  dépôt : Telepex l'affiche à Karl, qui y valide ce qu'il publie (session U) ; le journal
  `releves/publications.csv` garde ce qui est paru.
- Journal des parutions : seule la tâche GitHub l'enregistre (`build.py
  --enregistrer-parutions`) ; un essai de `build.py` en session le lit sans le modifier.
- Tableau de bord : `/tableau-de-bord/`, page française non référencée (noindex, hors plan du
  site, du journal des pages et de `llms.txt`, sans compteur GoatCounter), écrite par
  `build.py` avec `statique/tableau.css` et `tableau.js` ; mode d'emploi : `releves/README.md`.
  Il lit les relevés de `releves/` et GoatCounter par son API (clé en lecture seule du secret
  `GOATCOUNTER_JETON` ; sans elle, le site se construit quand même). Historique
  `vitrine/donnees/historique.json` (totaux de chaque relevé, photo par photo sur cinq
  semaines, semaines de GoatCounter) : seule la tâche GitHub l'enregistre
  (`--enregistrer-historique`). Il publie aussi `/tableau-de-bord/compteur.json`, que relit toutes
  les heures le compteur de la barre des menus du MacBook M1 de Karl (SwiftBar,
  `releves/barre-des-menus/`) ; il remplace l'écran Turing du plan de départ, que Karl n'a pas.
- Référencement IA (`referencement/README.md`) : `build.py` écrit `llms.txt` et
  `llms-full.txt` (une version par langue), la page « Questions fréquentes »
  (`vitrine/questions.ini`) et les données Person de l'auteur, dont l'identifiant
  `https://karlforterre.fr/#auteur` est partagé avec karlforterre.fr (rubrique
  `[personne]` de `site.ini`). Journal des pages `vitrine/donnees/pages.json` (empreinte
  et date de dernière modification, pour `lastmod` et IndexNow) : seule la tâche GitHub
  l'enregistre (`--indexnow`), puis signale les pages une fois le site en ligne
  (`--envoyer-indexnow`, travail `signaler`). La clé IndexNow de `site.ini` est publique
  par nature. Ne jamais lancer `--envoyer-indexnow` en session : il contacte Bing.
- Galeries : les mots-clés Pexels de la fiche de suivi comptent pour les règles `mots` de
  `vitrine/galeries.ini`, qui les emploient souvent à tort (« portrait » pour un format
  vertical, « pau » ajouté par lots) ; les lignes `ajouter` et `retirer` gardent le
  classement photo par photo fait en session B. Depuis la session I, Niort, Poitiers
  (« Poitiers et son pays pictave ») et le Marais poitevin ont chacun leur galerie de lieu ;
  `[niort-poitou]` est devenue « Marais poitevin » sans changer d'identifiant (adresse et flux
  Pinterest gardés). Classement et raisons : `atelier/resultats/niort-classement.csv` et
  `poitiers-marais-classement.csv`.
- Titres et mots-clés : Pexels ne permet guère de les modifier après publication.
  L'atelier sert donc avant chaque import, et ses tableaux alimentent le site.
- Photos sans titre : leur adresse Pexels ne contient que le numéro
  (`https://www.pexels.com/photo/<numéro>/`) et leur texte alternatif vaut « Free
  stock photo of » suivi des trois premiers mots-clés par ordre alphabétique. Ne pas
  le reprendre tel quel. Les photos titrées ont, elles, un texte alternatif soigné.
  Inventaire des 919 photos : `atelier/inventaire.csv` ; titres rédigés :
  `atelier/resultats/`.
- Envoi de photos par SwissTransfer : la page du lien contient un JSON
  (`<script data-page="app">`) avec les identifiants du lien et du fichier ;
  `GET https://www.swisstransfer.com/api/1/links/<lien>/files/<fichier>` renvoie une
  adresse de téléchargement valable une heure.
- Fiche de suivi : `releves/suivi-pexels.csv` (relevé du 24 septembre 2026, que Telepex
  remplacera à chaque relevé une fois la session T faite) donne pour chaque photo vues,
  téléchargements, J'aime, statut de modération et mots-clés Pexels. Au 24 septembre, les
  89 photos retenues par la modération faisaient 81 % des vues ; aucune photo importée
  sans titre n'a été retenue.
- Usages par des tiers : `vitrine/usages.csv` (sites signalés par Pexels : CNN.com,
  NYTimes.com, Cambridge.org, Dictionary.com, TheFreeDictionary.com ; et la campagne
  « Niort à Gauche », type `campagne`) : page dédiée « Utilisées dans des projets »
  (`/galeries/photos-utilisees/`), présentée comme une exposition (les photos accrochées
  côte à côte à l'ouverture, puis une photo par écran, avec son cartel), et annoncée en
  tête de la page des galeries par un index des noms en très grand, une bande par photo
  où défilent comme au générique les sites qui l'ont utilisée (la photo au survol) ;
  ligne sur la page de chaque photo ; les sites web
  aussi sur l'accueil et en fin de galerie et de série. Noms des sites en texte, sans
  logo ni chiffre d'audience.
- Logo KF’ : `vitrine/statique/logo.svg` (vectorisé, `currentColor`) et
  `vitrine/statique/logo-kf.webp` (original texturé).
- Captures d'écran en session : Chromium ne charge pas les images de
  images.pexels.com à travers le proxy. Intercepter ces requêtes (Playwright,
  `page.route`) et y répondre avec les fichiers téléchargés par curl, qui passe.
