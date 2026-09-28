# Vidéos des carrousels

Deux programmes transforment un carrousel RedNote en vidéos, en chinois, en français et
en anglais, musique libre de droits comprise :

- **le studio** (`studio.py`, depuis le 28 septembre 2026) : vidéos rythmées, calées sur
  la musique, dans les formats des réseaux (9:16 et 3:4), avec couvertures, sous-titres
  et contrôle qualité automatique. C'est lui qu'il faut employer ;
- **le premier programme** (`fabrique.py`, 27 septembre 2026) : les quinze diaporamas
  3:4 déjà livrés. Il reste intact pour pouvoir les refaire à l'identique (voir en fin de
  page).

Les deux tournent dans une session Claude Code, pas sur GitHub Actions. Règles des
vidéos (textes, musique, versions françaises) : `reseaux/README.md`, « Vidéos diaporama
des carrousels ». Cahier des charges et plan d'amélioration : `docs/plan-videos.md`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `donnees.py` | Pour chaque carrousel : photos, textes des trois langues, accroche, musiques. Adresses et crédits des musiques. |
| `studio.py` | Commandes du studio : preparer, planche, videos, couvertures, qualite. |
| `montage.py` | Moteur du studio : accroche, sous-titres animés, cadrages guidés par le sujet, transitions, barre de progression, fin, encodage, son. |
| `rythme.py` | Analyse de la musique : temps, accents, premiers temps de mesure, attaques des notes. |
| `qualite.py` | Contrôle qualité : le cahier des charges en tests, rapport lisible. |
| `fabrique.py`, `diaporama.py` | Premier programme (diaporamas 3:4). |
| `diapositive.py` | Diapositive de carrousel au style RedNote (photo en paysage sur fond flou). |
| `travail/` | Dossier de travail, ignoré par git : photos, musiques, polices, analyses, vidéos. |

## Faire les vidéos avec le studio, pas à pas

1. Installer les trois outils (une fois par session) :
   `pip install pillow numpy imageio-ffmpeg`
2. Télécharger les photos (4000 pixels de large), les musiques et les polices, et
   analyser les musiques et les photos (quelques minutes la première fois) :
   `python3 reseaux/videos/studio.py preparer`
   Les photos viennent d'images.pexels.com, les musiques d'Internet Archive et
   d'incompetech.com, les polices de Google Fonts. Si un site répond « 503 » ou coupe la
   connexion, relancer : ce qui est déjà téléchargé est gardé, un fichier incomplet
   jamais. Les images de la page des carrousels ne sont plus nécessaires.
3. Vérifier le montage d'une vidéo sans la fabriquer (quelques secondes) :
   `python3 reseaux/videos/studio.py planche 04-roadtrip-fr`
   Dans `travail/studio/04-roadtrip-fr-9x16/` : `planche.jpg` (une image par plan) et
   `chronogramme.png` (les notes de la musique, les coupes posées dessus, la dernière
   note en doré).
4. Aperçu rapide d'une vidéo (une image sur trois, une minute environ) :
   `python3 reseaux/videos/studio.py videos 04-roadtrip-fr --formats=9x16 --apercu`
   L'aperçu est dans `travail/studio/04-roadtrip-fr-9x16/`.
5. Fabriquer les vidéos :
   `python3 reseaux/videos/studio.py videos 04-roadtrip`
   Par défaut, chaque vidéo sort en 9:16 et en 3:4 ; `--formats=9x16` pour un seul
   format, `--formats=9x16,3x4,1x1` pour ajouter le carré (Facebook). Trois minutes
   environ par vidéo, quatre à la fois. `--hq` ajoute une version haute qualité (plus
   lourde, dans `travail/studio/<vidéo>/`) pour une mise en ligne depuis l'ordinateur.
6. Fabriquer les couvertures (3:4 et 9:16, à choisir comme couverture sur RedNote,
   Instagram ou TikTok) :
   `python3 reseaux/videos/studio.py couvertures 04-roadtrip`
7. Tout est dans `travail/sortie/Studio/`, rangé par langue (« Chinois (RedNote) »,
   « Français », « Anglais ») :
   - la vidéo 9:16, sous le nom que reconnaît Telepex (`4 - Road trip d'août (chinois).mp4`),
     30 Mo au plus ;
   - ses sous-titres (`.srt`, pour YouTube et Facebook) et ses deux couvertures ;
   - le fichier « Musiques et licences » de la langue ;
   - la version 3:4 dans le sous-dossier `3x4/`, sous le même nom.

   Envoyer à Karl les vidéos 9:16 une par une, avec les trois fichiers « Musiques et
   licences », comme pour les premières vidéos (Telepex les range dans
   `Documents Locaux/Caroussels`).

Le filtre des commandes retient les vidéos dont le nom « carrousel-langue » le
contient : `04-roadtrip` (les trois langues), `fr` (toutes les vidéos françaises),
`05-bordeaux-zh` (une seule vidéo). Sans filtre, tout est fait.

## Ce que fait le studio

Chaque vidéo suit le cahier des charges de `docs/plan-videos.md` (règles A, R, T, I, S, M
et C) :

- **Accroche** (0 à 3 s) : la vidéo s'ouvre sur une photo déjà en mouvement, en plein
  cadre, et sa promesse s'écrit mot à mot sur les premières notes : le titre de la
  couverture du carrousel (en chinois, mot pour mot ; en français et en anglais, 7 mots
  au plus). Photo de l'accroche : `accroche_photo` dans `donnees.py` (la photo 1, celle
  de la couverture, sauf indication contraire).
- **Rythme** : `rythme.py` repère dans la musique les temps, les premiers temps de
  mesure et les attaques des notes. Musique à pulsation nette (la pop des versions
  françaises) : les coupes tombent sur les temps, de préférence les premiers temps et
  les débuts de phrase ; l'image bat légèrement sur les temps forts ; des transitions
  « glissées » marquent certains changements. Piano joué en rubato (Chopin, Bach) : les
  coupes et les fondus tombent sur les notes les plus fortes. Dans les deux cas, les
  mots des sous-titres apparaissent sur les attaques des notes.
- **Barre de progression et compteur** : un segment par photo, qui se remplit en doré
  et brille sur les temps forts ; le compteur (« 03 / 08 ») bascule à chaque nouvelle
  photo, donc sur un temps. Signature « © Karl Forterre » à côté.
- **Cadrage** : une carte de ce qui attire l'œil (saillance) donne le sujet de chaque
  photo ; les mouvements (poussée, recul, travelling, bascule, révélation, dérive)
  vont vers lui, jamais deux fois le même de suite. Une photo en paysage alterne vue
  entière sur fond flou (le style des carrousels) et détail en plein cadre ; plusieurs
  sous-titres sur une même photo alternent plan large et plan serré. Une photo n'est
  jamais agrandie au-delà de sa taille réelle.
- **Sous-titres** : textes validés du carrousel, mot pour mot, coupés en sous-titres de
  deux lignes au plus (38 caractères par ligne en français et en anglais, 16 en
  chinois), de préférence après une ponctuation, affichés assez longtemps pour être lus
  (15 caractères par seconde au plus, 8 en chinois). Apostrophes et espaces insécables
  à la française. Le fond s'assombrit juste assez sous le texte pour un contraste d'au
  moins 4,5 : 1.
- **Petit cours de français** (chinois et anglais) puis **fin** : logo KF’ tracé à
  l'écran, appel à chercher « Karl Forterre » sur Pexels ; la dernière ligne tombe sur
  une note forte, puis la musique s'éteint en fondu. Crédit de la musique quand sa
  licence l'exige.
- **Formats** : zones de sécurité mesurées pour ne rien cacher sous les boutons des
  applications.

  | Format | Taille | Réseaux | Marges (haut, bas, gauche, droite) |
  |---|---|---|---|
  | 9x16 | 1080 × 1920 | Reels, TikTok, YouTube Shorts, Stories, RedNote | 250, 420, 60, 140 px |
  | 3x4 | 1080 × 1440 | RedNote, grille du profil Instagram, Facebook | 90, 150, 70, 70 px |
  | 1x1 | 1080 × 1080 | Facebook | 70, 90, 70, 70 px |

- **Son et fichier** : volume à −14 LUFS, crêtes à −1 dBTP au plus ; H.264 High, 4:2:0,
  couleurs BT.709, 30 images par seconde, son AAC 48 kHz, lecture immédiate en ligne ;
  grain très fin contre les bandes dans les dégradés (ciels, fonds flous).

## Contrôle qualité

Chaque vidéo est contrôlée dès sa fabrication ; son rapport est dans
`travail/studio/<vidéo>/qualite.txt`, une ligne par règle (✔ réussi, ✘ échec,
! à surveiller). Une vidéo en échec n'est pas livrée : elle part dans
`travail/sortie/Studio/Refusées/`. Le contrôle vérifie notamment :

- les caractéristiques du fichier (lues par ffmpeg), son poids et sa durée ;
- le volume et les crêtes (filtre ebur128 de ffmpeg) ;
- la synchronisation, **mesurée sur la vidéo finie** : décalage du son par rapport aux
  notes prévues, et coupes franches retrouvées dans l'image, à deux images (67 ms) au
  plus du temps musical ;
- l'accroche (promesse, première seconde), la durée des plans, la variété des
  mouvements, la place du sujet ;
- les sous-titres (lignes, vitesse de lecture, taille, contraste, zone de sécurité),
  la typographie, les caractères absents de la police ;
- les mots interdits de la ligne éditoriale (`CLAUDE.md`), l'absence de lien sur
  RedNote, le crédit des musiques CC BY et CC BY-SA.

Pour relancer le contrôle sur des vidéos déjà faites :
`python3 reseaux/videos/studio.py qualite 04-roadtrip`

Karl relit et approuve toujours avant de publier : le contrôle ne juge ni le sens des
textes ni la ligne politique.

## Changer un texte, une accroche ou une musique

Tout est dans `donnees.py` :

- textes des plans : `plans` de chaque langue (en chinois, les lignes validées ; en
  français et en anglais, une phrase coupée automatiquement) ;
- accroche : en chinois, `accroche` (surtitre, titre, mots du bas), repris de la
  couverture du carrousel ; en français et en anglais, le titre de `couverture`, ou
  `promesse` s'il faut plus court (7 mots au plus) ;
- photo de l'accroche : `accroche_photo` ; photo des couvertures : `couverture_photo`
  (la photo 1 par défaut) ;
- musique : `musique` (chinois et anglais) et `musique_fr` ; un morceau nouveau
  s'ajoute à `MUSIQUES` avec son adresse et son crédit. Le studio choisit seul son style
  (vif ou calme) d'après la netteté de la pulsation ; `"style": "calme"` ou
  `"style": "vif"` dans `MUSIQUES` l'impose.

Relancer ensuite `preparer` (nouvelle musique ou nouvelle photo), puis `videos`.

## Ajouter un carrousel

Dans `donnees.py`, copier une entrée de `CARROUSELS` et la remplir :

- `cle` (`06-sujet`) et `fichier` (nom des vidéos : `6 - Sujet`) ;
- `photos` : numéro dans le carrousel, puis numéro Pexels de la photo ;
- `musique` (chinois et anglais : classique) et `musique_fr` (pop), prises dans
  `MUSIQUES` ;
- pour chaque langue, la `couverture` (en chinois, l'image 1 du carrousel, et
  `accroche` ; en français et en anglais : surtitre, titre, mots du bas, mention des
  photos), les `plans` (numéro de la photo, texte) et le `lecon` (chinois et anglais
  seulement).

Les textes chinois et français reprennent mot pour mot les textes validés du
carrousel ; l'anglais est traduit du français. Relire la ligne éditoriale de
`CLAUDE.md` : pas de « photographe français » ni de « ma fiancée » en français.

## Premier programme : les diaporamas 3:4

Il a fabriqué les quinze vidéos des cinq premiers carrousels (27 et 28 septembre 2026) :
format 3:4, zoom lent, couverture et image de fin des carrousels. Relancé depuis le
dépôt, il les refait à l'identique (images au pixel près, son identique).

1. `pip install pillow imageio-ffmpeg`
2. Déposer la couverture et l'image de fin chinoises de chaque carrousel dans
   `reseaux/videos/travail/carrousels/` sous le nom `04-roadtrip-01.jpg` et
   `04-roadtrip-09.jpg` : ce sont les images `01.jpg` et `09.jpg` du dossier
   `reseaux/publications/<publication>/images/`.
3. `python3 reseaux/videos/fabrique.py preparer 04-roadtrip`
4. `python3 reseaux/videos/fabrique.py cartes 04-roadtrip`
5. Planche de contrôle : `python3 reseaux/videos/fabrique.py apercu 04-roadtrip`
6. `python3 reseaux/videos/fabrique.py videos 04-roadtrip` ; vidéos dans
   `reseaux/videos/travail/sortie/Caroussels/`.

Changer la musique sans tout recalculer : modifier `musique` ou `musique_fr`, relancer
`preparer`, puis `python3 reseaux/videos/fabrique.py musique 04-roadtrip`.

## Diapositive de carrousel

`diapositive.py` refait une image de carrousel RedNote au style des carrousels
existants (photo en paysage entière sur fond flou, étape en doré, légende, compteur) :

    python3 reseaux/videos/diapositive.py photo.jpg 4 9 "第2站 · 加利西亚（西班牙）" "日全食当晚，人们在加利西亚山顶坐看金色日落" zh sortie.jpg

Il a servi à ajouter la photo du soir de l'éclipse au road trip. Les photos en
portrait, la couverture et l'image de fin ne sont pas encore reproduites (chantier V1
de `docs/plan-videos.md`).
