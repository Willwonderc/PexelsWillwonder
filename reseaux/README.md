# Photo du jour sur Bluesky et Mastodon — mode d'emploi

Chaque matin, la tâche GitHub **Photo du jour** publie une photo sur Bluesky et sur
Mastodon (ou Pixelfed) : l'image, son titre, le hashtag #Photography suivi de quatre
mots-clés en hashtags, et le lien
vers sa page du site, d'où elle se télécharge sur Pexels. Exemple :

    Beautiful twilight sky with a crescent moon and serene gradient of colors

    Royalty-free, free to download on Pexels: https://photos.karlforterre.fr/en/photo/13102252/

    #Photography #Sky #CrescentMoon #Gradient #Twilight

- **Ordre** : des photos les plus vues sur Pexels aux moins vues (fiche de suivi
  `releves/suivi-pexels.csv`). Avec 919 photos, il y a de quoi publier pendant deux ans et demi.
- **Jamais deux fois la même** : le journal `reseaux/photo-du-jour.json`, enregistré sur
  `main` après chaque passage, note pour chaque réseau les photos publiées, leur date et
  le lien de la publication. Un réseau ne reçoit qu'une photo par jour, même si la tâche
  est relancée.
- **Heure** : 8 h 47 à Paris en été, 7 h 47 en hiver (6 h 47 UTC).
- **Sans accès** : un réseau dont les secrets ne sont pas renseignés est simplement
  laissé de côté. On peut donc commencer par un seul des deux.

Ne collez jamais un mot de passe ou un jeton dans une conversation avec Claude, dans un
fichier du dépôt ou dans un message : uniquement dans les secrets du dépôt, comme
indiqué ci-dessous. Le dépôt est public.

## 1. Bluesky

### Créer le compte (10 minutes)

1. Ouvrez https://bsky.app et cliquez sur **Create account** (Créer un compte).
2. Laissez l'hébergeur proposé (**Bluesky Social**), puis saisissez votre adresse
   électronique, un mot de passe solide et votre date de naissance.
3. Choisissez un pseudonyme, par exemple `karlforterre` : l'identifiant du compte sera
   `karlforterre.bsky.social`. Confirmez l'adresse électronique avec le code reçu.
4. Complétez le profil (**Profil** → **Modifier le profil**) : photo (le logo KF’ de
   `vitrine/statique/logo-kf.webp` ou un portrait), nom « Karl Forterre », et une
   courte présentation avec le lien https://photos.karlforterre.fr.

Facultatif : prendre `karlforterre.fr` comme identifiant, plus parlant. Dans Bluesky,
**Paramètres** → **Compte** → **Identifiant** → **J'ai mon propre domaine** : Bluesky
indique un enregistrement TXT à ajouter dans la zone DNS de karlforterre.fr chez OVH.
Si vous changez d'identifiant, mettez à jour le secret `BLUESKY_IDENTIFIANT`.

### Créer le mot de passe d'application

Un mot de passe d'application permet à la tâche GitHub de publier sans connaître votre
vrai mot de passe ; il se révoque à tout moment sans toucher au compte.

1. Dans Bluesky : **Paramètres** → **Confidentialité et sécurité** →
   **Mots de passe d'application** → **Ajouter un mot de passe d'application**.
2. Nommez-le `GitHub photo du jour`. Ne cochez pas l'accès aux messages privés.
3. Bluesky affiche le mot de passe (quatre groupes de quatre caractères) **une seule
   fois** : gardez la page ouverte pour l'étape 3 ci-dessous.

## 2. Mastodon (ou Pixelfed)

Mastodon est un réseau fait de nombreux serveurs (« instances ») qui communiquent entre
eux. Le plus simple : **mastodon.social**, le plus grand, aux inscriptions ouvertes. Il
existe aussi des instances tournées vers la photo ; lisez leurs règles avant de vous
inscrire, car certaines demandent de signaler les publications automatiques.

### Créer le compte (10 minutes)

1. Ouvrez https://mastodon.social, cliquez sur **Créer un compte**, acceptez les règles,
   puis saisissez un nom d'utilisateur (par exemple `karlforterre`), votre adresse
   électronique et un mot de passe. Confirmez l'adresse par le lien reçu.
2. Complétez le profil (**Préférences** → **Profil public**) : nom, présentation, photo,
   et dans les **champs supplémentaires** le lien https://photos.karlforterre.fr.
   Chaque page du site renvoie vers le profil (réglage `mastodon` de `vitrine/site.ini`) :
   Mastodon affiche alors une coche verte à côté de ce lien. Si elle n'apparaît pas,
   réenregistrez le profil une fois le site reconstruit pour relancer la vérification.

### Créer le jeton d'accès

1. Dans Mastodon : **Préférences** → **Développement** → **Nouvelle application**.
2. Nom de l'application : `GitHub photo du jour`. Site web : https://photos.karlforterre.fr
   (facultatif).
3. **Autorisations** : décochez `read`, `write` et `follow`, puis cochez seulement
   `write:media` et `write:statuses` (publier des images et des messages, rien d'autre).
4. Cliquez sur **Envoyer**, puis sur le nom de l'application : la page affiche
   **Votre jeton d'accès**. Gardez la page ouverte pour l'étape 3.

**Avec Pixelfed** (réseau de photographes, compatible avec Mastodon) : créez le compte
sur une instance Pixelfed, par exemple https://pixelfed.social, puis cherchez dans ses
paramètres la rubrique **Applications** ou **Développement** pour créer un jeton d'accès
personnel avec le droit d'écriture. Le secret `MASTODON_INSTANCE` reçoit alors l'adresse
de l'instance Pixelfed. Un seul des deux, Mastodon ou Pixelfed, est publié à la fois.

## 3. Ranger les accès dans les secrets du dépôt

Sur GitHub, dépôt `willwonderc/PexelsWillwonder` : **Settings** → **Secrets and
variables** → **Actions** → **New repository secret**. Créez ces quatre secrets, un
par un (nom exact, en majuscules, puis la valeur, puis **Add secret**) :

| Nom | Valeur |
|---|---|
| `BLUESKY_IDENTIFIANT` | l'identifiant Bluesky, sans @ : `karlforterre.bsky.social` |
| `BLUESKY_MOT_DE_PASSE_APPLI` | le mot de passe d'application de l'étape 1 |
| `MASTODON_INSTANCE` | l'adresse du serveur : `mastodon.social` (ou celle de l'instance Pixelfed) |
| `MASTODON_JETON` | le jeton d'accès de l'étape 2 |

Une fois enregistré, un secret ne se relit plus, même sur GitHub : il ne peut qu'être
remplacé (**Update**) ou supprimé. Vous pouvez ensuite fermer les pages de Bluesky et
de Mastodon.

## 4. Premier essai

1. Onglet **Actions** du dépôt → **Photo du jour** → **Run workflow** → **Run workflow**.
2. Une minute plus tard, la ligne passe au vert : la photo la plus vue est publiée sur
   les deux réseaux, et le journal `reseaux/photo-du-jour.json` note les deux liens.
3. En cas de croix rouge, ouvrez la tâche, puis l'étape **Publier la photo du jour** :
   le message indique le réseau et l'erreur (le plus souvent un secret mal nommé ou un
   jeton sans l'autorisation `write:media`). L'autre réseau, s'il a réussi, est tout de
   même enregistré dans le journal. GitHub vous prévient aussi par courriel.

Ensuite, la tâche tourne seule chaque matin. Relancée le même jour, elle ne publie rien
de plus.

## Réglages

- **Langue des publications** : `vitrine/site.ini`, rubrique `[photo_du_jour]`, ligne
  `langue` : `en` (anglais, par défaut), `fr` (français) ou `zh` (chinois). Titre,
  hashtags et lien suivent cette langue.
- **Hashtag de chaque publication** : `HASHTAG_FIXE` dans `reseaux/photo_du_jour.py`
  (#Photography, #Photographie ou #摄影 selon la langue), suivi des quatre premiers
  mots-clés de la photo.
- **Heure** : ligne `cron` de `.github/workflows/photo-du-jour.yml`, en heure UTC
  (minute, puis heure). Évitez la minute 0, souvent retardée par GitHub.
- **Faire une pause** : onglet **Actions** → **Photo du jour** → bouton **…** →
  **Disable workflow** ; **Enable workflow** pour reprendre là où la tâche s'était
  arrêtée.
- **Remettre une photo en file** : dans `reseaux/photo-du-jour.json`, supprimez sa ligne
  (numéro, date et lien) dans la rubrique du réseau.
- **Couper l'accès** : supprimez le mot de passe d'application dans Bluesky ou
  l'application dans Mastodon, puis les secrets de ce réseau sur GitHub ; sans eux, la
  tâche laisse ce réseau de côté.

## Essai en session

    python3 reseaux/photo_du_jour.py --essai

affiche les publications du jour, telles qu'elles partiraient, sans rien publier ni
enregistrer, et sans secrets. `--langue fr` essaie une autre langue.

## Contenu du dossier

    photo_du_jour.py     choisit la photo, publie sur Bluesky et Mastodon, tient le journal
    photo-du-jour.json   journal des publications, tenu par la tâche GitHub
