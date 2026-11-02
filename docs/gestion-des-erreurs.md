# Que faire quand une alerte arrive

Le site photo, le site d'auteur et leurs tâches tournent seuls, et envoient parfois une
alerte par courriel. La plupart ne demandent rien. Pour chacune, ce document dit ce
qu'elle veut dire et ce qu'il faut faire. Les sessions Claude le tiennent à jour.

## Trois règles

1. **Ne jamais coller un mot de passe, une clé ou un jeton dans une conversation**, même
   avec Claude. Un jeton se colle seulement dans GitHub (Settings → Secrets) ou dans
   Telepex.
2. **Une alerte isolée se règle souvent seule** : chaque tâche repasse le lendemain, ou
   le jour même. Si elle revient deux jours de suite, l'envoyer à une session Claude, avec
   une capture d'écran ou le lien du courriel.
3. **Dans Search Console, ne cliquer sur « Valider la correction » qu'après une
   correction.**

## Point au 2 novembre 2026

- **Search Console, « Explorée, actuellement non indexée »** : ce n'est pas une erreur
  (voir plus bas). Sur les pages anglaises du site photo, 389 photos portaient encore leur
  titre français. Le 2 novembre, 346 ont reçu un titre anglais ; les 43 autres ont un titre
  qui se lit dans toutes les langues (« Sushi », « Pizza », un nom de lieu). Des pages plus
  distinctes ont plus de chances d'entrer dans Google.
- **« Champ copyrightNotice manquant »** : il ne manquait que sur la page « Utilisées dans
  des projets », dans ses trois langues. Il y est depuis le 2 novembre, et toutes les
  images décrites du site ont désormais cette mention. La correction est en ligne quelques
  minutes après son enregistrement sur `main` : la valider alors dans Search Console (voir
  plus bas).
- **Jetons GitHub (courriels des 23 et 24 octobre)** : rien ne s'est arrêté. Telepex a
  envoyé son relevé le 2 novembre au matin, et la tâche « Jeton Instagram » a réussi le
  26 octobre. Le jeton expiré n'était donc ni celui de Telepex ni celui de la tâche
  Instagram. Pour tout autre jeton, comme « Claude », regarder sa dernière utilisation
  (voir « GitHub »).

## Google Search Console (et Bing Webmaster Tools)

| Message | Ce que cela veut dire | Que faire |
|---|---|---|
| « Explorée, actuellement non indexée » | Google a lu la page, mais ne l'a pas mise (pour l'instant) dans ses résultats. C'est son choix, fréquent pour un site jeune dont beaucoup de pages se ressemblent : une par photo, en trois langues. | Rien, et ne pas lancer de validation. Pour une page importante seulement (accueil, galeries) : **Inspection de l'URL** → **Demander une indexation**. Google limite ces demandes à quelques-unes par jour. |
| « Détectée, actuellement non indexée » | Google connaît l'adresse, mais ne l'a pas encore lue. | Rien : attendre. |
| « Page avec redirection », « Autre page avec balise canonique correcte », « Exclue par la balise noindex » | C'est normal : ce sont d'anciennes adresses qui renvoient ailleurs, des variantes d'une même page, ou le tableau de bord, caché exprès. | Rien. |
| « Introuvable (404) » | L'adresse n'existe plus : une ancienne adresse ou une photo retirée. | Rien, sauf si la page est récente ou importante : alors, une capture à une session. |
| Courriel « Échec de certaines corrections pour Indexation des pages » | Une validation lancée sur « Explorée, actuellement non indexée » ne peut pas réussir tant que Google choisit de ne pas indexer ces pages. Rien n'est cassé. | Rien. Ne pas relancer la validation. |
| Courriel « Données structurées … problèmes non critiques » (par exemple « Champ "copyrightNotice" manquant ») | C'est une suggestion, pas une erreur : la page s'affiche quand même dans Google. | Une capture à une session, qui ajoute le champ. Une fois la correction en ligne : **Améliorations** → le rapport concerné → **Valider la correction**. |
| « Problèmes critiques » dans les données structurées | Plus rare : une information obligatoire manque. | Une capture à une session. |

## GitHub

| Message | Ce que cela veut dire | Que faire |
|---|---|---|
| Courriel « Run failed », croix rouge dans **Actions** | Une tâche automatique a échoué. Site photo : « Site » chaque nuit, « Photo du jour », « Jeton Instagram » le lundi. Site d'auteur : « Pages en anglais et en chinois », « Darshan ». | Une fois : rien, elle repasse. Deux fois de suite : ouvrir la tâche (lien du courriel), puis l'étape en rouge. Pour la photo du jour, le tableau « En cas de croix rouge » de `reseaux/README.md` (partie 5.9) donne la cause. Sinon, envoyer le lien à une session. |
| « Your fine-grained personal access token is about to expire » ou « has expired » | Un jeton, c'est-à-dire une clé d'accès à GitHub, arrive à échéance. Son nom figure dans le courriel. | Ouvrir GitHub → photo de profil → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**. Chaque jeton y montre son nom, son échéance et sa dernière utilisation (*Last used*). S'il ne sert plus : le laisser expirer, puis le supprimer (**Delete**). S'il sert encore : l'ouvrir, puis **Regenerate token** (ou en créer un nouveau, avec les mêmes droits) ; choisir une nouvelle échéance, puis coller la nouvelle valeur là où il sert (ci-dessous). |
| « Scheduled workflows disabled » | GitHub arrête les tâches planifiées d'un dépôt public resté 60 jours sans activité. Les relevés de Telepex l'évitent. | **Actions** → la tâche → **Enable workflow**. |

Où sert chaque jeton connu :

- **« Jeton Instagram »** : secret `JETON_GITHUB` du dépôt PexelsWillwonder. Il permet de
  renouveler le jeton Instagram chaque lundi. Le mode d'emploi conseille de le créer sans
  échéance (*No expiration*) : un courriel d'échéance à son nom veut dire qu'il en a une,
  et il faut alors le refaire avant la date. Pour le remplacer : dépôt → **Settings** → **Secrets and variables** →
  **Actions** → `JETON_GITHUB` → **Update secret** (pas à pas : `reseaux/README.md`, 5.7).
- **Le jeton de Telepex** : rangé dans le trousseau du Mac, par les réglages de Telepex,
  qui prévient un mois avant son échéance.
- **Tout autre jeton** (par exemple « Claude ») : regarder sa dernière utilisation. Si
  aucune tâche n'échoue après son échéance, il ne servait plus.

## Photo du jour (Bluesky, Mastodon, Instagram)

| Message | Ce que cela veut dire | Que faire |
|---|---|---|
| Pas de photo ce matin | GitHub lance ses tâches avec 4 à 8 heures de retard ; des passages de secours suivent dans la journée. | Attendre le soir. Toujours rien le lendemain : voir la croix rouge ci-dessus. |
| Instagram, « code 190 » (*Session has expired*) | Le jeton Instagram a expiré, parce que la tâche « Jeton Instagram » a échoué. | Refaire le jeton : `reseaux/README.md`, étape 5.6. |

## Wikipédia et Commons

| Ce qui arrive | Ce que cela veut dire | Que faire |
|---|---|---|
| Une photo retirée d'un article (notification « modification annulée », ou contrôle de la semaine) | Un autre contributeur a fait un autre choix. | Ne **jamais** la remettre : ce serait une guerre d'édition. Lire la raison dans l'historique de l'article, puis prévenir une session, qui la note « Refusée » dans le suivi. Pour en parler : un message poli sur la page de discussion de l'article, comme pour l'hôtel de ville de Niort. |
| Un message sur votre page de discussion | Un contributeur vous écrit. | Le lire et répondre poliment, en signant `~~~~`. Une session peut préparer la réponse. |
| Un courriel de l'équipe VRT, ou un `{{Permission pending}}` qui dure | Commons attend la confirmation de votre autorisation pour des photos déjà sur Pexels. Sans elle, le fichier peut être supprimé au bout d'environ un mois. | Répondre au courriel de l'équipe VRT, en ajoutant les noms des nouveaux fichiers. |
| « Deletion request » (demande de suppression) sur Commons | Quelqu'un propose d'effacer un fichier, souvent pour une question de droits (œuvre ou bâtiment récent en France). | Pas de panique : la discussion dure au moins une semaine. Envoyer le lien à une session, qui prépare une réponse. |
| L'article a perdu tout son texte après votre modification | Une case de partie a été collée dans l'éditeur de la page entière. | **Historique** de l'article → **annuler** sur votre modification → publier. C'est arrivé le 28 octobre 2026 sur « Moyemont », rétabli en une modification. |
| Wikipédia refuse d'enregistrer | Un filtre a bloqué la modification, par exemple pour un lien interdit. | Ne pas insister : envoyer une capture à une session. |

## Pexels, Telepex et tableau de bord

| Ce qui arrive | Ce que cela veut dire | Que faire |
|---|---|---|
| « Refusée » dans Telepex ou dans la fiche de suivi | La modération de Pexels n'a pas mis la photo en avant. Elle est bien publiée. | Rien. |
| Telepex signale un envoi échoué | Pas de réseau, ou jeton expiré. | Telepex réessaie au relevé suivant. Si son jeton a expiré : voir « GitHub ». |
| Une rubrique du tableau de bord signale un accès manquant (Google, Bing, GoatCounter) | Un secret manque ou a expiré. Le site se construit quand même. | Une capture à une session : elle explique pas à pas comment refaire l'accès. |

## À qui s'adresser

Ouvrez une session Claude Code sur claude.ai/code, dans les dépôts du site, et donnez-lui
la capture d'écran ou le lien de l'alerte, avec ce document. Elle répond pas à pas. Elle
ne demande jamais de mot de passe ni de jeton.
