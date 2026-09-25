# 2 — Pinterest

Objectif : que les épingles se créent sans intervention et ramènent les visiteurs vers
les photos Pexels.

- **Flux RSS, pour toutes les photos** : chaque galerie du site publie un flux relié à
  un tableau Pinterest ; le flux « More photos » regroupe les photos rangées dans aucune
  galerie. Les nouvelles photos y entrent aussitôt, le fonds au compte-gouttes, d'après
  le journal des parutions (ci-dessous). Pinterest crée les épingles dans les 24 heures,
  sans session ni crédit. Il exige qu'elles mènent au site revendiqué : elles ouvrent
  donc la page de la photo, qui renvoie vers Pexels.
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
   Recommencer pour chaque galerie. Pinterest crée au plus 200 épingles par jour. Pour
   une nouvelle galerie, créer d'abord son tableau (bouton « + » → Tableau, avec le titre
   anglais de la galerie), puis relier son flux de préférence le jour de sa mise en
   ligne, au plus tard dans la semaine : un flux ne présente que ses 12 dernières
   parutions, et Pinterest lit tout le flux d'un coup quand on le relie.
6. **Importer le fonds** : une session prépare les fichiers d'import. Pour qu'ils
   correspondent exactement au modèle de Pinterest, télécharger l'exemple de fichier
   proposé dans « Importer du contenu » et le transmettre à la session. Les
   importer ensuite au même endroit, un fichier à la fois.

Les intitulés de Pinterest peuvent varier légèrement selon les versions.

## Journal des parutions

`vitrine/donnees/parutions.json` note, pour chaque flux, le jour où chaque photo y a paru.
La tâche de nuit le complète puis l'enregistre sur `main`, comme les fiches Pexels.
Chaque flux présente ses 12 dernières parutions (`flux_max` dans `vitrine/site.ini`).
Chaque nuit :

1. les nouvelles photos (lues sur Pexels après `fonds_date`) entrent aussitôt dans les
   flux de leurs galeries ;
2. le fonds suit, des photos les plus vues sur Pexels aux moins vues (fiche de suivi de
   `releves/`) : une photo par galerie et par nuit (`epingles_par_jour`), trois pour
   « More photos » (`epingles_par_jour_autres`) ;
3. un flux qui démarre, celui d'une nouvelle galerie, reçoit d'abord 6 photos (la moitié
   de `flux_max`), puis le même rythme. Aucun flux ne reçoit plus de 6 photos en une
   nuit : chacune y reste au moins deux jours, le temps que Pinterest la lise ;
4. jamais plus de 200 épingles par jour, tous flux confondus (`epingles_max_par_jour`).

Une photo ne paraît qu'une fois dans un flux : une photo ajoutée à une galerie, reclassée
ou nouvellement titrée prend sa place dans la file, sans être sautée ni republiée dans le
même tableau. Elle peut en revanche paraître dans plusieurs tableaux, un par galerie.

Le journal reprend les parutions de l'ancien compte-gouttes, commencé le 25 septembre
2026, jusqu'à sa mise en service ; les parutions que ce dernier avait prévues pour les
jours suivants sont oubliées au premier passage de la tâche de nuit. Un essai de
`vitrine/build.py` en session ne modifie pas le journal : seule la tâche GitHub
l'enregistre (option `--enregistrer-parutions`).

Calendrier prévu, sans nouvelle photo (photos par flux, date de la dernière épingle) :
`python3 pinterest/epingles.py --calendrier`.

## Flux des galeries

Ces flux sont en anglais, car l'audience de Pinterest est d'abord anglophone. Pour
des épingles en français, remplacer `/en/galleries/<galerie>/feed.xml` par
`/galeries/<galerie>/flux.xml` et donner aux tableaux les titres français des
galeries.

| Tableau (en anglais) | Photos | Flux à coller | Relié |
|---|---|---|---|
| Loire Valley château gardens | 24 | `https://photos.karlforterre.fr/en/galleries/jardins-chateaux-loire/feed.xml` | oui |
| Sky and astrophotography | 21 | `https://photos.karlforterre.fr/en/galleries/ciel-astrophotographie/feed.xml` | oui |
| Clouds and sunsets | 28 | `https://photos.karlforterre.fr/en/galleries/nuages-couchers-de-soleil/feed.xml` | **à relier** |
| Landscapes and countryside | 39 | `https://photos.karlforterre.fr/en/galleries/paysages-campagne/feed.xml` | **à relier** |
| Trees and forests | 79 | `https://photos.karlforterre.fr/en/galleries/arbres-et-forets/feed.xml` | **à relier** |
| Flowers and macro | 71 | `https://photos.karlforterre.fr/en/galleries/fleurs-et-macro/feed.xml` | oui |
| Sea and coast | 25 | `https://photos.karlforterre.fr/en/galleries/mer-et-littoral/feed.xml` | **à relier** |
| Rivers, lakes and canals | 55 | `https://photos.karlforterre.fr/en/galleries/rivieres-et-lacs/feed.xml` | **à relier** |
| Architecture and heritage | 96 | `https://photos.karlforterre.fr/en/galleries/architecture-patrimoine/feed.xml` | **à relier** |
| Churches and cathedrals | 44 | `https://photos.karlforterre.fr/en/galleries/eglises-cathedrales/feed.xml` | **à relier** |
| Cities and street scenes | 62 | `https://photos.karlforterre.fr/en/galleries/villes-et-rues/feed.xml` | **à relier** |
| Transport | 11 | `https://photos.karlforterre.fr/en/galleries/transports/feed.xml` | **à relier** |
| Portraits | 48 | `https://photos.karlforterre.fr/en/galleries/portraits/feed.xml` | oui |
| Everyday life | 51 | `https://photos.karlforterre.fr/en/galleries/scenes-de-vie/feed.xml` | **à relier** |
| Wedding | 7 | `https://photos.karlforterre.fr/en/galleries/mariage/feed.xml` | oui |
| Protests and activism | 10 | `https://photos.karlforterre.fr/en/galleries/manifestations/feed.xml` | **à relier** |
| Animals | 62 | `https://photos.karlforterre.fr/en/galleries/animaux/feed.xml` | **à relier** |
| Food and drink | 20 | `https://photos.karlforterre.fr/en/galleries/cuisine-et-boissons/feed.xml` | **à relier** |
| Objects and still life | 31 | `https://photos.karlforterre.fr/en/galleries/objets-natures-mortes/feed.xml` | **à relier** |
| Black and white | 68 | `https://photos.karlforterre.fr/en/galleries/noir-et-blanc/feed.xml` | oui |
| Abstract backgrounds | 43 | `https://photos.karlforterre.fr/en/galleries/fonds-abstraits/feed.xml` | oui |
| Basque Country | 13 | `https://photos.karlforterre.fr/en/galleries/pays-basque/feed.xml` | oui |
| Asturias | 11 | `https://photos.karlforterre.fr/en/galleries/asturies/feed.xml` | oui |
| Galicia | 29 | `https://photos.karlforterre.fr/en/galleries/galice/feed.xml` | oui |
| Camino de Santiago | 15 | `https://photos.karlforterre.fr/en/galleries/chemin-saint-jacques/feed.xml` | oui |
| Pyrenees | 47 | `https://photos.karlforterre.fr/en/galleries/pyrenees/feed.xml` | oui |
| Bordeaux | 6 | `https://photos.karlforterre.fr/en/galleries/bordeaux/feed.xml` | oui |
| Niort and Poitou | 45 | `https://photos.karlforterre.fr/en/galleries/niort-poitou/feed.xml` | oui |
| Loire Valley | 33 | `https://photos.karlforterre.fr/en/galleries/val-de-loire/feed.xml` | **à relier** |
| Charente: Cognac and Angoulême | 17 | `https://photos.karlforterre.fr/en/galleries/charente/feed.xml` | **à relier** |
| Paris | 12 | `https://photos.karlforterre.fr/en/galleries/paris/feed.xml` | **à relier** |
| Normandy and Brittany | 13 | `https://photos.karlforterre.fr/en/galleries/normandie-bretagne/feed.xml` | **à relier** |
| Vosges, Lorraine and Alsace | 15 | `https://photos.karlforterre.fr/en/galleries/vosges-lorraine-alsace/feed.xml` | **à relier** |
| Photos by Karl Forterre | 0 | `https://photos.karlforterre.fr/en/more-photos/feed.xml` | oui |

Les 19 flux marqués « à relier » sont ceux des galeries créées par la session B (septembre 2026) :
créer chaque tableau avec le titre anglais de la galerie, puis y relier son flux (étape 5).
Tant que toutes les photos sont rangées dans une galerie, le flux « More photos » ne
reçoit plus rien ; il reste relié pour les photos à venir qui n'entreraient dans aucune.
Une galerie qui compte moins de 4 photos, comme Toulouse aujourd'hui, n'a pas encore de
flux : il apparaîtra à la même adresse.

## Précautions

- Une signature sur les visuels Pinterest est permise ; jamais sur les fichiers
  importés chez Pexels.
- Pas de publication en rafale au-delà de ce que Pinterest accepte : les fichiers
  d'import étalent les dates de publication.
