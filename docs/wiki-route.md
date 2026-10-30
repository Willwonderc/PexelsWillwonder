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
- Les photos de Karl sont presque toutes sur Pexels. Leur numéro Pexels se lit dans leur
  description sur Commons (« Aussi publiée par l'auteur sur Pexels : … »), se retrouve
  par leur titre dans `vitrine/donnees/textes-fr.csv`, ou en comparant les vignettes.
  Attention : dans la fiche de suivi, « refusée » veut dire seulement que Pexels ne l'a pas
  mise en avant ; la photo est bien publiée. Si elle n'est pas encore sur le site (absente
  de `vitrine/photos.txt`, souvent parce qu'elle n'a pas de titre), l'ajouter à
  `photos.txt` avec ses titres (anglais dans `atelier/resultats/`, français et chinois dans
  `vitrine/donnees/`), comme le 30 octobre pour la Justice et la cathédrale de Bilbao.
- Une photo versée seulement sur Commons entre aussi dans le panneau : sa colonne `photo`
  reste vide, et ses titres et sa taille sont dans `wikipedia.csv` ; son image vient de
  Commons, et « Voir la photo » mène à sa page Commons (vue de face de l'hôtel de ville de
  Niort).

### 6. Suivre (session)

- Un contrôle chaque semaine : chaque photo est toujours dans son article, rien de neuf
  sur la page de discussion de Karl, aucun blocage dans le journal. La liste de toutes
  les Wikipédias où Karl a contribué, avec le nombre de ses modifications, est à
  `https://meta.wikimedia.org/wiki/Special:CentralAuth/Karl_Forterre` : les contributions
  de chacune y montrent les modifications annulées.
- Une photo retirée par un autre contributeur ne se remet pas : pas de guerre
  d'édition. On lit la raison, on en tient compte pour les suivantes, et on retire sa
  ligne de `wikipedia.csv`.
- Le journal des versements de Karl sur Commons
  (`https://commons.wikimedia.org/w/index.php?title=Special:Log&type=upload&user=Karl_Forterre`)
  garde chaque fichier, même supprimé : il dit si un fichier a disparu.

### Quand une photo de Karl a été remplacée

L'exemple de l'hôtel de ville de Niort (29 octobre 2026) :

- L'infobox vide (`{{Infobox Monument}}`) prend sa photo dans Wikidata. Remettre la photo
  écartée, dans l'article ou dans Wikidata, serait une guerre d'édition.
- Ce qui a marché : comprendre le choix (une vue de face avec le beffroi), puis
  prendre une nouvelle photo qui y répond (de face, entière, sans passants, en très haute
  définition, perspective redressée). Elle a été versée sur Commons avant Pexels, et sa
  page Commons a reçu « dépeint » (l'élément Wikidata).
- Elle a ensuite remplacé l'image de l'élément Wikidata, en changeant aussi la date et
  la légende jointes. Wikidata n'a pas de case de résumé : l'explication est allée dans un
  message à celui qui avait fait le choix, sur la page de discussion de l'article, avec
  `{{Notif|Nom}}` et la signature `~~~~`, en lui laissant le dernier mot.
- La première photo, de biais, a trouvé une autre place : la partie dont le texte parle
  de ce qu'elle montre (l'escalier d'accès), sans toucher à l'infobox.
- La notoriété d'une photo ailleurs (Pexels) n'est jamais un argument sur Wikipédia.

## Bonnes manières avec les serveurs de Wikimédia

- Une demande toutes les 8 à 15 secondes, avec un User-Agent qui donne un contact
  (contact@karlforterre.fr) ; sur une erreur 429, attendre 20, puis 40, puis 80 secondes.
- Lectures seulement, par `action=raw` et l'API publique.

## Où en est la route (30 octobre 2026)

Sur les 24 fichiers que Karl a versés sur Commons, 22 illustrent un article (dont un par
l'image de Wikidata) et 2 attendent leur tour (Cognac, sans place libre ; la Loi, refusée).
Les vingt-deux sont dans `vitrine/wikipedia.csv` et dans le panneau du site ; seule la vue de
face de l'hôtel de ville de Niort n'est que sur Commons.

Pour Villandry, Karl a ajouté le 29 octobre à l'article anglais une partie « Gardens »
qui manquait, écrite d'après les pages officielles du château (restauration de Joachim
Carvallo, jardin du soleil de 2008, entretien biologique depuis 2009), avec deux photos
versées pour l'occasion ; le parterre de l'Amour passionné a rejoint la galerie de l'article. La photo des parterres vus d'en haut, prévue pour « History »,
reste en attente. Les nouvelles photos de Villandry sont déjà sur Pexels : leur page
Commons porte `{{Permission pending}}`, et Karl ajoute leurs noms à son autorisation
envoyée par courriel.

### Les 336 propositions du 30 octobre

Karl a fourni le 30 octobre deux listes écrites par un autre modèle d'après les titres et
les mots-clés, sans voir les photos : `propositions-wiki-336.md` (336 photos, priorités 1 à
3) et `propositions-wiki-priorites.md` (les 97 des priorités 1 et 2). Relues le 30 octobre
en regardant chaque photo retenue et les articles visés. Leçons :

- **Les identifications sont souvent fausses** : 23414381 et 23414382 montrent Saint-André
  et non Notre-Dame de Niort ; 40189681 est la tour de l'Universidad Laboral de Gijón ;
  Statue de la Liberté, aqueducs, églises « sans nom » restent à identifier par Karl.
- **Écartées** : œuvres et bâtiments récents en France (Commons les supprime faute de
  liberté de panorama : pont Chaban-Delmas, tour Montparnasse, monuments aux morts au
  sculpteur inconnu, vitraux modernes) ; manifestations et personnes reconnaissables ;
  sujets génériques (fleurs, cafés, chats, flous), soit l'essentiel de la priorité 3 ;
  articles déjà bien illustrés (Girondins, Quinconces, Zubizuri, tour Iberdrola, Isozaki
  Atea, Poitiers, Mont-Saint-Michel, Évron, Villandry, déjà riche de cinq photos).
- **Retenues** : pic du Midi d'Ossau (en, fait), phare du Loup (fr « Îles Chausey », fait).
- **Pistes vérifiées, à confirmer par Karl** : 23414382, Saint-André au-dessus de la
  Sèvre, pour l'article italien « Niort », sans photo dans son texte ; 13263155, viaduc de
  Laval en noir et blanc, pour « Viaduc de Laval » (partie Description : neuf arches de
  granite) ; 39228273, l'église de Buzy, pour l'article basque « Buzy », sans aucune photo
  (nom de l'église à confirmer : Saint-Saturnin, de la fin du XVIIIe siècle, n'est pas
  romane).
- **À identifier par Karl** : 32053231 (église néogothique d'Angers), 39517000 (façade
  plateresque en Espagne), 35104307 et 35104310 (remparts médiévaux, peut-être Fougères),
  35168742 (campanile en Mayenne), 19047674 (réplique de la statue de la Liberté),
  34939467 (tourelle « à Saint-Planchers »), 34894969 (pyramide à Chausey), 12076681
  (Angoulême), 34849705 (chœur gothique du Mont-Saint-Michel).
- Plusieurs photos récentes, sans titre sur Pexels, ne sont pas encore sur le site (Évron
  402743xx, Bilbao 4001463x, 400607xx) : les ajouter comme la Justice et la cathédrale de
  Bilbao si elles entrent dans un article.

### En attente

| Photo sur Commons | Piste |
|---|---|
| Bilbao - hôtel de ville, statue de la Loi - 2026.jpg | aucune pour l'instant : l'article espagnol « Casa consistorial de Bilbao » l'a refusée deux fois (Xabier, 6 octobre : « Imagen repetida, ya supra » ; 29 octobre : « Imagen duplicada, no repetir imágenes »), ne plus l'y proposer |
| Cognac - hôtel de ville - 2025.jpg | l'hôtel de ville est déjà montré dans les articles français, anglais, allemand et espagnol sur Cognac et dans « Cognac Public Garden » : chercher ailleurs |

### Déjà dans des articles

| Photo | Wikipédia | Article | Partie | Ajoutée |
|---|---|---|---|---|
| Îles Chausey, phare du Loup dans la brume | français | Îles Chausey | galerie de « Pour mémoire » | 30 octobre 2026 |
| Pic du Midi d'Ossau, vu du nord | anglais | Pic du Midi d'Ossau | Appearance | 30 octobre 2026 |
| Villandry, parterres vus d'en haut | anglais | Parterre | Gallery | 30 octobre 2026 |
| Niort, flèches de Saint-André dans la verdure | espagnol | Niort | Geografía | 30 octobre 2026 |
| Bilbao, cathédrale, façade et flèche | français | Cathédrale Saint-Jacques de Bilbao | Description | 30 octobre 2026 |
| Villandry, parterre de l'Amour passionné | anglais | Château de Villandry | Gallery | 29 octobre 2026 |
| Villandry, potager décoratif | anglais | Château de Villandry | Gardens | 29 octobre 2026 |
| Villandry, miroir d'eau du jardin d'eau | anglais | Château de Villandry | Gardens | 29 octobre 2026 |
| Xonrupt-Longemer, chapelle Saint-Florent | français | Lac de Longemer | Histoire religieuse | 29 octobre 2026 |
| Îles Chausey, le phare vu de la mer | espagnol | Islas Chausey | Geografía | 29 octobre 2026 |
| Niort, hôtel de ville, vue de face (seulement sur Commons) | français | Hôtel de ville de Niort | image de l'infobox, par Wikidata (Q56863003) ; Baidax prévenu | 29 octobre 2026 |
| Niort, hôtel de ville, escalier d'accès | français | Hôtel de ville de Niort | Statut patrimonial | 29 octobre 2026 |
| Galice, éclipse totale (couronne solaire) | français | Éclipse solaire du 12 août 2026 | Galerie | 29 octobre 2026 |
| Bilbao, statue de la Justice | basque | Bilboko udaletxea | Eraikina | 29 octobre 2026 |
| Irun, hôtel de ville | basque | Irungo Udala | Udaletxea | 28 octobre 2026 |
| Gijón, Universidad Laboral | asturien | Universidá Llaboral de Xixón | La torre | 28 octobre 2026 |
| Bordeaux, Génie de la Liberté | français | Monument aux Girondins | Description | 28 octobre 2026 |
| Moyemont, chemin bordé d'arbres | français | Moyemont | Géologie et relief | 28 octobre 2026 |
| Buzy, dolmen | français | Dolmen de Buzy | Description | 8 octobre 2026 |
| Niort, hôtel de préfecture | français | Hôtel de préfecture des Deux-Sèvres | image de l'infobox | 8 octobre 2026 |
| Niort, église Saint-André | français | Église Saint-André de Niort | Extérieur | 6 octobre 2026 |
| Îles Chausey, tour du phare | français | Phare de Chausey | Historique | 6 octobre 2026 |
