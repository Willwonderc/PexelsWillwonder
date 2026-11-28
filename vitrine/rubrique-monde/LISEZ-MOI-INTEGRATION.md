# Intégrer la rubrique « Mes photos utilisées dans le monde » (version 4A)

Paquet préparé le 28 novembre 2026 pour la session qui gère le dépôt git de photos.karlforterre.fr. Ce dossier se suffit : sources, données, contrôle, aperçus. Aucune clé, aucun secret, aucun chemin absolu.

**Règle de Karl** : il valide chaque publication. Rien ne part en ligne sans son accord, donné avant la mise en ligne. Travaillez sur une branche, montrez-lui la page en local, puis attendez son accord pour fusionner et publier.

## 1. Le but

Sur la page `/galeries/` de photos.karlforterre.fr, un bouton de la largeur de la grille porte le titre « Mes photos utilisées dans le monde ». Il se place **après la bande noire « Utilisées dans des projets » et avant la section « Thèmes »**.

Au clic, la photo du bouton couvre l'écran, puis se referme sur Villandry, le lieu où elle a été prise. Un globe de nuit (three.js) apparaît, avec un arc par parution, du lieu de la prise de vue jusqu'au média. Chaque photo a ensuite son affiche claire :
- un titre « Cognac, une photographie qui voyage », pris dans un éclat de triangles aux couleurs de la photo ;
- « 04 publications » ;
- « Une image, quatre regards » : une carte par média, avec un bouton de couleur vers l'article.

Contenu : 14 photos, 23 parutions, 22 médias.

## 2. Le contenu du paquet

| Dossier | Contenu |
|---|---|
| `sources/src/` | `rubrique-monde.js` (globe, index, fiches), `coquille.js` (ouverture, fermeture, adresses, clavier, son), `affiche.js`, `eclat.js`, `dialogue.js` (injecte le dialogue), `amorce.js` (chargement au premier clic) |
| `sources/styles/` | `bouton.css` (avec la page), `rubrique.css`, `affiche.css`, `p4a.css` (au premier clic) |
| `sources/gabarit/` | `fragment-galeries.html` (le bouton à insérer) ; `demo.html` et `demo-hote.css` (page de démonstration seulement) |
| `sources/construire.mjs` | construit `sources/dist/` et `demo/index.html` depuis `donnees/` |
| `sources/package.json`, `package-lock.json` | three 0.187.0, motion 14.14.0, esbuild 0.24.0 (versions exactes, verrouillées) |
| `sources/outils/palette.py` | calcule la palette d'une nouvelle photo (Pillow) |
| `donnees/` | `rubrique-monde.json` (le registre de la rubrique), `geo-terres.json` (points de terre du globe), `travail-par-parution.csv` |
| `controle/` | `scenario.py` (87 contrôles, joués pour la 4A seule) et sa notice |
| `apercus/` | planches, vidéos, page de démonstration autonome (images embarquées, s'ouvre par un double-clic) |
| `demo/index.html` | la page Galeries simulée, qui charge `sources/dist/` comme le fera le site |
| `A-VERIFIER.md` | ce qui reste supposé et ce qui n'a pas été essayé |

## 3. Construire

```
cd sources
npm ci
node construire.mjs --base /statique/rubrique-monde/
```

Cela produit `sources/dist/` :
- `rubrique-monde-amorce.js` (2 Ko) : se charge avec la page ;
- `bouton.css` : à fusionner dans la feuille du site ;
- `rubrique-monde.css`, `rubrique-monde-donnees.js` et `rubrique-monde.js` (environ 670 Ko, 180 Ko compressé) : chargés au premier clic ;
- `fragment-galeries.html` : le bouton, avec le détail calculé.

`--base` est l'adresse où le site servira ces fichiers ; `/statique/rubrique-monde/` suit le dossier `/statique/` du site.

## 4. Ce qui s'ajoute au site

1. **Gabarit de `/galeries/`** : insérer le contenu de `dist/fragment-galeries.html` entre la section « Utilisées dans des projets » et la section « Thèmes », dans la même enveloppe que « Thèmes ». Il contient :
   - la `<section class="h-entree">` du bouton (attribut `style="--bande:url(…)"` : la bande de photographie, la photo 38694055 de Villandry, servie par Pexels) ;
   - la balise `<script … defer>` de l'amorce.

   Le dialogue (`#voile`, `#monde`) n'est pas dans le gabarit : le script l'ajoute à la fin de `<body>`.
2. **Styles** : ajouter `bouton.css` à `style.css`. Il attend les variables `--police`, `--h-fond`, `--h-encre` et `--h-doux`. Reliez-les aux variables du site, ou remplacez-les par leurs valeurs : Archivo, `#fff`, `#121212`, `#6b6b70`, relevées sur le site le 28 nov. 2026. Le reste des styles se charge au premier clic.
3. **Fichiers statiques** : servir les fichiers de `dist/` sous `/statique/rubrique-monde/`, avec le même suffixe de version que `style.css` (`?v=…`) si le site en met un.

## 5. Chargement au premier clic

L'amorce ne charge rien avec la page.
- Au survol, au toucher ou au focus du bouton, elle précharge la feuille de style, puis les données, puis le script.
- Au clic, elle attend la fin du chargement, puis rejoue le clic : l'ouverture se joue normalement.
- Échap pendant le chargement annule l'ouverture.
- Une adresse `#monde…` à l'arrivée sur la page charge tout de suite (lien direct).
- Si un fichier ne se charge pas, le bouton revient à son état de départ. On peut alors cliquer de nouveau.

## 6. Polices

- **Archivo** : celle du site (`/statique/archivo.woff2`). Elle doit couvrir l'axe de largeur (`wdth` 62 à 125) : la rubrique emploie `font-stretch` de 68 % à 125 %. Vérifiez que la police servie est la version variable ; sinon les noms étroits s'élargiront.
- **Newsreader** (noms des médias, chiffres du compteur) : licence SIL Open Font, Google Fonts. **À servir par le site**, comme Archivo : ajoutez un `@font-face` vers `/statique/newsreader.woff2` (axes `opsz` 6 à 72, `wght` 400 à 600). La démonstration l'appelle encore chez Google Fonts ; le site ne doit pas le faire. Sans elle, la pile se replie sur Georgia.

## 7. Images

Toutes les images viennent de Pexels, comme le reste du site, en `https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&cs=tinysrgb&w=600` (vignettes) et `w=1300` (grandes) ; champs `vignette` et `grande` de `rubrique-monde.json`. Aucune image n'est embarquée. Le site emploie `srcset` (300 à 1300 w) : on peut l'ajouter dans `rubrique-monde.js`, fonctions `indexHTML` et `ficheHTML`.

## 8. Ce qui doit continuer à marcher

- **Liens directs** : `/galeries/#monde` (index) et `/galeries/#monde/photo-<id>` (fiche). Exemple : `#monde/photo-34500384`, Cognac.
  - Pour un visiteur arrivé ainsi, « Fermer » devient « Fermer, vers les galeries » et ramène au bouton.
  - En lecture ordinaire, « Fermer » ou Échap ramène au bouton, à la même hauteur de lecture.
- **Mouvement réduit** (`prefers-reduced-motion`) : pas d'ouverture, pas de vagues ni de respiration du globe ; l'état final s'affiche, net.
- **Téléphone** : le globe en haut, l'affiche compacte en dessous ; le premier regard se lit au premier écran (contrôlé à 390 × 844).
- **Sans WebGL** : un message le dit, et la liste et les fiches restent complètes.
- **Clavier** : tabulation, focus visible, flèches gauche et droite entre les fiches, Échap.
- « Fermer » reste visible et cliquable pendant l'ouverture ; « Passer l'ouverture » la coupe.

## 9. Contrôler

Voir `controle/LISEZ-MOI.md`. En bref : `python3 controle/scenario.py http://127.0.0.1:<port>/galeries/` contre le site servi en local. Il faut 87 contrôles réussis sur 87, comme sur `demo/index.html`. Puis montrer la page à Karl, sur Safari et sur son iPhone (jamais essayés, voir `A-VERIFIER.md`).

## 10. Mettre à jour

- Une parution confirmée de plus : l'ajouter dans `donnees/rubrique-monde.json`, sous sa photo. Champs : `id`, `nom`, `support`, `texte`, `titre`, `date`, `url`, `hote`, `lien`, `langue`, `lieu` (ou `null` : « en ligne, lieu non établi »), `raconte`. L'ajouter aussi à `repertoire` et ajuster `total`, puis `node construire.mjs`.
- Une photo nouvelle :
  1. donner son lieu de prise (`origine`) et son titre court (`titre`) ;
  2. calculer sa palette avec `python3 sources/outils/palette.py <original.jpeg>` ;
  3. mettre à jour `controle/comptes-attendus.json`.
- Le registre complet de traçabilité reste chez Karl. Ce paquet en contient l'extrait publiable : les parutions confirmées, tiers.
