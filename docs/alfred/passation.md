# Passation pour Alfred — méthode, travail fait, travail en attente

Écrit le 19 novembre 2026 par la session Claude en ligne qui travaille sur les sites de
Karl (dépôts Willwonderc/PexelsWillwonder et Willwonderc/karlforterre.fr). Lisible à :
https://raw.githubusercontent.com/Willwonderc/PexelsWillwonder/main/docs/alfred/passation.md

## 1. La méthode

- **Les sessions préparent, Karl publie.** Sur Wikipédia, Commons et Wikidata, seul Karl
  publie, connecté au compte « Karl Forterre ». Les sessions écrivent les textes et les
  cases à coller, puis vérifient après coup.
- **Une ou deux publications Wikipédia par jour**, pas plus : un compte récent qui ajoute
  beaucoup de ses propres photos d'un coup peut passer pour de la promotion.
- **Vérifier avant d'écrire.** Avant de proposer un article « à créer », chercher s'il
  existe déjà dans toutes les langues (deux erreurs faites ainsi, corrigées : « Halles de
  Niort » existait en anglais, « Mairie de Bilbao » en français). Tout fait vient d'une
  source citée ; jamais de citation inventée. Rendu testé sans enregistrer
  (`action=parse`).
- **Une case de partie se colle seulement dans le lien de cette partie**
  (`action=edit&section=N`) ; collée dans la page entière, elle efface le reste.
- **Code :** chaque session travaille sur la branche `claude/quirky-feynman-uox27a`,
  ouvre une pull request vers `main`, vérifie (captures, essais), puis fusionne. Rien
  d'automatique n'est lancé en session vers des services extérieurs (IndexNow, Bing,
  réseaux) : seules les tâches GitHub le font. Les clés et jetons ne sont jamais écrits.
- **Ligne éditoriale** (`CLAUDE.md` du dépôt PexelsWillwonder) : Karl est communiste ;
  aucun texte ne doit laisser croire à une sympathie monarchiste, conservatrice ou de
  droite. Échanges en français, avec « tu ».

## 2. Travail fait (octobre–novembre 2026)

**Wikipédia**
- 26 photos de Karl illustrent 23 articles dans 5 Wikipédias (fr, en, es, eu, ast) ;
  liste : `vitrine/wikipedia.csv`. Elles ont eu 7 581 vues d'articles depuis leur ajout
  (jusqu'au 18 novembre) ; en tête : répliques de la statue de la Liberté (en), îles
  Chausey, éclipse du 12 août 2026.
- Panneau « Mes photos dans Wikipédia » et carte sur le site photo ; ligne sur la page de
  chaque photo concernée.
- Suivi complet : `docs/wiki-suivi/` (PDF « Vos photos dans Wikipédia », pistes.csv,
  creations.csv) ; protocole : `docs/wiki-route.md`.
- Textes prêts à publier : article « Halles de Niort », partie « Architecture » de
  « Mairie de Bilbao », article « Universidad Laboral de Gijón », cases pour 4 photos
  déjà sur Commons (`docs/wiki-suivi/articles/`).

**Sites**
- Site photo : albums (séries et galeries), titres anglais, données de licence des photos
  pour Google, langue par défaut dans le plan du site, image de partage des pages
  secondaires.
- Site d'auteur : plan du site daté, signalement automatique à Bing par IndexNow (7 pages
  acceptées le 19 novembre), image de partage des mentions légales.
- Audit SEO des deux sites (19 novembre) : aucune erreur bloquante.
- Rapport de fréquentation du 19 novembre (PDF de 6 pages, remis à Karl, hors dépôt) :
  Pexels 1 112 404 vues au 16 novembre (+26 % de rythme en un mois), 4 589
  téléchargements, 104 photos retenues ; site photo presque absent de Google depuis la
  semaine du 9 novembre, au moment de la grande mise à jour de Google lancée le 10
  novembre (le site n'a aucun défaut) ; site d'auteur stable ; Bluesky en progrès.

## 3. En attente, côté Karl (dans l'ordre, 1 ou 2 par jour)

Procédure détaillée, liens et résumés à coller : `docs/wiki-suivi/a-faire.md`.

1. Publier l'article « Halles de Niort », puis le relier à l'article anglais.
2. Publier la partie « Architecture » de « Mairie de Bilbao ».
3. Publier l'article « Universidad Laboral de Gijón », puis le relier à l'article espagnol.
4. Placer les 4 photos déjà sur Commons (éclipse en galicien, Moyemont et hôtel de ville
   de Niort en anglais, Universidad Laboral en galicien).
5. Verser 3 photos sur Commons (place Saint-Jean sous le givre, Niort et Saint-André,
   église de Buzy), puis demander à une session les cases à coller.
6. Commons : retirer la licence en double sur les fiches de Laval et de Nancy.
7. Wikidata : corriger la date de la photo de l'hôtel de ville de Cognac (22 juillet 2025).
8. Répondre à l'équipe VRT de Commons (dossier 2026092910011941) avec la liste des
   fichiers encore en attente d'autorisation : sans cela, ils peuvent être supprimés.
9. Pinterest : relier les flux des 5 nouvelles galeries.
10. Search Console, une fois la mise à jour de Google finie (vers fin novembre) : rapport
    « Pages », « Actions manuelles », inspection de `/en/galleries/pays-basque/`, puis
    envoyer des captures à une session.

## 4. En attente, côté sessions

- Traductions anglaises (église Saint-André de Niort, phare de Chausey, dolmen de Buzy),
  possibles quand le compte anglais de Karl aura 10 modifications (il en a 6).
- Cases du jour pour les 3 photos de l'étape 5, une fois versées.
- Vérifier chaque publication quand Karl dit « c'est fait », et mettre la photo dans le
  panneau du site.

## 5. Ce qu'Alfred peut faire

- Garder cette liste dans la boîte Hermès et rappeler à Karl l'étape suivante.
- Noter dans `docs/alfred/reponse.md` : date, étape faite, remarque. La session suivante
  le lit et vérifie.
