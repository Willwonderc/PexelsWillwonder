# Site de photographe — mode d'emploi

Le site présente les photos de Karl Forterre publiées sur Pexels, en français, en
anglais et en chinois simplifié : un accueil en plein écran, une sélection de 24 photos, des séries racontées,
des galeries par thème et par lieu, des pages par couleur et une page par photo. Chaque
photo mène à sa page Pexels, où elle se télécharge gratuitement : les visites du site
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
   contient les mots. Si elle n'entre dans aucune, ajoutez son numéro à la ligne
   `ajouter` d'une galerie (voir « Modifier une galerie »).

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
  d'un commentaire) ; un `#` en début de ligne la retire. Le début du commentaire,
  jusqu'au tiret long (« Voie lactée — 74 188 vues »), sert de titre court en français
  dans le carrousel de karlforterre.fr : pensez à l'écrire pour chaque photo ajoutée.
- **Preuve sociale** : « 878 500 vues et 3 950 téléchargements sur Pexels » s'affiche
  près des boutons « Suivre sur Pexels ». Les chiffres viennent des relevés de
  `releves/` : la dernière ligne de `vues-pexels.csv` pour les vues, le total de la
  fiche de suivi (`suivi-pexels.csv`, ou toute autre `suivi-….csv` déposée au même
  format) pour les téléchargements. Rien à faire de plus : un nouveau relevé met la
  phrase à jour.

## Aperçu pour le site d'auteur

Chaque nuit, le site publie aussi `https://photos.karlforterre.fr/apercu.json`, que le
site d'auteur karlforterre.fr (dépôt Willwonderc/karlforterre.fr) lit à chaque visite
pour sa section Photographie : les photos de la sélection (titre court, page du site,
page Pexels, image), les séries et les galeries avec leur couverture, les dernières
photos et les chiffres Pexels. Modifier `selection.txt`, `series.ini` ou
`galeries.ini` suffit donc à mettre à jour les deux sites. La page « À propos » présente
de son côté l'auteur et ses livres (réglages `auteur_fr` et `auteur_en` de `site.ini`),
avec un lien vers karlforterre.fr.

## Trois langues

Pages françaises à la racine du site, anglaises sous `/en/`, chinoises sous `/zh/`
(mêmes adresses qu'en anglais : `/zh/galleries/pyrenees/`, `/zh/photo/<numéro>/`). Le
bouton de langue de l'en-tête passe du français à l'anglais, puis au chinois, puis
revient au français.

- Textes chinois des galeries, des séries, de l'accueil et de la page « À propos » :
  champs `_zh` de `galeries.ini`, `series.ini` et `site.ini` (`titre_zh`,
  `description_zh`, `texte_zh`, `lieu_zh`, `date_zh`, `accroche_zh`, `auteur_zh`…).
- Titres et mots-clés chinois des photos : `donnees/textes-zh.csv` (colonnes `photo`,
  `titre_zh`, `mots_cles_zh`). Pour une nouvelle photo, reprendre les mots-clés du
  glossaire `donnees/glossaire-mots-cles-zh.csv` (anglais → chinois), dans l'ordre des
  mots anglais.
- Sans traduction chinoise, la page chinoise affiche l'anglais.
- Sur les pages chinoises, les liens vers Pexels mènent à son interface chinoise
  (`https://www.pexels.com/zh-cn/…`).
- Pinterest étant bloqué en Chine, les pages chinoises n'ont pas de flux RSS.

Pour faire connaître le site en Chine (Huaban, Xiaohongshu, Zhihu, Zcool, Bing) :
[docs/promotion-chine.md](../docs/promotion-chine.md).

## Séries

Les séries racontent un lieu ou un moment : un titre, un lieu, une date, un texte de
150 à 300 mots en français et en anglais (et en chinois), puis les photos. Leur mise en page de récit
les distingue des galeries : ouverture sur tout l'écran avec le titre au centre, premier
paragraphe en grand (le chapeau), photos plus grandes et plus espacées. Tout se règle dans
`vitrine/series.ini`, dont l'en-tête explique chaque réglage ; l'ordre des blocs est
celui de l'affichage. Adresses : `/series/<identifiant>/` et
`/en/series/<identifiant>/` et `/zh/series/<identifiant>/`.

## Photo en bandeau

Chaque série et chaque galerie s'ouvre sur une grande photo, derrière son titre, comme
l'accueil ; les pages « Séries » et « Galeries » aussi. Par défaut, c'est la photo de
couverture si elle est en largeur, sinon la première photo en largeur. Pour en choisir
une autre, ajoutez au bloc de la série (`series.ini`) ou de la galerie
(`galeries.ini`) une ligne `bandeau = <numéro Pexels>`, d'une photo qui en fait partie.

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
titres, descriptions et texte de présentation, mots qui font entrer une photo dans la
galerie, photos à ajouter ou à retirer, photo de couverture. Une galerie ne s'affiche
qu'à partir de 4 photos (réglage `galerie_min` de `vitrine/site.ini`).

- **Mots** : une photo entre dans la galerie si son titre, ses mots-clés de l'atelier ou
  ses mots-clés Pexels (colonne `mots_cles` de la fiche de suivi, `releves/suivi-pexels.csv`)
  contiennent l'un d'eux.
- **Ajouter, retirer** : les photos déjà en ligne ont été rangées une à une ; les lignes
  `ajouter` et `retirer` gardent ce classement. Pour déplacer une photo, ajoutez son numéro
  à la ligne `ajouter` d'une galerie ou à la ligne `retirer` d'une autre.
- **Texte** : `texte_fr` et `texte_en`, de 150 à 300 mots, s'affichent sous les photos
  de la galerie. Décaler les lignes suivantes de quelques espaces ; une ligne vide sépare
  deux paragraphes.

Chaque photo publiée est rangée dans au moins une galerie. Le programme signale celles
qui n'en ont aucune : elles paraissent alors dans le flux Pinterest « More photos ».

Une nouvelle galerie a aussi son flux Pinterest : le relier à un tableau (voir
`pinterest/README.md`) de préférence le jour de sa mise en ligne, au plus tard dans la
semaine.

## Pages par couleur

Six pages rangent les photos d'après la couleur moyenne que Pexels donne pour chacune :
bleu, vert, jaune et orange, rouge et rose, tons sombres, tons clairs. Une photo y entre
si sa couleur est assez marquée, ou assez foncée ou pâle ; une photo aux couleurs
neutres n'y figure pas. Le noir et blanc renvoie à sa galerie. Les pastilles des
couleurs sont en bas de la page « Galeries » ; chaque page de photo indique ses
couleurs. Adresses : `/couleurs/bleu/` et `/en/colors/blue/`, etc. Rien à régler : les
nouvelles photos s'y rangent seules.

## Photos proches, mots-clés et fil d'Ariane

- **Photos proches** : sous chaque photo, huit photos qui partagent le plus de mots-clés
  avec elle (les mots rares comptent davantage) ou les mêmes galeries.
- **Mots-clés** affichés : ceux de l'atelier, sinon une douzaine de mots-clés Pexels de la
  fiche de suivi (ceux du titre d'abord). Sans traduction dans `textes-fr.csv`, la page
  française affiche les mots anglais.
- **Fil d'Ariane** : en tête des pages (Accueil / Galeries / Pyrénées), avec ses données
  structurées pour Google. Une photo a pour parent sa galerie de lieu, sinon sa première
  galerie.

## Changer l'ordre des pages

Les galeries s'affichent dans l'ordre de `galeries.ini` : déplacez un bloc entier,
de son `[identifiant]` jusqu'au bloc suivant. Dans chaque galerie, les photos vont de
la plus récente à la plus ancienne.

## Modifier les textes

- Accroche de l'accueil et page « À propos » : `vitrine/site.ini`. La page « À propos »
  peut aussi afficher un portrait (`portrait`, numéro Pexels) et le matériel photo
  (`materiel_fr`, `materiel_en`).
- Textes des séries : `vitrine/series.ini` ; textes des galeries : `vitrine/galeries.ini`.
- Titres et mots-clés anglais : `atelier/resultats/*.csv`.
- Titres et mots-clés français : `vitrine/donnees/textes-fr.csv`. Pour traduire les
  mots-clés d'une nouvelle photo, reprendre ceux du glossaire
  `vitrine/donnees/glossaire-mots-cles.csv` (anglais → français).

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
- **Bing** (seul grand moteur utilisable en Chine) : même démarche dans Bing Webmaster
  Tools, code dans `bing_verification` ; pas à pas dans
  [docs/promotion-chine.md](../docs/promotion-chine.md). Le plan du site relie chaque
  page à ses deux traductions (`hreflang` fr, en et zh-Hans).
- **Pinterest** : pour revendiquer le site, recopiez le code de la balise fournie par
  Pinterest dans `site.ini` (`pinterest_verification`).
- **Mastodon** : l'adresse du profil dans `site.ini` (`mastodon`) ajoute à chaque page
  un lien `rel="me"`, qui vaut au lien du site une coche verte dans le profil Mastodon.
- **Fautes de frappe des mots-clés Pexels** : corrigées à la lecture de la fiche de
  suivi, d'après la liste `CORRECTIONS_MOTS` de `build.py` (« backgroud » →
  « background », etc.). Ajouter une ligne à cette liste pour en corriger une autre.

## Domaine personnel

Le site est servi à l'adresse photos.karlforterre.fr : un enregistrement CNAME
`photos` → `willwonderc.github.io.` dans la zone DNS de karlforterre.fr chez OVH, et le
domaine déclaré sur GitHub dans **Settings** → **Pages** → **Custom domain**, avec
**Enforce HTTPS** coché. Le réglage `adresse` de `site.ini` doit correspondre.

## Flux RSS, pour Pinterest

- Tout le site : `/flux.xml` en français, `/en/feed.xml` en anglais.
- Une galerie : `/galeries/<identifiant>/flux.xml` et `/en/galleries/<identifiant>/feed.xml`.
- Photos rangées dans aucune galerie : `/autres-photos/flux.xml` et `/en/more-photos/feed.xml`.

Chaque flux de galerie présente ses 12 dernières parutions. Le journal
`donnees/parutions.json` note le jour où chaque photo paraît dans chaque flux : la tâche
de nuit le complète et l'enregistre, comme les fiches Pexels. Règles et réglages :
`pinterest/README.md`.

## Contenu du dossier

- `build.py` : le programme qui construit le site (Python, sans bibliothèque à installer).
  Pour l'essayer : `python3 vitrine/build.py`, puis ouvrir `_site/index.html`.
- `photos.txt`, `galeries.ini`, `site.ini` : la liste des photos et les réglages.
- `selection.txt`, `series.ini` : la sélection de l'accueil et les séries. Avec les
  galeries, elles alimentent `apercu.json`, lu par karlforterre.fr.
- `donnees/fiches.json` : les fiches lues sur Pexels, tenues à jour automatiquement.
- `donnees/parutions.json` : le journal des parutions Pinterest, tenu par la tâche de nuit
  (`build.py --enregistrer-parutions`). Un essai de `build.py` sans cette option ne le
  modifie pas.
- `donnees/textes-fr.csv` et `donnees/textes-zh.csv` : les titres et mots-clés français
  et chinois.
- `donnees/glossaire-mots-cles-zh.csv` : les mots-clés anglais du site traduits en
  chinois (le site ne le lit pas non plus).
- `donnees/glossaire-mots-cles.csv` : la traduction des mots-clés Pexels, faite une fois
  pour toutes et à reprendre pour les suivants (le site ne le lit pas).
- `statique/` : feuille de style, visionneuse et fondu de l'accueil (`site.js`), police
  Archivo, logo KF’ (`logo.svg`, vectoriel ; `logo-kf.webp`, original texturé) et
  icônes du site (`favicon.svg`, `icone-180.png` pour l'écran d'accueil des
  téléphones).
- `../.github/workflows/site.yml` : reconstruction et publication automatiques.
