# Se faire connaître des moteurs de recherche et des assistants IA

Rédigé le 27 septembre 2026 (session « Référencement IA »), pour
https://photos.karlforterre.fr et https://karlforterre.fr.

ChatGPT, Copilot, Perplexity, Gemini et Claude répondent de plus en plus souvent en
citant leurs sources. Pour cela, ils s'appuient sur trois choses :

1. **Des moteurs de recherche.** Copilot lit l'index de Bing ; ChatGPT a son propre
   robot et plusieurs fournisseurs, dont Bing ; Gemini lit l'index de Google ;
   Perplexity a son propre index ; Claude s'appuie sur Brave Search. Une page que ces
   moteurs ne connaissent pas ne peut pas être citée.
2. **Des bases de connaissances**, Wikidata et Wikipédia en tête. Elles leur disent qui
   est qui : qu'un « Karl Forterre » photographe, auteur de *Darshan* et d'un mémoire
   sur la médiation auctoriale, est une seule et même personne.
3. **Des pages claires**, qu'ils peuvent comprendre et citer telles quelles : qui,
   quoi, où, sous quelle licence, avec des chiffres et des dates.

Le site s'occupe seul d'une bonne part du travail (première partie). Le reste se fait
une fois pour toutes, à la main, en suivant les modes d'emploi de ce document.

## Ce que le site fait tout seul

Tout est construit chaque nuit par `vitrine/build.py` ; rien à faire.

| Quoi | Où | Pour quoi faire |
|---|---|---|
| `llms.txt` et `llms-full.txt` | `/llms.txt`, `/en/llms.txt`, `/zh/llms.txt` | Présentation du site en texte simple pour les assistants IA (format [llmstxt.org](https://llmstxt.org/)) : l'auteur, la licence, le crédit à donner, les séries, les galeries, les questions fréquentes ; `llms-full.txt` y ajoute chacune des photos |
| Questions fréquentes | [/questions-frequentes/](https://photos.karlforterre.fr/questions-frequentes/), `/en/faq/`, `/zh/faq/` | Des réponses courtes et exactes, faciles à citer ; réglées dans `vitrine/questions.ini` |
| L'auteur dans les données structurées | chaque page | Pour Google, Bing et les assistants, le site photo, karlforterre.fr, Pexels, Mastodon, Bluesky, LinkedIn (et bientôt RedNote et Wikidata) désignent une seule personne ; réglages : rubrique `[personne]` de `vitrine/site.ini` |
| IndexNow | chaque nuit, une fois le site en ligne | Bing reçoit la liste des pages nouvelles, modifiées ou supprimées et la transmet à Yandex, Seznam, Naver, Yep et Amazon ; Bing sert Copilot, DuckDuckGo, Yahoo et une partie des recherches de ChatGPT |
| Plan du site daté | `/sitemap.xml` | Chaque page avec la date de sa dernière vraie modification (`lastmod`), que Bing et Google lisent pour savoir quoi relire |
| `robots.txt` ouvert | `/robots.txt` | Tous les robots sont admis, y compris ceux des assistants (OAI-SearchBot pour ChatGPT, Claude-SearchBot, PerplexityBot…) |

### IndexNow en deux mots

- **La clé** est le réglage `indexnow` de `vitrine/site.ini`. Elle n'a rien de secret :
  le site la publie lui-même à l'adresse `https://photos.karlforterre.fr/<clé>.txt`,
  et les moteurs y vérifient que les signalements viennent bien du site.
- **Le journal des pages**, `vitrine/donnees/pages.json`, tenu par la tâche de nuit,
  garde pour chaque page une empreinte de son contenu et la date de sa dernière
  modification. Une page n'est signalée que si son titre, sa description, ses données
  structurées ou son contenu changent : une retouche de la feuille de style ou du pied
  de page ne compte pas. Le premier passage signale toutes les pages, une seule fois :
  IndexNow l'admet pour un site nouveau ou entièrement refait, ce qui est le cas ; ensuite,
  seules les pages qui changent partent.
- **Le signalement** part une fois le site en ligne (travail **signaler** de la tâche
  **Site**, onglet **Actions**), sinon les moteurs liraient l'ancienne version.
- **Le résultat** se lit dans ce travail : « IndexNow : 12 pages signalées, réponse 200
  (adresses reçues) ». Une réponse 202 au premier envoi est normale : Bing vérifie la
  clé. Une croix rouge signale un refus (clé ou adresses) : le message dit lequel.
- **Changer de clé** : remplacer la valeur de `indexnow` par 32 chiffres et lettres de
  a à f pris au hasard (une session Claude peut en tirer une). Laisser vide pour ne plus
  rien signaler.

## À faire à la main, dans cet ordre

| Étape | Temps | Pourquoi |
|---|---|---|
| [1. Bing Webmaster Tools](#1-bing-webmaster-tools) | 20 minutes | Suivre l'indexation par Bing, et voir combien de fois Copilot cite vos pages |
| Google Search Console | 20 minutes | Déjà prévue (`vitrine/README.md`, « Référencement ») : Gemini et les réponses IA de Google s'appuient sur l'index de Google |
| Le profil RedNote | 2 minutes | Retirer le `#` de la ligne `RedNote` de la rubrique `[reseaux]` de `vitrine/site.ini` et y coller l'adresse du profil : il rejoint le pied de page et les données de l'auteur |
| [2. Wikidata](#2-wikidata) | 1 heure | Une fiche qui dit aux moteurs et aux assistants qui est Karl Forterre, avec ses livres et son mémoire |
| [3. Wikimedia Commons](#3-wikimedia-commons--douze-photos-de-lieux) | 2 heures | Douze photos de lieux, réutilisables par Wikipédia et Wikidata, avec le nom de l'auteur |
| [Brave Search](#être-présent-dans-les-trois-index-qui-comptent) | 5 minutes | Proposer quelques adresses : Brave fournit la recherche de Claude |
| [Dépôt du mémoire](#déposer-le-mémoire-dans-une-archive-ouverte) | 1 heure | Faire entrer le mémoire dans les bases universitaires, avec une adresse stable |

## 1. Bing Webmaster Tools

Bing Webmaster Tools montre ce que Bing sait du site : pages indexées, recherches qui y
mènent et, depuis février 2026, **les citations des pages dans les réponses de Copilot**
(rapport « AI Performance »). Il est gratuit. Faites la démarche pour les deux sites :
photos.karlforterre.fr, puis karlforterre.fr.

### Se connecter

1. Ouvrir https://www.bing.com/webmasters et cliquer sur **Se connecter** (**Sign in**).
2. Choisir un compte **Microsoft**, **Google** ou **Facebook** : le compte Google qui
   sert à Google Search Console est le plus pratique.
3. Pour l'interface en français : icône des paramètres → **Langue d'affichage** →
   **Français**.

### Ajouter les sites

**Si Google Search Console est déjà en place** (le plus simple) :

1. Dans l'encadré **Importer depuis Google Search Console**, cliquer sur **Importer**.
2. Choisir le même compte Google, puis **Autoriser** : Bing ne demande qu'une lecture.
3. Cocher les sites vérifiés dans Google (photos.karlforterre.fr, karlforterre.fr), puis
   **Importer**. Ils sont vérifiés d'office, avec leurs plans de site. Les données
   arrivent en 48 heures environ.

**Sinon, à la main**, pour photos.karlforterre.fr :

1. Dans **Ajouter votre site manuellement**, saisir `https://photos.karlforterre.fr/`,
   puis **Ajouter**.
2. **Choisissez une méthode de vérification** : **Balise META HTML**. Bing affiche une
   ligne de la forme `<meta name="msvalidate.01" content="0123456789ABCDEF" />`.
3. Sur GitHub, ouvrir `vitrine/site.ini`, cliquer sur le crayon et coller **seulement
   la valeur** entre les guillemets de `content` après `bing_verification =`, puis
   **Commit changes**.
4. Attendre que la tâche **Site** ait tourné (onglet **Actions**, coche verte, 3 à
   5 minutes), puis cliquer sur **Vérifier** dans Bing. Ne jamais retirer ensuite ce
   réglage : Bing revérifie de temps en temps.

Pour karlforterre.fr, à la main : choisir plutôt **Fichier XML**. Bing propose de
télécharger un fichier `BingSiteAuth.xml` ; sur GitHub, dépôt Willwonderc/karlforterre.fr,
**Add file** → **Upload files**, déposer ce fichier à la racine du dépôt, **Commit
changes**, attendre deux minutes, puis **Vérifier**.

### Déclarer les plans du site

Menu **Sitemaps** → **Envoyer le sitemap** :

- `https://photos.karlforterre.fr/sitemap.xml` (chaque page dans les trois langues,
  avec sa date de dernière modification) ;
- `https://karlforterre.fr/sitemap.xml`.

Bing les relit ensuite de lui-même, en général une fois par jour.

### Ce qu'il n'y a pas à faire

- **Soumettre des adresses une à une** : IndexNow le fait chaque nuit pour le site
  photo. Pour karlforterre.fr, après une modification importante (une nouvelle page, un
  nouveau livre), menu **Soumission d'URL** : coller l'adresse de la page modifiée.
- **Vérifier IndexNow** : il marche sans Bing Webmaster Tools. L'onglet **IndexNow**
  montre simplement ce que Bing a reçu (**Liste des URL envoyées**, les 1 000 dernières)
  et les pages découvertes autrement (**URL importantes manquantes**).

### Ce qu'il faut regarder ensuite

Une fois par mois, avec le relevé des vues Pexels :

- **AI Performance** : nombre de citations des pages dans Copilot et les résumés IA de
  Bing, pages les plus citées, et recherches qui ont mené à ces citations (« grounding
  queries »). Une citation n'est pas une visite : c'est une mention dans une réponse.
  Pour un petit site, les chiffres peuvent rester vides quelques semaines.
- **Performances de recherche** : clics et apparitions dans Bing, recherche par
  recherche et page par page.
- **Inspection d'URL** : sur une page de photo, la carte **Markup** montre les données
  structurées lues par Bing (ImageObject, Person, FAQPage…).
- **Recommendations** : les défauts relevés par Bing, du plus grave au moins grave.

## 2. Wikidata

Wikidata est la base de connaissances libre de la fondation Wikimedia. Google, Bing, les
assistants IA et Wikipédia y puisent pour savoir qui est qui. Une fiche « Karl Forterre »
y relie, par des identifiants vérifiables, ses deux sites, son profil Pexels, ses réseaux,
ses livres et son mémoire : c'est ce qui permet à un assistant de comprendre que le
photographe de Pexels, l'auteur de *Darshan* et l'auteur du mémoire sur la médiation
auctoriale sont une seule et même personne.

Compter une heure. Un seul compte sert pour Wikidata, Wikimedia Commons et Wikipédia.

### Ce que Wikidata accepte

Une fiche est admise si elle décrit une personne ou une œuvre clairement identifiable,
décrite par des sources sérieuses et publiques. C'est le cas ici : les deux livres ont un
ISBN et relèvent du dépôt légal (*Darshan* : 978-2-9588873-3-9 ; *L'histoire du petit
Théo* : 978-2-9588873-2-2), le mémoire est en ligne, le profil Pexels aussi.

Rien n'interdit de rédiger soi-même sa propre fiche, mais elle se relit comme les
autres : des faits, pas d'adjectifs, et une source pour chaque déclaration. Les fiches
promotionnelles ou invérifiables sont supprimées. Wikipédia, elle, déconseille
fortement d'écrire l'article qui vous concerne et supprime ceux qui n'ont pas de sources
indépendantes : ne pas en créer.

### Avant de commencer (10 minutes)

1. Chercher « Forterre, Karl » dans le catalogue de la BnF (https://catalogue.bnf.fr) :
   les livres déposés y ont leur notice. S'il existe une **notice d'autorité** au nom de
   Karl Forterre, noter son identifiant (huit chiffres suivis d'un caractère de
   contrôle, dans l'adresse de la notice) : il servira de référence et d'identifiant.
2. Créer un identifiant ORCID gratuit sur https://orcid.org (facultatif, voir partie 4) :
   il servira aussi.
3. Chercher « Karl Forterre » sur https://www.wikidata.org : si une fiche existe déjà, la
   compléter plutôt qu'en créer une autre.

### Créer le compte

1. https://www.wikidata.org → **Créer un compte**, en haut à droite. Nom d'utilisateur :
   `KarlForterre` (le même nom servira sur Commons, partie 3).
2. **Préférences** → **Informations sur l'utilisateur** → **Langue** : français.

### Créer la fiche de Karl Forterre

1. Menu de gauche → **Créer un nouvel élément**.
2. Langue `fr`, **Libellé** : `Karl Forterre` ; **Description** : `photographe et écrivain
   français` (en minuscules, sans éloge) ; **Alias** : rien. Puis **Créer**.
3. En haut de la fiche, ajouter l'anglais : libellé `Karl Forterre`, description
   `French photographer and writer` (et, si on veut, le chinois : `法国摄影师、作家`).
4. Ajouter les déclarations une à une : **+ ajouter une déclaration**, taper le nom de la
   propriété, puis la valeur, et choisir dans la liste proposée. Les numéros (P…) aident
   à trouver la bonne propriété.

| Propriété | Valeur | Source (référence) |
|---|---|---|
| nature de l'élément (P31) | être humain | — |
| pays de nationalité (P27) | France | https://karlforterre.fr/ |
| occupation (P106) | photographe | https://www.pexels.com/@karl-forterre-28489473 |
| occupation (P106) | écrivain | notice BnF d'un des livres |
| occupation (P106) | graphiste | https://karlforterre.fr/ |
| prénom (P735) | Karl (l'élément « prénom masculin ») | — |
| langues parlées, écrites ou signées (P1412) | français | — |
| scolarité (P69) | université de Poitiers | https://karlforterre.fr/memoire/ |
| site officiel (P856) | `https://karlforterre.fr/` | — |
| site officiel (P856) | `https://photos.karlforterre.fr/` | — |
| adresse Mastodon (P4033) | `KarlForterre@mastodon.social` | — |
| identifiant Bluesky | `karlforterre.bsky.social` | — |
| identifiant LinkedIn (P6634) | `karl-forterre-720b61220` | — |
| décrit à l'URL (P973) | `https://photos.karlforterre.fr/a-propos/` | — |
| identifiant ORCID (P496) | une fois créé | — |
| identifiant BnF (P268) | si la notice d'autorité existe | — |

   Pour une source : sous la déclaration, **+ ajouter une référence** → propriété
   **URL de la référence** (P854), coller l'adresse ; puis **date de consultation**
   (P813), la date du jour. **Publier** après chaque déclaration.
5. Noter le numéro de la fiche (Q suivi de chiffres, en haut) : il sert plus bas.

Le lieu de résidence (P551, Niort) et le genre (P21) sont facultatifs : ce sont des
données personnelles, à ne donner que si Karl le souhaite.

### Créer la fiche du mémoire

1. **Créer un nouvel élément** : libellé `L'influence de la médiation auctoriale du site
   d'auteur` ; description `mémoire de master de Karl Forterre (université de Poitiers,
   2023)` ; en anglais : `master's thesis by Karl Forterre (University of Poitiers,
   2023)`.
2. Déclarations :

| Propriété | Valeur |
|---|---|
| nature de l'élément (P31) | mémoire de master |
| titre (P1476) | `L'influence de la médiation auctoriale du site d'auteur` (langue : français) |
| auteur (P50) | Karl Forterre (la fiche créée plus haut) |
| date de publication (P577) | juin 2023 |
| thèse soumise à (P4101) | université de Poitiers |
| langue de l'œuvre ou du nom (P407) | français |
| œuvre complète disponible à l'URL (P953) | `https://karlforterre.fr/livres/memoire-mediation-auctoriale-2023.pdf` |
| décrit à l'URL (P973) | `https://karlforterre.fr/memoire/` |
| identifiant DOI (P356) | s'il est déposé sur Zenodo ou HAL (partie 4) |

3. Revenir sur la fiche de Karl Forterre : **+ ajouter une déclaration** → **thèse ou
   mémoire** (P1026) → le mémoire.

### Les livres, si le temps le permet

Une fiche par livre : nature de l'élément `œuvre littéraire` (P31), genre (P136)
`roman` ou `conte`, auteur (P50), date de publication (P577, celle imprimée dans le
livre), langue (P407) `français`, ISBN-13 (P212), et en source la notice BnF. Puis, sur la
fiche de Karl Forterre, **œuvre notable** (P800) → chaque livre.

### Relier Wikidata au site

Sur GitHub, dans `vitrine/site.ini`, rubrique `[personne]`, ligne `profils =`, coller
l'adresse de la fiche : `https://www.wikidata.org/wiki/Q…`, puis **Commit changes**. Les
données de l'auteur de chaque page la reprennent dès la nuit suivante. Faire de même sur
karlforterre.fr (liste `sameAs` des données structurées d'`index.html`), ou le demander
à une session Claude.

## 3. Wikimedia Commons : douze photos de lieux

Wikimedia Commons est la photothèque de Wikipédia. Une photo qui y est déposée peut
illustrer les articles de Wikipédia dans toutes les langues, et la fiche Wikidata du lieu
(propriété « image », que Google et Bing affichent souvent). Chaque réutilisation
mentionne l'auteur, avec un lien. Compter deux heures pour douze photos.

### D'abord, la licence : une décision de Karl

Commons n'accepte pas la licence Pexels : il demande une licence libre. L'auteur reste
propriétaire de ses photos et peut en donner plusieurs licences à la fois : la même
photo reste sur Pexels sous la licence Pexels et va sur Commons sous licence libre.

- **CC BY-SA 4.0** (proposée par défaut) : chacun peut réutiliser la photo, la modifier et
  même la vendre, à condition de **citer Karl Forterre** et de partager ses
  modifications sous la même licence. C'est le choix conseillé : le crédit devient
  obligatoire, alors qu'il est facultatif sur Pexels.
- **CC BY 4.0** : pareil, sans l'obligation de partage à l'identique.
- Ces licences sont **irrévocables** : une photo versée reste libre. D'où le choix de
  douze photos de lieux, pas des plus vendables.

### Précautions

- **Liberté de panorama.** En France, un bâtiment ou une sculpture dont l'auteur est
  mort depuis moins de 70 ans (après 1955) ne peut pas être le sujet principal d'une
  photo sur Commons. Les douze photos ci-dessous montrent des monuments anciens, des
  paysages, ou des lieux d'Espagne, où la loi permet de photographier les bâtiments
  visibles de la rue.
- **Personnes.** Pas de personne reconnaissable au premier plan.
- **Prouver qu'on est l'auteur.** Ces photos sont déjà sur Pexels : un bénévole de
  Commons pourrait croire à une copie. Pour l'éviter :
  1. déposer les **fichiers d'origine**, en pleine définition, avec leurs données
     d'appareil (EXIF), et non les fichiers téléchargés de Pexels ;
  2. sur sa **page utilisateur** Commons (lien « Utilisateur » en haut), écrire :
     `Je suis Karl Forterre, photographe. Mes photos sont aussi publiées sur Pexels
     (https://www.pexels.com/@karl-forterre-28489473) et sur https://photos.karlforterre.fr.` ;
  3. ajouter à la rubrique `[reseaux]` de `vitrine/site.ini` la ligne
     `Wikimedia Commons = https://commons.wikimedia.org/wiki/User:KarlForterre` : le lien
     `rel="me"` du site prouve que le compte est bien celui de l'auteur ;
  4. dans la description de chaque photo, ajouter `Aussi publiée par l'auteur sur Pexels :`
     suivi de l'adresse Pexels de la photo.

  Si un bénévole demande malgré tout une preuve, suivre le lien qu'il indique pour
  envoyer une autorisation par courriel, depuis contact@karlforterre.fr.

### Déposer les photos

1. Se connecter sur https://commons.wikimedia.org avec le compte créé pour Wikidata.
2. Menu de gauche → **Importer un fichier** (l'assistant d'import).
3. **Sélectionner des fichiers multimédias à partager** : choisir les douze fichiers
   d'origine.
4. **Cette œuvre est mon propre travail** ; licence : **Creative Commons Attribution –
   Partage dans les mêmes conditions 4.0** ; cocher la confirmation.
5. Pour chaque photo :
   - **Titre** : le nom de fichier proposé dans le tableau ci-dessous (sans « .jpg ») ;
   - **Légende** : une phrase en français, puis **Ajouter une légende dans une autre
     langue** pour l'anglais ;
   - **Description** : ce que montre la photo, le lieu, puis la ligne « Aussi publiée
     par l'auteur sur Pexels : … » ;
   - **Date** : reprise des données de l'appareil ;
   - **Catégories** : celles du tableau (taper le début du nom, choisir dans la liste) ;
   - **Ce que montre ce fichier** (données structurées) : taper le nom du lieu et choisir
     la fiche Wikidata proposée.
6. **Publier**. La page de chaque photo indique ensuite comment la créditer :
   « Karl Forterre, CC BY-SA 4.0, via Wikimedia Commons ».

### Les douze photos proposées

Choisies pour la qualité, la netteté du sujet et l'absence de problème de droits, en
privilégiant les lieux encore peu photographiés sur Commons (nombre de fichiers relevé le
27 septembre 2026). Chaque identification est à confirmer par Karl, qui sait ce qu'il a
photographié.

| # | Photo (page du site) | Nom de fichier proposé | Catégorie Commons | À savoir |
|---|---|---|---|---|
| 1 | [38694057](https://photos.karlforterre.fr/photo/38694057/) | Villandry - jardins du château vus du ciel | Gardens of the Château de Villandry (119 fichiers) | jardins recréés à partir de 1906 par Joachim Carvallo, mort en 1936 |
| 2 | [23414381](https://photos.karlforterre.fr/photo/23414381/) | Niort - flèches de l'église Saint-André au-dessus de la ville | Église Saint-André (Niort) (27) | église néogothique de 1855-1863 ; le site la nomme à tort Notre-Dame |
| 3 | [10187432](https://photos.karlforterre.fr/photo/10187432/) | Marais poitevin - barques amarrées le long d'un canal | Marais Poitevin | préciser la commune si Karl la connaît |
| 4 | [34500384](https://photos.karlforterre.fr/photo/34500384/) | Cognac - hôtel de ville | Town hall of Cognac (10) | bâtiment de 1840 |
| 5 | [34894970](https://photos.karlforterre.fr/photo/34894970/) | Granville - phare du cap Lihou | Phare du cap Lihou (18) | |
| 6 | [34939450](https://photos.karlforterre.fr/photo/34939450/) | Îles Chausey - phare vu de la mer | Phare de Chausey (13) | |
| 7 | [13087478](https://photos.karlforterre.fr/photo/13087478/) | Moyemont - chemin bordé d'arbres en été | Moyemont (14) | la photo la plus vue du compte après la Lune et la Voie lactée |
| 8 | [13041935](https://photos.karlforterre.fr/photo/13041935/) | Xonrupt-Longemer - chapelle Saint-Florent | Chapelle Saint-Florent (Xonrupt-Longemer) (5) | chapelle de 1727, au bord du lac de Longemer |
| 9 | [39376205](https://photos.karlforterre.fr/photo/39376205/) | Bordeaux - monument aux Girondins, génie de la Liberté | Monument aux Girondins | monument de 1894-1901, sculptures d'Alphonse Dumilâtre |
| 10 | [39564918](https://photos.karlforterre.fr/photo/39564918/) | Ribadeo - plage des Cathédrales, arches rocheuses | As Catedrais beach (161) | Espagne |
| 11 | [39423921](https://photos.karlforterre.fr/photo/39423921/) | Irun - hôtel de ville | Town hall of Irun (22) | Espagne |
| 12 | [39228699](https://photos.karlforterre.fr/photo/39228699/) | Gijón - Universidad Laboral, église et tour | Universidad Laboral de Gijón, Tower of Universidad Laboral de Gijón | Espagne ; photographiée depuis l'espace public |

En plus, si Karl le souhaite : [38995522](https://photos.karlforterre.fr/photo/38995522/),
l'éclipse totale du 12 août 2026 vue de Galice, dans la catégorie « Solar eclipse of 2026
August 12 », qui ne compte encore qu'une photo : les articles de Wikipédia sur cette
éclipse cherchent des images de la totalité.

### Ensuite

- **Wikidata** : sur la fiche Wikidata d'un lieu qui n'a pas encore d'image (propriété
  « image », P18), on peut y mettre la photo. C'est l'endroit le plus visible : les
  moteurs et les assistants reprennent cette image.
- **Wikipédia** : ajouter une photo à un article qui n'en a pas, ou qui n'en a pas de
  bonne (Moyemont, la chapelle Saint-Florent), est bienvenu ; remplacer une bonne photo
  par la sienne, ou ajouter ses photos partout, passe pour de la promotion. Dans le doute,
  proposer la photo sur la page de discussion de l'article.
- **Pexels** : rien ne change ; les photos y restent, sous licence Pexels.

## 4. Les autres leviers, du plus efficace au moins utile

État des connaissances au 27 septembre 2026, d'après les documentations des éditeurs et
les études publiées (sources en fin de document).

### Être présent dans les trois index qui comptent

| Index | Qui s'en sert | Ce qu'il faut faire |
|---|---|---|
| Google | Gemini, AI Overviews, AI Mode | Google Search Console (déjà prévu). Nouveau depuis le 31 août 2026 : le rapport **Generative AI performance** montre les apparitions dans les réponses IA de Google, et le réglage **Search generative AI** doit rester sur « inclus » (c'est le réglage par défaut) |
| Bing | Copilot, DuckDuckGo, Yahoo, une partie de ChatGPT, la recherche d'images de Claude | Bing Webmaster Tools (partie 1) ; IndexNow est déjà en place |
| Brave | Claude, et Vibe (l'ex-Le Chat de Mistral) | Pas d'outil pour les sites : Brave explore le web de lui-même. Pour accélérer, proposer quelques adresses sur https://search.brave.com/submit-url : l'accueil des deux sites, la page du mémoire, les séries, les questions fréquentes |

ChatGPT a aussi son propre robot (OAI-SearchBot), comme Perplexity (PerplexityBot),
Claude (Claude-SearchBot) et Mistral (MistralAI-Index). Le `robots.txt` des deux sites
les laisse tous passer : il n'y a rien à faire.

**Entraînement des modèles.** D'autres robots (GPTBot, ClaudeBot, CCBot…) ne servent
qu'à entraîner les modèles, pas à citer. Ils sont admis aussi, pour que les modèles
eux-mêmes connaissent Karl Forterre. Pour les refuser sans perdre les citations, il
suffirait d'ajouter à `robots.txt` un bloc `User-agent: GPTBot` / `Disallow: /` (de
même pour ClaudeBot, MistralAI-Training, CCBot et Applebot-Extended) : c'est un choix
personnel, que ce guide ne tranche pas.

### Être cité ailleurs que chez soi

C'est le levier le plus fort. Les assistants citent plus volontiers les sources tierces
(médias, encyclopédies, forums, réseaux professionnels) que le site de la personne
elle-même, et la visibilité dans leurs réponses suit davantage le nombre de mentions d'un
nom sur le web que le nombre de liens.

- **Wikidata et Wikimedia Commons** : parties 2 et 3.
- **Presse locale** (La Nouvelle République, Le Courrier de l'Ouest, France 3
  Nouvelle-Aquitaine) : « un photographe niortais, 880 000 vues, des photos reprises par
  CNN.com et NYTimes.com ». Un article de presse est la source que les assistants
  préfèrent citer.
- **LinkedIn** : une des sources les plus citées par les réponses IA de Google. Y
  publier un article sur le mémoire (voir plus bas) et, de temps à autre, une série de
  photos avec le lien de sa page.
- **Reddit et les forums** : très lus par Perplexity et par Google. À la main
  seulement, en participant aux discussions (voir `docs/plan-site-pro.md`, « Communautés
  et forums ») : les publications automatiques ou répétées mènent au bannissement.
- **Offices de tourisme et lieux photographiés** : leur proposer des photos gratuites ;
  un lien depuis leur site vaut une recommandation.
- **Les usages déjà connus** : chaque nouvel usage signalé par Pexels, noté dans
  `vitrine/usages.csv`, s'affiche sur le site et dans les réponses aux questions
  fréquentes. Une recherche d'image inversée (Google Lens, TinEye) sur les photos les
  plus téléchargées en fait souvent trouver d'autres.

### Le mémoire et la notion de médiation auctoriale

Un mémoire de master n'existe pour les assistants que s'ils le trouvent là où ils
cherchent les travaux universitaires : Google Scholar, OpenAlex, Semantic Scholar, les
archives ouvertes. Aujourd'hui, il n'est qu'un PDF sur karlforterre.fr.

1. **Une page du mémoire sur karlforterre.fr**, en HTML, avec la problématique, les
   définitions citées mot pour mot, la méthode, les principaux résultats et la façon de
   le citer, et les balises que lit Google Scholar. Les assistants citent bien plus
   volontiers une page claire qu'un PDF de 223 pages.
2. **Un dépôt dans une archive ouverte**, qui donne au mémoire une adresse stable et
   le fait entrer dans les bases universitaires (pas à pas plus bas).
3. **Un identifiant ORCID** (https://orcid.org, gratuit) : il relie le nom de l'auteur à
   ses travaux, et Wikidata peut s'y référer.
4. **Une fiche Wikidata du mémoire**, reliée à celle de Karl Forterre (partie 2).
5. **Un article LinkedIn** qui présente la notion avec les mots du mémoire : sa
   définition, la question posée, deux ou trois résultats chiffrés, le lien vers la page
   du mémoire. Pas de résumé inventé : tout doit se retrouver dans le mémoire.

À éviter : créer soi-même un article Wikipédia sur la notion ou sur l'auteur. Wikipédia
demande des sources indépendantes (articles, ouvrages qui en parlent) et supprime les
autobiographies.

### Déposer le mémoire dans une archive ouverte

Une archive ouverte donne au mémoire une adresse permanente et le fait entrer dans les
bases que consultent les chercheurs et les assistants spécialisés (Google Scholar,
OpenAlex, OpenAIRE). Deux voies gratuites :

- **DUMAS** (https://dumas.ccsd.cnrs.fr), l'archive des mémoires de master, rattachée à
  HAL. Le dépôt passe par l'université et demande l'accord du directeur de mémoire :
  écrire à la bibliothèque universitaire de Poitiers (service des thèses et mémoires)
  pour savoir si l'université y dépose ses mémoires et comment. C'est la voie la plus
  reconnue en France.
- **Zenodo** (https://zenodo.org), l'archive ouverte du CERN, ouverte à tous :
  1. créer un compte (possible avec l'identifiant ORCID) ;
  2. **New upload** → déposer le PDF ;
  3. type de ressource : **Publication** → **Thesis** ; titre, auteur (avec son ORCID),
     date de publication (juin 2023), langue (français), description (la question et la
     méthode, reprises de la page du mémoire), mots-clés (médiation auctoriale, site
     d'auteur…) ;
  4. choisir la licence, puis **Publish**. Zenodo attribue un **DOI**, identifiant
     permanent que reconnaissent Wikidata, ORCID et les bases universitaires.

La licence est à choisir par Karl. Les annexes reproduisent des entretiens avec des
personnes nommées : une licence qui interdit la modification, **CC BY-NC-ND 4.0**
(partage libre, avec citation, sans usage commercial ni modification), est la plus
prudente.

Après le dépôt, ajouter le DOI à la fiche Wikidata du mémoire (P356), au profil ORCID et
à la page du mémoire sur karlforterre.fr (une session Claude peut s'en charger).

### Ce qui ne sert à rien, ou pas encore

- **`llms.txt`** : le site en publie un, parce qu'il ne coûte rien et que des outils
  (agents de programmation, navigateurs à agents) le lisent. Mais aucun grand assistant
  ne dit s'en servir pour choisir ses sources, et les études de 2025 et 2026 ne
  mesurent aucun effet sur les citations.
- **Le balisage FAQPage** : Google n'affiche plus ces résultats enrichis depuis mai
  2026. Ce qui compte, ce sont les questions et réponses lisibles dans la page, que les
  assistants peuvent reprendre telles quelles ; le balisage reste utile à Bing.
- **La ligne `Content-Signal` dans `robots.txt`** : sans effet hors de Cloudflare.
- **Un GPT personnalisé** : OpenAI n'en laisse plus créer sur les comptes personnels, et
  les GPT disparaissent le 11 décembre 2026.
- **Un serveur MCP ou NLWeb** pour dialoguer avec les assistants : il faut un serveur, ce
  que GitHub Pages ne fournit pas.
- **Des pages écrites « pour l'IA »**, bourrées de mots-clés ou déclinées par dizaines :
  Google les traite comme du contenu abusif, et les études montrent que le bourrage de
  mots-clés fait reculer.
- **Acheter des liens, des avis ou des abonnés** : proscrit, sur tous les réseaux.

Ce qui marche, en revanche, d'après l'étude de référence sur le sujet (Aggarwal et al.,
2024) : des phrases qui donnent des chiffres, des citations exactes et leurs sources.
C'est l'esprit des questions fréquentes : « 878 500 vues et 3 950 téléchargements sur
Pexels », « utilisées sur CNN.com, d'après Pexels », la définition citée avec sa page.

## 5. Suivre les résultats, une fois par mois

Avec le relevé des vues Pexels, dix minutes :

1. **Bing Webmaster Tools**, rapport **AI Performance** : citations dans Copilot.
2. **Google Search Console**, rapport **Generative AI performance** : apparitions dans
   les réponses IA de Google.
3. **GoatCounter** (une fois son code dans `site.ini`), rubrique des sites de
   provenance : les visites venues de `chatgpt.com`, `perplexity.ai`,
   `copilot.microsoft.com`, `gemini.google.com` ou `claude.ai`.
4. **Poser les mêmes questions aux assistants**, et noter les réponses dans
   `releves/assistants-ia.csv` (une ligne par question et par assistant) :

| Langue | Question |
|---|---|
| français | Qui est Karl Forterre ? |
| français | Où trouver des photos libres de droits des jardins de Villandry ? |
| français | Photo gratuite de l'éclipse totale du 12 août 2026 en Galice |
| français | Qu'est-ce que la médiation auctoriale ? |
| anglais | Free photos of Niort, France |
| anglais | Who photographed the gardens of Villandry on Pexels? |
| chinois | 维朗德里城堡花园 免费 照片 |

Colonnes : `date`, `assistant`, `question`, `cite` (oui ou non : le site, Pexels ou
karlforterre.fr apparaît-il dans la réponse ou ses sources ?), `source` (l'adresse
citée) et `remarque`. Si une réponse contient une erreur, la corriger à la source : sur
le site, sur Wikidata ou sur le profil concerné ; les boutons « mauvaise réponse » des
assistants ne font que signaler l'erreur à leur éditeur.

## Sources

Consultées le 27 septembre 2026. Les chiffres des études sont des tendances, pas des
promesses.

- Robots des assistants et leur rôle : OpenAI, https://developers.openai.com/api/docs/bots ;
  Anthropic, https://support.claude.com/en/articles/8896518 ; Perplexity,
  https://docs.perplexity.ai/guides/bots ; Mistral, https://docs.mistral.ai/robots/ ;
  Google, https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers
- ChatGPT et les sites : https://help.openai.com/en/articles/12627856-publishers-and-developers-faq
- Brave, fournisseur de la recherche de Claude : https://trust.anthropic.com/subprocessors ;
  soumission d'adresses : https://search.brave.com/help/brave-search-crawler
- Google et les réponses IA : https://developers.google.com/search/docs/appearance/ai-features
  et https://developers.google.com/search/docs/fundamentals/ai-optimization-guide ;
  page de profil : https://developers.google.com/search/docs/appearance/structured-data/profile-page
- Bing, rapport AI Performance (10 février 2026) :
  https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/ ;
  import depuis Google Search Console :
  https://blogs.bing.com/webmaster/september-2019/Import-sites-from-Search-Console-to-Bing-Webmaster-Tools
- IndexNow : https://www.indexnow.org/documentation et https://www.indexnow.org/faq
- llms.txt : https://llmstxt.org/ (version 2, août 2026) ; étude d'Ahrefs sur son usage
  réel : https://ahrefs.com/blog/llmstxt-study/
- Ce qui fait citer une page : Aggarwal et al., « GEO: Generative Engine Optimization »,
  https://arxiv.org/abs/2311.09735 ; Chen et al. (2025), https://arxiv.org/abs/2509.08919
- Wikidata : https://www.wikidata.org/wiki/Wikidata:Notability
- Wikimedia Commons : licences, https://commons.wikimedia.org/wiki/Commons:Licensing ;
  liberté de panorama, https://commons.wikimedia.org/wiki/Commons:Freedom_of_panorama
