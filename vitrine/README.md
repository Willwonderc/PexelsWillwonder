# Site de photographe — mode d'emploi

Le site présente les photos de Karl Forterre publiées sur Pexels, en français et en
anglais : un accueil en plein écran, une sélection de 24 photos, des séries racontées,
des galeries par thème et par lieu et une page par photo. Chaque photo mène à sa page
Pexels, où elle se télécharge gratuitement : les visites du site profitent ainsi au
profil Pexels.

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

## Accueil et sélection

- **Ouverture plein écran** : quelques photos défilent en fondu lent derrière le nom,
  l'accroche et les boutons « Voir les galeries » et « Suivre sur Pexels ». Leurs
  numéros se règlent dans `vitrine/site.ini`, rubrique `[accueil]`, ligne
  `ouverture` (6 à 8 photos, de préférence en format paysage). Sur un téléphone, Pexels
  fournit directement l'image recadrée en hauteur.
- **Sélection** : les 24 photos présentées sous l'ouverture, dans l'ordre de
  `vitrine/selection.txt`. Une photo par ligne (lien Pexels ou numéro, suivi au besoin
  d'un commentaire) ; un `#` en début de ligne la retire.
- **Preuve sociale** : « 878 500 vues et 3 950 téléchargements sur Pexels » s'affiche
  près des boutons « Suivre sur Pexels ». Les chiffres viennent des relevés de
  `releves/` : la dernière ligne de `vues-pexels.csv` pour les vues, le total de la
  fiche de suivi (`suivi-pexels.csv`, ou toute autre `suivi-….csv` déposée au même
  format) pour les téléchargements. Rien à faire de plus : un nouveau relevé met la
  phrase à jour.

## Séries

Les séries racontent un lieu ou un moment : un titre, un lieu, une date, un texte de
150 à 300 mots en français et en anglais, puis les photos. Tout se règle dans
`vitrine/series.ini`, dont l'en-tête explique chaque réglage ; l'ordre des blocs est
celui de l'affichage. Adresses : `/series/<identifiant>/` et
`/en/series/<identifiant>/`.

## Visionneuse

Un clic sur une vignette ouvre la photo en plein écran, avec son titre et le bouton
« Télécharger gratuitement sur Pexels » toujours visibles. On passe d'une photo à
l'autre avec les flèches (à l'écran ou au clavier) ou en faisant glisser le doigt ;
Échap, la croix ou le bouton retour ferment la visionneuse. L'adresse affichée est
celle de la page de la photo : on peut la copier pour la partager. Le tout tient dans
`statique/site.js`, sans bibliothèque ; sans JavaScript, la vignette mène simplement
à la page de la photo.

## Pages « Utiliser mes photos », « Mentions légales » et « Confidentialité »

Liées en pied de page, elles se construisent seules :
- **Utiliser mes photos** explique la licence Pexels simplement, avec un lien vers le
  texte officiel.
- **Mentions légales** : éditeur, contact et hébergeur (GitHub). Les réglages sont dans
  `site.ini`, rubrique `[mentions]`. Pour un site professionnel, la loi demande aussi
  l'adresse et le téléphone de l'éditeur, et son numéro SIRET s'il en a un : il suffit
  de les inscrire sur les lignes prévues.
- **Confidentialité** : ni cookies ni bandeau. Le paragraphe sur GoatCounter
  n'apparaît qu'une fois son code inscrit dans `site.ini`.

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

- Accroche de l'accueil et page « À propos » : `vitrine/site.ini`. La page « À propos »
  peut aussi afficher un portrait (`portrait`, numéro Pexels) et le matériel photo
  (`materiel_fr`, `materiel_en`).
- Textes des séries : `vitrine/series.ini`.
- Titres et mots-clés anglais : `atelier/resultats/*.csv`.
- Titres et mots-clés français : `vitrine/donnees/textes-fr.csv`.

## Mesure d'audience

Créez un compte gratuit sur https://www.goatcounter.com, puis inscrivez son code dans
`site.ini` (`goatcounter = …`). Les clics vers Pexels y apparaissent sous les noms
`pexels-<numéro>` (bouton de téléchargement), `pexels-image-<numéro>` (clic sur la
photo) et `suivre-pexels` (bouton de l'en-tête), `suivre-pexels-accueil` (bouton de
l'ouverture) et `suivre-pexels-fin` (rappel en fin de galerie, de série et de page).
Une photo regardée dans la visionneuse compte comme une visite de sa page.

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
- `selection.txt`, `series.ini` : la sélection de l'accueil et les séries.
- `donnees/fiches.json` : les fiches lues sur Pexels, tenues à jour automatiquement.
- `donnees/textes-fr.csv` : les titres et mots-clés français.
- `statique/` : feuille de style, visionneuse et fondu de l'accueil (`site.js`), police
  Archivo, logo KF’ (`logo.svg`, vectoriel ; `logo-kf.webp`, original texturé) et
  icônes du site (`favicon.svg`, `icone-180.png` pour l'écran d'accueil des
  téléphones).
- `../.github/workflows/site.yml` : reconstruction et publication automatiques.
