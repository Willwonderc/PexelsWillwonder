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
- Lire l'historique de l'article (`…/w/index.php?title=<Article>&action=history`) et les
  contributions de Karl sur cette Wikipédia (`Special:Contributions/Karl_Forterre`). Une
  photo déjà retirée d'un article n'y est jamais reproposée : la remettre serait une
  guerre d'édition. C'est arrivé le 29 octobre, faute de cette lecture : la statue de la
  Loi, retirée le 6 octobre de l'article espagnol sur l'hôtel de ville de Bilbao, y a été
  reproposée et retirée de nouveau trois minutes plus tard.

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
- Le panneau ne montre que les photos publiées aussi sur Pexels, qui ont leur page sur le
  site : leur numéro Pexels se lit dans leur description sur Commons (« Aussi publiée par
  l'auteur sur Pexels : … ») ou se retrouve par leur titre dans
  `vitrine/donnees/textes-fr.csv`. Une photo versée seulement sur Commons illustre bien
  son article, mais reste hors du panneau tant qu'elle n'est pas sur Pexels.

### 6. Suivre (session)

- Un contrôle chaque semaine : chaque photo est toujours dans son article, rien de neuf
  sur la page de discussion de Karl, aucun blocage dans le journal. La liste de toutes
  les Wikipédias où Karl a contribué, avec le nombre de ses modifications, est à
  `https://meta.wikimedia.org/wiki/Special:CentralAuth/Karl_Forterre` : les contributions
  de chacune y montrent les modifications annulées.
- Une photo retirée par un autre contributeur ne se remet pas : pas de guerre
  d'édition. On lit la raison, on en tient compte pour les suivantes, et on retire sa
  ligne de `wikipedia.csv`.

## Bonnes manières avec les serveurs de Wikimédia

- Une demande toutes les 8 à 15 secondes, avec un User-Agent qui donne un contact
  (contact@karlforterre.fr) ; sur une erreur 429, attendre 20, puis 40, puis 80 secondes.
- Lectures seulement, par `action=raw` et l'API publique.

## Où en est la route (29 octobre 2026)

Sur les 18 fichiers que Karl a versés sur Commons, 10 illustrent un article, 3 sont
préparés et 5 attendent leur tour. Neuf des dix sont aussi sur Pexels, donc dans
`vitrine/wikipedia.csv` et dans le panneau du site ; la statue de la Justice de l'hôtel de
ville de Bilbao n'est que sur Commons.

### Préparées le 29 octobre (deuxième série)

| Photo sur Commons | Wikipédia | Article | Partie (n°) | Légende |
|---|---|---|---|---|
| Xonrupt-Longemer - chapelle Saint-Florent - 2022.jpg | français | Lac de Longemer | Histoire religieuse (3) | La chapelle Saint-Florent, sur la rive ouest du lac. |
| Villandry - jardins du château vus d'en haut - 2026.jpg | anglais | Château de Villandry | History (1) | Box-hedge parterres in the gardens, seen from above |
| Îles Chausey - le phare vu de la mer - 2025.jpg | espagnol | Islas Chausey | Geografía (1) | El faro de Chausey en la Gran Isla, visto desde el mar |

Les trois sont aussi sur Pexels (13041935, 38694047, 34894970) : elles entreront dans le
panneau une fois en place. L'article sur le lac parle de la chapelle sans la montrer ;
l'article anglais décrit les parterres de buis sans image dans son texte ; l'article
espagnol n'a qu'une photo, celle du fort. Aucun des trois n'a jamais retiré de photo de
Karl.

### En attente

| Photo sur Commons | Piste |
|---|---|
| Bilbao - hôtel de ville, statue de la Loi - 2026.jpg | aucune pour l'instant : l'article espagnol « Casa consistorial de Bilbao » l'a refusée deux fois (Xabier, 6 octobre : « Imagen repetida, ya supra » ; 29 octobre : « Imagen duplicada, no repetir imágenes »), ne plus l'y proposer |
| Bilbao - cathédrale Saint-Jacques, façade et flèche - 2026.jpg | basque, « Bilboko Done Jakue katedrala », partie « Fatxada eta dorrea », qui a déjà une image de la tour : à comparer avec les articles français et espagnol |
| Cognac - hôtel de ville - 2025.jpg | l'hôtel de ville est déjà montré dans « Cognac » (français) et « Cognac Public Garden » (anglais) : chercher ailleurs |
| Niort - hôtel de ville - 2026.jpg | pas l'article « Hôtel de ville de Niort » : Karl l'avait mise dans l'infobox en créant l'article le 11 octobre, et Baidax l'a remplacée le 12 (« meilleure photographie ») ; ne plus l'y proposer |
| Niort - flèches de l'église Saint-André dans la verdure - 2025.jpg | l'article « Église Saint-André de Niort » a déjà une photo de Karl : chercher un autre article |

### Déjà dans des articles

| Photo | Wikipédia | Article | Partie | Ajoutée |
|---|---|---|---|---|
| Galice, éclipse totale (couronne solaire) | français | Éclipse solaire du 12 août 2026 | Galerie | 29 octobre 2026 |
| Bilbao, statue de la Justice (seulement sur Commons) | basque | Bilboko udaletxea | Eraikina | 29 octobre 2026 |
| Irun, hôtel de ville | basque | Irungo Udala | Udaletxea | 28 octobre 2026 |
| Gijón, Universidad Laboral | asturien | Universidá Llaboral de Xixón | La torre | 28 octobre 2026 |
| Bordeaux, Génie de la Liberté | français | Monument aux Girondins | Description | 28 octobre 2026 |
| Moyemont, chemin bordé d'arbres | français | Moyemont | Géologie et relief | 28 octobre 2026 |
| Buzy, dolmen | français | Dolmen de Buzy | Description | 8 octobre 2026 |
| Niort, hôtel de préfecture | français | Hôtel de préfecture des Deux-Sèvres | image de l'infobox | 8 octobre 2026 |
| Niort, église Saint-André | français | Église Saint-André de Niort | Extérieur | 6 octobre 2026 |
| Îles Chausey, tour du phare | français | Phare de Chausey | Historique | 6 octobre 2026 |
