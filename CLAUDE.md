# Contexte pour les sessions Claude

Ce fichier est chargé automatiquement au début de chaque session : il évite de
réexpliquer le projet dans les consignes.

## Projet

Promotion des photos de Karl Forterre publiées sur Pexels
(https://www.pexels.com/@karl-forterre-28489473). Point de départ, septembre 2026 :
919 photos, environ 878 500 vues, 19 abonnés. Des sessions Claude Code construisent,
avant le 5 novembre 2026, quatre outils qui tournent ensuite seuls et gratuitement sur
GitHub. Plan complet : `docs/plan.md` ; consignes des sessions : `consignes/`.

1. Vitrine reliée à Pexels (`vitrine/`) : site statique sur GitHub Pages, reconstruit
   chaque nuit à partir des collections Pexels, flux RSS, mesure d'audience GoatCounter.
2. Fabrique d'épingles Pinterest (`pinterest/`) : visuels verticaux et fichier d'import.
3. Atelier titres et mots-clés (`atelier/`) : photos déposées dans `atelier/a-traiter/`,
   tableaux de titres et mots-clés rendus dans `atelier/resultats/`.
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
- **API Pexels** : lire les photos par les points d'accès « My Collections »
  (`GET https://api.pexels.com/v1/collections`) et « Collection media »
  (`GET https://api.pexels.com/v1/collections/:id`), en n'affichant que les
  collections publiques. Respecter les limites de débit, afficher « Photos provided
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
- Titres Pexels peu fiables : les photos récentes portent des titres automatiques
  (trois premiers mots-clés par ordre alphabétique, par exemple « architecture
  photography, asturias, bell tower » pour quatre photos différentes des Asturies).
  Ne pas les reprendre tels quels comme titres ou textes alternatifs.
