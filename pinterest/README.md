# 2 — Pinterest

Objectif : que les épingles se créent sans intervention et ramènent les visiteurs vers
les photos Pexels.

- **Flux RSS, pour les nouvelles photos** : chaque galerie du site publie un flux de ses
  12 photos les plus récentes. Relié à un tableau Pinterest, il crée une épingle pour
  chaque nouvelle photo, dans les 24 heures, sans session ni crédit. Pinterest exige que
  ces épingles mènent au site revendiqué : elles ouvrent donc la page de la photo sur le
  site, qui renvoie vers Pexels.
- **Fichiers d'import, pour les photos déjà publiées** : une session prépare des
  fichiers de 200 épingles au plus, avec des dates de publication étalées. Ces
  épingles-là mènent directement à la page Pexels de chaque photo.

## Démarche, étape par étape

1. **Compte professionnel** : sur Pinterest, menu en haut à droite → Paramètres →
   Gestion du compte → Convertir en compte professionnel (gratuit).
2. **Site en ligne** : fusionner la pull request du site, puis vérifier dans l'onglet
   Actions du dépôt que la tâche « Site » est verte.
3. **Revendiquer le site** : Paramètres → Comptes revendiqués → Sites web →
   Revendiquer → « Ajouter une balise HTML ». Recopier la valeur entre les guillemets
   de `content="…"`, la coller dans `vitrine/site.ini` après
   `pinterest_verification =`, puis enregistrer (Commit changes). Trois minutes plus
   tard, le site est reconstruit : saisir l'adresse
   `https://willwonderc.github.io/PexelsWillwonder` dans Pinterest et lancer la
   vérification.
4. **Créer les tableaux** : un tableau par galerie, avec les noms de la liste
   ci-dessous.
5. **Relier les flux** : Paramètres → Créer des épingles en masse → Publication
   automatique → coller l'adresse d'un flux, choisir son tableau, enregistrer.
   Recommencer pour chaque galerie. Pinterest crée au plus 200 épingles par jour.
6. **Importer le fonds** : une session prépare les fichiers d'import. Pour qu'ils
   correspondent exactement au modèle de Pinterest, télécharger l'exemple de fichier
   proposé dans « Créer des épingles en masse » et le transmettre à la session. Les
   importer ensuite au même endroit, un fichier à la fois.

Les intitulés de Pinterest peuvent varier légèrement selon les versions.

## Flux des galeries

Ces flux sont en anglais, car l'audience de Pinterest est d'abord anglophone. Pour
des épingles en français, remplacer `/en/galleries/<galerie>/feed.xml` par
`/galeries/<galerie>/flux.xml` et donner aux tableaux les titres français des
galeries.

| Tableau (en anglais) | Flux à coller |
|---|---|
| Loire Valley château gardens | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/jardins-chateaux-loire/feed.xml` |
| Sky and astrophotography | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/ciel-astrophotographie/feed.xml` |
| Black and white | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/noir-et-blanc/feed.xml` |
| Flowers and macro | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/fleurs-et-macro/feed.xml` |
| Portraits | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/portraits/feed.xml` |
| Abstract backgrounds | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/fonds-abstraits/feed.xml` |
| Wedding | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/mariage/feed.xml` |
| Basque Country | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/pays-basque/feed.xml` |
| Asturias | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/asturies/feed.xml` |
| Galicia | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/galice/feed.xml` |
| Camino de Santiago | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/chemin-saint-jacques/feed.xml` |
| Pyrenees | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/pyrenees/feed.xml` |
| Bordeaux | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/bordeaux/feed.xml` |
| Niort and Poitou | `https://willwonderc.github.io/PexelsWillwonder/en/galleries/niort-poitou/feed.xml` |
Une galerie qui dépassera 4 photos, comme Toulouse, aura son flux à la même adresse.

## Précautions

- Une signature sur les visuels Pinterest est permise ; jamais sur les fichiers
  importés chez Pexels.
- Pas de publication en rafale au-delà de ce que Pinterest accepte : les fichiers
  d'import étalent les dates de publication.
