# 2 — Pinterest

Objectif : que les épingles se créent sans intervention.

- **En continu** : le site publie un flux RSS par galerie. Un compte Pinterest
  professionnel qui a revendiqué le site peut relier chaque flux à un tableau :
  Pinterest crée alors une épingle pour chaque nouvelle photo, sans session ni crédit.
- **Pour les photos déjà publiées** : une session prépare des fichiers d'import par
  tableur, jusqu'à 200 épingles par fichier, avec titre, description, lien, tableau de
  destination et dates de publication échelonnées. Il ne reste qu'à les importer.
- **Visuels** : des visuels verticaux avec un titre court, générés et hébergés par le
  site, car l'import va chercher chaque image à une adresse publique.
- **Lien des épingles** : la page de la photo sur le site, qui mène à Pexels pour le
  téléchargement (à confirmer).

La publication directe par l'API Pinterest est possible, mais elle suppose de faire
valider une application par Pinterest ; les flux RSS rendent cette étape inutile.

Une signature sur les visuels Pinterest est permise ; jamais sur les fichiers importés
chez Pexels.

Prérequis : compte Pinterest professionnel (gratuit), site en ligne et revendiqué.
