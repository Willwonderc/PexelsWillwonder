# 3 — Atelier titres et mots-clés

Une session Claude regarde les photos et rend un tableau prêt à copier : un titre
descriptif propre à chaque cliché et jusqu'à 25 mots-clés en anglais. Pexels ne
permettant guère de modifier titres et mots-clés après publication, l'atelier sert
avant chaque import. Pour les photos déjà publiées, ses tableaux alimentent le site
de photographe.

## Mode d'emploi

1. Compresser le dossier de photos (clic droit → Compresser) et le déposer sur
   https://www.swisstransfer.com, qui fournit un lien de téléchargement gratuit.
   Les photos téléchargées depuis Pexels gardent leur nom `pexels-photo-<numéro>`,
   qui relie chaque ligne du tableau à sa page Pexels.
2. Donner ce lien à une session Claude Code ouverte sur ce dépôt. Elle télécharge
   l'archive, regarde les photos et rédige titres et mots-clés.
3. Le tableau (numéro, lien, titre, mots-clés) arrive dans `resultats/`.
4. Reporter les titres et mots-clés sur Pexels.

Les photos ne passent pas par le dépôt : rien n'est publié d'autre que les tableaux.
Autre possibilité, pour un petit lot : déposer des copies réduites (JPEG, côté long
d'environ 1600 pixels) dans `a-traiter/`, un sous-dossier par série, via Add file →
Upload files sur GitHub, puis les supprimer une fois traitées. Le dépôt étant public,
elles restent visibles dans l'historique.

## Fichiers

- [`inventaire.csv`](inventaire.csv) : les 919 photos du profil, avec pour chacune
  son lien et l'état de son titre sur Pexels (titré, sans titre ou non vérifié).
- [`resultats/ppex-photos-sans-titre.csv`](resultats/ppex-photos-sans-titre.csv) :
  titres et mots-clés rédigés le 24 septembre 2026 pour les 155 photos récentes sans
  titre et pour 2 photos pas encore publiées.

## Précaution

Aucune signature ni filigrane sur les fichiers importés chez Pexels.

## Choisir et préparer les prochains imports

Ce que montre la fiche de suivi du 24 septembre 2026 (`releves/suivi-pexels.csv`) :
89 photos retenues par la modération de Pexels sur 919, qui font 81 % des vues.

### Ce qui fait la différence : le titre et les mots-clés

| Photos | Retenues |
|---|---|
| Sans vrai titre (« Free stock photo of… ») : 351 | aucune |
| Titre en français, court ou poétique (« Rectiligne », « MOOD: MONO 1600-U ») et moins de 20 mots-clés | aucune |
| Titre descriptif et au moins 20 mots-clés : 106 | 89 (84 %) |

- Les 17 photos refusées de la dernière ligne ont toutes un titre court en français
  (« Empilement », « Ciel estival », « Fond de couleurs ») ou mal orthographié
  (« Coffe Time »). Toutes les photos à titre descriptif en anglais et à mots-clés
  nombreux ont été retenues.
- Les photos retenues ont 46 mots-clés en médiane, jamais moins de 25 ; les refusées
  en ont presque toujours moins de 10.
- En 2026, les 52 photos importées avec un titre descriptif ont toutes été retenues ;
  les 171 importées en « Free stock photo of… » ont toutes été refusées.
- La progression par année (aucune retenue en 2021, 2 à 3 % de 2022 à 2024, 9 % en
  2025, 23 % en 2026) suit de près la part de photos titrées : ce n'est pas l'âge
  des photos qui compte, c'est leur fiche.

Le sujet joue aussi, mais bien moins : à fiche soignée, presque tout passe.

### Sujets et formats

Part des photos retenues par galerie du site (toutes fiches confondues) :

- **Bien retenus** : jardins de Villandry (67 %), Normandie et Bretagne (62 %), mer et
  littoral (44 %), monuments de Niort (27 %), portraits d'un modèle posant (21 %),
  églises (18 %), oiseaux et animaux (15 %). Ce sont aussi les photos les plus vues :
  phares, croissant de lune, ciel étoilé, moineaux, mouettes.
- **Jamais retenus à ce jour** : couchers de soleil et nuages, scènes de vie prises sur
  le vif, cuisine et boissons, objets et natures mortes, manifestations. Presque
  jamais : fonds abstraits (2 %), campagne (3 %), fleurs (6 %), rues (6 %). Ce sont les
  sujets où Pexels a déjà des milliers de photos : il faut qu'ils sortent du lot.
- **Format** : 15 % des photos verticales retenues, contre 8 % des horizontales.
  Les photos verticales sont recherchées (téléphones, stories) : en proposer une
  version verticale quand le cadrage s'y prête.
- **Séries** : une série de photos proches passe bien si chaque fiche est soignée
  (le 23 juillet 2026, 16 vues des jardins de Villandry titrées : toutes retenues) ;
  les 4 refusées ce jour-là étaient en « Free stock photo of… ».

### Conseils pour chaque import

1. **Passer chaque lot par l'atelier avant l'import.** Aucune photo sans titre ni
   mots-clés préparés : « Free stock photo of… » condamne la photo.
2. **Titre en anglais, descriptif, de 6 à 12 mots** : sujet + détail + lieu ou
   ambiance (« Seagull Perched on a Stone Cross Against Sky », « Le Loup Lighthouse in
   France on Foggy Day »). Pas de titre poétique, de nom de préréglage (« MOOD: … »)
   ni de titre en français : ceux-là vont dans la description du site.
3. **30 à 45 mots-clés en anglais**, du plus précis au plus général : sujet, détails,
   lieu (ville, région, pays), couleurs, ambiance, usages (background, wallpaper,
   travel). Relire l'orthographe : « landmamrk », « cineamtic », « darth », « vertial »,
   « telefoto » figurent encore sur des photos publiées. Le mot « portrait » seulement
   pour une personne, jamais pour dire « format vertical ». Ne pas coller le même lieu
   (« pau ») à tout un lot.
4. **Choisir plutôt que tout verser** : mieux vaut 10 photos bien préparées que 40
   importées d'un coup sans fiche. Écarter les doublons, les photos floues ou
   sous-exposées ; dans une série, varier les vues (plan large, détail, vertical).
5. **Privilégier les sujets qui passent** : littoral, phares, monuments et patrimoine
   nommés, jardins, oiseaux, ciel de nuit, portraits posés. Pour les sujets saturés
   (couchers de soleil, fleurs, fonds, nourriture), n'importer que les images vraiment
   singulières, avec un titre qui dit ce qu'elles ont de particulier.
6. **Nommer le lieu** dans le titre et les mots-clés quand il est reconnaissable : les
   photos situées (Villandry, Granville, Niort, Irun) sont retenues et trouvées.
7. **Aucune signature ni filigrane** sur les fichiers importés.

Les tableaux de l'atelier donnent environ 20 mots-clés, ce qui suffit au site. Pour un
import, demander à la session « 30 à 45 mots-clés », ou compléter avec ceux que Pexels
propose à l'import.
