# Plan : un studio vidéo au niveau d'une agence

Feuille de route rédigée le 28 septembre 2026. Point de départ :
- le programme `reseaux/videos/` a fabriqué 15 vidéos diaporama : cinq carrousels
  RedNote en chinois, en français et en anglais, au format 3:4, de 40 à 63 secondes ;
- relancé depuis le dépôt sur le road trip, il a recalculé ses trois vidéos à
  l'identique (images au pixel près, son identique) ;
- les vidéos sont publiées à la main sur RedNote et sur le Facebook personnel de Karl ;
- Instagram (@karl_forterre, compte « Créateur ») reçoit chaque matin la photo du jour
  par l'API officielle (session H, 28 septembre), mais pas encore de vidéos ;
- chaque vidéo se fabrique dans une session Claude, donc avec du crédit.

## Objectif

**Que chaque vidéo qui sort du programme soit acceptée telle quelle par une agence de
communication exigeante ou par un créateur professionnel.** Ce niveau se voit à
l'accroche, au rythme, aux sous-titres, au son, aux formats propres à chaque réseau, à la
marque et à la conformité, et il se mesure aux résultats.

Cinq principes :
1. **Karl valide, le studio produit.** Karl n'ouvre jamais un logiciel de montage : il
   choisit un sujet, relit, enregistre sa voix s'il le souhaite, et approuve.
2. **Un sujet décrit une fois, toutes les sorties.** Toutes les langues, tous les formats
   et tous les réseaux, chacun avec son kit de publication.
3. **Rien ne sort sans contrôle qualité.** Le cahier des charges ci-dessous devient une
   batterie de tests automatiques : une vidéo qui échoue n'est pas livrée.
4. **Gratuit et libre.** Outils libres, tâches GitHub (gratuites pour un dépôt public),
   aucun service payant, aucun secret dans le code.
5. **Mesurer pour progresser.** Chaque vidéo est suivie, et les règles évoluent d'après
   les résultats.

## Le niveau visé : le cahier des charges « agence »

Ces règles reprennent les pratiques des créateurs et des agences sur les réseaux courts
(Reels, TikTok, Shorts, RedNote) et les consignes publiées par les plateformes. La
colonne « Contrôle » indique qui vérifie : le programme (automatique), l'œil d'une
session ou Karl.

### Accroche et structure

| | Règle | Contrôle |
|---|---|---|
| A1 | La première image est la photo la plus forte du sujet, déjà en mouvement. Pas de logo ni de carton de titre seul en ouverture. | automatique |
| A2 | Une promesse à l'écran dès la première seconde : 7 mots au plus en français et en anglais, 14 caractères en chinois. | automatique |
| A3 | Structure : accroche (0 à 3 s), récit, point d'orgue (l'image la plus spectaculaire vers la fin), appel à l'action. | gabarit et œil |
| A4 | Couverture choisie à part (3:4, titre lisible en vignette), qui n'est pas forcément la première image. | automatique |
| A5 | Durées : 15 s (teaser), 30 à 45 s (Reels, Shorts, TikTok), 60 à 90 s (récit RedNote et Facebook), jusqu'à 3 min (version longue ; Reels et Shorts l'acceptent). | automatique |
| A6 | Une fin courte (1 à 2 s) et adaptée au réseau ; pour les Reels, une version qui boucle : la dernière image s'enchaîne sur la première. | automatique |

### Rythme et mouvement

| | Règle | Contrôle |
|---|---|---|
| R1 | Plans de 1,5 à 3 s dans l'accroche, puis de 2,5 à 5 s (jusqu'à 6 s sur RedNote, pour lire) ; aucune image immobile. | automatique |
| R2 | Coupes calées sur les temps forts de la musique, à deux images près. | automatique |
| R3 | Mouvements variés et motivés : poussée vers le sujet, travelling sur un panorama, révélation, recul final. Jamais deux fois le même d'affilée. | automatique |
| R4 | Le sujet (visage, monument, horizon, soleil) n'est jamais coupé par le recadrage ni caché par le texte. | automatique |
| R5 | Transitions choisies : coupe franche par défaut ; fondu, fondu au noir ou raccord de mouvement aux changements d'étape. | automatique |

### Texte et sous-titres

| | Règle | Contrôle |
|---|---|---|
| T1 | Deux lignes au plus à l'écran : 38 caractères par ligne en français et en anglais, 16 en chinois. | automatique |
| T2 | Temps de lecture suffisant : 15 caractères par seconde au plus (8 en chinois). Le récit complet va dans le texte de la publication, pas à l'écran. | automatique |
| T3 | Texte lisible sur téléphone : corps du texte d'au moins 4 % de la largeur de l'image (43 px en 1080) ; contraste d'au moins 4,5 pour 1 avec le fond (norme d'accessibilité WCAG), grâce à une ombre ou à une plaque. | automatique |
| T4 | Zones de sécurité : rien d'important sous les boutons et les légendes des applications. En 9:16, environ 220 px en haut, 400 px en bas et une marge à droite ; un gabarit mesuré par réseau. | automatique |
| T5 | Typographie soignée : espaces insécables et guillemets « » en français, ponctuation chinoise pleine chasse, orthographe vérifiée dans les trois langues. | automatique (en partie) |
| T6 | Sous-titres animés mot à mot quand une voix parle ; fichier de sous-titres (SRT) livré à part pour YouTube et Facebook. | automatique |

### Image et formats

| | Règle | Contrôle |
|---|---|---|
| I1 | Formats natifs, sans bandes noires : 9:16 (1080 × 1920) pour Reels, TikTok, Shorts, Stories et RedNote ; 3:4 (1080 × 1440) pour RedNote et la grille du profil Instagram, en 3:4 depuis janvier 2025 ; 1:1 et 16:9 pour Facebook et YouTube. | automatique |
| I2 | Passage d'un format à l'autre par un recadrage guidé par le sujet, pas par le centre de l'image. | automatique |
| I3 | Encodage : 30 images par seconde constantes, H.264 High, 4:2:0, couleurs BT.709, son AAC à 48 kHz. Une version haute qualité pour la mise en ligne (les réseaux recompressent), une version légère (30 Mo au plus) pour l'envoi. | automatique |
| I4 | Couleurs homogènes dans une même vidéo ; pas de bandes visibles dans les dégradés et les fonds flous (grain léger). | œil et automatique |
| I5 | Photos à pleine résolution, jamais agrandies au-delà de leur taille réelle. | automatique |

### Son

| | Règle | Contrôle |
|---|---|---|
| S1 | Volume : −14 LUFS intégrés (volume moyen perçu, l'usage des plateformes), crêtes à −1 dBTP au plus. | automatique |
| S2 | Musique libre de droits, licence vérifiée, crédit exigé présent ; la vidéo se termine sur une fin de phrase musicale, pas sur une coupure. | automatique |
| S3 | Habillage sonore discret : ambiances (vagues, vent, ville) et effets de transition tirés de banques de sons libres (CC0). | automatique |
| S4 | Voix au premier plan, musique baissée pendant qu'elle parle. | automatique |
| S5 | Une version sans musique, pour ajouter dans l'application un son en vogue (配乐 sur RedNote, musique d'Instagram). | automatique |

### Marque

| | Règle | Contrôle |
|---|---|---|
| M1 | Charte KF’ écrite et appliquée : logo (`vitrine/statique/logo.svg`), couleurs (or, blanc, noir profond), polices (Archivo, Noto Sans SC), gabarits de titre, de sous-titre, de bas de titre et de fin. | gabarits |
| M2 | Signature « © Karl Forterre » discrète ; logo animé d'une seconde au plus, jamais en ouverture. | automatique |
| M3 | Aucun logo d'un autre réseau sur la vidéo : les réseaux défavorisent les vidéos marquées par un concurrent. | automatique |
| M4 | Même allure dans les trois langues et sur tous les réseaux. | œil |

### Conformité

| | Règle | Contrôle |
|---|---|---|
| C1 | Ligne éditoriale de `CLAUDE.md` : mots interdits selon le public (en français : « photographe français », « en France, on », « ma fiancée »), ligne politique. Karl relit et approuve avant toute publication. | automatique et Karl |
| C2 | Droit à l'image : pas de personne reconnaissable en gros plan sans son accord ; floutage possible. | automatique et Karl |
| C3 | Règles des réseaux : sur RedNote, ni lien ni invitation à quitter l'application (`docs/promotion-chine.md`). Côté Pexels, toute mention renvoie à la page de la photo. | automatique |
| C4 | Licences : crédit des musiques CC BY ; mention de la licence de la vidéo quand la musique est CC BY-SA ; fichier « Musiques et licences ». | automatique |
| C5 | Accessibilité : sous-titres toujours présents, texte alternatif dans le kit, pas de clignotement rapide. | automatique |
| C6 | Instagram : tout en français (texte à l'écran, sous-titres, légende), dans un style proche de l'expression de Karl (`reseaux/style-karl.md`). | automatique (langue) et Karl |

### Livraison et suivi

| | Règle | Contrôle |
|---|---|---|
| L1 | Nommage : date, sujet, réseau, format, langue, version (`2026-10-05_road-trip_reels_9x16_fr_v2.mp4`). | automatique |
| L2 | Fiche de livraison par vidéo : durée, format, poids, volume, musique, licence, résultat du contrôle qualité. | automatique |
| L3 | Kit de publication par réseau et par langue : titre, texte, hashtags, couverture, texte alternatif, heure conseillée. | automatique |
| L4 | Page d'aperçu où Karl valide chaque vidéo avant publication. | Karl |
| L5 | Suivi de chaque vidéo : vues, durée moyenne regardée, part de visionnages complets, partages, enregistrements, abonnés gagnés. | automatique si une API le permet, sinon à la main |

## Où en est le programme

Acquis : un mouvement fluide et précis (sous le pixel), trois langues, des sous-titres,
des musiques aux licences vérifiées et créditées, la ligne éditoriale respectée, des
vidéos reproductibles à l'identique.

Écarts avec le niveau visé :

| Règle | Aujourd'hui | À faire |
|---|---|---|
| A1, A2 | La vidéo s'ouvre sur une couverture fixe de 3,2 s. | Ouvrir sur la meilleure photo, en mouvement, avec une promesse. |
| R1 | Plans de 4,4 à 10 s, tous au même tempo. | Accroche rapide, puis rythme variable. |
| R2 | Coupes régulières, sans lien avec la musique. | Couper sur les temps forts. |
| R3, R4 | Le même zoom lent (6 à 8 %) partout, avec un léger glissement, sans viser le sujet. | Mouvements variés, dirigés vers le sujet. |
| T1, T2 | Jusqu'à 4 lignes, le récit entier à l'écran. | Deux lignes courtes ; le récit dans la légende. |
| T6 | Sous-titres incrustés seulement. | Mot à mot et fichier SRT. |
| I1 | Format 3:4 seulement. | 9:16, 3:4, 1:1 et 16:9, zones de sécurité. |
| S1 | −16 LUFS, crêtes à −1,5 dBTP. | −14 LUFS et contrôle automatique. |
| S3 à S5 | Musique seule. | Habillage sonore, voix, version sans musique. |
| M1 | Charte implicite ; Liberation Sans dans les vidéos, Archivo dans les carrousels. | Charte écrite, une seule famille de polices. |
| C1 | Relecture à l'œil. | Contrôle automatique, puis accord de Karl. |
| L3, L4 | Textes RedNote sur une page ; rien pour les autres réseaux. | Kits par réseau, page de validation. |
| Carrousels | Le programme d'origine des images RedNote est perdu ; seules les diapositives de photos en paysage sont reproduites. | Tout le carrousel regénéré, fidèle aux images existantes. |
| Production | En session (crédit), 5 minutes de calcul pour trois vidéos, images de carrousel à récupérer à la main. | Tâche GitHub, sans session. |

## Le studio visé

Le parcours d'une vidéo, du sujet à la publication :

1. **Le sujet** : Karl le choisit, ou le studio en propose un (nouvelle série, photos les
   plus vues, date anniversaire).
2. **Le projet** : un fichier lisible (`reseaux/videos/projets/<sujet>.ini`) décrit
   photos, textes des trois langues, musique, formats et réseaux. Le studio le prépare à
   partir de la série (`vitrine/series.ini`) et des titres traduits
   (`vitrine/donnees/textes-*.csv`) ; Karl relit, ou enregistre sa voix sur son iPhone.
3. **La fabrication** : sur la page **Actions** du dépôt, le bouton « Run workflow » de
   la tâche « Vidéos » fabrique toutes les versions (langues, formats, durées) sur les
   machines gratuites de GitHub (4 processeurs, 16 Go de mémoire). Elle joint le
   carrousel RedNote, les kits de publication, le rapport du contrôle qualité et une
   page d'aperçu, à télécharger pendant 90 jours.
4. **La validation** : Karl regarde l'aperçu sur son téléphone et approuve ou commente.
5. **La publication** : automatique sur Instagram et YouTube après accord, kits prêts
   pour RedNote et Facebook ; les résultats sont relevés et reviennent au tableau de
   bord.

Pièces du studio, dans `reseaux/videos/` :

| Pièce | Rôle |
|---|---|
| `projets/` | Un fichier par sujet, que Karl peut lire et corriger. |
| moteur de montage | Recettes (accroche, récit, carte d'itinéraire, cours de français, fin), mouvements, transitions, typographie animée ; un montage, plusieurs formats. |
| `qualite.py` | Les règles ci-dessus en tests ; rapport lisible, une ligne par règle. |
| `carrousel.py` | Les images RedNote complètes (couverture, photos, cours, fin), en chinois et en français. |
| `son.py` | Catalogue musical, temps forts, habillage, voix, volume. |
| `publication.py` | Kits par réseau, envoi vers Instagram et YouTube, relevés. |
| `.github/workflows/videos.yml` | La tâche « Vidéos », lancée à la demande. |

## Chantiers

Chaque chantier tient en une session (deux pour V2 si nécessaire) et se termine par une
pull request. Les consignes sont prêtes à coller dans
[consignes/prochaines-sessions.md](../consignes/prochaines-sessions.md).

### V1. Fondations du studio

- Projets en fichiers `.ini` ; conversion des cinq carrousels actuels ; création d'un
  projet à partir d'une série.
- Générateur complet des carrousels RedNote (couverture, photos en portrait et en
  paysage, petit cours de français, fin) en chinois et en français. Il doit être fidèle
  aux images existantes, mesuré au pixel comme `diapositive.py`. Les vidéos ne dépendent
  plus de la page des carrousels.
- Contrôle qualité, première version : caractéristiques techniques (lues par ffprobe),
  volume, durées, longueur des textes, zones de sécurité, mots interdits, poids. Rapport
  lisible.
- Tâche GitHub « Vidéos », lancée à la demande, avec vidéos, carrousel et rapport à
  télécharger.
- Miroir des musiques dans une version publiée (« release ») du dépôt, pour ne plus
  dépendre d'Internet Archive, momentanément indisponible le 28 septembre. Leurs
  licences le permettent.

Réussi quand : un nouveau sujet, décrit dans un fichier, donne son carrousel, ses trois
vidéos et son rapport sur GitHub en moins de dix minutes, sans session Claude.

### V2. Montage au niveau agence

- Accroche : ouverture sur la photo la plus forte, promesse à l'écran ; la couverture
  devient une image à part.
- Rythme calé sur la musique : repérage des temps forts, durées de plans variables,
  coupes sur les temps.
- Cadrage intelligent : carte de ce qui attire l'œil (calcul simple, sans modèle lourd)
  et détection des visages (OpenCV, libre), pour diriger zooms et recadrages et placer
  le texte hors du sujet.
- Une grammaire de mouvements et de transitions (poussée, travelling, révélation,
  raccord, fondu au noir), choisis selon l'image et le moment.
- Typographie animée : apparition mot à mot, surlignage, plaques de sous-titres
  lisibles ; gabarits de marque (logo animé, bas de titre, fin courte).
- Carte animée de l'itinéraire pour les récits de voyage : le tracé se dessine d'étape
  en étape sur un fond Natural Earth (domaine public).
- Couleurs homogènes (courbe propre à chaque vidéo) et grain léger contre les bandes.
- Calcul accéléré et aperçu rapide en basse définition.

Réussi quand : les cinq vidéos actuelles, refaites, passent toutes les règles A, R, T et
M, et Karl les préfère aux anciennes quand il les voit côte à côte.

### V3. Son et voix

- Volume à −14 LUFS et crêtes à −1 dBTP ; musique coupée sur une fin de phrase ;
  musique baissée sous la voix.
- Catalogue musical en fichier (morceau, ambiance, tempo, licence, crédit, adresse), avec
  un choix automatique qui respecte les règles de `CLAUDE.md` : classique en chinois et
  en anglais, pop en français, morceaux très employés en publicité.
- Habillage sonore tiré de banques de sons libres (CC0).
- Voix : Karl enregistre le récit sur son iPhone (Dictaphone) et dépose le fichier. La
  transcription et les sous-titres mot à mot se font automatiquement avec Whisper
  (logiciel libre), et le montage se cale sur la voix. En option, une voix de synthèse
  libre (Piper) pour l'anglais et le chinois, si la licence de la voix le permet ; à
  défaut, les sous-titres seuls.
- Version sans musique pour chaque vidéo.

Réussi quand : toutes les vidéos passent les règles S, et une vidéo racontée par Karl ne
lui demande pas plus d'un quart d'heure.

### V4. Formats natifs et diffusion

- Déclinaisons 9:16, 3:4, 1:1 et 16:9 d'un même montage, avec les zones de sécurité
  mesurées de chaque réseau ; durées par réseau (15 s, 30 à 45 s, 60 à 90 s, 3 min).
- Kits de publication par réseau et par langue, et page d'aperçu où Karl valide. Sur
  Instagram, tout est en français, dans le style de Karl (règle C6).
- Instagram : Reels publiés par l'API officielle (conteneur « REELS », 100 publications
  par jour au plus), avec la connexion et le jeton de la photo du jour (session H),
  en file d'attente, seulement après accord de Karl.
- YouTube Shorts : API officielle, environ six envois par jour avec le quota gratuit.
  Les vidéos envoyées par une application non vérifiée restent privées : il faut
  passer l'audit gratuit de Google pour publier en public.
- Une page par vidéo sur photos.karlforterre.fr, avec le lecteur YouTube, des données
  structurées « VideoObject » et un plan de site vidéo, pour apparaître dans les
  résultats vidéo de Google.
- RedNote et Facebook : kits complets pour la publication à la main.

Réussi quand : entre l'accord de Karl et la mise en ligne sur Instagram et YouTube,
aucun geste manuel ; RedNote et Facebook ne demandent qu'un copier-coller.

### V5. Mesure et amélioration continue (après la session F)

- Relevés : Instagram Insights et YouTube Analytics par leurs API ; RedNote et Facebook
  notés à la main dans un fichier de `releves/` ; le tout dans le tableau de bord.
- Indicateurs par vidéo : spectateurs restés après 3 secondes, durée moyenne regardée,
  part de visionnages complets, partages, enregistrements, abonnés gagnés, clics vers
  le site.
- Tests A/B : deux accroches ou deux couvertures pour le même sujet. Les « Reels à
  l'essai » d'Instagram montrent d'abord une vidéo à des non-abonnés ; ils sont ouverts
  aux comptes professionnels à partir d'un certain nombre d'abonnés, seuil à vérifier
  (Karl en a 170).
- Bilan mensuel automatique : ce qui marche ajuste les règles (durées, accroches,
  musiques, heures).

Réussi quand : des objectifs chiffrés sont fixés après quatre semaines de relevés, puis
suivis chaque mois.

### V6. Explorations, plus tard

- Effet de profondeur (parallaxe 2,5D) : premier plan et fond qui glissent à des
  vitesses différentes, grâce à une carte de profondeur estimée par un modèle libre.
  Calcul lourd, à essayer sur GitHub.
- Cinémagraphes : l'eau, les nuages ou les étoiles qui bougent dans une photo fixe.
- Formats récurrents : « une photo, une histoire », « le mois en 30 secondes »,
  compilations par série, versions longues pour RedNote.
- Sous-titres dans d'autres langues, par exemple l'espagnol pour les photos d'Espagne.

## Mesures de réussite

Production, dès V1 :

| Indicateur | Cible |
|---|---|
| Vidéos livrées qui passent le contrôle qualité | 100 % |
| Temps de calcul pour un sujet (trois langues, tous formats), sur GitHub | moins de 10 minutes |
| Temps de Karl par sujet (relecture, voix éventuelle, publication à la main) | moins de 15 minutes |
| Sessions Claude pour refaire ou décliner une vidéo existante | aucune |
| Coût | 0 € |

Audience, dès V5 : spectateurs restés après 3 secondes, durée moyenne regardée,
visionnages complets, partages, enregistrements et abonnés gagnés, relevés chaque
semaine ; les cibles se fixent après quatre semaines de mesures, réseau par réseau.

## Contraintes et garde-fous

- **Gratuit** : outils libres, tâches GitHub gratuites pour un dépôt public (une tâche
  dure 6 heures au plus), API gratuites d'Instagram et de YouTube.
- **Dépôt public** : les jetons d'Instagram et de YouTube vont dans les secrets du
  dépôt, jamais dans le code ni dans la conversation.
- **Licences** : musiques CC0, CC BY ou CC BY-SA seulement, crédits exigés ; se méfier
  des fichiers marqués « domaine public » par n'importe qui (`reseaux/README.md`).
- **Réseaux** : aucun lien sur RedNote ; pas de procédé artificiel pour gonfler les
  vues ; toute mention de Pexels renvoie à la page de la photo.
- **Ligne éditoriale** : règles de `CLAUDE.md`, vérifiées par le programme et relues
  par Karl.
- **Droit à l'image** : prudence avec les personnes reconnaissables.
- **Simplicité** : chaque nouveauté arrive avec son mode d'emploi pas à pas dans
  `reseaux/videos/README.md`.

## Calendrier et crédit

| Quand | Session | Quoi |
|---|---|---|
| Octobre, si le crédit le permet | V1 | Fondations : projets, carrousels complets, contrôle qualité, tâche GitHub |
| Ensuite | V2 | Montage au niveau agence |
| Ensuite | V3 | Son et voix |
| Ensuite | V4 | Formats natifs, kits, Reels sur Instagram, YouTube |
| Après la session F | V5 | Mesure et amélioration continue |
| Plus tard | V6 | Explorations |

Les sessions prévues (A à I) passent d'abord ; H et I sont faites. Si le crédit baisse
avant le 5 novembre : V1, puis V2. Après V1, refaire une vidéo ne coûte plus de crédit :
la tâche GitHub s'en charge.

## Sources

- Instagram, Reels de 3 minutes et grille du profil en 3:4 (janvier 2025) :
  https://www.businesstoday.in/technology/news/story/instagram-head-announces-big-changes-3-minute-reels-and-new-look-for-profile-grid-461527-2025-01-21
- Instagram, « Reels à l'essai » : https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/
- Instagram, publication par l'API (Reels, 100 publications par 24 heures) :
  https://developers.facebook.com/docs/instagram-platform/content-publishing/
- YouTube, envois des applications non vérifiées bloqués en privé :
  https://developers.google.com/youtube/v3/docs/videos/insert
- GitHub, machines gratuites des dépôts publics (4 processeurs, 16 Go) :
  https://github.blog/news-insights/product-news/github-hosted-runners-double-the-power-for-open-source/
- Zones de sécurité des Reels (valeurs approchées, à mesurer) :
  https://www.outfy.com/blog/instagram-safe-zone/
- RedNote, formats vidéo (3:4 et 9:16, couverture 3:4) :
  https://resouci.com/xiaohongshu-image-size-guide-2026/
