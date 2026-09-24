# Site de photographe — mode d'emploi

Le site présente les photos de Karl Forterre publiées sur Pexels, en français et en
anglais, avec une page par photo et des galeries par thème et par lieu. Chaque photo
mène à sa page Pexels, où elle se télécharge gratuitement : les visites du site
profitent ainsi au profil Pexels.

Adresse : https://photos.karlforterre.fr/ (l'adresse GitHub y redirige)

Le site se reconstruit tout seul :
- chaque nuit, entre 4 h et 5 h du matin (heure de Paris) ;
- quelques minutes après chaque modification enregistrée sur la branche `main` ;
- à la demande : onglet **Actions** du dépôt → **Site** → **Run workflow**.

## Ajouter une photo

1. Publiez-la sur Pexels avec un titre. L'atelier peut le rédiger avant l'import.
2. Sur GitHub, ouvrez `vitrine/photos.txt`, cliquez sur le crayon, collez le lien Pexels
   de la photo sur une nouvelle ligne, puis cliquez sur **Commit changes**.
3. Quelques minutes plus tard, la photo a sa page et rejoint les galeries dont elle
   contient les mots.

Une photo publiée sans titre sur Pexels n'apparaît qu'une fois que l'atelier lui en a
rédigé un.

## Retirer une photo

Dans `vitrine/photos.txt`, placez un `#` au début de sa ligne.

## Modifier une galerie

Tout se règle dans `vitrine/galeries.ini`, dont l'en-tête explique chaque réglage :
titres et descriptions, mots qui font entrer une photo dans la galerie, photos à
ajouter ou à retirer, photo de couverture. Une galerie ne s'affiche qu'à partir de
4 photos (réglage `galerie_min` de `vitrine/site.ini`).

## Changer l'ordre des pages

Les galeries s'affichent dans l'ordre de `galeries.ini` : déplacez un bloc entier,
de son `[identifiant]` jusqu'au bloc suivant. Dans chaque galerie, les photos vont de
la plus récente à la plus ancienne.

## Modifier les textes

- Accroche de l'accueil et page « À propos » : `vitrine/site.ini`.
- Titres et mots-clés anglais : `atelier/resultats/*.csv`.
- Titres et mots-clés français : `vitrine/donnees/textes-fr.csv`.

## Mesure d'audience

Créez un compte gratuit sur https://www.goatcounter.com, puis inscrivez son code dans
`site.ini` (`goatcounter = …`). Les clics vers Pexels y apparaissent sous les noms
`pexels-<numéro>`, `pexels-image-<numéro>` et `suivre-pexels`.

## Référencement

- **Google** : ajoutez le site dans Google Search Console, recopiez le code de la
  balise de validation dans `site.ini` (`google_verification`), puis déclarez le plan
  du site : `https://photos.karlforterre.fr/sitemap.xml`.
- **Pinterest** : pour revendiquer le site, recopiez le code de la balise fournie par
  Pinterest dans `site.ini` (`pinterest_verification`).

## Domaine personnel

Le site est servi à l'adresse photos.karlforterre.fr : un enregistrement CNAME
`photos` → `willwonderc.github.io.` dans la zone DNS de karlforterre.fr chez OVH, et le
domaine déclaré sur GitHub dans **Settings** → **Pages** → **Custom domain**, avec
**Enforce HTTPS** coché. Le réglage `adresse` de `site.ini` doit correspondre.

## Flux RSS, pour Pinterest

- Tout le site : `/flux.xml` en français, `/en/feed.xml` en anglais.
- Une galerie : `/galeries/<identifiant>/flux.xml` et `/en/galleries/<identifiant>/feed.xml`.

## Contenu du dossier

- `build.py` : le programme qui construit le site (Python, sans bibliothèque à installer).
  Pour l'essayer : `python3 vitrine/build.py`, puis ouvrir `_site/index.html`.
- `photos.txt`, `galeries.ini`, `site.ini` : la liste des photos et les réglages.
- `donnees/fiches.json` : les fiches lues sur Pexels, tenues à jour automatiquement.
- `donnees/textes-fr.csv` : les titres et mots-clés français.
- `statique/` : feuille de style, police Archivo et icône.
- `../.github/workflows/site.yml` : reconstruction et publication automatiques.
