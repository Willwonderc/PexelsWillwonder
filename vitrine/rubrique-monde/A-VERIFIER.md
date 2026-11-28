# À vérifier avant la mise en ligne

Marquage : [C] constaté ; [S] supposé.

## Ce qui reste supposé dans les données

1. **Le lieu de certains médias** [S]. Le registre n'a pas de champ « pays ». Le lieu vient de son texte (« média espagnol », « au Texas », « à La Rochelle »), de la langue ou du domaine. Le pays seul est donné quand la ville n'est pas établie. Le détail est dans `donnees/travail-par-parution.csv`, colonne « suppose ».
   - **Torre Eiffel est placé au Brésil sur son seul domaine `.com.br`.**
   - Idealista/news est compté en France (édition `idealista.fr` d'un groupe espagnol).
   - Les médias français sans ville sont posés au centre de la France.
   - Six parutions n'ont aucun lieu établi et sont dites « en ligne, lieu non établi » : DailyAstroAI, Plutonic Planes, iMean AI, Vesper, Off We Gooo, Nipuni Dissanayake.
2. **Le lieu de prise de vue** [C pour 9 photos ; S pour 5]. Il vient du titre de la photo ou de sa galerie « Lieux » du site. Cinq photos n'ont pas de lieu : la lune, la voie lactée, les fleurs des champs et les deux portraits. Elles partent du centre de la France, avec la mention « lieu non indiqué ».
3. **Les cinq titres courts inventés** [S] : « La lune » (13102252), « La voie lactée » (27116682), « Fleurs des champs » (35086239), « Au café » (38536476), « Un portrait » (38536479). Ils font « La lune, une photographie qui voyage ». Les neuf autres reprennent le lieu de prise. À relire par Karl, champ `titre`.
4. **Le nom de la photo 23414381** [C, écart à trancher par Karl]. Le site la nomme « église Saint-André » ; Pexels la titre « Eglise Notre-Dame de Niort ». La rubrique suit le site.
5. **Les palettes** sont calculées : les teintes viennent de chaque photo, rendues plus franches. Les photos en noir et blanc ou de nuit ont une gamme de gris : c'est voulu. Elles sont à juger à l'œil par Karl.
6. **Les notices** reprennent le texte du registre. Trois viennent du brief (USE-021, USE-022, USE-023), ainsi que les noms affichés d'Edvenn et de Nipuni Dissanayake. À relire par Karl.
7. **La licence** : le registre ne conclut pas sur le canal d'obtention des photos par les médias (« base de licence non déterminée »). La rubrique dit où les photos ont paru ; elle ne qualifie pas ces usages.

## Ce qui n'a pas été essayé

- **Safari (macOS) et un iPhone réel** : jamais essayés. Le contrôle s'est fait dans Chromium sans tête, sur ordinateur (1 280 × 800), téléphone simulé (390 × 844, tactile) et mouvement réduit.
- Un téléphone modeste : performance du globe WebGL non mesurée.
- Un lecteur d'écran (VoiceOver).
- Les liens vers les articles des médias : non suivis, seules leurs adresses sont comparées au registre.
- Le son facultatif (coupé par défaut) : non écouté.
- L'intégration réelle dans le code du site : le gabarit, `style.css` et `site.js` n'ont pas été ouverts. La page hôte de la démonstration est simulée d'après la page en ligne.
- La police Archivo du site : la couverture de l'axe de largeur n'est pas vérifiée. Newsreader est à ajouter au site.
