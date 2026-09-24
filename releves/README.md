# 4 — Relevés pour le tableau de bord

[vues-pexels.csv](vues-pexels.csv) rassemble le total de vues Pexels, noté à la main
une fois par semaine : l'API Pexels ne fournit pas ce chiffre, et les conditions de
Pexels interdisent la collecte automatique sur leurs pages.

## Ajouter un relevé

Sur GitHub, ouvrir `vues-pexels.csv`, cliquer sur le crayon, ajouter une ligne à la fin,
puis « Commit changes ». Exemple de ligne, chiffres fictifs :

    2026-10-01,880000,920,20,épingles Pinterest lancées

- `date` : au format AAAA-MM-JJ ;
- `vues` : total de vues affiché par Pexels, sans espaces ;
- `photos` et `abonnes` : facultatifs, laisser vide au besoin ;
- `remarque` : facultative, pour noter un événement de la semaine.

Ce relevé alimentera la page de tableau de bord du site (session 4) et le compteur de
l'écran Turing.

Chaque relevé compte aussi comme une activité du dépôt. GitHub suspend les tâches
planifiées d'un dépôt public resté 60 jours sans activité : un relevé par semaine garde
donc en marche la reconstruction nocturne du site.
