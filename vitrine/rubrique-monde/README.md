# Rubrique « Mes photos utilisées dans le monde » (version 4A)

Bouton de la page française des galeries (`/galeries/`), entre la bande « Utilisées dans des
projets » et les « Thèmes ». Au clic, un globe de nuit relie chaque photo à ses parutions,
puis chaque photo a son affiche. Paquet d'intégration reçu de Karl le 28 novembre 2026 :
mode d'emploi détaillé dans `LISEZ-MOI-INTEGRATION.md`, points à vérifier dans
`A-VERIFIER.md`.

## Ce qui est en place dans le site

- `fragment-galeries.html` : le bouton. `build.py` (fonction `rubrique_monde`) l'insère sur
  la page française des galeries seulement : la rubrique est écrite en français.
- `../statique/style.css` : les styles du bouton, à la fin du fichier.
- `../statique/rubrique-monde/` : l'amorce (chargée avec la page) ; les styles, les données
  et le script (three.js et Motion inclus), chargés au premier clic seulement.
- `../statique/newsreader.woff2` : la police Newsreader (SIL Open Font License), servie par
  le site ; aucun appel à Google Fonts.

La tâche de nuit ne lance ni Node ni npm : elle publie les fichiers déjà construits.

## Mettre à jour les données

Après une modification de `donnees/rubrique-monde.json` (une parution, une photo) :

    cd vitrine/rubrique-monde/sources
    npm ci
    node construire.mjs --base /statique/rubrique-monde/
    cp dist/rubrique-monde*.js dist/rubrique-monde.css ../../statique/rubrique-monde/
    cp dist/fragment-galeries.html ..

`dist/` et `node_modules/` ne vont pas dans le dépôt. Ensuite, le contrôle :
`python3 controle/scenario.py http://127.0.0.1:8000/galeries/` contre le site construit
(`python3 vitrine/build.py --max-appels 0`, puis `python3 -m http.server 8000` dans `_site`).

## Écart corrigé à l'intégration

La démonstration du paquet cachait tout élément `[hidden]` ; le site, non. Le dialogue
fermé restait donc posé sur la page et captait les clics. `sources/styles/rubrique.css` cache
désormais lui-même `#voile`, `#monde` et leurs éléments `[hidden]`. La police Newsreader y
est aussi déclarée, servie par le site.

## Retouches demandées par Karl (28 novembre 2026)

- Téléphone : le globe ne montre que le lieu de prise de vue et les pays ; flèches entre les photos en tête de fiche.
- Sur chaque fiche, le globe s'approche du lieu de prise de vue.
- Corps de texte en Newsreader, à empattement.
- Bouton « Son » retiré : le son synthétisé reste coupé.
- Téléphone, index : le globe ne se fait plus glisser ; une démonstration continue va d’N lieu à l’utre (3,6 s chacun), s’en approche, n’llume que ses arcs et ne nomme que lui.
