# Photos Pexels de Karl Forterre — espace de travail

Dépôt du projet de promotion des photos publiées sur Pexels
(profil : [@karl-forterre-28489473](https://www.pexels.com/@karl-forterre-28489473)).

Point de départ, septembre 2026 : 919 photos, environ 878 500 vues et 19 abonnés.
Des sessions Claude Code menées avant le 5 novembre 2026 construisent quatre outils
qui tournent ensuite seuls et gratuitement sur GitHub.
Plan détaillé : [docs/plan.md](docs/plan.md). Feuille de route du site et de la promotion :
[docs/plan-site-pro.md](docs/plan-site-pro.md) ; consignes des prochaines sessions :
[consignes/prochaines-sessions.md](consignes/prochaines-sessions.md).

## Les quatre chantiers

|   | Chantier | Dossier | Lancement | État |
|---|----------|---------|-----------|------|
| 1 | Site de photographe, pensé pour le référencement | [vitrine/](vitrine/) | construit le 24 septembre | [mode d'emploi](vitrine/README.md) |
| 2 | Pinterest automatique | [pinterest/](pinterest/) | 25 septembre | flux RSS en place, [démarche](pinterest/README.md) |
| 3 | Atelier titres et mots-clés | [atelier/](atelier/) | en même temps que la 1 | [premier lot rédigé](atelier/resultats/ppex-photos-sans-titre.csv) |
| 4 | Tableau de bord de campagne | [releves/](releves/) | fin octobre | relevés ouverts |

## Par où commencer

1. Faire les [préparatifs](docs/preparatifs.md), environ une heure.
2. Fusionner la pull request qui contient le site : il est publié quelques minutes
   plus tard. Mode d'emploi : [vitrine/README.md](vitrine/README.md).
3. Noter chaque semaine le total de vues Pexels dans
   [releves/vues-pexels.csv](releves/vues-pexels.csv).

## Intégrer le travail d'une session

Chaque session Claude travaille sur sa propre branche. En fin de session, lui demander
« ouvre une pull request vers main », puis, sur GitHub, ouvrir cette pull request et
cliquer sur « Merge pull request » : le travail rejoint `main`, la branche publiée.

## Organisation

    CLAUDE.md     contexte et règles lus automatiquement par chaque session Claude
    docs/         plan du projet et liste des préparatifs
    consignes/    consignes de lancement des sessions, prêtes à coller
    vitrine/      site de photographe (chantier 1) et page du tableau de bord (chantier 4)
    pinterest/    visuels verticaux et fichiers d'import (chantier 2)
    atelier/      photos à décrire et tableaux de titres (chantier 3)
    releves/      relevés hebdomadaires des vues Pexels (chantier 4)

## À savoir

- Le dépôt doit être public pour que le site soit hébergé gratuitement : tout ce qui
  y est déposé devient visible de tous.
- La clé API Pexels ne figure jamais dans le dépôt : elle est rangée dans les secrets
  GitHub et dans l'environnement cloud.
- Grâce à `CLAUDE.md`, inutile de réexpliquer le projet à chaque session : la consigne
  suffit.
