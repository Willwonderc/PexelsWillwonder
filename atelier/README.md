# 3 — Atelier titres et mots-clés

Une session Claude regarde les photos et rend un tableau prêt à copier : un titre
descriptif propre à chaque cliché et jusqu'à 25 mots-clés en anglais. Pexels ne
permettant guère de modifier titres et mots-clés après publication, l'atelier sert
avant chaque import. Pour les photos déjà publiées, ses tableaux alimentent le site
de photographe.

## Mode d'emploi

1. Compresser le dossier de photos (clic droit → Compresser) et le déposer sur
   https://www.swisstransfer.com, qui fournit un lien de téléchargement gratuit.
   Les photos téléchargées depuis Pexels gardent leur nom `pexels-photo-<numéro>`,
   qui relie chaque ligne du tableau à sa page Pexels.
2. Donner ce lien à une session Claude Code ouverte sur ce dépôt. Elle télécharge
   l'archive, regarde les photos et rédige titres et mots-clés.
3. Le tableau (numéro, lien, titre, mots-clés) arrive dans `resultats/`.
4. Reporter les titres et mots-clés sur Pexels.

Les photos ne passent pas par le dépôt : rien n'est publié d'autre que les tableaux.
Autre possibilité, pour un petit lot : déposer des copies réduites (JPEG, côté long
d'environ 1600 pixels) dans `a-traiter/`, un sous-dossier par série, via Add file →
Upload files sur GitHub, puis les supprimer une fois traitées. Le dépôt étant public,
elles restent visibles dans l'historique.

## Fichiers

- [`inventaire.csv`](inventaire.csv) : les 919 photos du profil, avec pour chacune
  son lien et l'état de son titre sur Pexels (titré, sans titre ou non vérifié).
- [`resultats/ppex-photos-sans-titre.csv`](resultats/ppex-photos-sans-titre.csv) :
  titres et mots-clés rédigés le 24 septembre 2026 pour les 155 photos récentes sans
  titre et pour 2 photos pas encore publiées.

## Précaution

Aucune signature ni filigrane sur les fichiers importés chez Pexels.
