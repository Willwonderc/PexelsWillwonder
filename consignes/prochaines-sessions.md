# Prochaines sessions : consignes prêtes à coller

Rédigées le 25 septembre 2026, d'après la feuille de route
[docs/plan-site-pro.md](../docs/plan-site-pro.md).

## Mode d'emploi

1. Sur claude.ai/code, ouvrir une **nouvelle session** sur le dépôt
   Willwonderc/PexelsWillwonder, dans l'environnement habituel. La clé Pexels n'est
   pas nécessaire : les fiches des 919 photos sont en cache.
2. Coller la consigne telle quelle, après avoir rempli ce qui est entre crochets.
3. En fin de session, laisser la session ouvrir sa pull request, puis la fusionner
   **avant de lancer la suivante** : chaque session part de `main`, et les sessions
   modifient les mêmes fichiers.
4. Une session à la fois, dans l'ordre. Si une session s'allonge, lui faire ouvrir
   sa pull request, la fusionner et continuer dans une nouvelle session : chaque
   échange d'une longue conversation coûte plus cher.

| Ordre | Session | Quand | Avant de la lancer |
|---|---|---|---|
| A | Site professionnel | semaine du 29 septembre | la pull request de ce plan est fusionnée ; logo déposé si disponible |
| B | Classement et file Pinterest | début octobre | A fusionnée |
| C | Traductions françaises | mi-octobre | B fusionnée |
| D | Atelier des photos sans titre | mi-octobre | C fusionnée |
| E | Réseaux : photo du jour | fin octobre | D fusionnée |
| F | Tableau de bord | fin octobre | GoatCounter créé, quelques relevés notés |

Si le crédit baisse plus vite que prévu : A, B et D d'abord. Après le 5 novembre,
les sessions restent possibles dans les limites de l'abonnement.

**Logo** (facultatif, avant A) : sur GitHub, ouvrir le dossier `vitrine/statique`,
puis Add file → Upload files, déposer le logo KF’ au format SVG sous le nom
`logo.svg` et cliquer sur Commit changes.

## A — Site professionnel

```text
Session A de docs/plan-site-pro.md : chantiers 1, 3, 5, 6 et 8, puis 2.
- Accueil plein écran et rubrique « Sélection » de 24 photos (vitrine/selection.txt) : propose une première sélection d'après les titres et les couvertures des galeries, je la corrigerai.
- Visionneuse plein écran en JavaScript léger, sans bibliothèque, qui met à jour l'adresse de la page.
- Preuve sociale « vues sur Pexels » tirée du dernier relevé de releves/vues-pexels.csv.
- Pages « Utiliser mes photos », « Mentions légales » et « Confidentialité ». Éditeur : Karl Forterre ; contact à afficher : [adresse e-mail].
- Logo : vitrine/statique/logo.svg s'il existe, sinon le nom en texte.
- Pages de séries (chantier 2), avec leurs textes en français et en anglais.
Garde le style sobre actuel. Vérifie le rendu sur ordinateur et sur téléphone, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## B — Classement et file Pinterest

```text
Session B de docs/plan-site-pro.md : chantiers 4 et 7.
1. D'abord le journal des parutions (chantier 4) : remplace le calcul du compte-gouttes de selection_flux (vitrine/build.py) par un fichier vitrine/donnees/parutions.json que la tâche de nuit complète et enregistre comme fiches.json. Il reprend les parutions déjà faites ; ensuite, les photos ajoutées ou reclassées entrent dans la file sans être sautées ni republiées dans le même tableau, et jamais plus de 200 épingles par jour au total.
2. Range chaque photo publiée dans au moins une galerie (vitrine/galeries.ini), en créant les galeries de thèmes et de lieux qui manquent. Travaille par lots avec des agents.
3. Pages par couleur, « photos proches » et fil d'Ariane.
4. Un texte de 150 à 300 mots par galerie, en français et en anglais.
Complète le tableau des flux de pinterest/README.md et donne-moi la liste des nouveaux flux à relier dans Pinterest. Ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## C — Traductions françaises

```text
Session C de docs/plan-site-pro.md, chantier 7 : traduis en français le titre et les mots-clés des photos publiées qui n'en ont pas encore dans vitrine/donnees/textes-fr.csv (environ 517 ; colonnes photo, titre_fr, mots_cles_fr), par lots avec des agents. Un français naturel, pas du mot à mot, avec les noms de lieux en usage en français. Vérifie que vitrine/build.py tourne, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## D — Atelier des photos sans titre

```text
Session D de docs/plan-site-pro.md : atelier titres et mots-clés pour les 196 photos que vitrine/build.py laisse « en attente d'un titre ». Regarde chaque image en petite taille (adresse « image » de sa fiche dans vitrine/donnees/fiches.json, suivie de ?auto=compress&cs=tinysrgb&w=500), par lots avec des agents. Titres et mots-clés en anglais dans un nouveau fichier de atelier/resultats/, au format de ppex-photos-sans-titre.csv ; leur traduction dans vitrine/donnees/textes-fr.csv. Range ensuite ces photos dans les galeries de vitrine/galeries.ini. Ouvre une pull request vers main et demande-moi avant de la fusionner.
```

## E — Réseaux : photo du jour

```text
Session E de docs/plan-site-pro.md, promotion automatique : chaque matin, une tâche GitHub publie une « photo du jour » sur Bluesky et sur Mastodon (ou Pixelfed) : l'image, son titre, trois ou quatre mots-clés en hashtags et le lien vers sa page du site. Jamais deux fois la même photo, grâce à un journal tenu comme fiches.json. Secrets du dépôt : BLUESKY_IDENTIFIANT, BLUESKY_MOT_DE_PASSE_APPLI, MASTODON_INSTANCE et MASTODON_JETON. Explique-moi d'abord pas à pas comment créer ces comptes et ces accès, sans jamais me demander de coller un mot de passe ou un jeton dans la conversation. Ouvre ensuite une pull request vers main et demande-moi avant de la fusionner.
```

Si le connecteur Typefully est branché (https://claude.ai/customize/connectors),
ajouter à la fin : « Programme aussi un mois de publications sur X et Threads avec
Typefully. »

## F — Tableau de bord

```text
Session F : chantier 4 de docs/plan.md, le tableau de bord. Une page du site non référencée (noindex, absente du plan du site) qui suit semaine après semaine les vues et abonnés Pexels (releves/vues-pexels.csv, relevés à la main), les clics vers Pexels mesurés par GoatCounter et les statistiques Pinterest, avec la solution la plus simple et gratuite pour les récupérer. Prévois aussi le compteur du petit écran Turing décrit dans docs/plan.md. Explique-moi d'abord les accès à créer, puis ouvre une pull request vers main et demande-moi avant de la fusionner.
```
