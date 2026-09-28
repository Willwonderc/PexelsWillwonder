# Compteur des vues Pexels dans la barre des menus du Mac

Le nombre de vues Pexels s'affiche en haut de l'écran du MacBook, près de l'heure, précédé
d'un œil. Un clic montre le détail et mène au tableau de bord :

- vues sur Pexels, avec leur progression depuis le relevé précédent ;
- abonnés, téléchargements, J'aime et photos retenues, et la date du relevé ;
- visites du site et clics vers Pexels des 7 derniers jours, une fois GoatCounter relié ;
- liens vers le tableau de bord, le profil Pexels et GoatCounter, et « Actualiser ».

Les chiffres viennent du tableau de bord du site
(https://photos.karlforterre.fr/tableau-de-bord/compteur.json), relu toutes les heures ; ils
changent à chaque relevé, de Telepex ou noté à la main. Le programme ne lit rien d'autre, et
rien sur pexels.com. Si le site ne répond pas, il garde les derniers chiffres et le dit.

Il fonctionne avec SwiftBar, une application gratuite et libre qui affiche dans la barre des
menus le résultat d'un petit programme. Il faut macOS 12 ou plus récent ; les Mac M1
conviennent. Le petit écran Turing prévu au départ est remplacé par ce compteur.

## Installer, une fois (10 minutes)

1. **SwiftBar** : ouvrir https://github.com/swiftbar/SwiftBar/releases/latest, télécharger
   le fichier `SwiftBar` en `.zip` de la rubrique **Assets**, l'ouvrir, glisser SwiftBar
   dans le dossier **Applications**, puis le lancer.
2. **Dossier des programmes** : au premier lancement, SwiftBar demande où ranger ses
   programmes. Créer un dossier, par exemple `SwiftBar` dans **Documents**, et le choisir.
3. **Le compteur** : copier l'adresse ci-dessous dans la barre d'adresse de Safari, puis
   valider et autoriser l'ouverture de SwiftBar. Il télécharge le programme dans son dossier,
   et le nombre de vues apparaît dans la barre des menus.

       swiftbar://addplugin?src=https://raw.githubusercontent.com/Willwonderc/PexelsWillwonder/main/releves/barre-des-menus/vues-pexels.1h.py

4. **Au démarrage du Mac** : Réglages Système → Général → éléments ouverts à la connexion,
   bouton **+**, puis choisir SwiftBar dans Applications.

## Si le compteur n'apparaît pas

- **SwiftBar affiche ⚠️** : cliquer dessus pour lire l'erreur.
- **macOS propose d'installer les « outils de ligne de commande »** : accepter. Le compteur
  se sert du Python fourni par Apple, déjà présent avec Xcode.
- **Installation à la main** : sur GitHub, ouvrir
  [vues-pexels.1h.py](vues-pexels.1h.py), bouton **Download raw file**, et ranger le fichier
  dans le dossier de SwiftBar. Puis, dans Terminal (à adapter si le dossier est ailleurs) :

      chmod +x ~/Documents/SwiftBar/vues-pexels.1h.py

  et, dans le menu de SwiftBar, **Refresh All**.

## À savoir

- **« 1h » dans le nom du fichier** : SwiftBar relance le programme toutes les heures. Pour
  une autre fréquence, renommer le fichier, par exemple `vues-pexels.30m.py`.
- **« Pexels ? »** : le tableau de bord n'a encore jamais répondu. **« Chiffres de la dernière
  lecture »** : il ne répond pas pour l'instant, les chiffres affichés sont ceux de la
  dernière lecture réussie.
- **Nouvelle version du programme** : recommencer l'étape 3.
