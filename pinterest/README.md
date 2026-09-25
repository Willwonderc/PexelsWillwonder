# 2 — Pinterest

Objectif : que les épingles se créent sans intervention et ramènent les visiteurs vers
les photos Pexels.

- **Flux RSS, pour toutes les photos** : chaque galerie du site publie un flux relié à
  un tableau Pinterest. Les nouvelles photos y entrent aussitôt ; le fonds y entre au
  compte-gouttes, une photo de plus par galerie et par nuit (réglage
  `epingles_par_jour` de `vitrine/site.ini`). Le flux « More photos » fait de même,
  trois photos par nuit, pour les photos rangées dans aucune galerie. Pinterest crée
  les épingles dans les 24 heures, sans session ni crédit. Il exige qu'elles mènent au
  site revendiqué : elles ouvrent donc la page de la photo, qui renvoie vers Pexels.
- **Fichiers d'import, en complément** : ils mènent directement à la page Pexels de
  chaque photo, mais Pinterest ne garde que 10 épingles programmées à la fois, à
  30 jours au plus. Ils servent donc aux petits lots ponctuels, comme le fichier d'essai
  qui a créé les tableaux.

## Démarche, étape par étape

1. **Compte professionnel** : sur Pinterest, menu en haut à droite → Paramètres →
   Gestion du compte → Convertir en compte professionnel (gratuit).
2. **Site en ligne** : fusionner la pull request du site, puis vérifier dans l'onglet
   Actions du dépôt que la tâche « Site » est verte.
3. **Revendiquer le site** : Paramètres → Lien vers Pinterest → Sites web →
   Revendiquer → « Ajouter une balise HTML ». Recopier la valeur entre les guillemets
   de `content="…"`, la coller dans `vitrine/site.ini` après
   `pinterest_verification =`, puis enregistrer (Commit changes). Trois minutes plus
   tard, le site est reconstruit : saisir l'adresse
   `https://photos.karlforterre.fr` dans Pinterest et lancer la
   vérification.
4. **Créer les tableaux** : importer le fichier d'essai
   `pinterest/imports/essai-2-une-epingle-par-galerie.csv` (Paramètres → Importer du
   contenu → Importer un fichier). Il publie une épingle par galerie, et Pinterest
   crée au passage les tableaux qui n'existent pas. Pour le régénérer :
   `python3 pinterest/epingles.py --essai`.
5. **Relier les flux** : Paramètres → Importer du contenu (anciennement « Créer des
   épingles en masse ») → Publication automatique → coller l'adresse d'un flux, choisir son tableau, enregistrer.
   Recommencer pour chaque galerie. Pinterest crée au plus 200 épingles par jour.
6. **Importer le fonds** : une session prépare les fichiers d'import. Pour qu'ils
   correspondent exactement au modèle de Pinterest, télécharger l'exemple de fichier
   proposé dans « Importer du contenu » et le transmettre à la session. Les
   importer ensuite au même endroit, un fichier à la fois.

Les intitulés de Pinterest peuvent varier légèrement selon les versions.

## Flux des galeries

Ces flux sont en anglais, car l'audience de Pinterest est d'abord anglophone. Pour
des épingles en français, remplacer `/en/galleries/<galerie>/feed.xml` par
`/galeries/<galerie>/flux.xml` et donner aux tableaux les titres français des
galeries.

| Tableau (en anglais) | Flux à coller |
|---|---|
| Loire Valley château gardens | `https://photos.karlforterre.fr/en/galleries/jardins-chateaux-loire/feed.xml` |
| Sky and astrophotography | `https://photos.karlforterre.fr/en/galleries/ciel-astrophotographie/feed.xml` |
| Black and white | `https://photos.karlforterre.fr/en/galleries/noir-et-blanc/feed.xml` |
| Flowers and macro | `https://photos.karlforterre.fr/en/galleries/fleurs-et-macro/feed.xml` |
| Portraits | `https://photos.karlforterre.fr/en/galleries/portraits/feed.xml` |
| Abstract backgrounds | `https://photos.karlforterre.fr/en/galleries/fonds-abstraits/feed.xml` |
| Wedding | `https://photos.karlforterre.fr/en/galleries/mariage/feed.xml` |
| Basque Country | `https://photos.karlforterre.fr/en/galleries/pays-basque/feed.xml` |
| Asturias | `https://photos.karlforterre.fr/en/galleries/asturies/feed.xml` |
| Galicia | `https://photos.karlforterre.fr/en/galleries/galice/feed.xml` |
| Camino de Santiago | `https://photos.karlforterre.fr/en/galleries/chemin-saint-jacques/feed.xml` |
| Pyrenees | `https://photos.karlforterre.fr/en/galleries/pyrenees/feed.xml` |
| Bordeaux | `https://photos.karlforterre.fr/en/galleries/bordeaux/feed.xml` |
| Niort and Poitou | `https://photos.karlforterre.fr/en/galleries/niort-poitou/feed.xml` |
| Photos by Karl Forterre | `https://photos.karlforterre.fr/en/more-photos/feed.xml` |
Une galerie qui dépassera 4 photos, comme Toulouse, aura son flux à la même adresse.

## Précautions

- Une signature sur les visuels Pinterest est permise ; jamais sur les fichiers
  importés chez Pexels.
- Pas de publication en rafale au-delà de ce que Pinterest accepte : les fichiers
  d'import étalent les dates de publication.
