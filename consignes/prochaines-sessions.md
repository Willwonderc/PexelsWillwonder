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
| T | Telepex : envoi automatique au tableau de bord | faite le 28 septembre | premier relevé envoyé le 28 septembre (voir T) |
| U | Telepex : tableau de bord, publications et vidéos | faite le 28 septembre | Telepex 1.2 (voir U) |
| F | Tableau de bord | faite le 28 septembre | GoatCounter relié le 28 septembre (voir F) |
| G | Google et Bing dans le tableau de bord | quelques jours après la vérification des deux sites | Search Console et Bing Webmaster Tools vérifiés (voir G) |
| H | Instagram | faite le 28 septembre | @karl_forterre est un compte « Créateur » depuis le 28 septembre |
| I | Galerie Niort | quand vous voulez | la pull request précédente fusionnée |
| L | Légendes Instagram | quand l'essai de la photo du jour annonce moins de 14 légendes prêtes | la pull request précédente fusionnée |
| V1 | Studio vidéo : fondations | quand vous voulez | la pull request précédente fusionnée |
| V2 | Studio vidéo : montage au niveau agence | après V1 | V1 fusionnée |
| V3 | Studio vidéo : son et voix | après V2 | V2 fusionnée |
| V4 | Studio vidéo : formats et diffusion | après V3 | V3 fusionnée |
| V5 | Studio vidéo : mesure | après V4 | V4 et F fusionnées |

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

## T — Telepex : envoi automatique au tableau de bord

Telepex est l'application Mac de Karl qui relève, pour chaque photo de son profil Pexels,
les vues, les téléchargements, les J'aime et le statut de modération, et qui en fait le
classeur Excel « Suivi photos Pexels » ; c'est de lui que vient la fiche de suivi du
24 septembre. Il reste sur le Mac, hors de ce dépôt public : ni son code ni sa méthode n'y
figurent. La session T lui fait envoyer tout seul, après chaque relevé, la feuille des
photos au tableau de bord : le site la traite automatiquement et se reconstruit en quelques
minutes. Le tableau de bord (F), la preuve sociale du site, les mots-clés des nouvelles
photos, l'ordre des épingles et la photo du jour partent alors de chiffres frais.

La feuille part en CSV, le format que lit le site : les mêmes lignes que les onglets
« Publiées » et « Non publiées » du classeur, plus légères et lisibles sur GitHub ; le
classeur Excel reste sur le Mac. La session se lance sur le Mac, dans Claude Code, dans le
dossier de Telepex, et non sur claude.ai/code : Telepex n'est pas sur GitHub et se compile
avec Xcode. Un envoi par semaine suffit aux courbes du tableau de bord et ménage le site de
Pexels ; chaque jour reste possible.

```text
Session T, dans le dossier de Telepex : Telepex doit envoyer tout seul, après chaque relevé, la feuille des photos au tableau de bord du site photo (dépôt public Willwonderc/PexelsWillwonder), qui la traite automatiquement. Rien de Telepex ne va dans ce dépôt, ni code, ni clé, ni adresse d'API : seulement la feuille du relevé.
1. À la fin de chaque scan complet, lancé à la main ou par le réglage du point 3, écris la feuille au format de releves/suivi-pexels.csv du dépôt (colonnes décrites dans https://github.com/Willwonderc/PexelsWillwonder/blob/main/releves/README.md), en UTF-8 sans BOM : photo, moderation (retenue pour approved, refusée sinon), import (AAAA-MM-JJ), vues, telechargements, jaime, evenement (oui ou non), titre (le titre Pexels, vide pour une photo sans titre, jamais le texte « Free stock photo of… »), mots_cles (séparés par des virgules), puis releve (date et heure du relevé, ISO 8601). Ce sont les lignes des onglets « Publiées » et « Non publiées » du classeur, qui reste sur le Mac. Un scan incomplet, où manquent des statistiques ou l'onglet Événements marquants, n'envoie rien.
2. Envoie-la par l'API de GitHub, en un seul commit « Relevé Telepex du AAAA-MM-JJ » qui remplace releves/suivi-pexels.csv et ajoute à releves/vues-pexels.csv la ligne du relevé : date, total des vues, nombre de photos, abonnés si le profil les donne, remarque « Telepex ». Jeton à grain fin limité à ce dépôt (Contents en lecture et écriture), que je range moi-même dans le trousseau du Mac. Si l'envoi échoue (pas de réseau, jeton expiré), Telepex le dit dans sa barre d'état et réessaie au relevé suivant ; il me prévient un mois avant l'expiration du jeton. Sans jeton, la feuille reste sur le Mac, prête à déposer à la main.
3. Un réglage de fréquence : chaque semaine, le lundi matin (par défaut), ou chaque jour, à heure fixe, même Telepex fermé (tâche launchd) ; un envoi par jour au plus ; et un bouton « Envoyer au tableau de bord » pour le faire à la demande.
4. Mets à jour CLAUDE.md et README.md de Telepex : la feuille du relevé, et elle seule, est envoyée au dépôt public. Vérifie sans prendre le contrôle de mon écran, et explique-moi pas à pas la création du jeton et le réglage, sans jamais me demander de coller le jeton dans la conversation.
```

Session faite le 28 septembre : premier envoi réel, commit « Relevé Telepex du
2026-09-28 » (919 photos, 895 030 vues, 20 abonnés), repris aussitôt par le tableau de bord
et `compteur.json`.

## U — Telepex : tableau de bord, publications et vidéos

La session U fait de Telepex le poste de publication de Karl, sur son Mac : le tableau de
bord du site en entier ; les publications à faire à la main (RedNote, Facebook), à copier
puis valider ; les vidéos des carrousels dans chaque langue. Les publications viennent
du site : chaque session qui en prépare une la dépose dans `reseaux/publications/`
(format : `reseaux/README.md`, « Publications à la main, dans Telepex »), et
`build.py` les publie dans `/tableau-de-bord/publications.json`, que lit Telepex. Chaque
validation rejoint le journal `reseaux/publications-validees.csv`, grâce au jeton de la
session T : la publication n'est plus proposée, et les sessions suivantes savent ce qui
est paru. Comme T, la session se lance sur le Mac, dans Claude Code, dans le dossier de
Telepex.

```text
Session U, dans le dossier de Telepex, après la session T : fais de Telepex mon poste de publication. Quatre onglets en haut de la fenêtre, dans le style actuel : « Photos » (la liste actuelle), « Tableau de bord », « Publications » et « Vidéos ». Telepex ne supprime jamais une photo ni une vidéo, et n'envoie au dépôt public Willwonderc/PexelsWillwonder que la feuille du relevé (session T) et le journal des publications (point 3).
1. Tableau de bord : la page https://photos.karlforterre.fr/tableau-de-bord/ en entier dans l'application (WKWebView), en mode clair ou sombre comme le Mac, avec « Actualiser », « Ouvrir dans le navigateur » et l'heure de sa dernière mise à jour (champ mis_a_jour de https://photos.karlforterre.fr/tableau-de-bord/compteur.json). Les liens vers d'autres sites s'ouvrent dans le navigateur. Après un envoi au tableau de bord (session T), Telepex attend que compteur.json change, le site se reconstruisant en quelques minutes, puis recharge l'onglet.
2. Publications : la liste https://photos.karlforterre.fr/tableau-de-bord/publications.json, que le site réécrit chaque nuit et après chaque modification (format décrit dans https://github.com/Willwonderc/PexelsWillwonder/blob/main/reseaux/README.md, « Publications à la main, dans Telepex ») : pour chaque publication RedNote ou Facebook, id, reseau, langue, titre, texte (hashtags compris), traduction, hashtags, images (adresse publique et nom, dans l'ordre), video, conseil, prevue et validee. Liste « À publier » par date prévue, celles du jour et en retard en tête, avec une notification à 13 h le jour prévu ; puis « Publiées ». Pour chaque publication : le pas à pas ; les images dans l'ordre (la 1 est la couverture), à envoyer sur mon iPhone par AirDrop, à glisser vers le navigateur ou à afficher dans le Finder ; chaque texte avec son bouton « Copier » (le presse-papiers universel le colle sur l'iPhone), la traduction à côté, sans bouton ; les vidéos du même sujet (champ carrousel) ; et « Valider » : publiée à telle date et heure (maintenant par défaut, modifiable), avec le lien de la publication, facultatif, gardé sur le Mac. « Annuler » la remet dans « À publier ».
3. Journal : chaque validation ajoute une ligne à reseaux/publications-validees.csv dans le dépôt (colonnes date,id,reseau,langue,remarque ; remarque « Telepex » ; jamais de lien), par l'API de GitHub avec le jeton de la session T, en un commit « Publication validée : <id> » : la publication n'est alors plus proposée. Sans réseau ou sans jeton, la validation attend sur le Mac et part à l'envoi suivant.
4. Vidéos : le dossier Documents Locaux/Caroussels (cherche où il est sur mon Mac, sans rien y modifier ; « Changer » en choisit un autre, mémorisé), avec ses dossiers « Chinois (RedNote) », « Français » et « Anglais ». Une ligne par carrousel, dans l'ordre des numéros (vidéos nommées « 1 - Ciels et nuits étoilées (chinois).mp4 », « … (français).mp4 », « … (anglais).mp4 »), une colonne par langue : vignette, durée, lecture dans l'application, Finder, AirDrop et partage, glisser vers le navigateur, « Copier le crédit musical » (tiré de « Musiques et licences (langue).txt ») et « Valider une publication » (réseau au choix, même journal). Une langue absente est signalée. Les vidéos ainsi nommées qui arrivent dans Téléchargements sont repérées : « Ranger » les déplace dans le dossier de leur langue, et me demande avant de remplacer une vidéo existante.
5. Mets à jour CLAUDE.md et README.md de Telepex : le journal des publications part désormais aussi au dépôt public. Vérifie sans prendre le contrôle de mon écran, avec une liste d'essai et de fausses vidéos rangées hors de mes dossiers, puis explique-moi pas à pas chaque onglet.
```

Session faite le 28 septembre : Telepex 1.2, qui ne verse au dépôt que la feuille du
relevé et le journal des publications.

- **Publications**, pas à pas : images datées dans l'ordre, envoyées par AirDrop ou
  glissées vers le navigateur ; vidéo du même sujet ; titre et texte à copier, la
  traduction à côté. Les boutons s'accrochent aux étapes de chaque publication, d'après
  quelques mots (`reseaux/README.md`, « Publications à la main, dans Telepex »).
- **Validation** datée (maintenant par défaut, modifiable), avec un lien facultatif gardé
  sur le Mac et jamais écrit dans le journal ; « Annuler » ; rappel à 13 h le jour prévu.
- **Carrousels** : vidéos repérées dans Téléchargements et rangées, même quand le
  téléchargement a simplifié leur nom ; crédit musical ; validation d'une vidéo publiée
  hors de la liste.
- **Tableau de bord** : heure de `compteur.json` (`mis_a_jour`) et rechargement après un
  envoi.

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

Session faite le 28 septembre 2026, avant la session T : le tableau de bord est en ligne sur
https://photos.karlforterre.fr/tableau-de-bord/ et se remplira des relevés de Telepex dès
leur arrivée. Pinterest reste relevé à la main : son API demande une application approuvée
et un jeton à renouveler. GoatCounter est relié depuis le 28 septembre (pas à pas :
`releves/README.md`, « Relier GoatCounter »). L'écran Turing prévu au départ est remplacé, au
choix de Karl, par un compteur des vues dans la barre des menus de son MacBook M1
(SwiftBar ; mode d'emploi : `releves/barre-des-menus/README.md`).

## G — Google et Bing dans le tableau de bord

Ajoute au tableau de bord du site, que Telepex affiche dans son onglet « Tableau de bord »
(session U), les chiffres de Google Search Console et de Bing Webmaster Tools. Google
apporte l'essentiel des visiteurs ; Bing, peu de visiteurs mais l'index de Copilot,
DuckDuckGo, Yahoo et d'une partie de ChatGPT, et un rapport des citations dans Copilot. À
lancer quelques jours après la vérification des deux sites (`referencement/README.md`,
« Reste à faire à la main »), pour que la session ait de vraies données à vérifier. Les
clés restent dans les secrets du dépôt : rien n'est à régler sur le Mac.

```text
Session G : Google Search Console et Bing Webmaster Tools dans le tableau de bord du site (que Telepex affiche dans son onglet « Tableau de bord »).
Les deux sites (photos.karlforterre.fr et karlforterre.fr) sont vérifiés dans Search Console, par la propriété de domaine karlforterre.fr. Si Bing Webmaster Tools n'est pas encore branché, guide-moi d'abord pas à pas (referencement/README.md, partie 1 : import depuis Search Console).
Ajoute ensuite au tableau de bord (/tableau-de-bord/, écrit par vitrine/build.py) une rubrique « Moteurs de recherche », remplie chaque nuit par la tâche GitHub, Google et Bing côte à côte :
1. Google, par l'API officielle de Search Console (Search Analytics, lecture seule), pour chaque site séparément : clics, impressions, taux de clic et position moyenne sur 28 jours et semaine par semaine, recherche web et recherche d'images à part ; les 10 recherches et les 10 pages qui amènent le plus de clics. Accès : un compte de service Google Cloud ajouté comme utilisateur « Restreint » de la propriété, sa clé JSON dans un secret du dépôt ; jeton obtenu dans la tâche GitHub par l'action officielle google-github-actions/auth, puis appels par urllib, sans dépendance Python.
2. Bing, par l'API officielle de Bing Webmaster Tools (clé API dans un secret du dépôt), pour chaque site : clics, impressions et position semaine par semaine, les 10 recherches et les 10 pages qui amènent le plus de clics, et les citations des pages dans Copilot (rapport AI Performance) si l'API les fournit.
3. Garde l'historique des semaines dans vitrine/donnees/historique.json, comme les autres chiffres. Aucune clé dans le code ni dans les journaux ; sans les secrets, le site se construit quand même et la rubrique le signale.
Vérifie la documentation officielle des deux API avant d'écrire le code (quotas, délai des données). Explique-moi d'abord pas à pas la création du compte de service Google, de sa clé, de la clé API Bing et des secrets, sans jamais me demander de coller une clé dans la conversation. Ouvre ensuite une pull request vers main et demande-moi avant de la fusionner.
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

## L — Légendes Instagram

Sur Instagram, tout est en français, dans un style proche de l'expression de Karl
(`reseaux/style-karl.md`). La photo du jour y prend la légende écrite à l'avance pour
chaque photo dans `reseaux/legendes-instagram.csv` (30 prêtes le 28 septembre, soit
jusque vers le 28 octobre) ; sans légende prête, elle garde le titre français.

```text
Session L : légendes Instagram de la photo du jour. Lance python3 reseaux/photo_du_jour.py --a-venir 90 : il liste la file Instagram et les légendes qui restent à écrire. Écris dans reseaux/legendes-instagram.csv les légendes des 60 photos suivantes de la file Instagram (ordre de photo_suivante : les plus vues d'abord), en français, dans le style de reseaux/style-karl.md (et les précisions de Karl qui y sont notées) : une à trois phrases, 300 caractères au plus, avec dans la colonne hashtags cinq hashtags choisis, rien d'inventé (titres, séries, galeries, souvenirs de reseaux/README.md), ligne éditoriale de CLAUDE.md. Regarde chaque photo en petite taille (adresse « image » de sa fiche dans vitrine/donnees/fiches.json, suivie de ?auto=compress&cs=tinysrgb&w=500) avant d'écrire. Montre-moi les dix premières avant d'écrire les autres, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## V — Studio vidéo

Plan complet et cahier des charges « agence » : [docs/plan-videos.md](../docs/plan-videos.md).
Programme actuel : `reseaux/videos/`, avec son mode d'emploi. Une session par chantier,
dans l'ordre, chaque pull request fusionnée avant la suivante.

### V1 — Fondations du studio

```text
Session V1 de docs/plan-videos.md : fondations du studio vidéo (programme actuel : reseaux/videos/, mode d'emploi dans son README).
1. Projets : un fichier .ini par sujet dans reseaux/videos/projets/ (photos, textes des trois langues, musiques, formats), lisible par moi. Convertis les cinq carrousels de donnees.py sans rien changer aux vidéos, et ajoute la création d'un projet à partir d'une série de vitrine/series.ini et des titres de vitrine/donnees/textes-*.csv.
2. Carrousels RedNote complets, en chinois et en français : couverture, photos en portrait et en paysage, petit cours de français, fin, au style des images de la page des carrousels (https://claude.ai/artifact/MpieDE6XVwk37bEa8quksx, à lire avec l'outil Artifact). Mesure-les au pixel comme diapositive.py, qui reproduit déjà les photos en paysage. Les vidéos chinoises ne doivent plus dépendre de cette page.
3. Contrôle qualité : reseaux/videos/qualite.py vérifie les règles du cahier des charges qui peuvent l'être dès maintenant (caractéristiques techniques lues par ffprobe, volume, durées, longueur et vitesse de lecture des textes, zones de sécurité, mots interdits de la ligne éditoriale, poids) et écrit un rapport lisible ; une vidéo en échec n'est pas livrée.
4. Tâche GitHub « Vidéos » (.github/workflows/videos.yml), lancée à la demande avec le nom du projet : carrousel, vidéos des trois langues et rapport à télécharger.
5. Miroir des musiques dans une version publiée (release) du dépôt, utilisé quand Internet Archive ne répond pas.
Vérifie que les cinq vidéos actuelles se refont à l'identique (images au pixel près), mets à jour reseaux/videos/README.md pas à pas, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

### V2 — Montage au niveau agence

```text
Session V2 de docs/plan-videos.md : montage au niveau d'une agence (règles A, R, T et M du cahier des charges). Accroche sur la photo la plus forte avec une promesse à l'écran, couverture à part ; rythme calé sur les temps forts de la musique ; cadrage guidé par le sujet (carte de saillance simple, détection des visages avec OpenCV) ; mouvements et transitions variés ; typographie animée mot à mot et gabarits de marque (logo animé discret, bas de titre, fin courte) ; carte animée de l'itinéraire pour les récits de voyage, sur fond Natural Earth ; couleurs homogènes et grain léger ; aperçu rapide en basse définition. Étends qualite.py aux nouvelles règles. Refais les cinq vidéos actuelles et montre-les-moi à côté des anciennes, en images et en vidéo, avant de les remplacer. Mets à jour le mode d'emploi, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

### V3 — Son et voix

```text
Session V3 de docs/plan-videos.md : son et voix (règles S du cahier des charges). Volume à −14 LUFS et crêtes à −1 dBTP, fin sur une phrase musicale, musique baissée sous la voix ; catalogue musical en fichier (morceau, ambiance, tempo, licence, crédit, adresse) avec un choix automatique conforme à CLAUDE.md ; habillage sonore tiré de banques CC0 ; version sans musique de chaque vidéo. Voix : je dépose un enregistrement fait sur mon iPhone ; transcription et sous-titres mot à mot avec Whisper, montage calé sur la voix. Voix de synthèse libre (Piper) en option pour l'anglais et le chinois, seulement si la licence de la voix le permet. Explique-moi d'abord comment enregistrer et déposer ma voix. Mets à jour le mode d'emploi, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

### V4 — Formats natifs et diffusion

```text
Session V4 de docs/plan-videos.md : formats natifs et diffusion (règles I, L et C du cahier des charges). Déclinaisons 9:16, 3:4, 1:1 et 16:9 d'un même montage, avec les zones de sécurité mesurées de chaque réseau et des durées par réseau ; kits de publication par réseau et par langue (titre, texte, hashtags, couverture, texte alternatif, heure conseillée), déposés dans reseaux/publications/ pour Telepex (reseaux/README.md) ; page d'aperçu où je valide chaque vidéo. Reels sur Instagram par l'API officielle, avec la connexion et le jeton de la photo du jour, seulement après mon accord, tout en français et dans le style de reseaux/style-karl.md ; YouTube Shorts par l'API officielle (vérifie sa documentation, le quota et l'audit nécessaire pour publier en public) ; une page par vidéo sur photos.karlforterre.fr avec le lecteur YouTube, des données VideoObject et un plan de site vidéo. Explique-moi d'abord pas à pas les accès à créer, sans jamais me demander de coller un mot de passe ou un jeton dans la conversation. Ouvre ensuite une pull request vers main et demande-moi avant de la fusionner.
```

### V5 — Mesure et amélioration continue

```text
Session V5 de docs/plan-videos.md : mesure et amélioration continue. Relevés par vidéo (spectateurs restés après 3 secondes, durée moyenne regardée, visionnages complets, partages, enregistrements, abonnés gagnés, clics vers le site) par les API d'Instagram et de YouTube, et à la main pour RedNote et Facebook dans un fichier de releves/ ; intégration au tableau de bord de la session F ; tests A/B de deux accroches ou de deux couvertures (Reels à l'essai d'Instagram si le compte y a accès) ; bilan mensuel qui propose d'ajuster les règles. Ouvre ensuite une pull request vers main et demande-moi avant de la fusionner.
```
