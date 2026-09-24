# Session 1 — Vitrine photo reliée à Pexels

À lancer sur claude.ai/code, sur ce dépôt et dans l'environnement qui contient la clé
`PEXELS_API_KEY`, dès que les [préparatifs](../docs/preparatifs.md) sont faits. Peut
tourner en même temps que la session 3. Consigne à coller telle quelle :

```text
Crée un site vitrine statique pour mes photos Pexels
(profil : https://www.pexels.com/@karl-forterre-28489473).

Source : mes collections Pexels, lues avec l'API Pexels (clé dans la
variable d'environnement PEXELS_API_KEY, points d'accès « My Collections »
et « Collection media »). Respecte les limites de l'API et affiche la
mention « Photos provided by Pexels ».

Contenu :
- une page d'accueil et une page par collection, textes en français et
  en anglais, soignés pour le référencement (titres, descriptions,
  textes alternatifs) ;
- chaque photo renvoie vers sa page Pexels : aucun téléchargement
  direct depuis le site ;
- un flux RSS des dernières photos ajoutées ;
- une mesure d'audience sans cookies (GoatCounter) qui compte les clics
  vers Pexels, avec un emplacement pour mon identifiant.

Automatisation : une GitHub Action reconstruit le site chaque nuit et le
publie sur GitHub Pages. La clé API passe par les secrets du dépôt,
jamais dans le code.

Style : sobre, grille régulière, rapide sur mobile.
Termine par un fichier LISEZMOI expliquant simplement comment ajouter
une photo et changer l'ordre des pages.
```
