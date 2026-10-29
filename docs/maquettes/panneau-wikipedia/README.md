# Panneau « Sur Wikipédia » : les maquettes

Le 28 octobre 2026, Karl a demandé que ses photos versées dans Wikipédia soient présentées
sur le site photo, sous « Couleurs » de la page des galeries : « un panneau interactif dans
lequel on pourrait faire défiler les photos et avoir des éléments de présentation et aller
vers l'article wikipédia », « cohérent graphiquement avec le reste du site mais de très
moderne dans son fonctionnement et le découpage des éléments », avec une mise en valeur
« exceptionnelle ». Ce dossier garde les cinq propositions qui lui ont été présentées, dans
un seul fichier HTML, et ce qu'il en a retenu.

## Les cinq propositions

1. **La salle de projection** : une photo à la fois, en grand (deux tiers du panneau, zoom
   lent, fondu enchaîné, nom du lieu sur la photo). À droite, le cartel prend la couleur
   moyenne de la photo : numéro, langue, « Article de Wikipédia », titre de l'article,
   partie, légende dans la langue de l'article, titre de la photo, boutons « Lire
   l'article ↗ » et « Voir la photo », licence et lien vers Commons. Les photos passent
   seules toutes les huit secondes, avec une barre par photo. Flèches, clavier, glissement
   du doigt.
2. **L'atlas** : carte de la France et du nord de l'Espagne, dessinée d'avance. Les
   épingles numérotées gardent leur taille à l'écran. Au survol, un aperçu ; au clic, la
   carte se rapproche de l'épingle. À côté, la liste des lieux et la fiche ; des pastilles
   trient par langue.
3. **Le fil** : un récit au défilement, dans un cadre. La photo reste en place et se
   découvre de bas en haut à chaque chapitre ; un rail de points montre l'avancée.
4. **Recto verso** : une pile de cartes qu'on fait glisser. Retournée, la carte montre la
   photo dans l'article de Wikipédia (aperçu dessiné par le site).
5. **La mosaïque vivante** : une mosaïque de tailles variées, un tri par langue animé, des
   chiffres qui s'animent, une visionneuse plein écran.

## Le choix de Karl (29 octobre 2026)

> « Mon préféré est la salle de projection auquel il faudrait retirer cette bande
> disgracieuse et il faudrait si c'est possible intégrer l'atlas par une animation quelque
> en cliquant sur le bouton localisation dans la partie droite avec la description
> wikipedias pour faire apparaître la position de la photo sur la carte. et si on pouvais
> intégrer un système de défilement en plus comme sur "le fil" ca serait parfait. »

- La « bande disgracieuse » est la rangée des barres d'avancée, avec le nom des lieux, en
  bas du panneau : sa capture d'écran la montrait.
- Le bouton de localisation va dans le cartel, la partie droite où se trouve la
  description Wikipédia. Il fait apparaître, avec une animation, la position de la photo
  sur la carte de l'atlas.
- Le défilement « comme sur le fil » : les photos avancent au défilement (molette, pavé
  tactile, doigt), avec un repère d'avancée comme le rail de points du fil.

## Les photos (au 28 octobre 2026)

| Photo Pexels | Lieu | Lon, lat | Wikipédia | Article | Partie | Légende dans l'article | Fichier Commons | Ajoutée |
|---|---|---|---|---|---|---|---|---|
| 39423921 | Irun | -1.7889, 43.3381 | eu | Irungo Udala | Udaletxea | Irungo udaletxearen fatxada. | Irun - hôtel de ville (Casa consistorial) - 2026.jpg | 2026-10-28 |
| 39228699 | Gijón | -5.6130, 43.5250 | ast | Universidá Llaboral de Xixón | La torre | La torre y la ilesia de la Universidá Llaboral. | Gijón - Universidad Laboral, tour et église - 2026.jpg | 2026-10-28 |
| 39376205 | Bordeaux | -0.5747, 44.8452 | fr | Monument aux Girondins | Description | Le Génie de la Liberté brisant ses chaînes, au sommet de la colonne. | Bordeaux - monument aux Girondins, Génie de la Liberté - 2026.jpg | 2026-10-28 |
| 13087478 | Moyemont | 6.5397, 48.3517 | fr | Moyemont | Géologie et relief | Chemin de terre bordé d'arbres à Moyemont, en été. | Moyemont - chemin bordé d'arbres - 2022.jpg | 2026-10-28 |
| 39182179 | Buzy | -0.4600, 43.1370 | fr | Dolmen de Buzy | Description | La table de couverture en marbre gris, longue de 3,75 m, et ses orthostates. | Buzy - dolmen - 2026.jpg | 2026-10-08 |
| 38279508 | Niort | -0.4589, 46.3238 | fr | Hôtel de préfecture des Deux-Sèvres | (infobox) | (aucune) | Niort - hôtel de préfecture des Deux-Sèvres - 2026.jpg | 2026-10-08 |
| 23414381 | Niort | -0.4606, 46.3268 | fr | Église Saint-André de Niort | Extérieur | Les flèches jumelles dominent les toits de Niort. | Niort - église Saint-André au-dessus de la ville - 2024.jpg | 2026-10-06 |
| 34894959 | Îles Chausey | -1.8237, 48.8738 | fr | Phare de Chausey | Historique | La tour carrée du phare, en granite de l'île, et sa lanterne. | Îles Chausey - la tour du phare - 2025.jpg | 2026-10-06 |

Chaque fichier est versé par Karl sous licence CC BY-SA 4.0 (`{{self|cc-by-sa-4.0}}`). La
photo de la préfecture est l'image de l'infobox, en tête de l'article : ni partie ni
légende. Les deux photos de Niort partagent le même lieu : sur la carte, leurs épingles
sont décalées de quelques pixels.

## Les fichiers

- `modele.html` : les cinq propositions, sans bibliothèque. Quatre marques y sont
  remplacées à l'assemblage : `/*POLICE*/`, `/*LOGO*/`, `/*DONNEES*/` et `/*CARTE*/`.
- `assembler.py` : écrit le fichier complet, avec la police Archivo et le logo du site
  intégrés, les données des photos (lues aussi dans `vitrine/donnees/fiches.json` pour la
  taille et la couleur) et la carte.
- `carte.py` : a dessiné `carte.json`, les contours projetés et simplifiés et la position
  des photos, d'après les données Natural Earth (domaine public) de world-atlas 2.0.2
  (`https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-50m.json`) :
  `python3 carte.py countries-50m.json carte.json`. Projection de Mercator, longitudes
  −7,6 à 8,6, latitudes 41,2 à 51,4, 1 000 unités de large sur 915,2 de haut.
- `captures.js` : captures sur ordinateur, sur téléphone et en mode sombre, avec quelques
  gestes, et relevé des erreurs de script.

## Assembler et vérifier, en session

Le fichier assemblé et les captures s'écrivent hors du dépôt, dans le dossier de travail
de la session (`$S` ci-dessous). Chromium ne charge pas les images de images.pexels.com à
travers le proxy : les captures lui répondent avec les fichiers téléchargés par curl.

```sh
python3 docs/maquettes/panneau-wikipedia/assembler.py "$S/cinq-panneaux.html"
mkdir -p "$S/photos"
for id in 39423921 39228699 39376205 13087478 39182179 38279508 23414381 34894959; do
  for w in 800 1600; do
    curl -sS -o "$S/photos/$id-$w.jpg" "https://images.pexels.com/photos/$id/pexels-photo-$id.jpeg?auto=compress&cs=tinysrgb&w=$w"
  done
done
PW=$(npm root -g)/playwright node docs/maquettes/panneau-wikipedia/captures.js "$S/cinq-panneaux.html" "$S/photos" "$S/captures"
```

Un dernier argument (`ordi`, `tel` ou `sombre`) limite les captures à une seule vue.
