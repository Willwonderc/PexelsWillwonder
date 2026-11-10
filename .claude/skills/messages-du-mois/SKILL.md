---
name: messages-du-mois
description: >-
  Écrit les messages de la photo du jour des six prochaines semaines sur Bluesky,
  Mastodon et Instagram (reseaux/calendrier.csv, reseaux/legendes-instagram.csv) après
  le bilan d'audience du mois écoulé (reseaux/audience.md), les vérifie, puis ouvre et
  fusionne la pull request. C'est la tâche du 26 de chaque mois, autrefois consigne M
  de consignes/prochaines-sessions.md. À employer dès qu'il est question des messages
  du mois, de la session M, du calendrier de la photo du jour, des défis
  #UnJourUnePhoto, des légendes Instagram à écrire ou du bilan Bluesky et Mastodon,
  même si le mot « skill » n'est pas prononcé ; aussi pour retoucher un message déjà
  prévu.
argument-hint: "[mois visé, par exemple 2026-11]"
effort: max
---

# Messages du mois : Bluesky, Mastodon, Instagram

Règle de Karl, 30 septembre 2026 : aucune partie à la main ; des messages humains, dans
son style ; pour chaque message, le français ou l'anglais selon l'audience qu'il peut
toucher. Chaque jour, `reseaux/photo_du_jour.py` publie ce que tu écris ici (Bluesky et
Instagram à 6 h 47 UTC, Mastodon à 15 h 47 UTC). Un jour sans ligne, la photo part avec
un texte automatique (hashtags et titre) : c'est ce que ce travail évite. Le but : gagner
le plus d'audience possible, sans rien inventer.

La routine « Messages du mois, dans la conversation de Karl » lance ce travail le 26 de
chaque mois à 9 h 13, heure de Paris. Fonctionnement d'ensemble : `reseaux/README.md`,
« Des messages écrits à l'avance ».

## Période

- **Mois visé** : celui que donne la demande (par exemple `2026-11`) ; sinon, le mois qui
  suit la date du jour.
- **Bluesky et Mastodon** : une ligne par jour et par réseau dans `reseaux/calendrier.csv`,
  du 1er du mois visé au 7 du mois suivant, sans jour manquant. Les sept premiers jours du
  mois visé ont pu être écrits le mois dernier, avant que la liste des défis paraisse :
  réécris-les si tu fais mieux. Les lignes des jours passés, du jour même et des jours qui
  restent du mois en cours ne bougent pas, sauf erreur à corriger.
- **Instagram** : les 45 prochaines photos de sa file ont chacune leur légende.

## Garde-fous

La pull request est fusionnée sans relecture humaine, dans un dépôt public : rien d'autre
que ce travail ne doit y entrer.

- Ne modifie que `reseaux/calendrier.csv`, `reseaux/legendes-instagram.csv` et
  `reseaux/audience.md`, et n'ajoute qu'eux au commit, nommément (`git add` de ces trois
  fichiers, jamais `git add .`). Tes fichiers de travail (images, planches, relevés) vont
  dans un dossier hors du dépôt : le dossier temporaire de la session, ou à défaut
  `/tmp/messages-du-mois/`.
- Si la procédure elle-même doit changer (une API qui a bougé, une règle à préciser), ne
  touche pas à cette skill : propose le changement en tête de la pull request et dans ton
  message à Karl, qui décidera.
- Ne lance `reseaux/photo_du_jour.py` comme programme qu'avec `--essai`, `--calendrier`
  ou `--a-venir` : sans ces options, il publierait. Importer ses fonctions depuis Python
  (`lire_photos`) est sans risque.
- Jamais : publier toi-même sur un réseau ; aimer, suivre ou répondre à qui que ce soit
  (on mesure, on ne touche à rien : ce serait se faire passer pour Karl, et les réseaux le
  sanctionnent) ; collecter quoi que ce soit sur pexels.com (conditions de Pexels) ;
  lancer `--renouveler-jeton` (`photo_du_jour.py`) ou `--envoyer-indexnow`
  (`vitrine/build.py`) ; écrire un secret où que ce soit.

## 0. Préparer

1. Si le dépôt Willwonderc/PexelsWillwonder n'est pas dans la session : rattache-le avec
   l'outil `add_repo` (accès push), clone-le comme l'outil l'indique, puis appelle
   `register_repo_root`.
2. Travaille sur la branche que nomme la demande, sinon sur une nouvelle branche, repartie
   de `main` à jour (`git fetch origin main`, puis `git checkout -B <branche> origin/main`).
   Si cette branche existe déjà sur GitHub et que sa dernière pull request a été
   fusionnée, elle ne contient que de l'historique déjà fusionné : tu la pousseras avec
   `git push --force-with-lease`. Si une pull request est encore ouverte sur elle, ne
   l'écrase pas : prends une nouvelle branche et signale-le en tête de ta pull request.
3. Lis `CLAUDE.md` (sa ligne éditoriale surtout), puis dans `reseaux/` : `README.md`
   (« Des messages écrits à l'avance », et « Souvenirs et repères de Karl » dans la
   rubrique RedNote), `style-karl.md` et `audience.md`.

## 1. Bilan du mois écoulé, en lecture seule

Les résultats des messages de Karl mesurent son vrai public : c'est la meilleure boussole
pour le mois suivant.

1. Relève chaque message de Karl paru depuis le dernier bilan (la section datée la plus
   récente de `reseaux/audience.md`). Le journal `reseaux/photo-du-jour.json` donne,
   réseau par réseau, la photo, la date et le lien de chaque publication : c'est la clé
   sûre entre un message et sa photo (une ligne du calendrier inutilisable a pu laisser
   partir une autre photo). Les chiffres :
   - Bluesky : `https://api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=karlforterre.bsky.social&limit=100`
     (« j'aime », partages, réponses, citations ; `cursor` pour la suite) ;
   - Mastodon : `https://mastodon.social/api/v1/accounts/117335880653931296/statuses?limit=40`,
     puis les pages suivantes avec `max_id` (favoris, partages, réponses).

   Si le tableau de bord relève déjà ces chiffres (session R de
   `consignes/prochaines-sessions.md`, historique dans `vitrine/donnees/historique.json`),
   pars de ses données et complète par ces API.
2. Rapproche chaque message de sa ligne de `reseaux/calendrier.csv` (photo, sujet, langue,
   hashtags, jour de la semaine, défi ou non, forme du texte) et tire les leçons : quels
   sujets, quelles communautés, quelle langue, quels jours, quelle forme de texte ont le
   plus touché.
3. Mesure l'audience des hashtags candidats :
   - Bluesky, les 100 derniers messages de chacun
     (`https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=%23Hashtag&sort=latest&limit=100`) :
     messages par jour, « j'aime » en médiane, part en français (champ `langs`) ;
   - Mastodon : `https://mastodon.social/api/v1/tags/HASHTAG`, avec le nom du hashtag sans
     dièse (usages par jour sur une semaine).
4. Ajoute à `reseaux/audience.md` une section datée, au-dessus de la plus récente et sur
   son modèle : ces tableaux, les leçons, et les choix qui en découlent.

Si une API ne répond pas, fais le bilan avec ce qui reste (l'autre réseau, les mesures
précédentes de `reseaux/audience.md`) et dis-le en tête de la pull request : les messages
s'écrivent quand même, et cela n'empêche pas la fusion.

## 2. Langue de chaque message

Celle où la photo touche le plus de monde ce jour-là. Les résultats de Karl l'emportent sur
ceux des hashtags, car ils mesurent son vrai public. Par défaut, d'après les dernières
mesures : Bluesky en français, Mastodon en anglais. Un message peut partir dans l'autre
langue quand la photo a sa place dans une communauté nettement plus active et fidèle dans
cette langue. Instagram reste en français (règle de Karl).

## 3. Rendez-vous de la période

- **Défis #UnJourUnePhoto** : la communauté publie vers le 25 la liste des thèmes du mois
  suivant, un par jour, souvent en image. Cherche-la sur Bluesky (`searchPosts` avec
  `#UnJourUnePhoto`, puis `#PhotoNovember`, `#PhotoNovembre`… selon le mois), ouvre
  l'image et lis les thèmes. Garde le hashtag du mois tel que la liste l'écrit. Si la liste
  n'a pas encore paru, ces jours restent hors défi : dis-le en tête de la pull request.
- **Jours marquants** qui ont une photo sur le site : fêtes, changements de saison,
  rendez-vous du ciel (pleine lune, étoiles filantes, éclipse), journées nationales ou
  mondiales, dans la ligne éditoriale de `CLAUDE.md`.

## 4. Photos, une par jour et par réseau

Règles d'audience, resserrées par Karl le 10 novembre 2026 d'après le bilan d'octobre
(`reseaux/audience.md`) : elles priment sur le nombre de vues Pexels, qui ne dit rien du
public des réseaux. Seul un bilan qui les contredit, chiffres à l'appui, permet d'y
déroger, et tu le dis alors en tête de la pull request.

- **Bluesky : le défi du jour, tous les jours où une photo du site répond vraiment au
  thème** (cherche dans les titres et les mots-clés, fonction `lire_photos` de
  `reseaux/photo_du_jour.py`) : c'est lui qui porte les messages (médiane 7 « j'aime »,
  contre 4,5 hors défi). Cherche large avant de renoncer : un thème se prend aussi au
  figuré ou par la couleur, tant que le texte le dit sans tricher. Un jour sans photo
  possible part hors défi avec une communauté (`#FleurisTonFil` pour des fleurs,
  `#NoirEtBlanc` pour du noir et blanc) et un sujet qui a marché : animaux, Niort « chez
  moi », cuisine, mer, noir et blanc. **Jamais un monument ou un bâtiment officiel seul**
  (hôtel de ville, préfecture, façade), ni défi ni hors défi.
- **Mastodon : aucune ville, aucun monument, aucun phare, aucun portrait**, quel que soit
  le jour (0 à 5 favoris, médiane 1, contre 8 à 14 pour les sujets ci-dessous). Les deux
  seules exceptions : le vendredi, une fenêtre, un balcon ou un vitrail cadré serré
  (`#FensterFreitag`), et un jour marquant qui a sa photo (11 Novembre, par exemple).
  Chaque jour de la semaine a son sujet :
  - samedi, un chat (`#Caturday`, `#CatsOfMastodon` ; galerie `[chats]` de
    `vitrine/galeries.ini`, ou le mot-clé « chat ») ;
  - lundi, du noir et blanc (`#MonochromeMonday`), de préférence nature, animal ou objet ;
  - vendredi, une fenêtre (`#FensterFreitag`) ; à défaut, des champignons ou des fleurs ;
  - dimanche, le sujet le plus sûr qui reste : un animal ou des fleurs (pas de
    `#SilentSunday`, qui veut des photos sans texte) ;
  - les autres jours, dans cet ordre : oiseaux (`#BirdsOfMastodon`), fleurs, autres
    animaux, arbres et forêts, eau et paysages sans bâtiment, ciel et astronomie.
- **Les autres jours** de Bluesky, et à sujet égal sur Mastodon : parmi les photos jamais
  publiées sur ce réseau, d'abord les sujets qui ont le mieux marché (bilan) et les photos
  de circonstance (rendez-vous). L'ordre de
  `python3 reseaux/photo_du_jour.py --a-venir 80 --reseau bluesky --jour AAAA-MM-01` (ou
  `--reseau mastodon`), des plus vues sur Pexels aux moins vues, ne sert qu'à départager
  deux photos du même sujet.
- Au bilan (étape 1), classe chaque message de Karl par sujet (chat, oiseau, autre animal,
  fleurs, noir et blanc, fenêtre, paysage, ciel, ville ou monument, portrait, cuisine) et
  donne la médiane de chacun : c'est ce tableau qui confirme ou corrige ces règles.
- Varie les sujets et les lieux : jamais deux fois le même sujet deux jours de suite sur
  un réseau. L'homme à lunettes des portraits n'est jamais nommé.
- Regarde chaque photo en petite taille avant d'écrire, une à une ou en planches de
  plusieurs images : un texte écrit sans voir la photo finit par décrire autre chose.
  Télécharge-les dans ton dossier de travail, hors du dépôt :
  `curl -s -o DOSSIER/NUMÉRO.jpg "https://images.pexels.com/photos/NUMÉRO/pexels-photo-NUMÉRO.jpeg?auto=compress&cs=tinysrgb&w=500"`.

## 5. Textes

Dans le style de `reseaux/style-karl.md` (en français, et sa rubrique « En anglais »), et
dans la forme qui a le mieux marché au bilan. Une ou deux phrases humaines : ce qu'on voit
et où, puis une touche (image, jeu de mots, formule). Les lignes déjà écrites de
`reseaux/calendrier.csv` donnent le ton.

- **Rien d'inventé** : ce que la photo montre, où et quand, vient seulement des titres,
  mots-clés, galeries, séries de `vitrine/series.ini`, souvenirs notés dans
  `reseaux/README.md` et reprises de `vitrine/usages.csv` ; un lieu douteux ne se nomme
  pas. Le peu de contexte qu'admet `reseaux/style-karl.md` (histoire du lieu, nature,
  astronomie, date d'une pleine lune ou d'une journée mondiale) doit être exact et
  vérifié ; dans le doute, on s'en passe.
- Ligne éditoriale de `CLAUDE.md` ; pas d'émoji ; typographie française en français.
- **Bluesky** : `#UnJourUnePhoto #PhotoMois #Photography` (le hashtag du défi du mois ;
  plus `#FleurisTonFil` pour des fleurs, `#NoirEtBlanc` pour du noir et blanc), ligne vide,
  « 1. Thème », ligne vide, le texte ; hors défi : `#UnJourUnePhoto #Photography` (et la
  communauté qui convient, comme `#FleurisTonFil`), ligne vide, le texte. 300 caractères
  au plus. Le lien part tout seul en réponse.
- **Mastodon** : le texte, ligne vide, quatre ou cinq hashtags parmi les plus suivis
  (`reseaux/audience.md`). Le programme insère le lien avant les hashtags ; 500 caractères
  au plus avec lui.
- **Colonne `alt`** : ce que montre l'image, pour qui ne la voit pas, en une ou deux
  phrases factuelles dans la langue du message, sans hashtag ni « photo de » (sur Mastodon,
  beaucoup ne partagent que les images décrites).
- Une ligne par jour et par réseau dans `reseaux/calendrier.csv` : `date`, `reseau`,
  `photo`, `langue`, `theme` (pour mémoire, par exemple « #PhotoOctober 1 : Orange »),
  `texte`, `alt` ; `\n` pour aller à la ligne.

## 6. Légendes Instagram

Lance `python3 reseaux/photo_du_jour.py --a-venir 90`, puis écris dans
`reseaux/legendes-instagram.csv` les légendes qui manquent, pour que les 45 prochaines
photos d'Instagram en aient une. Règles de `reseaux/style-karl.md` : une à trois phrases,
300 caractères au plus, cinq hashtags, et pas le même texte qu'un message Bluesky ou
Mastodon de la même photo à quelques jours d'écart.

## 7. Vérifier

0. Relis la colonne `photo` de chaque ligne Mastodon de la période : aucune ville, aucun
   monument, aucun phare, aucun portrait hors des deux exceptions de l'étape 4 ; et chaque
   jour de défi Bluesky a sa photo, ou la raison de son absence en tête de la pull request.
1. `python3 reseaux/photo_du_jour.py --calendrier --jour AAAA-MM-JJ`, avec la date de
   demain, doit finir par « Calendrier prêt. ». Pars de demain : la ligne du jour est
   partie ou part dans la journée, et le contrôle la signalerait « déjà parue » une fois
   publiée.
2. `python3 reseaux/photo_du_jour.py --essai --jour AAAA-MM-JJ` sur trois jours de la
   période, dont un jour de défi s'il y en a et un samedi.
3. `python3 reseaux/photo_du_jour.py --a-venir 45` : aucune légende « à écrire ».
4. Relis chaque texte : faits, orthographe, typographie, longueur, langue.

## 8. Pull request, fusion et message à Karl

1. Commit en français (les trois fichiers seulement), pousse la branche, ouvre une pull
   request vers `main`. En tête : les leçons du mois et ce qui change. Puis le calendrier
   jour par jour (date, réseau, langue, photo avec son lien
   `https://photos.karlforterre.fr/photo/NUMÉRO/`, début du texte), la liste des défis et
   sa source, les légendes Instagram ajoutées.
2. Si les mesures montrent qu'une autre heure de publication gagnerait du public sur un
   réseau, propose-la en tête, sans la changer toi-même (elle se règle dans
   `.github/workflows/photo-du-jour.yml`).
3. Fusionne-la toi-même (squash) : Karl l'a autorisé le 30 septembre 2026, rien ne reste
   à la main. Si la demande dit de lui laisser la fusion, laisse-la ouverte.
4. Si une vérification échoue et que tu ne peux pas la corriger, ne fusionne pas : dis-le
   en tête de la pull request et préviens Karl. Les photos du jour partent quand même ;
   celles du mois visé, avec le texte automatique.
5. Termine par un message court à Karl : les leçons du mois, ce qui change, et le lien de
   la pull request.

## Retoucher un message déjà prévu

Pour corriger ou remplacer quelques lignes sans refaire le mois : garde les règles des
étapes 2, 4 et 5, vérifie comme à l'étape 7, puis ouvre une pull request et demande avant
de la fusionner, sauf si la demande t'y autorise. Karl peut aussi corriger une ligne
directement sur GitHub (crayon, *Edit*, puis *Commit changes*).
