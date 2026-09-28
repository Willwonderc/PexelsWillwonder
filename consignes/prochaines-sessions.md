# Prochaines sessions : consignes prêtes à coller

Rédigées le 25 septembre 2026, d'après la feuille de route
[docs/plan-site-pro.md](../docs/plan-site-pro.md) et la fiche de suivi
[releves/suivi-pexels.csv](../releves/suivi-pexels.csv).

## Mode d'emploi

1. Sur claude.ai/code, ouvrir une **nouvelle session** sur le dépôt
   Willwonderc/PexelsWillwonder, dans l'environnement habituel. La clé Pexels n'est
   pas nécessaire : les fiches des 919 photos sont en cache.
2. Coller la consigne telle quelle.
3. En fin de session, laisser la session ouvrir sa pull request, puis la fusionner
   **avant de lancer la suivante** : chaque session part de `main`, et les sessions
   modifient les mêmes fichiers.
4. Une session à la fois, dans l'ordre. Si une session s'allonge, lui faire ouvrir
   sa pull request, la fusionner et continuer dans une nouvelle session : chaque
   échange d'une longue conversation coûte plus cher.

| Ordre | Session | Quand | Avant de la lancer |
|---|---|---|---|
| A | Site professionnel | semaine du 29 septembre | la pull request de ces consignes est fusionnée |
| B | Classement et file Pinterest | début octobre | A fusionnée |
| C | Traductions françaises | mi-octobre | B fusionnée |
| D | Atelier et modération | mi-octobre | C fusionnée |
| E | Réseaux : photo du jour | fin octobre | D fusionnée |
| T | Telepex : relevés frais pour le tableau de bord | octobre, avant F | rien ; elle se lance sur le Mac, dans Claude Code, dans le dossier de Telepex (voir T) |
| F | Tableau de bord | fin octobre | T faite et une semaine de relevés publiés par Telepex ; GoatCounter : fait, il compte depuis le 28 septembre |
| H | Instagram | faite le 28 septembre | @karl_forterre est un compte « Créateur » depuis le 28 septembre |
| I | Galerie Niort | quand vous voulez | la pull request précédente fusionnée |

Le site d'auteur karlforterre.fr (dépôt Willwonderc/karlforterre.fr) lit chaque visite
`https://photos.karlforterre.fr/apercu.json`, écrit par `vitrine/build.py` : une session
qui modifie `build.py` garde ce fichier et son format.

Si le crédit baisse plus vite que prévu : A, B et D d'abord. Après le 5 novembre,
les sessions restent possibles dans les limites de l'abonnement.

## A — Site professionnel

```text
Session A de docs/plan-site-pro.md : chantiers 1, 3, 5, 6 et 8, puis 2.
- Accueil plein écran et rubrique « Sélection » de 24 photos (vitrine/selection.txt) : propose-la parmi les photos les plus vues et les plus téléchargées de releves/suivi-pexels.csv, en variant sujets et lieux ; je la corrigerai.
- Visionneuse plein écran en JavaScript léger, sans bibliothèque, qui met à jour l'adresse de la page.
- Preuve sociale (vues et téléchargements sur Pexels) tirée des derniers relevés de releves/.
- Logo KF’ : vitrine/statique/logo.svg (vectoriel, currentColor) dans l'en-tête et comme icône du site ; version texturée d'origine : vitrine/statique/logo-kf.webp.
- Pages « Utiliser mes photos », « Mentions légales » et « Confidentialité ». Éditeur : Karl Forterre, contact@karlforterre.fr.
- Pages de séries (chantier 2), avec leurs textes en français et en anglais.
Garde le style sobre actuel. Vérifie le rendu sur ordinateur et sur téléphone, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## B — Classement et file Pinterest

```text
Session B de docs/plan-site-pro.md : chantiers 4 et 7.
1. D'abord le journal des parutions (chantier 4) : remplace le calcul du compte-gouttes de selection_flux (vitrine/build.py) par un fichier vitrine/donnees/parutions.json que la tâche de nuit complète et enregistre comme fiches.json. Il reprend les parutions déjà faites ; ensuite, les nouvelles photos passent en tête, le fonds suit par vues décroissantes (releves/suivi-pexels.csv), les photos ajoutées ou reclassées entrent dans la file sans être sautées ni republiées dans le même tableau, et jamais plus de 200 épingles par jour au total.
2. Ajoute les mots-clés Pexels de releves/suivi-pexels.csv au texte qui sert à composer les galeries, et affiche-en une douzaine sur les pages des photos qui n'ont pas de mots-clés de l'atelier.
3. Range chaque photo publiée dans au moins une galerie (vitrine/galeries.ini), en créant les galeries de thèmes et de lieux qui manquent. Travaille par lots avec des agents.
4. Pages par couleur, « photos proches » et fil d'Ariane.
5. Un texte de 150 à 300 mots par galerie, en français et en anglais.
Complète le tableau des flux de pinterest/README.md et donne-moi la liste des nouveaux flux à relier dans Pinterest. Ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## C — Traductions françaises

```text
Session C de docs/plan-site-pro.md, chantier 7 : traduis en français le titre et les mots-clés des photos publiées qui n'en ont pas encore dans vitrine/donnees/textes-fr.csv (environ 517 ; colonnes photo, titre_fr, mots_cles_fr). Traduis d'abord une seule fois le vocabulaire des mots-clés, sous forme de glossaire, puis les titres par lots avec des agents. Un français naturel, pas du mot à mot, avec les noms de lieux en usage en français. Vérifie que vitrine/build.py tourne, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## D — Atelier et modération

```text
Session D de docs/plan-site-pro.md : atelier titres et mots-clés.
1. Pour les 196 photos que vitrine/build.py laisse « en attente d'un titre » : titre et mots-clés en anglais, d'après leurs mots-clés Pexels (releves/suivi-pexels.csv, 186 en ont) et l'image en petite taille (adresse « image » de sa fiche dans vitrine/donnees/fiches.json, suivie de ?auto=compress&cs=tinysrgb&w=500), par lots avec des agents. Résultat dans un nouveau fichier de atelier/resultats/, au format de ppex-photos-sans-titre.csv ; traduction dans vitrine/donnees/textes-fr.csv. Range ensuite ces photos dans les galeries de vitrine/galeries.ini.
2. Compare les photos retenues et refusées par la modération de Pexels (colonne moderation de releves/suivi-pexels.csv) : sujets, titres, mots-clés, format, année d'import. Ajoute à atelier/README.md des conseils concrets pour choisir et préparer les prochains imports.
Ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## E — Réseaux : photo du jour

```text
Session E de docs/plan-site-pro.md, promotion automatique : chaque matin, une tâche GitHub publie une « photo du jour » sur Bluesky et sur Mastodon (ou Pixelfed) : l'image, son titre, trois ou quatre mots-clés en hashtags et le lien vers sa page du site. Elle commence par les photos les plus vues (releves/suivi-pexels.csv) et ne publie jamais deux fois la même, grâce à un journal tenu comme fiches.json. Secrets du dépôt : BLUESKY_IDENTIFIANT, BLUESKY_MOT_DE_PASSE_APPLI, MASTODON_INSTANCE et MASTODON_JETON. Explique-moi d'abord pas à pas comment créer ces comptes et ces accès, sans jamais me demander de coller un mot de passe ou un jeton dans la conversation. Ouvre ensuite une pull request vers main et demande-moi avant de la fusionner.
```

Si le connecteur Typefully est branché (https://claude.ai/customize/connectors),
ajouter à la fin : « Programme aussi un mois de publications sur X et Threads avec
Typefully. »

## T — Telepex : relevés frais pour le tableau de bord

Telepex est l'application Mac de Karl qui relève, pour chaque photo de son profil Pexels,
les vues, les téléchargements, les J'aime et le statut de modération ; c'est d'elle que
vient la fiche de suivi du 24 septembre. Elle reste sur le Mac, hors de ce dépôt public :
ni son code ni sa méthode n'y figurent. La session T lui fait publier son relevé dans
`releves/`, chaque semaine ou chaque jour, pour que le tableau de bord (F), la preuve
sociale du site, les mots-clés des nouvelles photos, l'ordre des épingles et la photo du
jour partent de chiffres frais. Chaque relevé publié reconstruit le site en quelques
minutes.

Elle se lance sur le Mac, dans Claude Code, dans le dossier de Telepex, et non sur
claude.ai/code : Telepex n'est pas sur GitHub et se compile avec Xcode. Une fois par
semaine suffit aux courbes du tableau de bord et ménage le site de Pexels ; chaque jour
reste possible.

```text
Session T, dans le dossier de Telepex : fais alimenter par Telepex le tableau de bord du dépôt public Willwonderc/PexelsWillwonder en relevés frais. Rien de Telepex ne va dans ce dépôt, ni code, ni clé, ni adresse d'API : seulement le relevé.
1. Après chaque scan complet, écris le relevé au format de releves/suivi-pexels.csv du dépôt (https://github.com/Willwonderc/PexelsWillwonder/blob/main/releves/README.md), en UTF-8 sans BOM : photo, moderation (retenue pour approved, refusée sinon), import (AAAA-MM-JJ), vues, telechargements, jaime, evenement (oui ou non), titre (le titre Pexels, vide pour une photo sans titre, jamais le texte « Free stock photo of… »), mots_cles (séparés par des virgules), puis une colonne releve (date et heure du relevé, ISO 8601). Un scan incomplet, où manquent des statistiques ou l'onglet Événements marquants, ne publie rien.
2. Publie-le à la place de releves/suivi-pexels.csv par l'API de GitHub, en un commit « Relevé Telepex du AAAA-MM-JJ », puis ajoute à releves/vues-pexels.csv la ligne du relevé : date, total des vues, nombre de photos, abonnés si le profil les donne, remarque « Telepex ». Jeton à grain fin limité à ce dépôt (Contents en lecture et écriture), que je range moi-même dans le trousseau du Mac ; sans jeton, le relevé reste sur le Mac, prêt à déposer à la main.
3. Un réglage de fréquence : chaque semaine, le lundi matin (par défaut), ou chaque jour, à heure fixe, même Telepex fermé (tâche launchd) ; un relevé par jour au plus ; et un bouton « Publier le relevé » pour le faire à la demande.
4. Mets à jour CLAUDE.md et README.md de Telepex : le relevé CSV, et lui seul, est publié dans le dépôt. Vérifie sans prendre le contrôle de mon écran, et explique-moi pas à pas la création du jeton et le réglage, sans jamais me demander de coller le jeton dans la conversation.
```

## F — Tableau de bord

La session F construit une page de suivi sur le site photo, que Karl garde dans ses
favoris et qu'aucune autre page ne mentionne, ainsi que le compteur du petit écran Turing
branché sur son PC. La page reprend aussi la consultation de Telepex (toutes les photos,
avec recherche, filtres et tri), depuis n'importe quel appareil ; la collecte des
chiffres, elle, reste sur le Mac. La page se met à jour chaque nuit, et quelques minutes
après chaque relevé enregistré sur GitHub :

| Chiffres | Source | Relevés par |
|---|---|---|
| Vues, téléchargements, J'aime, photos retenues par la modération, photos les plus vues | Telepex, l'application Mac de Karl | Telepex, chaque semaine ou chaque jour : il remplace `releves/suivi-pexels.csv` et ajoute une ligne à `releves/vues-pexels.csv` (session T) |
| Abonnés Pexels | profil Pexels | Telepex, si le profil les donne ; sinon Karl, dans `releves/vues-pexels.csv` |
| Visites, provenance, pages vues, clics vers Pexels | GoatCounter, qui compte depuis le 28 septembre | la tâche de nuit, par l'API de GoatCounter |
| Impressions, clics sortants, enregistrements, abonnés Pinterest | statistiques Pinterest | Karl, chaque semaine, dans `releves/pinterest.csv`, à moins que l'API de Pinterest se révèle simple (la session compare) |
| Citations du site par les assistants IA | `releves/assistants-ia.csv` | Karl, une fois par mois (déjà prévu) |

Ni le dépôt, ni ses tâches GitHub, ni la session ne vont chercher de chiffres sur
pexels.com : ils viennent des relevés de Telepex, et l'API officielle de Pexels, qui sert
aux fiches des photos, ne donne ni les vues ni les téléchargements.

Avant de la lancer :
1. Session T faite, et au moins une semaine de relevés publiés par Telepex.
2. Connaître le modèle de l'écran Turing (sa taille en pouces) et le système du PC où il
   est branché (Windows, Linux ou macOS) : la session les demandera.

La clé GoatCounter se crée pendant la session, qui explique comment la ranger dans les
secrets du dépôt.

```text
Session F : chantier 4 de docs/plan.md, le tableau de bord. Commence par m'expliquer pas à pas les accès à créer, sans jamais me demander de coller une clé ou un jeton dans la conversation, et par me demander le modèle de mon écran Turing et le système de mon PC ; construis la suite sans attendre ces accès.
1. Page https://photos.karlforterre.fr/tableau-de-bord/, en français seulement, écrite par vitrine/build.py à chaque passage, dans le style sobre du site : noindex, sans hreflang ni compteur GoatCounter, qu'aucune page ne mentionne, absente du plan du site, du journal des pages (donc d'IndexNow) et de llms.txt. Elle reste publique : rien de confidentiel dessus.
2. Pour chaque source, les derniers chiffres et leur évolution semaine après semaine (du lundi au dimanche), en tableau et en courbes SVG tracées par build.py, sans bibliothèque ; la date du dernier relevé, avec un rappel quand celui d'une source a plus de huit jours (Telepex arrêté, relevé oublié) ; un lien vers le détail (karlforterre.goatcounter.com, statistiques Pinterest, Google Search Console).
   - Vues et abonnés Pexels : releves/vues-pexels.csv.
   - Téléchargements, J'aime, photos retenues par la modération (dont les nouvelles de la semaine), dix photos les plus vues et leur gain de la semaine : releves/suivi-pexels.csv et son historique.
   - Toutes les photos, comme dans Telepex : vignette, titre, vues, téléchargements, J'aime, statut de modération, événement marquant, date d'import, gain de la semaine et lien vers sa page Pexels ; recherche par titre, mot-clé ou numéro, filtres (retenues, refusées, événements marquants) et tri (date, vues, téléchargements, J'aime, gain), en JavaScript léger sans bibliothèque, les vignettes chargées seulement à l'affichage.
   - Visites, provenance (Google, Bing, Pinterest, Bluesky, Mastodon, karlforterre.fr, assistants IA : chatgpt.com, perplexity.ai, copilot.microsoft.com, gemini.google.com, claude.ai), pages les plus vues, clics vers Pexels (événements pexels-<numéro>, pexels-image-<numéro> et suivre-pexels… de vitrine/README.md, « Mesure d'audience ») et dix photos les plus cliquées : GoatCounter.
   - Impressions, clics sortants, enregistrements et abonnés Pinterest.
   - Citations du site par les assistants IA : releves/assistants-ia.csv, relevé une fois par mois.
3. Relevés de Telepex (session T) : releves/suivi-pexels.csv, remplacé à chaque relevé, chaque semaine ou chaque jour (colonne releve : date et heure), et releves/vues-pexels.csv, qui reçoit une ligne par relevé. Tiens-en un historique compact : les totaux de chaque relevé et, par photo, de quoi calculer les gains de la semaine et du mois, dans un journal amorcé en session avec la fiche du 24 septembre 2026 (historique git de suivi-pexels.csv), puis enregistré par la seule tâche de nuit, comme parutions.json, et qui ne grossit que de quelques centaines de Ko par an. Une photo absente d'un relevé ou sans statistiques compte comme inconnue, jamais comme zéro.
4. GoatCounter : son API (vérifie d'abord sa documentation, https://www.goatcounter.com/help/api), avec une clé qui ne fait que lire les statistiques, rangée dans le secret du dépôt GOATCOUNTER_JETON et passée à build.py par .github/workflows/site.yml. Chiffres recalculés chaque nuit depuis le 28 septembre 2026, ou gardés dans un journal que seule la tâche de nuit enregistre, comme parutions.json. Sans clé, ou si GoatCounter ne répond pas, le site se construit et se publie quand même, et la page le signale.
5. Pinterest : compare le relevé à la main (releves/pinterest.csv, une ligne par semaine, lue dans Statistiques → Vue d'ensemble, ou l'export CSV de ces statistiques s'il existe) et l'API v5 (GET /v5/user_account/analytics : application à faire approuver par Pinterest, 90 jours d'historique au plus, jeton à renouveler au moins tous les 60 jours). Recommande-moi la solution la plus simple, gratuite et durable avant de la programmer.
6. Écran Turing : build.py publie aussi /tableau-de-bord/compteur.json (vues et abonnés Pexels, téléchargements, visites et clics vers Pexels des 7 derniers jours, date de chaque relevé). Sur mon PC, le programme libre turing-smart-screen-python (https://github.com/mathoudebine/turing-smart-screen-python ; vérifie qu'il prend en charge mon modèle) le relit toutes les heures grâce à une source de données personnalisée et l'affiche avec un thème, rangés dans releves/ecran-turing/ avec un mode d'emploi pas à pas. Essaie-le en session avec son écran simulé et montre-moi une capture ; l'essai final se fera sur mon PC.
Règles : Python sans dépendance pour le site ; ni la tâche de nuit ni toi n'allez chercher de chiffres sur pexels.com, ils viennent des relevés ; la clé n'apparaît ni dans le code ni dans les journaux ; garde apercu.json et son format ; essaie avec des chiffres fictifs que tu ne laisses pas dans le dépôt. Mets à jour releves/README.md (relevés de Telepex, relevés à la main, lecture du tableau de bord, écran Turing), README.md, docs/plan-site-pro.md et CLAUDE.md. Vérifie que vitrine/build.py tourne, que la page n'apparaît ni dans sitemap.xml, ni dans vitrine/donnees/pages.json, ni dans llms.txt, et son rendu sur ordinateur et sur téléphone ; puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## H — Instagram

Le compte Instagram @karl_forterre est passé en compte professionnel « Créateur » le
28 septembre 2026. Pour mémoire : sur instagram.com, « Plus », « Paramètres », puis,
dans la colonne des paramètres, rubrique « Pour les professionnels », « Type de compte
et outils », « Passer à un compte professionnel » ; si la rubrique manque sur le web,
dans l'application : profil, menu ☰, même rubrique. C'est gratuit et réversible, sans
Page Facebook ; le compte doit rester public. Le type de compte ne change pas les Reels
proposés à Karl : ils suivent ce qu'il regarde.

```text
Session H de docs/plan-site-pro.md, promotion automatique sur Instagram : mon compte Instagram @karl_forterre est un compte professionnel « Créateur ». Ajoute Instagram à la tâche « Photo du jour » (reseaux/photo_du_jour.py, .github/workflows/photo-du-jour.yml), par l'API officielle de Meta avec connexion Instagram, qui ne demande pas de Page Facebook. Vérifie d'abord sa documentation : image JPEG à une adresse publique (celle de images.pexels.com convient), rapport largeur/hauteur entre 4:5 et 1,91:1 (recadre les photos en hauteur en 4:5), 100 publications par 24 heures au plus, jeton valable 60 jours à renouveler automatiquement. Légende : titre, hashtags et renvoi vers le lien du site dans la biographie, puisque les légendes n'ont pas de liens cliquables. Tiens le journal reseaux/photo-du-jour.json comme pour les autres réseaux. Explique-moi d'abord pas à pas comment créer l'application Meta et le jeton, sans jamais me demander de coller un mot de passe ou un jeton dans la conversation. Ouvre ensuite une pull request vers main et demande-moi avant de la fusionner.
```

Session faite le 28 septembre 2026 : Instagram rejoint la photo du jour, et la tâche
« Jeton Instagram » renouvelle le jeton chaque lundi. Réglages à faire une fois, pas à
pas : `reseaux/README.md`, partie 5.

## I — Galerie Niort

```text
Session I de docs/plan-site-pro.md : une galerie de lieu dédiée à Niort, où j'habite. Aujourd'hui, Niort partage la galerie « Niort et le Poitou » ([niort-poitou] de vitrine/galeries.ini) avec Poitiers. Crée une galerie [niort] qui rassemble toutes mes photos prises à Niort, et garde [niort-poitou] pour le reste du Poitou. Mène une recherche consciencieuse, photo par photo, sur les 919 photos :
1. Mots-clés Pexels (releves/suivi-pexels.csv), titres et mots-clés de l'atelier (atelier/resultats/*.csv), titres français et chinois (vitrine/donnees/textes-fr.csv, textes-zh.csv), inventaire (atelier/inventaire.csv) et textes alternatifs des fiches (vitrine/donnees/fiches.json) : niort, niortais, deux-sèvres, sèvre niortaise, et les lieux de la ville (donjon, église Saint-André, Notre-Dame, les Halles, le Pilori, l'hôtel de ville, Port Boinot, la Brèche, la Coulée verte, le Moulin du Roc, les quais, le Vieux-Pont, le jardin des plantes…). Méfie-toi des mots-clés ajoutés par lots, souvent faux (voir CLAUDE.md).
2. Les photos d'un même import qu'une photo de Niort confirmée (numéros Pexels voisins, même date de publication) : regarde-les une à une en petite taille (adresse « image » de la fiche, suivie de ?auto=compress&cs=tinysrgb&w=500), par lots avec des agents.
3. Range le résultat dans un fichier de atelier/resultats/ en trois colonnes (sûre, probable, écartée) avec la raison de chaque choix, et montre-moi les photos « probables » sur une planche d'images avant de les ranger.
Ensuite : lignes mots, ajouter et retirer de [niort] ; texte de 150 à 300 mots en français, en anglais et en chinois, dans la ligne éditoriale de CLAUDE.md ; corrige les titres faux repérés en chemin ; donne-moi le nouveau flux Pinterest à relier. Vérifie que vitrine/build.py tourne, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```
