# Vidéos diaporama des carrousels

Ce programme transforme un carrousel RedNote en vidéos : chinois, français et anglais,
format 3:4 (1080 × 1440 pixels), musique libre de droits comprise. Il a fabriqué les
quinze vidéos des cinq premiers carrousels (27 et 28 septembre 2026). Relancé le
28 septembre depuis le dépôt, il en a refait trois : les images calculées étaient
identiques au pixel près, le son identique. Seul l'encodage final varie d'une machine
à l'autre, sans différence visible.

Il tourne dans une session Claude Code, pas sur GitHub Actions. Règles des vidéos
(textes, musique, versions françaises) : `reseaux/README.md`, « Vidéos diaporama des
carrousels ». Plan d'amélioration : `docs/plan-videos.md`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `donnees.py` | Pour chaque carrousel : photos, textes des trois langues, musiques. Adresses et crédits des musiques. |
| `fabrique.py` | Commandes : préparer, cartes, vidéos, musique, aperçu. |
| `diaporama.py` | Moteur : zoom lent, fond flou, sous-titres, fondus, encodage. |
| `diapositive.py` | Diapositive de carrousel au style RedNote (photo en paysage sur fond flou). |
| `travail/` | Dossier de travail, ignoré par git : photos, musiques, polices, vidéos. |

## Faire les vidéos, pas à pas

1. Installer les deux outils (une fois par session) :
   `pip install pillow imageio-ffmpeg`
2. Déposer la couverture et l'image de fin chinoises de chaque carrousel dans
   `reseaux/videos/travail/carrousels/` : ce sont les images 1 et 9 de la page des
   carrousels RedNote (https://claude.ai/artifact/MpieDE6XVwk37bEa8quksx). Une
   session les récupère avec l'outil Artifact, action `read` avec
   `paths: ["images/04-roadtrip-01.jpg", "images/04-roadtrip-09.jpg"]`, puis les copie
   dans ce dossier sous le même nom (`04-roadtrip-01.jpg`…).
3. Télécharger les photos, musiques et polices :
   `python3 reseaux/videos/fabrique.py preparer 04-roadtrip`
   Les photos viennent d'images.pexels.com, les musiques d'Internet Archive et
   d'incompetech.com, les polices de Google Fonts. Si un site répond « 503 », il est
   momentanément indisponible : réessayer plus tard.
4. Fabriquer les cartes (couvertures et fins française et anglaise, petits cours de
   français) :
   `python3 reseaux/videos/fabrique.py cartes 04-roadtrip`
5. Vérifier la planche de contrôle (le milieu de chaque plan, une ligne par langue) :
   `python3 reseaux/videos/fabrique.py apercu 04-roadtrip`
6. Fabriquer les vidéos (environ cinq minutes pour trois vidéos sur quatre
   processeurs) :
   `python3 reseaux/videos/fabrique.py videos 04-roadtrip`
7. Les vidéos sont dans `reseaux/videos/travail/sortie/Caroussels/`, rangées par
   langue, avec le fichier « Musiques et licences ». Les envoyer à Karl une par une
   (30 Mo au plus par fichier), la langue dans le nom ; il les range sur son Mac dans
   `Documents Locaux/Caroussels`.

Le filtre des commandes retient les vidéos dont le nom « carrousel-langue » le
contient : `04-roadtrip` (les trois langues), `fr` (toutes les vidéos françaises),
`05-bordeaux-zh` (une seule vidéo). Sans filtre, tout est fait.

## Changer la musique sans tout recalculer

Modifier `musique` ou `musique_fr` dans `donnees.py` (ajouter le morceau à `MUSIQUES`,
avec son adresse et son crédit), relancer `preparer`, puis :
`python3 reseaux/videos/fabrique.py musique 04-roadtrip`
L'image déjà calculée est reprise telle quelle. Une musique sous licence CC BY ou
CC BY-SA demande aussi `credit_fr` (ou `credit_en`), écrit sur l'image de fin : relancer
alors `cartes` et `videos`.

## Ajouter un carrousel

Dans `donnees.py`, copier une entrée de `CARROUSELS` et la remplir :

- `cle` (`06-sujet`) et `fichier` (nom des vidéos : `6 - Sujet`) ;
- `photos` : numéro dans le carrousel, puis numéro Pexels de la photo ;
- `musique` (chinois et anglais : classique) et `musique_fr` (pop), prises dans
  `MUSIQUES` ;
- pour chaque langue, la `couverture` (en chinois, l'image 1 du carrousel ; en
  français et en anglais : surtitre, titre, mots du bas, mention des photos), les
  `plans` (numéro de la photo, texte) et le `lecon` (chinois et anglais seulement).

Les textes chinois et français reprennent mot pour mot les textes validés du
carrousel ; l'anglais est traduit du français. Relire la ligne éditoriale de
`CLAUDE.md` : pas de « photographe français » ni de « ma fiancée » en français.

## Diapositive de carrousel

`diapositive.py` refait une image de carrousel RedNote au style des carrousels
existants (photo en paysage entière sur fond flou, étape en doré, légende, compteur) :

    python3 reseaux/videos/diapositive.py photo.jpg 4 9 "第2站 · 加利西亚（西班牙）" "日全食当晚，人们在加利西亚山顶坐看金色日落" zh sortie.jpg

Il a servi à ajouter la photo du soir de l'éclipse au road trip. Les photos en
portrait, la couverture et l'image de fin ne sont pas encore reproduites :
c'est la première étape du plan d'amélioration.
