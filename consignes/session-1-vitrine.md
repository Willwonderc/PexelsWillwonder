# Session 1 — Site de photographe

À lancer dans une nouvelle session sur claude.ai/code, sur ce dépôt et dans
l'environnement qui contient la clé `PEXELS_API_KEY`. Le but est le référencement :
chaque photo doit avoir sa propre page, bien décrite, qui mène vers Pexels pour le
téléchargement. Consigne à coller telle quelle :

```text
Crée mon site de photographe, statique et bilingue (français et anglais),
pensé pour le référencement de mes photos Pexels
(profil : https://www.pexels.com/@karl-forterre-28489473).

Source : la liste de mes photos dans atelier/inventaire.csv (numéros Pexels).
Lis la fiche de chaque photo avec l'API Pexels, point d'accès « Photo »
(clé dans la variable d'environnement PEXELS_API_KEY), et garde les fiches
en cache dans le dépôt : l'API limite à environ 200 appels par heure, le
premier remplissage prendra donc plusieurs heures. Titres et mots-clés :
ceux de atelier/resultats/*.csv quand ils existent, sinon le titre et le
texte alternatif de Pexels ; jamais les textes « Free stock photo of … ».
Traduis titres et descriptions en français.

Contenu :
- une page par photo : titre, description, mots-clés, lieu, texte
  alternatif, et un bouton « Télécharger gratuitement sur Pexels » vers sa
  page Pexels (aucun téléchargement direct depuis le site) ;
- des galeries par thème et par lieu, composées d'après les titres et
  mots-clés, dans un fichier facile à modifier ;
- une page d'accueil avec une sélection, et une page « À propos » avec un
  emplacement pour mon texte ;
- référencement : title et description uniques par page, données
  structurées schema.org ImageObject (auteur, licence Pexels, page
  d'obtention de la licence), plan du site XML avec les images, balises
  Open Graph, versions française et anglaise liées (hreflang) ;
- un flux RSS par galerie, pour Pinterest ;
- une mesure d'audience sans cookies (GoatCounter) qui compte les clics
  vers Pexels, avec un emplacement pour mon identifiant ;
- la mention « Photos provided by Pexels ».

Images : servies depuis Pexels (adresses fournies par l'API), dans des
tailles adaptées à chaque écran.

Automatisation : une GitHub Action reconstruit le site chaque nuit, ne lit
que les photos nouvelles, et le publie sur GitHub Pages. La clé passe par
les secrets du dépôt, jamais dans le code. Prévois un domaine personnalisé,
par exemple un sous-domaine de karlforterre.fr, à activer plus tard.

Style : sobre, la photo d'abord, rapide sur mobile.
Termine par un mode d'emploi simple (README.md) : ajouter une photo,
modifier une galerie, changer l'ordre des pages.
```
