# Photo du jour sur Bluesky, Mastodon et Instagram — mode d'emploi

Chaque matin, la tâche GitHub **Photo du jour** publie une photo sur Bluesky, sur
Mastodon (ou Pixelfed) et sur Instagram, avec un texte écrit à l'avance dans le style de
Karl (`reseaux/style-karl.md`) et le lien vers sa page du site, d'où elle se télécharge
sur Pexels. Une session Claude programmée écrit chaque mois les textes du mois suivant,
les vérifie et les propose en pull request ; le seul geste de Karl est de la fusionner,
d'un clic (voir « Des messages écrits à l'avance », plus bas).

- **Bluesky**, en français le plus souvent, à la manière de la communauté
  #UnJourUnePhoto ; le lien part en réponse sous la photo. Exemple :

      #UnJourUnePhoto #PhotoOctober #Photography

      1. Orange

      Pour ouvrir le mois, un chaton roux se faufile dans les herbes sèches, à pas de velours. Orange de la tête aux pattes, et l'œil vert aux aguets.

        ↳ en réponse : Libre de droits, à télécharger gratuitement sur Pexels : https://photos.karlforterre.fr/photo/10405558/

- **Mastodon**, en anglais le plus souvent, avec les hashtags que suivent les
  photographes du Fediverse. Exemple :

      A pale pink rose against the dark, and nothing else. Up close, a rose is all folds and patience: each petal keeps a little light for the next one.

      Royalty-free, free to download on Pexels: https://photos.karlforterre.fr/en/photo/31514838/

      #Photography #Flowers #Rose #MacroPhotography #Nature

- **Instagram**, toujours en français ; les légendes n'y ont pas de liens cliquables, et
  le lien est remplacé par un renvoi vers celui de la biographie (voir la partie 5,
  « Instagram »).

- **Ordre** : des photos les plus vues sur Pexels aux moins vues (fiche de suivi
  `releves/suivi-pexels.csv`), sauf les jours où le calendrier en choisit une autre (défi
  du mois, jour à thème). Avec 919 photos, il y a de quoi publier pendant deux ans et demi.
- **Pas de répétition** : le journal `reseaux/photo-du-jour.json`, enregistré sur
  `main` après chaque passage, note pour chaque réseau les photos publiées, leur date et
  le lien de la publication. Un réseau ne reçoit qu'une photo par jour, même si la tâche
  est relancée. Une photo ne revient sur un même réseau qu'après 180 jours au moins
  (réglage `rediffusion_jours`) : quand le calendrier la choisit, ou, une fois toutes les
  photos publiées, par ordre d'ancienneté. Le journal garde alors la trace de
  la publication précédente (`precedentes`).
- **Heure** : 8 h 47 à Paris en été, 7 h 47 en hiver (6 h 47 UTC).
- **Sans accès** : un réseau dont les secrets ne sont pas renseignés est simplement
  laissé de côté. On peut donc commencer par un seul réseau.

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
   Chaque page du site renvoie vers le profil (rubrique `[reseaux]` de `vitrine/site.ini`) :
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

## 5. Instagram

La photo du jour part aussi sur le compte @karl_forterre, par l'API officielle de Meta
« avec connexion Instagram », qui ne demande pas de Page Facebook. Elle suit le même
ordre que les autres réseaux, à partir de la photo la plus vue, et le journal
`reseaux/photo-du-jour.json` note chaque publication dans sa rubrique `instagram`.

- **Légende**, toujours en français (règle de Karl du 28 septembre 2026) : un texte
  écrit à l'avance dans son style (`reseaux/legendes-instagram.csv`, d'après le guide
  `reseaux/style-karl.md`) ou, à défaut, le titre français de la photo ; puis « Libre de
  droits, à télécharger gratuitement sur Pexels : lien dans la bio. », puis cinq
  hashtags : Instagram n'en accepte pas davantage depuis décembre 2025. Les légendes
  n'ont pas de liens cliquables : c'est le lien de la biographie qui mène au site.
- **Image** : Instagram la télécharge lui-même chez Pexels, en JPEG de 1 440 pixels de
  large. Il n'accepte que les proportions comprises entre 4:5 (en hauteur) et 1,91:1
  (en largeur) : les photos en hauteur sont recadrées au centre en 4:5, les neuf
  panoramas en 1,91:1 ; les autres restent entières.
- **Jeton** : l'accès se fait par un jeton valable 60 jours. Chaque lundi, la tâche
  **Jeton Instagram** l'échange contre un neuf et le range elle-même dans les secrets du
  dépôt : il n'y a rien à refaire tant qu'elle passe au vert.
- **Limite** : 100 publications par 24 heures au plus ; la tâche en fait une par jour.
- **Sans Page Facebook ni examen de Meta** : l'application reste « Non publiée » (en
  développement), réservée à votre propre compte, ce qui dispense de l'examen des
  applications (App Review). Ses photos sont pourtant visibles de tous : constaté à la
  première publication, le 28 septembre 2026.

Ces étapes suivent la documentation de Meta, vérifiée le 28 septembre 2026, et les
libellés relevés le même jour dans le tableau de bord en français. Meta change parfois
le nom de ses menus, et son site peut s'afficher en anglais : les libellés anglais sont
donnés en italique ; si l'un d'eux diffère un peu, cherchez le plus proche.
Comptez une demi-heure en tout, sur un ordinateur. Comme pour les autres réseaux, un
jeton se colle uniquement dans un secret du dépôt, jamais dans une conversation, un
fichier ou un message.

### 5.1 Le lien de la biographie

Sur Instagram : **Modifier le profil** → **Liens** → **Ajouter un lien externe** :
adresse `https://photos.karlforterre.fr`, titre « Photos libres de droits ».

### 5.2 Le compte de développeur Meta

1. Ouvrez https://developers.facebook.com, cliquez sur **Commencer** (*Get Started*) et
   connectez-vous avec votre compte Facebook personnel : il sert seulement à gérer
   l'application, rien n'est publié sur Facebook.
2. Acceptez les conditions de Meta et confirmez votre adresse électronique ou votre
   numéro de téléphone si Meta le demande.

### 5.3 L'application

1. **Mes applications** (*My Apps*) → **Créer une app** (*Create app*).
2. Nom de l'application : par exemple `Photo du jour KF`. Meta refuse les noms qui
   contiennent Instagram, Insta, IG, Facebook ou Meta. Adresse de contact : la vôtre.
3. Cas d'utilisation : **Gérer les messages et les contenus sur Instagram** (*Manage
   messaging & content on Instagram*). S'il n'est pas proposé : **Autre** (*Other*),
   puis le type **Entreprise** (*Business*), puis, dans le tableau de bord, le produit
   **Instagram** → **Configurer** (*Set up*).
4. Portefeuille business : **Je ne veux pas encore associer de portefeuille business**
   (*I don't want to connect a business portfolio yet*).
5. Terminez la création. Meta peut redemander le mot de passe Facebook : tapez-le sur son
   site, jamais ailleurs. Le tableau de bord s'ouvre, avec la mention « Non publiée » à
   côté de **Publier** dans le menu de gauche : c'est normal, laissez-la ainsi. Le
   produit *Facebook Login for Business*, ajouté d'office au menu, ne sert pas ici.

### 5.4 Le droit de publier

1. Dans le tableau de bord de l'application : **Personnaliser le cas d'utilisation Gérer
   les messages et les contenus sur Instagram** (ou menu de gauche **Cas
   d'utilisation**, *Use cases*, puis **Personnaliser**, *Customize*) → **Autorisations
   et fonctionnalités** (*Permissions and features*).
2. Vérifiez que `instagram_business_basic` et `instagram_business_content_publish`
   sont ajoutées : elles portent alors la mention « Prête pour le test » et un bouton
   **Actions** ; sinon, cliquez sur **Ajouter** (*Add*). La seconde donne le droit de
   publier ; les autres autorisations ne servent pas. Faites-le **avant** de créer le
   jeton : un jeton garde les autorisations qu'il avait à sa création.

### 5.5 @karl_forterre, testeur de l'application

Une application en développement n'agit que sur les comptes qui y ont un rôle.

1. Tableau de bord, menu de gauche : **Rôles dans l'application** (*App roles*) →
   **Rôles** → **Ajouter des personnes** (*Add People*) → **Testeur Instagram**
   (*Instagram Tester*) → saisissez `karl_forterre` → **Ajouter**. Le rôle apparaît
   « En attente ».
2. Sur un ordinateur, connecté à @karl_forterre (l'application Instagram du téléphone
   n'affiche pas toujours l'invitation), ouvrez
   https://www.instagram.com/accounts/manage_access/ (**Paramètres** → **Applications
   et sites Web**), onglet **Invitations à tester** (*Tester Invites*), et acceptez
   l'invitation. L'application y porte son nom suivi de « -IG » (« Photo du jour
   KF-IG ») ; une fois l'invitation acceptée, elle affiche « Autorisée par vous le … »
   et un bouton **Supprimer**, sur lequel il ne faut pas cliquer.

### 5.6 Le jeton Instagram, rangé dans les secrets du dépôt

1. Tableau de bord : **Cas d'utilisation** → **Personnaliser** à côté du cas Instagram →
   **Configuration de l'API avec la connexion Instagram** (*API setup with Instagram
   login*) ; ou, dans le menu de gauche, **Instagram** → *API setup with Instagram
   business login*.
2. Rubrique **Générer des tokens d'accès** (*Generate access tokens*) : **Ajouter un
   compte** (*Add account*), puis connectez-vous à @karl_forterre dans la fenêtre qui
   s'ouvre (autorisez les fenêtres surgissantes si le navigateur les bloque) et acceptez
   les autorisations demandées.
3. Le compte apparaît dans la liste : cliquez sur **Générer un token** (*Generate
   token*). Meta affiche un long jeton, valable 60 jours, **une seule fois** : laissez la
   fenêtre ouverte.
4. Dans un autre onglet, sur GitHub, dépôt `willwonderc/PexelsWillwonder` : **Settings**
   → **Secrets and variables** → **Actions** → **New repository secret**. Nom :
   `INSTAGRAM_JETON` ; valeur : copiez le jeton depuis la fenêtre de Meta et collez-le
   directement ici ; **Add secret**. Fermez ensuite la fenêtre de Meta.

### 5.7 Le jeton GitHub qui renouvelle le jeton Instagram

La tâche **Jeton Instagram** doit pouvoir réécrire le secret `INSTAGRAM_JETON` chaque
lundi. Le jeton que GitHub donne à ses tâches n'a pas ce droit : il lui faut un jeton
GitHub personnel, limité aux secrets de ce seul dépôt. Il ne permet pas de lire les
secrets, seulement de les remplacer.

1. Sur GitHub, votre photo de profil (en haut à droite) → **Settings** → tout en bas
   à gauche **Developer settings** → **Personal access tokens** → **Fine-grained
   tokens** → **Generate new token**.
2. **Token name** : `Jeton Instagram`. **Expiration** : **No expiration** (sinon,
   GitHub prévient par courriel avant l'échéance et il faut le refaire). **Resource
   owner** : Willwonderc.
3. **Repository access** : **Only select repositories** → `Willwonderc/PexelsWillwonder`.
4. **Permissions** → **Repository permissions** → **Secrets** : **Read and write**
   (GitHub ajoute de lui-même **Metadata** en lecture). Rien d'autre.
5. **Generate token** : GitHub l'affiche une seule fois. Dans un autre onglet :
   **Settings** du dépôt → **Secrets and variables** → **Actions** → **New repository
   secret** ; nom : `JETON_GITHUB` ; valeur : le jeton, collé directement ;
   **Add secret**.

### 5.8 Premier essai

1. Onglet **Actions** → **Photo du jour** → **Run workflow**. Si Bluesky et Mastodon
   ont déjà publié ce jour-là, seul Instagram publie. Après une à deux minutes, la ligne
   passe au vert : la photo la plus vue est sur Instagram, et le journal note le lien
   de la publication.
2. Vérifiez qu'elle est visible de tous : demandez à quelqu'un de regarder votre profil
   depuis son compte, ou ouvrez https://www.instagram.com/karl_forterre/ dans une
   fenêtre de navigation privée, sans être connecté. Au premier essai, le 28 septembre
   2026, elle l'était, l'application restant « Non publiée ». Si ce n'était plus le
   cas, passez l'application « en ligne » (*Live*) : menu de gauche **Publier**
   (*Publish*). Meta demande alors une adresse de politique de confidentialité
   (`https://photos.karlforterre.fr/confidentialite/`), des instructions de suppression
   des données (la même adresse), une icône (le logo KF’ de
   `vitrine/statique/logo-kf.webp`) et une catégorie. L'accès « standard », qui suffit
   pour votre propre compte, ne demande pas d'examen.
3. Le renouvellement se fait seul le lundi suivant. Pour l'essayer sans attendre, au
   moins 24 heures après la création du jeton : **Actions** → **Jeton Instagram** →
   **Run workflow**. Au vert, le jeton est renouvelé et rangé dans `INSTAGRAM_JETON`
   (la date du secret change dans **Settings** → **Secrets and variables** →
   **Actions**).

### 5.9 En cas de croix rouge

Ouvrez la tâche, puis l'étape en rouge : le message indique le réseau et l'erreur.

| Message | Cause et remède |
|---|---|
| `erreur 400` et `"code": 190` (*Invalid OAuth access token*, *Session has expired*) | Jeton expiré ou révoqué : refaites l'étape 5.6 et remplacez le secret `INSTAGRAM_JETON` (**Update secret**). |
| `"code": 10` ou `permission` | L'autorisation de publier manque : refaites l'étape 5.4, puis 5.6 (nouveau jeton). |
| `image non préparée par Instagram` (*Media download has failed*, 2207052, 9004) | Instagram n'a pas pu télécharger l'image chez Pexels : la même photo sera retentée le lendemain. Si cela se répète, signalez-le dans une session Claude. |
| `secret JETON_GITHUB absent` ou `ne donne pas accès aux secrets` | Refaites l'étape 5.7 : dépôt PexelsWillwonder, droit **Secrets** en **Read and write**. |
| `jeton non renouvelé` | Jeton créé depuis moins de 24 heures (réessayez le lendemain) ou déjà expiré (étape 5.6). |

Instagram peut aussi, rarement, répondre par une erreur alors que la photo est publiée :
la tâche le vérifie auprès d'Instagram avant de conclure, et ne la republie pas.

### 5.10 Couper l'accès

Sur https://www.instagram.com/accounts/manage_access/, retirez l'application (bouton
**Supprimer**) ; ou supprimez-la dans le tableau de bord de Meta. Supprimez ensuite les secrets
`INSTAGRAM_JETON` et `JETON_GITHUB` du dépôt, et le jeton `Jeton Instagram` dans
**Developer settings** de GitHub. Sans eux, les deux tâches laissent Instagram de côté.

## Des messages écrits à l'avance

Karl l'a demandé le 30 septembre 2026 : des messages humains, pas des titres de banque
d'images ; aucune partie à la main ; et, pour chaque message, le français ou l'anglais
selon l'audience qu'il peut toucher.

### La langue de chaque message

Elle se choisit d'après les mesures de `reseaux/audience.md`, reprises chaque mois :

- **Bluesky : le français.** Le public de Karl y est francophone : ses messages en
  français ont reçu plus de 100 « j'aime », ses photos du jour en anglais 3 à 7. La
  communauté #UnJourUnePhoto (65 messages par jour, 91 % en français, 14 « j'aime » en
  médiane) fait mieux que les hashtags anglais, pourtant plus fréquentés.
- **Mastodon : l'anglais.** Sur mastodon.social, #photography réunit environ 1 160
  messages par jour, #photographie 62, #UnJourUnePhoto presque aucun.
- **Instagram : le français**, règle de Karl (`reseaux/style-karl.md`).

La session du mois peut en décider autrement pour un message donné : une photo qui a sa
place dans une communauté anglaise très active part en anglais, même sur Bluesky.

### Bluesky

- **Les défis du mois** : la communauté publie vers le 25 la liste des thèmes du mois
  suivant, un par jour (octobre 2026 : Orange, Oiseau, Oh !…, publiée par
  @elisabethlaffay.bsky.social). Les jours où une photo de Karl répond vraiment au thème,
  elle part avec `#UnJourUnePhoto #PhotoOctober #Photography`, puis « 1. Orange » et le
  texte ; `#FleurisTonFil` s'y ajoute pour des fleurs, `#NoirEtBlanc` pour le noir et
  blanc.
- **Les autres jours** : `#UnJourUnePhoto #Photography` (et la communauté qui convient),
  puis le texte.
- **Le lien** part en réponse sous la photo ; le profil renvoie au site.

### Mastodon

Le Fediverse n'a pas d'algorithme : on y trouve les photos par les hashtags qu'on suit.
Chaque message finit donc par quatre ou cinq hashtags choisis parmi les plus suivis
(`#Photography`, `#Nature`, `#Architecture`, `#BirdsOfMastodon`…), et suit les jours à
thème : un chat le samedi (`#Caturday`, `#CatsOfMastodon`), du noir et blanc le lundi
(`#MonochromeMonday`), une fenêtre le vendredi (`#FensterFreitag`). Le lien vers la
page de la photo s'insère avant les hashtags.

### Le calendrier

`reseaux/calendrier.csv` : une ligne par jour et par réseau (`bluesky` ou `mastodon`),
colonnes `date` (AAAA-MM-JJ), `reseau`, `photo` (numéro Pexels), `langue` (`fr` ou `en`),
`theme` (pour mémoire : défi du jour, jour à thème) et `texte` (le message complet,
hashtags compris, sans le lien ; `\n` pour aller à la ligne ; 300 caractères au plus sur
Bluesky, 500 sur Mastodon avec le lien). Les hashtags deviennent cliquables tout seuls.
Une photo prévue par le calendrier ne part pas avant son jour dans la file ordinaire.
Une ligne inutilisable (photo absente, parue il y a moins de 180 jours, langue inconnue)
laisse partir la file ordinaire ce jour-là, avec son texte automatique (hashtags et
titre).

Instagram garde ses légendes, une par photo, dans `reseaux/legendes-instagram.csv`.

### Qui les écrit

Une session Claude programmée, le 26 de chaque mois à 9 h 13 (consigne M de
`consignes/prochaines-sessions.md`) :

1. mesure l'audience (API publiques de Bluesky et de mastodon.social, en lecture) et
   complète `reseaux/audience.md` ;
2. cherche la liste des défis du mois suivant ;
3. choisit les photos : celles des défis, puis la file ordinaire (les plus vues pas
   encore publiées sur ce réseau), avec les jours à thème de Mastodon ;
4. écrit chaque message dans la langue retenue, dans le style de Karl, sans rien
   inventer, et complète les légendes Instagram des six semaines suivantes ;
5. vérifie le tout (`--calendrier`, `--essai`) et ouvre une pull request.

Karl la fusionne d'un clic (*Merge pull request*, puis *Confirm*) : une routine qui
fusionnerait elle-même, sans relecture humaine, est refusée par les garde-fous de
Claude Code. Tant qu'elle attend, rien ne casse : les photos du jour partent avec le
texte automatique. Pour corriger un message, il suffit de modifier sa ligne sur GitHub
(crayon, *Edit*, puis *Commit changes*) ; pour le retirer, de la supprimer.

### Ce que le programme ne fait jamais

Ni « j'aime », ni abonnements, ni réponses automatiques : ce serait se faire passer pour
Karl dans une conversation, et les réseaux le sanctionnent. Répondre aux commentaires
reste possible pour Karl, quand il le veut, sans que rien n'en dépende.

Vérifier le calendrier à venir, puis voir ce qui partirait un jour donné :

    python3 reseaux/photo_du_jour.py --calendrier
    python3 reseaux/photo_du_jour.py --essai --jour 2026-10-01

## Réglages

- **Langue des publications** : chaque ligne du calendrier a la sienne. Les jours sans
  ligne, `vitrine/site.ini`, rubrique `[photo_du_jour]` : ligne `langue` pour Mastodon,
  `en` (anglais, par défaut), `fr` (français) ou `zh` (chinois) ; ligne `langue_bluesky`
  pour Bluesky, `fr`, à la manière de la communauté #UnJourUnePhoto (une autre langue
  reprend l'ancienne formule : titre, lien et mots-clés en hashtags) ; ligne
  `langue_instagram` pour Instagram, `fr`, à garder (règle de Karl).
- **Rediffusions** : ligne `rediffusion_jours` de la même rubrique, 180 par défaut.
- **Hashtags de Bluesky, les jours sans ligne** : `HASHTAGS_BLUESKY` et
  `COMMUNAUTES_BLUESKY` dans `reseaux/photo_du_jour.py` (hashtag de communauté et mots qui
  le déclenchent).
- **Légendes Instagram** : `reseaux/legendes-instagram.csv`, une ligne par photo (numéro
  Pexels, légende, et, si l'on veut, les hashtags de la photo, cinq au plus, qui
  remplacent alors ses hashtags automatiques), à corriger au besoin directement sur
  GitHub. L'essai (`--essai`) indique pour combien des prochaines photos une légende est
  prête, et `--a-venir 40` liste les 40 prochaines photos d'Instagram avec celles qui
  attendent encore la leur ; la session du 26 (consigne M) en écrit chaque mois pour les
  six semaines suivantes.
- **Hashtag des publications automatiques** (Mastodon et Instagram) : `HASHTAG_FIXE` dans
  `reseaux/photo_du_jour.py` (#Photography, #Photographie ou #摄影 selon la langue), suivi
  des quatre premiers mots-clés de la photo. Instagram n'en prend jamais plus de cinq en
  tout.
- **Phrase de la légende Instagram** : `TEXTES_INSTAGRAM` dans
  `reseaux/photo_du_jour.py`, une par langue.
- **Heure** : ligne `cron` de `.github/workflows/photo-du-jour.yml`, en heure UTC
  (minute, puis heure). Évitez la minute 0, souvent retardée par GitHub.
- **Faire une pause** : onglet **Actions** → **Photo du jour** → bouton **…** →
  **Disable workflow** ; **Enable workflow** pour reprendre là où la tâche s'était
  arrêtée. Laissez la tâche **Jeton Instagram** active pendant la pause : elle garde le
  jeton Instagram valable.
- **Remettre une photo en file** : dans `reseaux/photo-du-jour.json`, supprimez sa ligne
  (numéro, date et lien) dans la rubrique du réseau.
- **Couper l'accès** : supprimez le mot de passe d'application dans Bluesky ou
  l'application dans Mastodon, puis les secrets de ce réseau sur GitHub ; sans eux, la
  tâche laisse ce réseau de côté. Pour Instagram, voir la partie 5.10.

## Essai en session

    python3 reseaux/photo_du_jour.py --essai

affiche les publications du jour, telles qu'elles partiraient, sans rien publier ni
enregistrer, et sans secrets, avec l'adresse de l'image qu'Instagram téléchargerait
(recadrage compris). `--langue fr` essaie une autre langue, `--jour 2026-10-01` un autre
jour (calendrier compris), et `--calendrier` vérifie le calendrier à venir. `--a-venir 40`
liste les 40 prochaines photos d'Instagram, dans l'ordre de parution, et dit si leur
légende est prête ; `--a-venir 40 --reseau mastodon` (ou `bluesky`) liste les photos que
le calendrier ne prévoit pas encore sur ce réseau, dans l'ordre de la file ordinaire
(`--jour` pour partir d'un autre jour). Ne jamais lancer `--renouveler-jeton` en session : c'est l'affaire de la tâche **Jeton Instagram**.

## RedNote (小红书), à la main

RedNote n'offre pas d'accès automatique : une session Claude prépare des carrousels et
les envoie par courriel à forterrekarl@gmail.com, avec un lien vers une page qui
regroupe les images et des boutons pour copier les textes. Karl les publie depuis
l'application, deux ou trois fois par semaine, entre 13 h et 15 h à Paris (le soir en
Chine), sur le compte « Soviet Croissant » (rednote ID 26225410141,
https://www.xiaohongshu.com/user/profile/678629da000000000801aa88), au ton léger
et sympathique. Chaque carrousel rejoint aussi l'onglet « Publications » de Telepex (voir
« Publications à la main, dans Telepex », plus bas). Règles de chaque carrousel :

- **Récit** : à la première personne et sur un ton léger, comme le compte, il met en
  avant que Karl est un photographe français et relie chaque image à la France (lieu,
  histoire, culture, façon de vivre). Il s'appuie sur des faits vrais et sur les
  souvenirs de Karl ci-dessous, sans jamais inventer d'anecdote personnelle.
- **Petit cours de français** (法语小课堂) : deux ou trois mots français liés aux photos.
- **Deux versions** : la version chinoise, à publier, et à côté la même en français
  (images et texte), pour que Karl comprenne ce qu'il publie ; celle-ci ne se publie pas.
- **Images** : 9 au format 3:4 (1080 × 1440 pixels). Une couverture titrée, sous-titrée
  « 一个法国摄影师的… » (vu par un photographe français) et signée KF’ Karl Forterre ;
  7 photos avec leur titre (en portrait, plein cadre ; en paysage, entières sur fond
  flou) ; une image de fin : photos gratuites sur Pexels, chercher « Karl Forterre ».
  Une discrète signature « © Karl Forterre » est permise : ces fichiers ne vont pas sur
  Pexels. Pour un récit de voyage, chaque photo peut porter son étape (« 第1站 · … »).
  S'il manque une photo, une image du petit cours de français complète les neuf.
- **Texte** : titre de 20 caractères au plus ; récit, petit cours de français, liste des
  photos, invitation à les télécharger sur Pexels, une ligne en anglais et une dizaine
  de hashtags chinois, dont #法国摄影师. En tout, hashtags compris, 1 000 caractères au
  plus (un émoji peut compter pour deux) : viser 950. Pas de lien : RedNote
  ne les rend pas cliquables et pénalise les publications qui renvoient ailleurs.
- **Choix des photos** : par série, galerie ou lieu, en commençant par les plus vues ;
  titres et mots-clés chinois dans `vitrine/donnees/textes-zh.csv`.
- **Sur le site photo** : chaque carrousel rejoint aussi la série de son sujet, dans
  `vitrine/series.ini`. Le récit y va en français, en anglais et en chinois
  (`recit_fr`, `recit_en`, `recit_zh`), sans ce que le texte de la série dit déjà. Le
  petit cours de français ne figure que sur les pages anglaises et chinoises
  (`francais_en`, `francais_zh`). Ses photos y entrent si elles n'y sont pas. Un sujet
  sans série reçoit la sienne (voir `vitrine/README.md`, rubrique « Séries »).

Souvenirs et repères de Karl pour les récits :

- Il habite Niort, dans l'ouest de la France, entre La Rochelle et Poitiers.
- Villandry : il y est allé pour admirer des jardins héritiers d'une tradition de
  plusieurs siècles de jardin à la française.
- Éclipse totale du 12 août 2026, en Galice : il a eu le sentiment d'un paysage écrasé
  par l'événement singulier qui se produisait.
- Road trip du 10 au 19 août 2026, en voiture depuis Niort, avec Maëlle, sa fiancée,
  que les récits peuvent nommer. Voyage sans programme rigide, à pied dans les villes :
  - **Gijón** (Asturies), plusieurs jours : intérêt pour son passé industriel et ouvrier.
    Une journée à l'Universidad Laboral, avec une pause pâtisseries et Cola Cao, puis le
    Jardín Botánico Atlántico voisin, bien plus vaste qu'il n'y paraît depuis l'entrée.
    Une autre journée : l'aquarium et le musée du chemin de fer. Le Cola Cao est devenu
    un souvenir rapporté du voyage.
  - **Galice**, quelques jours : l'éclipse du 12 août, la plage des Cathédrales à
    Ribadeo.
  - **Pays basque** : logés près de Bilbao, en métro jusqu'au centre. La vieille ville
    (Casco Viejo), les quais de la ria, le Teatro Arriaga, le funiculaire pour voir la
    ville d'en haut. Le pastel de arroz, le chocolate con churros et du turrón rapporté
    en souvenir. Le 16 août, le musée Guggenheim et le Puppy de Jeff Koons, couvert de
    fleurs.
  - **Béarn**, deux nuits près de Pau : le 18 août, l'église de L'Hôpital-Saint-Blaise,
    sur le chemin de Saint-Jacques, inscrite au patrimoine mondial de l'UNESCO.
  - **Bordeaux**, le 19 août, sur la route du retour : la Cité du Vin, son exposition
    permanente sur l'histoire et les cultures du vin, et la dégustation qui la termine.
  - Photos sur Pexels : Gijón (la Laboral), la Galice (dont le coucher de soleil du soir
    de l'éclipse), Irun, le Béarn et Bordeaux (les fontaines de la place des
    Quinconces) ; presque rien de Bilbao (deux vues industrielles).
  - Ne citer ni les dépenses, ni les hébergements, ni d'autres proches.
- Lieux confirmés par Karl le 28 septembre 2026 : le TGV vu d'en haut (photo 19047681)
  est en gare de Poitiers ; le phare du Loup (34894953) et le phare de la Grande-Île
  (34894970) sont aux îles Chausey. L'homme à lunettes du portrait 38536479 n'est pas à
  nommer.

Premiers carrousels, envoyés le 27 septembre 2026 : ciels et nuits étoilées, jardins de
Villandry, Normandie et Bretagne. Sur le site, ils ont rejoint les séries « Nuits
étoilées » (petit cours de français et deux photos), « Éclipse totale de Soleil en
Galice » (récit), « Les jardins de Villandry » (récit et petit cours de français) et la
nouvelle série « Phares et marées, de Granville à Saint-Malo ».

Deuxième envoi, le même jour : le road trip d'août et Bordeaux, devenus sur le site les
séries « Dix jours de route, de Niort au nord de l'Espagne » et « Bordeaux et les
fontaines des Quinconces ». Le 28 septembre, à la demande de Karl, le coucher de soleil
du soir de l'éclipse (photo 39236039) a pris dans le road trip la place de l'hôtel de
ville d'Irun (image 4), dans le carrousel comme dans les vidéos, et rejoint la série.

## Vidéos diaporama des carrousels

Chaque carrousel peut aussi devenir une vidéo, à publier à sa place ou en plus. Les cinq
premiers l'ont été le 27 septembre 2026 en diaporamas 3:4, puis refaits le 28 septembre
par le studio de `reseaux/videos/` (`studio.py`, mode d'emploi dans son README) : vidéos
rythmées, calées sur la musique, contrôlées automatiquement. Cahier des charges et
suite du travail : `docs/plan-videos.md`. Règles actuelles :

- **Formats** : 9:16 (1080 × 1920 pixels : Reels, TikTok, YouTube Shorts, RedNote) et
  3:4 (1080 × 1440 : RedNote, grille du profil Instagram, Facebook), sans bandes noires,
  rien d'important sous les boutons des applications ; de 40 à 75 secondes selon la
  longueur du récit.
- **Déroulé** : une accroche de 3 secondes (une photo déjà en mouvement et la promesse
  du titre, écrite mot à mot), puis chaque photo avec son récit en sous-titres de deux
  lignes au plus ; le petit cours de français (versions chinoise et anglaise
  seulement) et une fin courte : logo KF’, appel à chercher « Karl Forterre » sur Pexels.
- **Rythme** : les coupes tombent sur les temps forts de la musique (ou sur ses notes
  les plus fortes pour le piano), les mots des sous-titres sur les notes ; une barre de
  progression et un compteur (« 03 / 08 ») avancent au même rythme. Couverture à part,
  en 3:4 et en 9:16, et sous-titres en fichier SRT pour YouTube et Facebook.
- **Textes** : les sous-titres reprennent les textes validés, mot pour mot en chinois ;
  l'anglais est traduit du français. Chinois et anglais présentent Karl en photographe
  français. La version française, destinée à un public français (son Facebook
  personnel), ne met pas en avant ce côté français, que Karl trouve peu sérieux : ni
  « photographe français », ni « en France, on… ». Couvertures et fins française et
  anglaise sont refaites dans le style des carrousels, sans ce sous-titre.
- **Musique**, libre de droits, au volume conseillé pour les réseaux (−14 LUFS, crêtes à
  −1 dBTP), qui finit sur une note forte puis en fondu :
  - en chinois et en anglais, de la musique classique dans des enregistrements dédiés
    au domaine public : Chopin par Musopen (https://archive.org/details/musopen-chopin),
    Bach par Kimiko Ishizaka (https://archive.org/details/bach-well-tempered-clavier-book-1) ;
  - en français, de la pop instrumentale, choisie parmi des artistes qui publient
    eux-mêmes tout leur catalogue en CC0 (Loyalty Freak Music) ou parmi les morceaux
    très diffusés de Kevin MacLeod (CC BY), sauf quand le sujet appelle autre chose : les
    jardins à la française de Villandry ont « Le Printemps » de Vivaldi (John Harrison et
    le Wichita State University Chamber Players, CC BY-SA), la Normandie et la Bretagne
    un air celtique (« Thatched Villagers », Kevin MacLeod, CC BY).

  Privilégier les morceaux les plus employés dans la publicité et les médias. Une licence
  CC BY ou CC BY-SA impose un crédit, écrit en petit sur l'image de fin ; avec CC BY-SA,
  la vidéo passe sous la même licence. Se méfier des fichiers d'Internet Archive marqués
  « domaine public » par n'importe qui : beaucoup sont des disques du commerce. Chaque
  dossier contient un fichier « Musiques et licences ». Sur RedNote, Karl peut aussi
  remplacer la musique par un morceau de la bibliothèque de l'application (配乐).
- **Version française** : pas de « photographe français » ni de « en France, on… », et
  « Maëlle » plutôt que « ma fiancée ». Ligne politique de tous les textes : `CLAUDE.md`,
  « Ligne éditoriale des textes ».
- **Envoi** : un fichier par vidéo (30 Mo au plus par fichier), la langue dans le nom.
  Karl les range sur son Mac dans `Documents Locaux/Caroussels`, en trois dossiers :
  « Chinois (RedNote) », « Français » et « Anglais ». Telepex (session U, faite le
  28 septembre) les repère dans Téléchargements, même quand le téléchargement a simplifié
  leur nom (« 4 - Road trip daoût chinois.mp4 »), les range sous le nom du dépôt et les
  montre dans son onglet « Carrousels ». Envoyer avec elles les trois fichiers « Musiques
  et licences » : Telepex en tire son bouton « Copier le crédit musical ».

## Facebook personnel, à la main

Karl publie lui-même les carrousels sur son profil Facebook personnel : Meta ne permet
aucune publication automatique sur un profil, seulement sur une Page. Les sessions
préparent la version française (images, vidéo et texte, dans `reseaux/publications/` pour
Telepex), sans mettre en avant le côté
français (voir ci-dessus) : les images françaises des carrousels RedNote, faites pour
que Karl comprenne ce qu'il publie, portent encore « d'un photographe français » sur la
couverture et sont donc à refaire. Rythme et forme des textes restent à fixer avec lui.

## Publications à la main, dans Telepex

Chaque publication à faire à la main, RedNote ou Facebook, a son dossier
`reseaux/publications/<id>/` : `publication.json`, en UTF-8, et ses images. La tâche de
nuit, comme chaque modification de `main`, en tire
https://photos.karlforterre.fr/tableau-de-bord/publications.json et publie les images à
côté : l'onglet « Publications » de Telepex, l'application Mac de Karl, les y lit (textes à
copier, images dans l'ordre, vidéo du même sujet, validation). Ce fichier n'apparaît ni dans
le plan du site, ni dans `llms.txt`, ni dans IndexNow, et ne contient que ce qui est fait
pour être publié. GitHub Pages le garde en cache jusqu'à dix minutes (`max-age=600`), et
un paramètre ajouté à l'adresse n'y change rien : Telepex garde donc chaque validation sur
le Mac en attendant la liste suivante.

Champs de chaque publication dans `publications.json` : `id`, `reseau`, `langue`, `titre`,
`texte`, `traduction`, `hashtags`, `images` (adresse publique et nom, dans l'ordre),
`video`, `conseil`, `prevue` et `validee` (date de validation, ou `null`), puis, quand
`publication.json` les a, `etapes`, `forme`, `sujet` et `carrousel`, repris tels quels.

Exemple de `publication.json`, textes abrégés :

    {
      "format": 1,
      "id": "2026-09-28-rednote-01-ciel",
      "reseau": "rednote",
      "langue": "zh",
      "forme": "carrousel",
      "sujet": "Ciels et nuits étoilées",
      "carrousel": "1 - Ciels et nuits étoilées",
      "date_prevue": "2026-09-28",
      "heure_conseillee": "entre 13 h et 15 h, heure de Paris (le soir en Chine)",
      "etapes": ["Envoyer les 9 images sur l'iPhone (AirDrop) : elles arrivent dans Photos.", "…"],
      "images": ["images/01.jpg", "…", "images/09.jpg"],
      "textes": [
        {"nom": "Titre", "texte": "法国人拍的星空｜…"},
        {"nom": "Texte et hashtags", "texte": "我是 Karl，…"}
      ],
      "traduction": {"langue": "fr", "textes": [
        {"nom": "Titre", "texte": "Le ciel vu par un Français | …"},
        {"nom": "Texte", "texte": "Je suis Karl, …"}
      ]}
    }

- `id` : date prévue, réseau et sujet, en minuscules sans accents ; c'est aussi le nom du
  dossier. Une publication refaite garde son `id`.
- `reseau` : `rednote` ou `facebook`, les deux que montre Telepex ; `langue` : `zh`, `fr`
  ou `en` ; `forme` : `carrousel`, `video` ou `texte`.
- `sujet` : en français, pour s'y retrouver.
- `carrousel` (facultatif) : le nom des vidéos du même sujet, sans la langue (champ
  `fichier` de `videos/donnees.py`) ; Telepex reçoit le nom du fichier de la langue, par
  exemple « 4 - Road trip d'août (chinois).mp4 ».
- `date_prevue` et `heure_conseillee` (facultatifs) : le jour et le moment conseillés.
- `etapes` (facultatif) : le pas à pas, une phrase par étape. Telepex y accroche ses
  boutons d'après ces mots, à garder :
  - « AirDrop », ou « envoyer » avec « image » ou « vidéo » : bouton d'envoi ;
  - « copier » ou « coller » : textes à copier ;
  - « sélectionner », « toucher + » ou « choisir les » : choix des images dans l'ordre ;
  - « publier » : publication ;
  - toute autre phrase reste une simple consigne.
- `images` : dans l'ordre de publication, la première en couverture ; aucune pour une
  vidéo seule ou un texte.
- `textes` : le titre, pour RedNote (nom commençant par « Titre »), puis le texte à
  publier, hashtags compris, que Telepex propose de copier tels quels. La `traduction`,
  facultative, sert à comprendre : Telepex l'affiche à côté.

`python3 reseaux/publications.py` contrôle toutes les publications (champs, images, limites
de RedNote : titre de 20 caractères, texte de 1 000, un émoji comptant pour deux) : à lancer
avant de pousser. `build.py` laisse de côté une publication illisible ou incomplète, et le
signale dans son journal.

Quand Karl valide une publication dans Telepex, Telepex ajoute une ligne à
`publications-validees.csv` (colonnes `date,id,reseau,langue,remarque`, date au format
AAAA-MM-JJ, remarque « Telepex »), en un commit « Publication validée : <id> » ; seul
Telepex tient ce journal, qu'il ne réécrit jamais. La publication n'est plus proposée :
elle reste 30 jours dans la liste, marquée validée, sans ses images. Celles-ci ne servent
plus : une session peut alors les retirer du dépôt, en gardant `publication.json` pour
mémoire.

Le journal se lit dans l'ordre du fichier, et la dernière ligne d'un `id` l'emporte :

- remarque « Telepex » : publication faite, à la date indiquée ;
- remarque « Telepex annulation » (commit « Publication annulée : <id> ») : Karl a annulé
  la validation ; la publication redevient à faire, avec ses images ;
- vidéo publiée hors de la liste (onglet « Carrousels » de Telepex) : remarque « Telepex »,
  avec un `id` de la forme `AAAA-MM-JJ-<reseau>-video-<n>-<titre>-<langue>`, par exemple
  `2026-09-30-facebook-video-4-road-trip-d-aout-fr` ; réseau `rednote`, `facebook`,
  `instagram`, `youtube` ou `tiktok`. Ces lignes n'ont pas de dossier dans
  `publications/` : `build.py` les ignore, mais elles disent aux sessions ce qui est paru.

Les liens des publications restent sur le Mac : le journal n'en contient jamais.

Premières publications : les cinq carrousels RedNote prévus du 28 septembre au
7 octobre 2026.

## Contenu du dossier

    photo_du_jour.py     choisit la photo, publie sur Bluesky, Mastodon et Instagram, tient
                         le journal ; avec --renouveler-jeton, renouvelle le jeton Instagram
    photo-du-jour.json   journal des publications, tenu par la tâche GitHub
    calendrier.csv       photo, langue et texte de chaque jour sur Bluesky et Mastodon,
                         écrits chaque mois par la session programmée (consigne M)
    legendes-instagram.csv
                         légendes Instagram, une par photo, en français
    audience.md          mesures d'audience qui décident de la langue de chaque message
    style-karl.md        le style de Karl, pour tout texte publié en son nom
    publications/        publications à faire à la main, une par dossier, lues par Telepex
    publications.py      contrôle ces publications
    publications-validees.csv
                         publications validées dans Telepex, journal tenu par Telepex
    videos/              programme des vidéos diaporama des carrousels (mode d'emploi :
                         videos/README.md ; plan d'amélioration : docs/plan-videos.md)

Tâches GitHub : `.github/workflows/photo-du-jour.yml` (chaque matin) et
`.github/workflows/jeton-instagram.yml` (chaque lundi).
