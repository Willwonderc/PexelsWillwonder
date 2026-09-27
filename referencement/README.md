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
| L'auteur dans les données structurées | chaque page | Pour Google, Bing et les assistants, le site photo, karlforterre.fr, Pexels, Mastodon, Bluesky, LinkedIn, RedNote (et bientôt Wikidata) désignent une seule personne ; réglages : rubrique `[personne]` de `vitrine/site.ini` |
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
  (adresses reçues) ». Au premier envoi, Bing vérifie d'abord la clé : il répond 202, ou
  refuse l'envoi le temps de lire le fichier de clé (« SiteVerificationNotCompleted ») ;
  le travail patiente alors et renvoie la liste, pendant une vingtaine de minutes au
  plus. Une croix rouge signale un refus (clé ou adresses) : le message dit lequel.
- **Après une croix rouge**, relancer le travail le jour même : onglet **Actions** →
  tâche **Site** → **Re-run failed jobs**. La liste des pages à signaler n'est gardée
  qu'un jour ; passé ce délai, elles ne partiront qu'à leur prochaine modification.
- **Changer de clé** : remplacer la valeur de `indexnow` par 32 chiffres et lettres de
  a à f pris au hasard (une session Claude peut en tirer une). Laisser vide pour ne plus
  rien signaler.

## À faire à la main, dans cet ordre

| Étape | Temps | Pourquoi |
|---|---|---|
| [1. Bing Webmaster Tools](#1-bing-webmaster-tools) | 20 minutes | Suivre l'indexation par Bing, et voir combien de fois Copilot cite vos pages |
| Google Search Console | 20 minutes | Déjà prévue (`vitrine/README.md`, « Référencement ») : Gemini et les réponses IA de Google s'appuient sur l'index de Google |
| [2. Wikidata](#2-wikidata) | 20 minutes | Mettre les photos déposées sur Commons sur les fiches des lieux ; la fiche de Karl Forterre viendra après une notice BnF ou un dépôt du mémoire |
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
y relierait, par des identifiants vérifiables, ses deux sites, son profil Pexels, ses
réseaux, ses livres et son mémoire. Mais elle ne se crée pas n'importe comment.

### Où en est-on (vérifié le 27 septembre 2026)

- **Aucune fiche** Karl Forterre sur Wikidata, ni pour ses livres, son mémoire ou la
  Société des Éditions du Poitou.
- **Aucune notice d'autorité** à son nom à la BnF, dans IdRef (la base des universités)
  ou dans ISNI. Le catalogue de la BnF n'a pas non plus de notice pour les ISBN des deux
  livres.
- **Wikidata déconseille fortement de créer la fiche qui vous concerne**, ou celle de
  vos œuvres : c'est de l'autopromotion, et ces fiches sont souvent supprimées (page
  « Wikidata:Self-promotion »). Une réforme en discussion en septembre 2026 l'interdirait.
  En revanche, compléter une fiche qui existe déjà, avec des sources, est permis
  (« Wikidata:Autobiography »).
- Une fiche est admise si la personne est décrite par des **sources sérieuses,
  publiques et indépendantes** : une notice de la BnF, un dépôt dans une archive
  universitaire, un article de presse. Un profil Pexels, un site personnel ou un compte
  sur un réseau ne suffisent pas.

D'où l'ordre de marche : d'abord les sources indépendantes, puis la fiche, créée de
préférence par quelqu'un d'autre, que Karl pourra compléter.

### Étape 1, dès maintenant : les sources indépendantes

1. **Le dépôt légal des livres à la BnF.** Il est obligatoire pour tout livre diffusé en
   France : l'éditeur (ou l'auteur qui s'édite lui-même) le déclare en ligne sur
   https://depotlegal.bnf.fr et envoie un exemplaire. Le livre entre alors au catalogue
   général de la BnF, qui crée en général une notice d'autorité pour l'auteur, puis
   demande pour lui un identifiant ISNI. Demander à la Société des Éditions du Poitou si
   le dépôt a été fait.
   Les ISBN retenus sont ceux des fichiers les plus récents (été 2023), un par format :
   *Darshan*, 978-2-9588873-3-9 pour le papier et 978-2-9588873-4-6 pour l'EPUB ;
   *L'histoire du petit Théo*, 978-2-9588873-2-2 pour le papier. L'EPUB de *L'histoire
   du petit Théo*, exporté plus tôt, porte par erreur le 978-2-9588873-3-9 de *Darshan* :
   avant tout dépôt, lui demander son propre numéro à la Société des Éditions du Poitou.
   La première édition de *L'histoire du petit Théo*, publiée en ligne en 2021, avait un
   autre ISBN, 979-10-699-7416-6. L'édition actuelle des deux livres date de 2023.
2. **Le dépôt du mémoire dans DUMAS**, par la bibliothèque de l'université de Poitiers
   (partie 4) : une notice relue par la bibliothèque, dans HAL.
3. **Un article de presse** sur le photographe et ses photos reprises par CNN.com ou
   NYTimes.com (partie 4).

### Étape 2, dès maintenant : les photos sur les fiches des lieux

Une fois les photos déposées sur Wikimedia Commons (partie 3), les proposer comme image
des lieux sur Wikidata est une contribution ordinaire, bien acceptée quand la fiche n'a
pas encore d'image, et c'est la plus visible : Google, Bing et les assistants reprennent
souvent l'image d'une fiche.

1. Sur la page Commons de la catégorie du lieu (par exemple « Moyemont »), suivre le lien
   **Élément Wikidata** du menu de gauche, ou chercher le lieu sur https://www.wikidata.org.
2. Si la fiche n'a pas de déclaration **image** (P18) : **ajouter une déclaration** →
   `image` → taper le nom du fichier déposé sur Commons → **publier**.
3. Si elle a déjà une image, ne pas la remplacer par la sienne : en proposer le
   changement sur la page de discussion de la fiche, et seulement si la photo est
   nettement meilleure.

### Étape 3, plus tard : la fiche de Karl Forterre

Quand une source indépendante existe (notice BnF, dépôt DUMAS, article), la fiche peut
être créée, idéalement par un bibliothécaire ou un contributeur de Wikidata (les notices
de la BnF y sont régulièrement reprises). Karl peut ensuite la compléter. S'il décide de
la créer lui-même, qu'il le fasse seulement à ce moment-là, en citant ces sources.

**Créer un compte** : https://www.wikidata.org → **Créer un compte**. Le même compte sert
sur Wikimedia Commons et Wikipédia ; nom d'utilisateur conseillé : `KarlForterre`.

**Créer une fiche** : menu de gauche → **Créer un nouvel élément** ; champs **Langue**,
**Libellé**, **Description**, **Alias**, puis **Créer**. Pour un nom de personne, le
libellé peut aller dans le champ « par défaut pour toutes les langues ». La description
est courte, sans éloge et ne forme pas une phrase : `photographe et écrivain français`
(en anglais : `French photographer and writer`).

**Ajouter une déclaration** : **ajouter une déclaration** → taper le nom ou le numéro de
la propriété → la valeur → **ajouter une référence** → **URL de la référence** (P854) et
**date de consultation** (P813) → **publier**. Le site de Karl ne peut servir de source
que pour ce qui le concerne lui-même.

Propriétés vérifiées pour sa fiche :

| Propriété | Valeur |
|---|---|
| nature de l'élément (P31) | être humain (Q5) |
| prénom (P735) | Karl (Q15731830) |
| nom de famille (P734) | Forterre (Q65104104) |
| pays de nationalité (P27) | France (Q142) |
| occupation (P106) | écrivain (Q36180), photographe (Q33231), graphiste (Q627325) |
| scolarité (P69) | université de Poitiers (Q661056), avec le qualificatif diplôme universitaire (P512) : master (Q3297843) |
| site officiel (P856) | `https://karlforterre.fr/` et `https://photos.karlforterre.fr/` |
| adresse Mastodon (P4033) | `KarlForterre@mastodon.social` |
| identifiant Bluesky (P12361) | `karlforterre.bsky.social` |
| identifiant d'un profil LinkedIn (P6634) | `karl-forterre-720b61220` |
| identifiant de profil REDnote (P12038) | les 24 caractères qui suivent `xiaohongshu.com/user/profile/` dans l'adresse du profil |
| a un compte sur (P553) | Pexels (Q101240504), avec le qualificatif nom du compte (P554) : `karl-forterre-28489473` (il n'existe pas de propriété propre à Pexels) |
| nom d'utilisateur Wikimédia (P4174) | `KarlForterre` |
| identifiants BnF (P268), ISNI (P213), IdRef (P269), ORCID (P496) | quand ils existent |
| thèse académique (P1026) | la fiche du mémoire |
| décrit à l'URL (P973) | `https://photos.karlforterre.fr/a-propos/` |

Pour le mémoire : nature de l'élément (P31) `mémoire de maîtrise ou de master`
(Q1907875), titre (P1476), auteur (P50), date de publication (P577) juin 2023, organisme
de soutenance (P4101) université de Poitiers, langue de l'œuvre (P407) français, sujet
principal (P921), œuvre intégrale disponible sur (P953) l'adresse du PDF, et identifiant
DOI (P356) s'il est déposé sur Zenodo. Pour les livres, Wikidata distingue l'œuvre
(nature « œuvre littéraire ») et son édition (nature « édition », qui porte l'ISBN-13,
P212, et l'éditeur).

**Relier la fiche au site** : dans `vitrine/site.ini`, rubrique `[personne]`, ligne
`profils =`, coller l'adresse de la fiche (`https://www.wikidata.org/wiki/Q…`), puis
**Commit changes** ; faire de même dans les données structurées de karlforterre.fr
(liste `sameAs` d'`index.html`), ou le demander à une session Claude.

## 3. Wikimedia Commons : douze photos de lieux

Wikimedia Commons est la photothèque de Wikipédia. Une photo qui y est déposée peut
illustrer les articles de Wikipédia dans toutes les langues, et la fiche Wikidata du lieu
(propriété « image », que Google et Bing affichent souvent). Chaque réutilisation
mentionne l'auteur, sur la page de la photo. Compter deux heures pour douze photos, plus
un courriel d'autorisation.

**À saisir maintenant** : le concours Wiki Loves Monuments France court du 15 septembre
au 15 octobre 2026. Les photos de monuments historiques (le château et les jardins de
Villandry, par exemple) déposées par le formulaire du concours y participent :
https://www.wikimedia.fr/wiki-loves-monuments-2026-concours-photo-patrimoine/

### D'abord, la licence : une décision de Karl

Commons n'accepte pas la licence Pexels : il demande une licence libre, qui permet à
chacun tout usage, y compris commercial. L'auteur reste propriétaire de ses photos et
peut en donner plusieurs licences à la fois : la même photo reste sur Pexels sous la
licence Pexels et va sur Commons sous licence libre.

- **CC BY-SA 4.0**, le choix conseillé : chacun peut réutiliser la photo, la modifier et
  même la vendre, à condition de **citer Karl Forterre** et de partager ses
  modifications sous la même licence. Le crédit devient obligatoire, alors qu'il est
  facultatif sur Pexels.
- **CC BY 4.0** : pareil, sans l'obligation de partage à l'identique.
- Ces licences sont **irrévocables** : une photo versée reste libre. D'où le choix de
  douze photos de lieux, pas des plus vendables. Pour garder la pleine définition à
  Pexels, Commons accepte une version réduite, pourvu qu'elle garde au moins
  3 mégapixels (par exemple 3 000 pixels de large).

### Précautions

- **Liberté de panorama.** En France, un bâtiment ou une sculpture dont l'auteur est
  mort depuis moins de 70 ans (après 1955) ne peut pas être le sujet principal d'une
  photo sur Commons. Les douze photos ci-dessous montrent des monuments anciens, des
  paysages, ou des lieux d'Espagne, où la loi permet de photographier les bâtiments
  visibles depuis la rue.
- **Personnes.** Pas de personne reconnaissable au premier plan : en France comme en
  Espagne, il faudrait son accord.
- **Pas de signature ni de filigrane** sur les fichiers.
- **Fichiers d'origine.** Déposer les fichiers de l'appareil, avec leurs données
  (EXIF), et non ceux téléchargés sur Pexels : un fichier sans données d'appareil ou de
  faible définition éveille les soupçons.

### Prouver qu'on est l'auteur : un courriel, une fois pour toutes

Ces photos sont déjà publiées sur Pexels, sous une autre licence. Commons demande alors
à l'auteur de prouver son identité, même s'il les dépose lui-même ; sans cela, les
fichiers sont supprimés au bout de 30 jours. Le plus simple : une autorisation
permanente, qui vaut pour toutes les photos déposées depuis le compte.

1. Créer le compte (partie 2, même compte que Wikidata ; nom conseillé : `KarlForterre`).
   Un compte de moins de quatre jours doit remplir un code de vérification à chaque
   dépôt : rien de grave.
2. Sur sa **page utilisateur** Commons, écrire :
   `Je suis Karl Forterre, photographe. Mes photos sont aussi publiées sur Pexels
   (https://www.pexels.com/@karl-forterre-28489473) et sur https://photos.karlforterre.fr.`
3. Ajouter à la rubrique `[reseaux]` de `vitrine/site.ini` la ligne
   `Wikimedia Commons = https://commons.wikimedia.org/wiki/User:KarlForterre` : le site
   renvoie alors au compte, preuve de plus qu'il est bien celui de l'auteur.
4. Envoyer, depuis **contact@karlforterre.fr** (l'adresse du site est la meilleure
   preuve), à **permissions-fr@wikimedia.org**, le modèle « Déclaration de consentement »
   (https://commons.wikimedia.org/wiki/Commons:Messages_type/D%C3%A9claration_de_consentement)
   ou celui du générateur (https://commons.wikimedia.org/wiki/Commons:Wikimedia_VRT_release_generator),
   complété ainsi : Karl Forterre est l'auteur et le titulaire des droits des photos
   publiées sur son profil Pexels et sur photos.karlforterre.fr ; le compte Commons
   `KarlForterre` est le sien et il est autorisé à publier ces photos sous licence
   CC BY-SA 4.0. Le modèle fait confirmer qu'on a compris que chacun pourra les
   réutiliser, même commercialement, et que la licence ne peut pas être retirée.
5. Sur la page de chaque photo déposée, ajouter le modèle `{{PP}}` (autorisation en
   cours) : un bénévole le retire une fois le courriel traité.

### Déposer les photos

Dans l'assistant d'import (https://commons.wikimedia.org/wiki/Special:UploadWizard, ou
menu de gauche → **Importer un fichier**), qui compte six étapes :

1. **Téléverser** : **Sélectionnez les fichiers multimédias à partager**, choisir les
   douze fichiers, puis **Continuer**.
2. **Droits accordés** : **Il s'agit de mon propre travail et tout le monde est libre de
   l'utiliser.** → **Il s'agit d'un travail entièrement personnel** → à la question de
   la licence, choisir **Creative Commons Attribution – Partage dans les mêmes
   conditions (CC BY-SA 4.0)** : aucune licence n'est cochée d'avance. Si l'assistant
   demande à quoi sert l'œuvre : **Cette œuvre fournit des connaissances, des
   instructions ou des informations à d'autres.**
3. **Décrire**, pour chaque photo :
   - **Titre** : le nom proposé dans le tableau ci-dessous, avec l'année de la prise de
     vue (à vérifier dans les données de l'appareil) ;
   - **Légende** (obligatoire) : une phrase en français, puis **Ajouter une légende dans
     une autre langue** pour l'anglais ;
   - **Description** : ce que montre la photo et où, puis `Aussi publiée par l'auteur
     sur Pexels :` suivi de l'adresse Pexels de la photo ;
   - **Date** : reprise des données de l'appareil ;
   - **Catégorie** : celles du tableau (taper le début du nom et choisir dans la
     liste) ; on peut y ajouter une catégorie personnelle, `Photos by Karl Forterre` ;
   - **Emplacement** : repris des données de l'appareil s'il y en a.
   **Copier les informations pour les autres téléversements** évite de tout retaper.
   Puis **Publier les fichiers**.
4. **Ajouter des données** : dans **Les principaux sujets visibles dans cet ouvrage**,
   taper le nom du lieu et choisir sa fiche Wikidata. **Publier les données pour tous les
   fichiers**.
5. Sur la page de chaque photo, ajouter `{{PP}}` tant que le courriel n'a pas été traité.

La page de chaque photo indique ensuite comment la créditer : « Karl Forterre, CC BY-SA
4.0, via Wikimedia Commons ».

### Les douze photos proposées

Choisies pour la qualité, la netteté du sujet et l'absence de problème de droits, en
privilégiant les lieux encore peu photographiés sur Commons (nombre de fichiers relevé le
27 septembre 2026). Chaque identification est à confirmer par Karl, qui sait ce qu'il a
photographié.

| # | Photo (page du site) | Nom de fichier proposé (ajouter l'année de la prise de vue) | Catégorie Commons | À savoir |
|---|---|---|---|---|
| 1 | [38694057](https://photos.karlforterre.fr/photo/38694057/) | Villandry - jardins du château vus du ciel | Gardens of the Château de Villandry (119 fichiers) | sur Pexels depuis 2026 ; jardins recréés à partir de 1906 par Joachim Carvallo, mort en 1936 |
| 2 | [23414381](https://photos.karlforterre.fr/photo/23414381/) | Niort - flèches de l'église Saint-André au-dessus de la ville | Église Saint-André (Niort) (27) | sur Pexels depuis 2024 ; église néogothique de 1855-1863 ; le site la nomme à tort Notre-Dame |
| 3 | [10187432](https://photos.karlforterre.fr/photo/10187432/) | Marais poitevin - barques amarrées le long d'un canal | Marais Poitevin | sur Pexels depuis 2021 ; préciser la commune si Karl la connaît |
| 4 | [34500384](https://photos.karlforterre.fr/photo/34500384/) | Cognac - hôtel de ville | Town hall of Cognac (10) | sur Pexels depuis 2025 ; bâtiment de 1840 |
| 5 | [34894970](https://photos.karlforterre.fr/photo/34894970/) | Granville - phare du cap Lihou | Phare du cap Lihou (18) | sur Pexels depuis 2025 |
| 6 | [34939450](https://photos.karlforterre.fr/photo/34939450/) | Îles Chausey - phare vu de la mer | Phare de Chausey (13) | sur Pexels depuis 2025 |
| 7 | [13087478](https://photos.karlforterre.fr/photo/13087478/) | Moyemont - chemin bordé d'arbres en été | Moyemont (14) | sur Pexels depuis 2022 ; la photo la plus vue du compte après la Lune et la Voie lactée |
| 8 | [13041935](https://photos.karlforterre.fr/photo/13041935/) | Xonrupt-Longemer - chapelle Saint-Florent | Chapelle Saint-Florent (Xonrupt-Longemer) (5) | sur Pexels depuis 2022 ; chapelle de 1727, au bord du lac de Longemer |
| 9 | [39376205](https://photos.karlforterre.fr/photo/39376205/) | Bordeaux - monument aux Girondins, génie de la Liberté | Monument aux Girondins | sur Pexels depuis 2026 ; monument de 1894-1901, sculptures d'Alphonse Dumilâtre |
| 10 | [39564918](https://photos.karlforterre.fr/photo/39564918/) | Ribadeo - plage des Cathédrales, arches rocheuses | As Catedrais beach (161) | sur Pexels depuis 2026 ; Espagne |
| 11 | [39423921](https://photos.karlforterre.fr/photo/39423921/) | Irun - hôtel de ville | Town hall of Irun (22) | sur Pexels depuis 2026 ; Espagne |
| 12 | [39228699](https://photos.karlforterre.fr/photo/39228699/) | Gijón - Universidad Laboral, église et tour | Universidad Laboral de Gijón, Tower of Universidad Laboral de Gijón | sur Pexels depuis 2026 ; Espagne ; photographiée depuis l'espace public |

En plus, si Karl le souhaite : [38995522](https://photos.karlforterre.fr/photo/38995522/),
l'éclipse totale du 12 août 2026 vue de Galice, dans la catégorie « Solar eclipse of 2026
August 12 », qui ne compte encore qu'une photo et quelques sous-catégories : une vue de
la totalité y serait précieuse pour les articles de Wikipédia sur cette éclipse.

### Ensuite

- **Wikidata** : mettre la photo sur la fiche du lieu qui n'a pas encore d'image (partie
  2, étape 2). C'est l'endroit le plus visible : les moteurs et les assistants
  reprennent cette image.
- **Wikipédia** : ajouter une photo de qualité à un article qui n'en a pas, ou qui n'en a
  pas de bonne (Moyemont, la chapelle Saint-Florent), est en général bien reçu, même par
  l'auteur de la photo ; remplacer une bonne photo par la sienne, ou ajouter ses photos
  partout, passe pour de la promotion et peut valoir un blocage. Dans le doute, proposer
  la photo sur la page de discussion de l'article. Le crédit reste sur la page Commons de
  la photo, jamais dans la légende de l'article.
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
  CNN.com et NYTimes.com ». Les articles de presse sont parmi les sources que les
  assistants citent le plus volontiers.
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
  plus téléchargées peut en faire trouver d'autres.

### Le mémoire et la notion de médiation auctoriale

Un mémoire de master n'existe pour les assistants que s'ils le trouvent là où ils
cherchent les travaux universitaires : Google Scholar, OpenAlex, Semantic Scholar, les
archives ouvertes. Jusqu'ici, il n'était qu'un PDF sur karlforterre.fr.

1. **Une page du mémoire sur karlforterre.fr** (https://karlforterre.fr/memoire/, faite
   dans la même session) : la question posée, les définitions citées mot pour mot avec
   leur page, la méthode, les principaux résultats, le résumé anglais de l'auteur, la
   référence à citer, et les balises que lit Google Scholar. Les assistants citent bien
   plus volontiers une page claire qu'un PDF de 223 pages.
2. **Un dépôt dans une archive ouverte**, qui donne au mémoire une adresse stable et
   le fait entrer dans les bases universitaires (pas à pas plus bas).
3. **Un identifiant ORCID** (https://orcid.org, gratuit) : il relie le nom de l'auteur à
   ses travaux.
4. **Plus tard, une fiche Wikidata du mémoire**, reliée à celle de Karl Forterre, une
   fois les sources indépendantes réunies (partie 2).
5. **Un article LinkedIn** qui présente la notion avec les mots du mémoire : sa
   définition, la question posée, deux ou trois résultats chiffrés, le lien vers la page
   du mémoire. Pas de résumé inventé : tout doit se retrouver dans le mémoire.

À éviter : créer soi-même un article Wikipédia sur la notion ou sur l'auteur. Wikipédia
demande des sources indépendantes (articles, ouvrages qui en parlent) et supprime les
autobiographies.

### Déposer le mémoire dans une archive ouverte

Une archive ouverte donne au mémoire une adresse permanente et le fait entrer dans les
bases que consultent les chercheurs et les assistants spécialisés. Commencer par un
préalable, qui sert à tout :

**Un PDF de 5 Mo au plus, au format PDF 1.4 ou plus récent.** Le PDF actuel pèse 6 Mo
(surtout ses 52 images) et relève de la version 1.3 : trop lourd pour Google Scholar,
trop ancien pour DUMAS. Le plus simple : le réexporter depuis Pages, avec une qualité
d'image un peu moindre (**Fichier** → **Exporter vers** → **PDF**, **Qualité de
l'image** : **Bonne**). Si le fichier obtenu reste en version 1.3, la bibliothèque de
Poitiers, qui contrôle chaque dépôt, indique comment le convertir ; une session Claude
peut aussi préparer une version allégée. Déposé dans le dossier `memoire/` du dépôt
karlforterre.fr, ce fichier permettra d'ajouter à la page du mémoire la balise qui signale
le texte intégral à Google Scholar (règle de Google : le PDF dans le même dossier que la
page, 5 Mo au plus).

**DUMAS, par la bibliothèque de l'université de Poitiers : la voie conseillée.** DUMAS
(https://dumas.ccsd.cnrs.fr) est l'archive des mémoires de master, rattachée à HAL.
L'université de Poitiers y participe, et les anciens étudiants peuvent demander un dépôt
(https://bu.univ-poitiers.fr/appui-a-la-recherche/dumas/) :

1. obtenir l'accord du directeur de mémoire, Jean-François Cerisier, pour une diffusion
   en ligne ;
2. remplir le « Formulaire des données de dépôt » et le « Formulaire d'autorisation de
   diffusion étudiant·e » de la page de la bibliothèque, signés comme elle l'indique ;
3. envoyer le PDF, nommé `FORTERRE_Karl_2023_mémoire_M2.pdf`, avec les deux
   formulaires, à support.dumas@univ-poitiers.fr ;
4. la bibliothèque vérifie le fichier et le dépose. Un dépôt ne peut plus être retiré ;
   un embargo (une date de mise en ligne différée) est possible.

Attention aux annexes : la bibliothèque refuse les données personnelles et les images
d'autrui sans autorisation. Les entretiens nomment leurs participants, et le mémoire
reproduit des pages de sites d'auteurs : lui en parler avant l'envoi, quitte à déposer
une version sans ces annexes.

**Zenodo, si DUMAS n'est pas possible.** Zenodo (https://zenodo.org), l'archive ouverte
du CERN, accepte tout auteur qui a les droits sur ce qu'il dépose :

1. se connecter avec l'identifiant ORCID (ou créer un compte) ;
2. **New upload** → **Upload files** : le PDF ; à **Do you already have a DOI?**,
   répondre non puis **Get a DOI now!** ;
3. **Resource type** : **Thesis** ; **Title**, **Publication date** (2023-06),
   **Add creator** (Karl Forterre, avec son ORCID) ; description (la question et la
   méthode, reprises de la page du mémoire), mots-clés, langue ;
4. licence : Zenodo propose CC BY 4.0 ; choisir plutôt **CC BY-NC-ND 4.0** (partage
   libre, avec citation, sans usage commercial ni modification), plus prudente pour un
   mémoire qui cite des entretiens et des images d'autrui ;
5. **Save draft** → **Preview** → **Publish**. Un dépôt ne se supprime que dans les
   30 jours.

Zenodo attribue un **DOI** (identifiant permanent) et alimente OpenAIRE et OpenAlex,
mais, d'après sa propre aide, pas Google Scholar : d'où l'intérêt de la page du mémoire
sur karlforterre.fr et de DUMAS.

**ORCID** (https://orcid.org) : gratuit. Rubrique **Works** → **+ Add** : ajouter le
mémoire (par son DOI s'il en a un, sinon à la main, avec l'adresse de sa page) et les
deux livres (par leur ISBN).

Après le dépôt, ajouter le DOI ou l'adresse DUMAS à la page du mémoire sur
karlforterre.fr, à ORCID et, le moment venu, à Wikidata.

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
- Wikidata : admissibilité, https://www.wikidata.org/wiki/Wikidata:Notability ;
  autopromotion, https://www.wikidata.org/wiki/Wikidata:Self-promotion ; fiche sur
  soi-même, https://www.wikidata.org/wiki/Wikidata:Autobiography
- BnF : dépôt légal, https://depotlegal.bnf.fr et
  https://www.bnf.fr/fr/le-depot-legal-de-lautoedition-la-bnf
- Wikimedia Commons : licences, https://commons.wikimedia.org/wiki/Commons:Licensing ;
  liberté de panorama, https://commons.wikimedia.org/wiki/Commons:Freedom_of_panorama ;
  photos déjà publiées ailleurs, https://commons.wikimedia.org/wiki/Commons:Volunteer_Response_Team ;
  noms de fichiers, https://commons.wikimedia.org/wiki/Commons:File_naming
- DUMAS à l'université de Poitiers : https://bu.univ-poitiers.fr/appui-a-la-recherche/dumas/
  et https://bu.univ-poitiers.fr/faq-dumas/
- Google Scholar, règles d'inclusion : https://scholar.google.com/intl/en/scholar/inclusion.html
- Zenodo : https://help.zenodo.org/docs/deposit/create-new-upload/ ; Zenodo et Google
  Scholar : https://support.zenodo.org/help/en-gb/18-general/61-is-zenodo-indexed-by-google-scholar
