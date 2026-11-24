# Audience des photos du jour : mesures et choix de langue

La langue de chaque message (français ou anglais) se choisit d'après l'audience qu'il
peut toucher (règle de Karl, 30 septembre 2026). Ce journal garde les mesures qui fondent
ce choix. La session programmée du 26 de chaque mois (skill `messages-du-mois`,
`.claude/skills/messages-du-mois/SKILL.md`) y ajoute les siennes, en tête, avant
d'écrire les messages du mois suivant.

Méthode, en lecture seule et sans compte :

- **Bluesky** : les 100 derniers messages de chaque hashtag
  (`https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=%23Hashtag&sort=latest&limit=100`) :
  messages par jour, « j'aime » en médiane, part en français (champ `langs`) ; et les
  messages de Karl du mois écoulé
  (`app.bsky.feed.getAuthorFeed?actor=karlforterre.bsky.social`).
- **Mastodon** : l'historique de chaque hashtag sur mastodon.social
  (`https://mastodon.social/api/v1/tags/HASHTAG`, usages et comptes par jour sur une
  semaine) ; et les messages de Karl
  (`/api/v1/accounts/117335880653931296/statuses`, favoris et partages).

Ne jamais aimer, suivre ni répondre par programme : on mesure, on ne touche à rien.

## 24 novembre 2026 (point intermédiaire, avant le bilan du 26)

Relevé en lecture seule des fils publics, du 1er au 23 novembre (le message du 24 est
écarté, trop récent), à la demande de Karl.

- **Bluesky : ça monte.** 21 abonnés (13 le 26 octobre, 21 déjà le 19 novembre).
  23 photos du jour, « j'aime » en médiane 12 (7,5 en octobre, 4 fin septembre), moyenne
  14,8, 341 au total, 11 partages. Les jours de défi #Photovember (médiane 12) font
  deux fois mieux que le seul jour hors défi (glycine, 20 novembre : 6). Mieux reçus :
  « Pluie » (35, 13 novembre), le cheval bai pour « Marron » (31), « Couleur(s) de
  saison » (30), « Ciel d'automne » et « Laine » (21), « Cosy » (19) ; moins bien :
  « Boisson chaude » et « Champignon » (4). Presque aucune conversation : une seule réponse
  d'un autre compte depuis l'ouverture (les autres réponses sont les liens de Karl). Le
  message écrit à la main le 22 novembre (« Merci à tous… », sans photo) : 0.
- **Mastodon : ça stagne.** 6 abonnés depuis octobre ; Karl ne suit qu'un compte.
  23 messages, favoris en médiane 3 (3 en octobre, 6 fin septembre), moyenne 4,3, 98 au
  total, 14 partages. Toujours le même partage : chats (#Caturday, médiane 13), fleurs (8),
  oiseaux (8), noir et blanc (5,5), puis architecture (3,5), et les lieux et les côtes à 0
  ou 1 (cormorans de Chausey, Ribadeo, maison en forêt, rive). Novembre a eu beaucoup de
  lieux. Le message du 3 novembre nomme « Pic du Midi d'Ossau » la photo 39212543, qui
  montre le pic de Ger.
- **Heures : en novembre, aucun message à l'heure** (octobre, depuis le 14 : presque tous).
  Retard médian 1 h 14 sur Bluesky et 2 h 27 sur Mastodon, jusqu'à 4 h 11 et 6 h 26 :
  GitHub lance les passages avancés plus tard qu'en octobre. Le 24 novembre, le passage
  Mastodon de la veille, lancé à 2 h 35, a attendu 15 h 47 du jour même et bloqué la file
  jusqu'à 8 h 31 ; corrigé le même jour dans `photo-du-jour.yml` (un passage de la veille
  s'arrête). En octobre, l'heure n'avait pas d'effet visible sur les réactions.
- **Pour décembre :** sur Bluesky, garder une photo pour chaque défi du mois ; sur
  Mastodon, plus de chats (#Caturday le samedi), de fleurs et d'oiseaux, le noir et blanc
  le lundi, moins de villes et de côtes.

## 26 octobre 2026

### Correction du bilan de septembre

Les 101 et 109 « j'aime » notés le 30 septembre n'étaient pas ceux de Karl : son fil
Bluesky (`getAuthorFeed`) mêle à ses messages ceux qu'il a repartagés, et ces deux-là
venaient d'autres comptes (@lowlow.bsky.social, 103 « j'aime », et
@sylvaingrandserre.bsky.social, 202). Ses propres photos du jour de fin septembre, en
anglais, en avaient eu 3 à 10. Le français sur Bluesky reste le bon choix (voir plus
bas), mais pour une raison plus modeste. Désormais, le bilan écarte les partages (champ
`reason` du fil) et les réponses.

### Bluesky : les messages de Karl, du 1er au 26 octobre

26 messages en français, tous à partir du calendrier, et 13 abonnés (compte ouvert le
26 septembre).

| | Messages | « J'aime » (médiane) | Écart |
|---|---:|---:|---|
| Tous | 26 | 6 | 2 à 24 |
| Jours de défi #PhotoOctober | 22 | 7 | 3 à 24 |
| Hors défi | 4 | 4,5 | 2 à 6 |
| Avec #NoirEtBlanc | 5 | 8 | 6 à 13 |
| Fin septembre, en anglais (rappel) | 5 | 4 | 3 à 10 |

Les mieux reçus : le moineau du défi « Oiseau » (24 « j'aime », 2 octobre), le banc de
Niort pour « Ocre » (18), la barque échouée pour « Oubli » (13), le café pour « Odorant »
(11), puis l'océan, le graffiti « je t'aime » et le pêcheur du Marais poitevin (10
chacun). Les moins bien : l'hôtel de ville de Cognac, hors défi (2), les cannelés (3), le
chaton du 1er octobre (3, parti à 13 h 56 UTC) et le feu d'artifice (3). Deux vraies
réponses en tout, cinq partages. Depuis le 14 octobre, les messages partent à 6 h 47 UTC
pile (passage avancé) ; avant, entre 7 h et 14 h UTC : aucune différence visible. Les
lignes d'octobre n'avaient pas de description d'image (colonne `alt` vide, le titre de la
photo en tenait lieu) ; celles de novembre en ont une.

### Bluesky : les hashtags

| Hashtag | Messages par jour | « J'aime » (médiane) | En français |
|---|---:|---:|---:|
| #UnJourUnePhoto | 86 | 8 | 93 % |
| #PhotoOctober (défi d'octobre) | 48 | 9 | 99 % |
| #Photovember (défi de novembre, tel que l'écrit la liste) | pas encore lancé | 15 | 97 % |
| #FleurisTonFil | 8,9 | 10 | 94 % |
| #NoirEtBlanc | 9,2 | 7 | 46 % |
| #Photographie | 63 | 5 | 68 % |
| #Photography | 2 892 | 2 | 3 % |
| #PhotoOfTheDay | 101 | 4 | 5 % |
| #NaturePhotography | 209 | 5,5 | 2 % |
| #LandscapePhotography | 135 | 9 | 0 % |
| #BlackAndWhitePhotography | 73 | 9 | 1 % |
| #MonochromeMonday (mesuré un lundi) | 843 | 7 | 8 % |
| #Automne | 6,6 | 2 | 60 % |
| #Autumn | 277 | 3 | 0 % |

La liste des défis de novembre a paru le 20 octobre (@elisabethlaffay.bsky.social,
reprise le 25 par @belladona.bsky.social) : trente thèmes sur l'automne, de « Plante
d'automne » à « Pomme, poire... ou scoubidou ». Celle de décembre paraîtra vers le
20 novembre.

### Mastodon : les messages de Karl, du 1er au 25 octobre

25 messages en anglais, 6 abonnés. Favoris : médiane 5, de 0 à 23 ; 31 partages en tout ;
six réponses sous cinq messages, dont trois auxquelles Karl a répondu lui-même (4 et
12 octobre).

| | Messages | Favoris (médiane) | Écart |
|---|---:|---:|---|
| #Caturday (samedi, un chat) | 4 | 13,5 | 3 à 23 |
| #MonochromeMonday (lundi, noir et blanc) | 3 | 14 | 8 à 22 |
| #FensterFreitag (vendredi, une fenêtre) | 1 | 12 | |
| Fleurs | 2 | 11 | 10 à 12 |
| Oiseaux (hors lundi) | 3 | 8 | 2 à 13 |
| Villes, monuments, phares | 9 | 1 | 0 à 5 |
| Dimanches | 4 | 0,5 | 0 à 4 |

Les mieux reçus : le chat au pot de glace (« Heure du goûter », 23), la barque aux feuilles
mortes en noir et blanc (22, et deux réponses touchées par le texte), le chat dans la rue
vu d'en bas (18), le goéland sur sa croix (14). Les villes ne prennent pas : Niort,
Poitiers, Cognac, Angoulême et Angers font 0 à 5 favoris, comme les phares de Chausey et
le portrait.

Heure : jusqu'au 13 octobre, les messages sont partis entre 15 h 47 et 20 h 32 UTC (retards
de GitHub), médiane 10 ; depuis le 14, presque toujours à 15 h 47 UTC pile, médiane 1,5.
Mais la première quinzaine avait les meilleurs sujets (chats, noir et blanc, fleurs), la
seconde la plupart des villes. Les quelque 1 100 messages #photography parus du 24 octobre
8 h au 25 octobre 8 h UTC sur mastodon.social, classés par heure de parution (comptes du
serveur seulement, dont les favoris sont complets), ne montrent pas d'heure nettement
meilleure : la médiane va de 0 à 19 favoris d'une heure à l'autre, au gré de petits
échantillons. L'heure ne change pas ; à revoir au bilan de novembre, avec des sujets plus
égaux.

### Mastodon : les hashtags (mastodon.social, moyenne sur 6 jours, du 20 au 25 octobre)

| Hashtag | Usages par jour | Comptes par jour |
|---|---:|---:|
| #photography | 1 156 | 641 |
| #nature | 457 | 248 |
| #travel | 368 | 139 |
| #france | 357 | 152 |
| #catsofmastodon | 189 | 135 |
| #photo | 184 | 111 |
| #cats | 171 | 115 |
| #autumn | 161 | 123 |
| #silentsunday (884 le dimanche) | 151 | 136 |
| #architecture | 137 | 77 |
| #caturday (635 le samedi) | 134 | 117 |
| #streetphotography | 133 | 81 |
| #blackandwhite | 119 | 90 |
| #naturephotography | 118 | 89 |
| #landscape | 95 | 68 |
| #photographie | 64 | 32 |
| #flowers | 54 | 43 |
| #trees | 50 | 41 |
| #fensterfreitag (259 le vendredi) | 47 | 43 |
| #sunset | 42 | 38 |
| #sky | 37 | 28 |
| #rain | 33 | 16 |
| #mushrooms | 26 | 16 |
| #birdsofmastodon | 22 | 20 |
| #lighthouse | 13 | 6 |
| #fog | 10 | 9 |
| #fungifriday (37 le vendredi) | 7,5 | 5,7 |
| #monochromemonday (pas de lundi dans la fenêtre ; 18 par jour en septembre) | 1,7 | 1,5 |
| #unjourunephoto | 0 | 0 |

### Leçons

- **Bluesky** : le défi du jour porte les messages (médiane 7 « j'aime », contre 4,5 hors
  défi). Les animaux, Niort « chez moi », la cuisine, la mer et le noir et blanc marchent ;
  les monuments seuls, non.
- **Mastodon** : les jours à thème et la nature font tout (chats, noir et blanc, fenêtres,
  fleurs, oiseaux : 8 à 14 favoris en médiane) ; les villes et les monuments tombent à 1.
  Les dimanches ont fait 0 à 4, mais trois sur quatre portaient une ville ou un phare : on
  ne peut pas encore accuser le jour. Ce jour-là, la communauté poste des photos sans
  texte sous #SilentSunday (884 messages), que la skill écarte.

### Choix pour novembre 2026 (et du 1er au 7 décembre)

- **Bluesky : français.** Défi #Photovember 29 jours sur 30 : le 20 (« Épice, épicé »),
  aucune photo ne s'y prête, il part hors défi avec #FleurisTonFil. #NoirEtBlanc trois
  fois, #FleurisTonFil deux fois. Du 1er au 7 décembre, hors défi : la liste de décembre
  n'a pas encore paru (la session du 26 novembre pourra réécrire ces jours).
- **Mastodon : anglais.** Un chat chaque samedi (5), du noir et blanc chaque lundi (6), une
  fenêtre ou un vitrail chaque vendredi (5) ; le 11 novembre, le monument aux morts de
  Villandry ; le 17, la Voie lactée pour les Léonides (maximum la nuit du 17 au 18) ; le
  24, une pleine lune (pleine lune à 14 h 53 UTC, d'après Star Walk et pleine-lune.org).
  Les autres jours : oiseaux, fleurs, paysages ; plus de ville hors des vendredis.
- **Instagram : français** (règle de Karl). 38 légendes ajoutées : les 45 prochaines photos
  ont la leur.
- **Heures** : inchangées (Bluesky et Instagram à 6 h 47 UTC, Mastodon à 15 h 47 UTC).

## 30 septembre 2026

### Bluesky

| Hashtag | Messages par jour | « J'aime » (médiane) | En français |
|---|---:|---:|---:|
| #UnJourUnePhoto | 65 | 14 | 91 % |
| #PhotoSeptember (défi du mois) | 59 | 16 | 93 % |
| #FleurisTonFil | 8,6 | 15 | 97 % |
| #NoirEtBlanc | 10,7 | 8 | 50 % |
| #Photographie | 165 | 3 | — |
| #Photography | 2 376 | 2 | 2 % |
| #PhotoOfTheDay | 97 | 7 | — |
| #LandscapePhotography | 137 | 10 | — |
| #NaturePhotography | 378 | 7 | — |
| #BlackAndWhitePhotography | 74 | 12 | — |
| #MonochromeMonday | 54 | 13 | — |
| #SilentSunday | 31 | 6 | — |
| #Astrophotography | 41 | 4 | — |

Karl : photos du jour automatiques en anglais, du 26 au 30 septembre, 3 à 7 « j'aime » ;
sa photo #FleurisTonFil du 26 septembre, en français, 101 « j'aime » ; son message du
30 septembre, en français, 109 (erreur, corrigée le 26 octobre : ces deux messages étaient
des partages de messages d'autres comptes). Les messages de la communauté paraissent surtout entre
6 h et 11 h, heure de Paris.

### Mastodon (mastodon.social, moyenne sur 7 jours)

| Hashtag | Usages par jour | Comptes par jour |
|---|---:|---:|
| #photography | 1 157 | 657 |
| #nature | 481 | 262 |
| #photo | 201 | 116 |
| #architecture | 168 | 78 |
| #catsofmastodon | 167 | 121 |
| #silentsunday (dimanche) | 156 | 140 |
| #caturday (samedi) | 127 | 108 |
| #blackandwhite | 120 | 94 |
| #naturephotography | 118 | 88 |
| #autumn | 104 | 79 |
| #landscape | 96 | 69 |
| #photographie | 62 | 32 |
| #flowers | 56 | 48 |
| #fensterfreitag (vendredi) | 46 | 39 |
| #birdsofmastodon | 36 | 17 |
| #monochromemonday (lundi) | 18 | 16 |
| #noiretblanc | 10 | 7 |
| #unjourunephoto | 0,3 | 0,3 |

Karl : photos du jour en anglais, du 26 au 30 septembre, 0 à 7 favoris et 0 à 4
partages.

### Choix pour octobre 2026

- **Bluesky : français** tous les jours : défis #PhotoOctober (26 jours) et
  #UnJourUnePhoto ; chat noir pour Halloween le 31.
- **Mastodon : anglais** tous les jours, file ordinaire ; un chat le samedi
  (#Caturday), du noir et blanc le lundi (#MonochromeMonday), une fenêtre le vendredi
  2 (#FensterFreitag). #SilentSunday, qui veut des photos sans texte, est laissé de côté.
- **Instagram : français** (règle de Karl).

### Heure de publication sur Mastodon

1 200 messages #photography de mastodon.social, du 29 septembre (18 h 51 UTC) au
30 septembre (20 h 24 UTC), classés par heure de parution : les messages de l'après-midi
(16 h et 17 h UTC), vieux de trois ou quatre heures seulement, avaient déjà autant de
réactions en médiane (5 à 6) que ceux de 6 h UTC au bout de quatorze heures (5). À
6 h 47 UTC, l'Amérique dort. D'où, à partir d'octobre, Mastodon à 15 h 47 UTC (17 h 47 à
Paris, 11 h 47 à New York) ; Bluesky et Instagram restent à 6 h 47 UTC, au plus fort de
la communauté #UnJourUnePhoto. Une seule journée de mesure : à confirmer par le bilan de
fin octobre.
