# Contexte pour les sessions Claude

Ce fichier est chargé automatiquement au début de chaque session : il évite de
réexpliquer le projet dans les consignes.

## Projet

Promotion des photos de Karl Forterre publiées sur Pexels
(https://www.pexels.com/@karl-forterre-28489473). Point de départ, septembre 2026 :
919 photos, environ 878 500 vues, 19 abonnés. Des sessions Claude Code construisent,
avant le 5 novembre 2026, quatre outils qui tournent ensuite seuls et gratuitement sur
GitHub. Plan complet : `docs/plan.md` ; consignes des sessions : `consignes/`.

1. Site de photographe (`vitrine/`) : site statique sur GitHub Pages, pensé pour le
   référencement, avec une page par photo et des galeries par thème et par lieu.
   Reconstruit chaque nuit à partir de la liste des photos et de l'API Pexels ; flux
   RSS par galerie, mesure d'audience GoatCounter.
2. Pinterest (`pinterest/`) : épingles créées automatiquement par Pinterest à partir
   des flux RSS du site, et fichiers d'import par tableur pour les photos existantes.
3. Atelier titres et mots-clés (`atelier/`) : photos reçues par lien SwissTransfer (ou
   déposées dans `atelier/a-traiter/`), tableaux rendus dans `atelier/resultats/`.
4. Tableau de bord (`releves/` et une page non référencée du site) : clics vers Pexels,
   statistiques Pinterest, vues Pexels relevées à la main.

## Façon de travailler

- Échanger en français. Textes du site en français et en anglais.
- Documentation en français. Les « LISEZMOI » demandés sont des `README.md`.
- Tout doit rester simple à utiliser et à maintenir sans compétences de développement :
  peu de dépendances, aucun service payant, modes d'emploi pas à pas.
- S'en tenir à la consigne de la session : le crédit est un budget compté.
- `main` est la branche publiée ; chaque session travaille sur sa branche et propose
  une pull request vers `main`.

## Règles impératives

- **Secret** : la clé Pexels n'apparaît jamais dans le code, les journaux ni
  l'historique. En session : variable d'environnement `PEXELS_API_KEY` ; dans GitHub
  Actions : secret du dépôt `PEXELS_API_KEY`. Le dépôt est public : tout ce qui est
  poussé est visible de tous.
- **API Pexels** : lire la fiche de chaque photo par le point d'accès « Photo »
  (`GET https://api.pexels.com/v1/photos/:id`), à partir de la liste
  `atelier/inventaire.csv`. Respecter les limites de débit, afficher « Photos provided
  by Pexels » avec un lien, et vérifier la documentation officielle avant d'implémenter.
- **Conditions Pexels** : chaque photo renvoie vers sa page Pexels, sans téléchargement
  direct ; ne pas reproduire les fonctions de base de Pexels ; aucune collecte
  automatique sur les pages de pexels.com. Les vues, que l'API ne fournit pas, sont
  notées à la main dans `releves/vues-pexels.csv`.
- **Filigranes** : aucune signature ni filigrane sur un fichier destiné à Pexels ; ils
  sont permis sur les visuels Pinterest.

## Repères techniques

- Adresse par défaut du site : https://willwonderc.github.io/PexelsWillwonder/. Le site
  vit dans un sous-chemin : liens relatifs ou chemin de base configurable (un domaine
  personnalisé reste possible).
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
