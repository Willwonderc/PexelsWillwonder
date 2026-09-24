# 3 — Atelier titres et mots-clés

Avant un import sur Pexels, déposer ici des copies réduites des photos. Une session
Claude regarde chaque image et rend un tableau prêt à copier : un titre descriptif
propre à chaque cliché et jusqu'à 25 mots-clés. Idéal pour traiter d'un coup les photos
d'un voyage, en commençant par les séries récentes aux intitulés génériques, comme les
Asturies.

## Mode d'emploi

1. Exporter les photos en JPEG, côté long d'environ 1600 pixels, en gardant leur nom
   de fichier : c'est lui qui relie chaque ligne du tableau à sa photo.
2. Les déposer dans `a-traiter/`, un sous-dossier par série (par exemple
   `a-traiter/asturies/`). Sur GitHub : Add file → Upload files.
3. Lancer une session Claude Code sur ce dépôt en indiquant le sous-dossier à traiter.
4. Le tableau de la série (nom du fichier, titre, mots-clés) arrive dans `resultats/`.
5. Une fois les titres reportés sur Pexels, supprimer le sous-dossier de `a-traiter/`.

## Précautions

- Le dépôt est public : n'y déposer que des photos destinées à Pexels, en taille
  réduite. L'historique Git garde une trace des fichiers, même supprimés.
- Aucune signature ni filigrane sur les fichiers importés chez Pexels.
