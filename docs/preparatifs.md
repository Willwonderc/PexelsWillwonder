# Préparatifs

Environ une heure, à faire soi-même avant de lancer les sessions. Pour cocher une case,
modifier ce fichier sur GitHub (icône crayon) et remplacer `[ ]` par `[x]`.

## Pexels

- Les collections par thème ne sont plus nécessaires : le site compose lui-même ses
  galeries (voir [plan.md](plan.md)).
- [x] Demander une clé API sur https://www.pexels.com/api/ (délivrée immédiatement à
      tout titulaire d'un compte).

## GitHub (dépôt Willwonderc/PexelsWillwonder)

- [x] Créer le dépôt et sa branche principale `main`.
- [x] Passer le dépôt en **public**, condition de l'hébergement gratuit du site.
- [ ] Ranger la clé dans les secrets du dépôt : Settings → Secrets and variables →
      Actions → New repository secret, nom `PEXELS_API_KEY`. Jamais dans le code.
- [ ] Une fois le dépôt public, choisir la publication par GitHub Actions :
      Settings → Pages → Build and deployment → Source : « GitHub Actions ».
- [ ] Facultatif : corriger la description du dépôt, qui indique « Promotion de Pixels ».
- [ ] Conseillé pour le référencement : prévoir un sous-domaine, par exemple
      photos.karlforterre.fr, pour le site. La session 1 indiquera le réglage DNS.

## claude.ai/code (environnement cloud)

- [ ] Ranger la clé dans l'environnement : menu de l'environnement dans la barre de
      titre d'une session → Edit, dans la rubrique des identifiants d'API si elle est
      proposée, sinon comme variable d'environnement nommée `PEXELS_API_KEY`. Les
      sessions ouvertes ensuite la reçoivent. Ne jamais coller la clé dans une
      conversation.
- [x] Accès réseau : l'environnement actuel joint déjà api.pexels.com et
      images.pexels.com (vérifié le 24 septembre 2026). Dans un nouvel environnement
      en accès « Custom », ajouter ces deux adresses.

## Pinterest

- [ ] Passer en compte professionnel (gratuit).
- [ ] Plus tard, une fois la vitrine en ligne : revendiquer le site, puis y relier son
      flux RSS.

## GoatCounter (mesure d'audience de la vitrine)

- [ ] Créer un compte gratuit sur https://www.goatcounter.com et noter l'identifiant
      choisi : la session 1 prévoit un emplacement pour lui.

## Après la session 1

- [ ] Faire pointer le lien du profil Pexels vers le site.
