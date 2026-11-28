# Scénario de contrôle

`scenario.py` joue dans Chromium sans tête le scénario du brief et les contrôles ajoutés en cours de route : 87 contrôles.

## Préparer (une fois)

```
python3 -m venv .venv && . .venv/bin/activate
pip install playwright==1.* && python -m playwright install chromium
```

## Lancer

- Contre la démonstration du paquet (après `node construire.mjs` dans `sources/`) : `python3 controle/scenario.py`
- Contre le site servi en local, par exemple : `python3 controle/scenario.py http://127.0.0.1:8000/galeries/`

Les images et les polices viennent du réseau (Pexels, Google Fonts pour la démonstration) : il faut une connexion. Code de sortie 0 si tout passe. Le détail est écrit dans `controle/resultats.txt` et `controle/resultats.json`. `comptes-attendus.json` donne le nombre de parutions de chaque photo.

## Ce qui est contrôlé

En trois contextes : ordinateur 1 280 × 800, téléphone 390 × 844 tactile, mouvement réduit.
- **Le parcours** : le bouton ouvre la rubrique.
  - Les deux guides du premier cliché de Villandry, et le lien « Lire le guide de Torre Eiffel » (adresse, nouvel onglet).
  - Le crédit « Karl Forterre » et les liens vers la photo du site et vers Pexels.
  - Le premier regard lisible au premier écran.
  - Le retour à l'index à la même place.
  - Le second cliché, son autrice, le titre original et la date.
  - « Fermer » ramène au bouton, à la même hauteur de lecture.
- **Pendant l'ouverture** : « Fermer » visible et cliquable ; « Passer l'ouverture » ; Échap pendant le voile et pendant la séquence.
- **Lien direct** `#monde/photo-38694057`, et sa sortie « Fermer, vers les galeries ».
- **Clavier seul** : tabulation, focus visible, flèches, Échap.
- **Pour les 14 fiches** :
  - le nombre de parutions est celui du registre ;
  - le titre est « <lieu>, une photographie qui voyage » ;
  - « Une image, N regards » est présent ;
  - le texte des boutons de couleur atteint au moins 4,5:1.
- **Étiquettes du globe** : aucune coupée, sous la barre, sous l'affiche ou recouverte, sur les 14 fiches et l'index.
- **Divers** : three.js dessine ; aucune erreur de script ; aucun défilement de côté.

Sur le site, si le gabarit change de noms, adaptez les sélecteurs en tête du script : `#entree`, `#monde`, `#scene`, `.panneau`, `.notice`, `.vue[data-cle]`.
