# Plan du projet

Plan de départ, septembre 2026. Les préparatifs sont détaillés dans
[preparatifs.md](preparatifs.md) ; les consignes des sessions sont dans
[consignes/](../consignes/).

## Mise à jour du 24 septembre 2026

- **Titres Pexels** : 155 des 206 photos les plus récentes ont été publiées sans titre,
  et Pexels ne permet guère de modifier titres et mots-clés après publication.
  L'atelier sert donc avant chaque import, et ses tableaux alimentent le site.
- **Le site devient un site de photographe**, pensé pour le référencement : une page
  par photo, bien décrite, avec un lien vers Pexels pour le téléchargement. Comme
  l'API ne renvoie pas les photos du propriétaire depuis ses collections, le site
  s'appuie sur la liste des 919 photos (`atelier/inventaire.csv`).
- **Pinterest devient automatique** : Pinterest crée les épingles à partir des flux
  RSS du site, et des fichiers d'import par tableur couvrent les photos existantes.

## État des lieux

Le profil Pexels a déjà une vraie audience : 919 photos et environ 878 500 vues au
total, mais seulement 19 abonnés. Deux points freinent la suite.

- **Le lien du profil** pointe vers karlforterre.fr, qui présente une activité de
  graphiste et d'éditeur à Poitiers. Un visiteur séduit par une photo tombe donc sur
  une offre de services plutôt que sur la suite des images.
- **Les intitulés automatiques** : les photos récentes portent des titres formés de
  leurs trois premiers mots-clés par ordre alphabétique. Dans la série des Asturies,
  quatre clichés différents affichent le même libellé « architecture photography,
  asturias, bell tower ». Probablement faute de titre renseigné, rien ne les distingue
  dans les résultats de recherche.

## Idée directrice

Traiter le crédit comme un budget de construction. Avant le 5 novembre, les sessions
cloud fabriquent des outils qui tournent ensuite seuls sur GitHub, gratuitement pour un
dépôt public, sans toucher au crédit ni au forfait.

## Les quatre chantiers

### 1. Une vitrine photo reliée à Pexels

Un site simple, hébergé gratuitement sur GitHub Pages, avec une page par thème :
Asturies, jardins des châteaux de la Loire, ciel et astrophotographie, fonds abstraits,
noir et blanc, mariage. Les photos viennent des collections Pexels, lues grâce à l'API,
qui peut lister toutes les collections et le contenu de chacune. Une tâche automatique
reconstruit le site chaque nuit : ajouter une photo à une collection sur Pexels suffit
pour qu'elle apparaisse.

Chaque image renvoie vers sa page Pexels pour le téléchargement, ce qui présente deux
avantages : les téléchargements comptent dans les statistiques du profil, et le site
respecte les règles de l'API, qui interdisent de reproduire les fonctions de base de
Pexels. C'est ce site que le lien du profil devrait désigner.

### 2. Une fabrique d'épingles Pinterest

Pinterest fonctionne comme un moteur de recherche d'images, ce qui convient bien à des
fonds d'écran, du ciel étoilé ou de l'architecture. Pour chaque collection, une session
prépare des visuels verticaux avec un titre court et le lien vers la page Pexels. Elle
prépare aussi le fichier d'import : l'import par tableur crée jusqu'à 200 épingles d'un
coup, avec titre, description, lien, tableau de destination et date de publication
différée.

Complément plus automatique encore : un compte professionnel qui a revendiqué son site
peut relier un flux RSS, et les épingles se créent seules en 24 à 48 heures ; la vitrine
peut fournir ce flux.

Précaution : une signature sur les visuels Pinterest ne pose aucun problème, mais Pexels
refuse les signatures et filigranes sur les fichiers importés chez lui.

### 3. Un atelier titres et mots-clés

Avant un import, des copies réduites des photos sont déposées dans un dossier du dépôt.
La session regarde chaque image et rend un tableau prêt à copier : un titre descriptif
propre à chaque cliché et jusqu'à 25 mots-clés, le plafond habituel. C'est idéal pour
traiter d'un coup toutes les photos d'un voyage, en commençant par les séries récentes
aux intitulés génériques.

### 4. Un tableau de bord de campagne

Pour savoir ce qui marche, une page du site, non référencée, rassemble trois chiffres :
les clics envoyés vers Pexels par la vitrine, les statistiques Pinterest et le total de
vues Pexels. Ce dernier chiffre est noté à la main une fois par semaine : les conditions
de Pexels interdisent strictement la collecte automatique de données sur leurs pages, et
l'API ne fournit pas les vues. Ce même relevé peut alimenter le compteur prévu sur le
petit écran Turing ; seul l'essai final se fera sur le PC où l'écran est branché.

## Calendrier

- Sessions 1 et 3 en parallèle, dès que les préparatifs sont faits.
- Session 2 une fois le site en ligne.
- Session 4 fin octobre.
- Après la première session, la jauge de consommation montre ce qu'elle a coûté, de quoi
  calibrer les suivantes.

## Levier gratuit, hors crédit

Les concours Pexels donnent une visibilité directe sur la plateforme ; le profil n'en a
encore remporté aucun.
