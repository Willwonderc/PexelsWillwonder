# Wiki route : verser une photo dans Wikipédia

Protocole suivi depuis le 28 octobre 2026 pour que les photos de Karl, partagées sous
licence libre (CC BY-SA 4.0) sur Wikimedia Commons, illustrent des articles de Wikipédia,
puis entrent dans le panneau « Mes photos dans Wikipédia » du site photo. Karl fait
lui-même chaque modification, connecté à son compte « Karl Forterre », valable sur toutes
les Wikipédias et sur Commons. Une session Claude prépare tout et vérifie ensuite ; elle
ne modifie jamais Wikipédia ni Commons elle-même.

## Le principe

- **Une photo, un article, une partie.** On choisit la partie dont le texte parle déjà
  de ce que montre la photo, de préférence une partie sans image. On ne remplace jamais
  une image existante et on évite les galeries déjà pleines.
- **Toutes les Wikipédias comptent** : français, basque, asturien, espagnol, galicien…
  La légende est écrite dans la langue de l'article ; elle est courte et factuelle, et ne
  nomme pas le photographe : le crédit figure sur Commons.
- **Aucun lien vers les sites de Karl** dans les articles : seulement la photo.
- **La ligne éditoriale du dépôt** s'applique aux légendes (`CLAUDE.md`, « Ligne
  éditoriale ») : un monument se présente par ce qu'il célèbre de républicain, de
  populaire ou d'ouvrier.

## Les étapes

### 1. Choisir les photos (session)

Lister les fichiers que Karl a versés sur Commons, puis garder ceux qu'aucun article
n'utilise encore :

- fichiers : `https://commons.wikimedia.org/w/api.php?action=query&list=allimages&aiuser=Karl_Forterre&aisort=timestamp&aidir=descending&ailimit=200&format=json` ;
- usages : `https://commons.wikimedia.org/w/api.php?action=query&prop=globalusage&titles=File:…|File:…&gulimit=500&guprop=namespace&format=json`
  (espace de noms `0` : un article).

La description de chaque fichier sur Commons (`…/w/index.php?title=File:…&action=raw`)
dit ce que montre la photo, avec ses coordonnées.

### 2. Trouver l'article et la partie (session)

- Chercher les articles du sujet dans chaque langue (recherche de chaque Wikipédia, ou
  liens interlangues).
- Lire leur texte brut (`https://<langue>.wikipedia.org/w/index.php?title=<Article>&action=raw`)
  et y repérer la partie qui parle de ce que montre la photo.
- Vérifier les images déjà présentes, dans la partie et dans tout l'article : pas de
  doublon du même sujet, pas de galerie déjà pleine.

### 3. Préparer ce que Karl copie (session)

Pour chaque photo, la session donne à Karl, dans cet ordre :

1. **Le lien de modification de la partie**, qui ouvre l'éditeur de cette seule partie :
   `https://<langue>.wikipedia.org/w/index.php?title=<Article>&action=edit&section=<N>`.
   `N` est le rang du titre de la partie dans le texte de l'article, tous niveaux de
   titres confondus, en comptant à partir de 1.
2. **La case entière à copier** : tout le texte actuel de la partie, avec la ligne de la
   photo ajoutée à la bonne place (juste sous le titre, ou dans la galerie).
3. **Le résumé de modification**, dans la langue de l'article.
4. **Le lien vers la photo sur Commons**, pour la reconnaître.

Le texte de la partie se lit juste avant, pour être à jour :
`…/w/index.php?title=<Article>&action=raw&section=<N>`. La ligne de la photo prend le nom
local des fichiers (`Fichier:` en français, `Fitxategi:` en basque, `Archivo:` en
espagnol, `Ficheiro:` en galicien, `Imaxe:` en asturien ; `File:` marche partout) :

    [[Fichier:Nom exact sur Commons.jpg|vignette|Légende.]]

Une photo en hauteur prend aussi `upright`, qui la garde à une taille raisonnable. Dans une
galerie (`<gallery>`), on ajoute une ligne `Fichier:Nom.jpg|Légende.` à côté des autres.

### 4. Modifier (Karl)

1. Ouvrir le lien de modification, connecté à son compte.
2. Cliquer dans la grande case, tout sélectionner (Cmd + A sur le Mac), coller la case
   entière donnée par la session : elle remplace tout le texte de la partie.
3. Coller le résumé dans la case « Résumé », vérifier si besoin avec « Prévisualiser »,
   puis cliquer sur le bouton bleu de publication (« Publier les modifications », ou sa
   traduction dans la langue de l'article).
4. Dire « c'est fait » à la session.

Deux précautions :

- **Une case de partie ne se colle que dans le lien de cette partie.** Collée dans
  l'éditeur de la page entière, elle efface tout le reste de l'article : c'est arrivé le
  28 octobre sur « Moyemont », rétabli le jour même d'une seule modification.
- **Si Wikipédia refuse d'enregistrer** (par exemple un lien vers un site bloqué, comme
  geneanet.org), ne pas insister : envoyer une capture d'écran à la session, qui donne
  une case corrigée.

Karl ne donne jamais son mot de passe à une session.

### 5. Vérifier, puis mettre la photo sur le site (session)

- Relire l'article en ligne : la photo est là, le reste n'a pas changé (même taille à
  quelques dizaines d'octets près, rien d'effacé), et l'historique ne montre aucune
  annulation.
- Ajouter la ligne de la photo à `vitrine/wikipedia.csv` (mode d'emploi :
  `vitrine/README.md`, « Photos dans Wikipédia ») : la Wikipédia, l'article, la partie,
  la légende telle que publiée, le fichier, la date de la modification, les coordonnées
  données par Commons, le lieu et sa région dans les trois langues. La pull request vers
  `main` met la photo dans le panneau à la construction suivante, et la page de la photo
  cite l'article.

### 6. Suivre (session)

- Un contrôle chaque semaine : chaque photo est toujours dans son article, rien de neuf
  sur la page de discussion de Karl, aucun blocage dans le journal.
- Une photo retirée par un autre contributeur ne se remet pas : pas de guerre
  d'édition. On lit la raison, on en tient compte pour les suivantes, et on retire sa
  ligne de `wikipedia.csv`.

## Bonnes manières avec les serveurs de Wikimédia

- Une demande toutes les 8 à 15 secondes, avec un User-Agent qui donne un contact
  (contact@karlforterre.fr) ; sur une erreur 429, attendre 20, puis 40, puis 80 secondes.
- Lectures seulement, par `action=raw` et l'API publique.

## Où en est la route (29 octobre 2026)

Sur les 18 fichiers que Karl a versés sur Commons, 8 illustrent un article (ils sont tous
dans `vitrine/wikipedia.csv`), 3 sont préparés, et 7 attendent leur tour.

### Préparées le 29 octobre

| Photo sur Commons | Wikipédia | Article | Partie (n°) | Légende |
|---|---|---|---|---|
| Bilbao - hôtel de ville, statue de la Justice - 2026.jpg | basque | Bilboko udaletxea | Eraikina (2) | Justizia irudikatzen duen eskultura, eskailera nagusian. |
| Bilbao - hôtel de ville, statue de la Loi - 2026.jpg | espagnol | Casa consistorial de Bilbao | Características (3) | Escultura de la Ley, con la inscripción «IN LEGIBUS SALUS», en la escalinata principal |
| Éclipse totale de Soleil du 12 août 2026 vue de Galice.jpg | français | Éclipse solaire du 12 août 2026 | Galerie (16) | [[Couronne solaire]] pendant la totalité. Depuis la [[Galice]], en Espagne. |

Les deux articles de l'hôtel de ville de Bilbao écrivent qu'« en la escalinata
principal, destacan dos esculturas que representan la ley y la justicia ». L'article
espagnol montre déjà un détail de la Justice : il reçoit donc la Loi, et l'article basque,
sans aucune image dans son texte, reçoit la Justice. Dans l'article français sur
l'éclipse, la galerie de l'éclipse totale ne montre encore que León.

### En attente

| Photo sur Commons | Piste |
|---|---|
| Bilbao - cathédrale Saint-Jacques, façade et flèche - 2026.jpg | basque, « Bilboko Done Jakue katedrala », partie « Fatxada eta dorrea », qui a déjà une image de la tour : à comparer avec les articles français et espagnol |
| Cognac - hôtel de ville - 2025.jpg | français : aucun article sur l'hôtel de ville ; voir « Cognac », lieux et monuments |
| Villandry - jardins du château vus d'en haut - 2026.jpg | français, « Château de Villandry », partie des jardins |
| Îles Chausey - le phare vu de la mer - 2025.jpg | français, « Îles Chausey » |
| Niort - hôtel de ville - 2026.jpg | français, « Hôtel de ville de Niort », qui a déjà deux images |
| Niort - flèches de l'église Saint-André dans la verdure - 2025.jpg | l'article « Église Saint-André de Niort » a déjà une photo de Karl : chercher un autre article |
| Xonrupt-Longemer - chapelle Saint-Florent - 2022.jpg | la galerie de « Xonrupt-Longemer » montre déjà la chapelle : chercher ailleurs |

### Déjà dans des articles

| Photo | Wikipédia | Article | Partie | Ajoutée |
|---|---|---|---|---|
| Irun, hôtel de ville | basque | Irungo Udala | Udaletxea | 28 octobre 2026 |
| Gijón, Universidad Laboral | asturien | Universidá Llaboral de Xixón | La torre | 28 octobre 2026 |
| Bordeaux, Génie de la Liberté | français | Monument aux Girondins | Description | 28 octobre 2026 |
| Moyemont, chemin bordé d'arbres | français | Moyemont | Géologie et relief | 28 octobre 2026 |
| Buzy, dolmen | français | Dolmen de Buzy | Description | 8 octobre 2026 |
| Niort, hôtel de préfecture | français | Hôtel de préfecture des Deux-Sèvres | image de l'infobox | 8 octobre 2026 |
| Niort, église Saint-André | français | Église Saint-André de Niort | Extérieur | 6 octobre 2026 |
| Îles Chausey, tour du phare | français | Phare de Chausey | Historique | 6 octobre 2026 |
