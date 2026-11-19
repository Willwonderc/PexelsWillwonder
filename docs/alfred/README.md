# Boîte aux lettres entre la session Claude en ligne et Alfred (Claude sur le Mac de Karl)

Karl ne doit rien avoir à copier d'une session à l'autre : tout passe par ces fichiers,
sur `main`. Le dépôt est public : rien de personnel ni de secret ici.

| Fichier | Qui écrit | Qui lit |
|---|---|---|
| `message.md` | la session en ligne | Alfred |
| `reponse.md` | Alfred | la session en ligne |
| `passation.md` | la session en ligne | Alfred (méthode, travail fait, en attente) |

## Règles communes

- On **ajoute à la fin** une entrée datée (`## AAAA-MM-JJ HH:MM — auteur`), sans jamais
  effacer les entrées précédentes.
- Chacun n'écrit que dans son fichier : pas de conflit possible.
- Une question à Karl se note `**Pour Karl :**` ; l'autre côté la lui transmet.

## Côté Alfred (sur le Mac)

À mettre en place une fois, puis cela tourne seul :

1. Cloner le dépôt : `git clone https://github.com/Willwonderc/PexelsWillwonder.git`
   (un jeton GitHub avec le droit d'écrire sur ce dépôt est nécessaire pour pousser ; il
   reste dans le trousseau du Mac, jamais dans un fichier du dépôt).
2. Programmer un passage chaque jour, vers 13 h (heure de Paris), et un autre après chaque
   action faite pour Karl :
   - `git pull` ;
   - lire les nouvelles entrées de `docs/alfred/message.md` et les appliquer ;
   - ajouter son compte rendu à la fin de `docs/alfred/reponse.md` (ce qui a été fait,
     ce que Karl a publié, les questions) ;
   - `git add docs/alfred/reponse.md && git commit -m "Alfred : compte rendu" && git push`.
3. Sans droit de pousser : lecture seule à l'adresse
   `https://raw.githubusercontent.com/Willwonderc/PexelsWillwonder/main/docs/alfred/message.md`,
   et le dire à Karl une fois, pour qu'il crée le jeton.

## Côté session en ligne

Une tâche programmée la réveille chaque jour à 13 h 45 (heure de Paris) : elle lit
`reponse.md`, vérifie ce qu'Alfred signale (publications Wikipédia de Karl, etc.), répond
dans `message.md`, et ne prévient Karl que s'il a une décision à prendre.
