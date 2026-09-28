"""Textes, photos et musiques des vidéos diaporama des carrousels RedNote.

Chaque carrousel : ses photos (numéro dans le carrousel : numéro Pexels), sa musique
(chinois et anglais) et sa musique française, puis pour chaque langue la couverture,
les plans et le petit cours de français. Un plan : (numéro de la photo, texte). En
chinois, le texte est une liste de lignes ; en français et en anglais, une phrase
coupée automatiquement ; None : la photo passe sans texte.

Chinois et français reprennent mot pour mot les textes validés de la page des
carrousels (seules des coupures) ; l'anglais est traduit du français. Ligne
éditoriale : CLAUDE.md, « Ligne éditoriale des textes ». Couverture et fin chinoises :
images 1 et 9 du carrousel, à déposer dans travail/carrousels/ (voir README.md).
"""
from urllib.parse import quote

C = "carrousels/"
M = "musiques/"


def archive(ident, nom):
    """Adresse de téléchargement d'un fichier d'Internet Archive."""
    return f"https://archive.org/download/{ident}/{quote(nom)}"


CARROUSELS = [
    {
        "cle": "01-ciel",
        "photos": {1: 27116682, 2: 39595391, 3: 13102252, 4: 27531658, 5: 24200555, 6: 38570570,
                   7: 38995522, 8: 13142737},
        "fichier": "1 - Ciels et nuits étoilées",
        "musique": M + "chopin-nocturne-op9-2.mp3",  # chinois et anglais
        "musique_fr": M + "lfm-soft-as-a-dry-pillow.mp3",  # français
        "zh": {
            "couverture": C + "01-ciel-01.jpg", "fin": C + "01-ciel-09.jpg",
            "plans": [
                (2, ["我是 Karl，一个法国摄影师", "住在法国西部的尼奥尔"]),
                (3, ["在法国，只要离开城市的灯光，", "乡村的夜空就会亮起满天星星"]),
                (4, ["这组照片拍在法国乡村", "和西班牙北部的加利西亚"]),
                (5, ["上一次在法国看到日全食，", "还是 1999 年"]),
                (6, ["这一次，我去了加利西亚追日食"]),
                (7, ["日全食来临的那一刻，", "天色骤暗，整片风景", "仿佛被这个罕见的时刻压住了"]),
                (8, ["那种感觉，我至今难忘"]),
            ],
            "lecon": ("法语小课堂", [("la Voie lactée", "银河，直译是「牛奶之路」"),
                                  ("le croissant de lune", "新月：没错，就是可颂面包的那个 croissant")]),
        },
        "fr": {
            "couverture": ("Nuits étoilées", "La Voie lactée\net le croissant\nde lune",
                           "Étoiles · lune · éclipse totale", "8 photos · gratuites sur Pexels"),
            "plans": [
                (2, "Il suffit de quitter les lumières de la ville pour que le ciel de campagne se couvre d'étoiles."),
                (3, "Ces photos ont été prises dans la campagne française et en Galice, au nord de l'Espagne."),
                (4, "La Voie lactée, le croissant de lune, et l'éclipse totale du 12 août 2026."),
                (5, "La dernière éclipse totale visible en France remonte à 1999."),
                (6, "Cette fois, je suis allé la chercher en Galice."),
                (7, "Au moment de la totalité, la lumière est tombée d'un coup et tout le paysage m'a semblé écrasé par cet événement singulier."),
                (8, "Une sensation que je n'oublie pas."),
            ],
        },
        "en": {
            "couverture": ("A French photographer's night sky", "The Milky Way and\nthe crescent moon",
                           "Stars · moon · total eclipse", "8 photos · free on Pexels"),
            "plans": [
                (2, "I'm Karl, a French photographer. I live in Niort, in western France."),
                (3, "In France, you only have to leave the city lights behind for the country sky to fill with stars."),
                (4, "These photos were taken in the French countryside and in Galicia, in northern Spain."),
                (5, "The last total eclipse visible in France was in 1999."),
                (6, "This time, I went to Galicia to see one."),
                (7, "At the moment of totality, the light dropped all at once, and the whole landscape seemed crushed by this singular event."),
                (8, "A feeling I have not forgotten."),
            ],
            "lecon": ("French lesson", [("la Voie lactée", "the Milky Way · lait means milk"),
                                     ("le croissant de lune", "the crescent moon · yes, like the pastry")]),
        },
    },
    {
        "cle": "02-villandry",
        "photos": {1: 38694057, 2: 38694051, 3: 38694047, 4: 38694060, 5: 38694052, 6: 38694059,
                   7: 38694055, 8: 38694043},
        "fichier": "2 - Jardins de Villandry",
        "musique": M + "bach-prelude-1-ishizaka.mp3",  # chinois et anglais
        "musique_fr": M + "vivaldi-printemps-harrison.mp3",  # français
        "credit_fr": "Musique : Vivaldi, « Le Printemps », John Harrison et le Wichita State University Chamber Players (CC BY-SA 3.0). Vidéo sous licence CC BY-SA 3.0.",
        "zh": {
            "couverture": C + "02-villandry-01.jpg", "fin": C + "02-villandry-09.jpg",
            "plans": [
                (2, ["我是 Karl，一个法国摄影师", "住在法国西部的尼奥尔"]),
                (3, ["在法国，说起「法式园林」", "我们会想到对称、几何", "还有修剪得一丝不苟的黄杨"]),
                (4, ["我去维朗德里，", "就是为了亲眼欣赏这些花园：", "它们延续了几个世纪的法式园林传统"]),
                (5, ["维朗德里城堡建于 1536 年，", "是卢瓦尔河谷最后建成的", "文艺复兴大城堡之一"]),
                (6, ["这里最特别的是菜园：", "卷心菜、韭葱和生菜", "也被种成几何图案"]),
                (7, ["从高处看像一幅刺绣"]),
                (8, ["在法国，很多家庭", "至今仍有自己的小菜园"]),
            ],
            "lecon": ("法语小课堂", [("le potager", "菜园"), ("le jardin", "花园")]),
        },
        "fr": {
            "couverture": ("Val de Loire", "L'art du jardin\nà la française",
                           "Parterres · potager · Renaissance", "8 photos · gratuites sur Pexels"),
            "plans": [
                (2, "Quand on parle de « jardin à la française », on pense symétrie, géométrie et buis taillés au cordeau."),
                (3, "Je suis allé à Villandry pour admirer ces jardins, héritiers d'une tradition de plusieurs siècles de jardin à la française."),
                (4, "Le château, achevé en 1536, est l'un des derniers grands châteaux Renaissance du Val de Loire."),
                (5, None),
                (6, "Le plus étonnant est le potager : choux, poireaux et salades y sont plantés en motifs géométriques,"),
                (7, "et vus d'en haut ils ressemblent à une broderie."),
                (8, None),
            ],
        },
        "en": {
            "couverture": ("A French photographer's Loire Valley", "The art of the\nFrench formal garden",
                           "Parterres · kitchen garden · Renaissance", "8 photos · free on Pexels"),
            "plans": [
                (2, "I'm Karl, a French photographer. I live in Niort, in western France."),
                (3, "In France, when we speak of a “jardin à la française”, a French formal garden, we think of symmetry, geometry and box hedges clipped to perfection."),
                (4, "I went to Villandry to admire these gardens, heirs to a tradition of French formal gardens that goes back several centuries."),
                (5, "The château, completed in 1536, is one of the last great Renaissance châteaux of the Loire Valley."),
                (6, "The most surprising part is the kitchen garden: cabbages, leeks and lettuces are planted in geometric patterns,"),
                (7, "and seen from above they look like embroidery."),
                (8, "In France, many families still keep a small kitchen garden."),
            ],
            "lecon": ("French lesson", [("le potager", "the kitchen garden · from potage, soup"),
                                     ("le jardin", "the garden")]),
        },
    },
    {
        "cle": "03-normandie",
        "photos": {1: 34894953, 2: 34849705, 3: 34894970, 4: 34894969, 5: 34908867, 6: 34939469,
                   7: 34939467, 8: 13243887},
        "fichier": "3 - Normandie et Bretagne",
        "musique": M + "chopin-prelude-op28-15.mp3",  # chinois et anglais
        "musique_fr": M + "macleod-thatched-villagers.mp3",  # français
        "credit_fr": "Musique : « Thatched Villagers », Kevin MacLeod (incompetech.com), licence CC BY 4.0.",
        "zh": {
            "couverture": C + "03-normandie-01.jpg", "fin": C + "03-normandie-09.jpg",
            "plans": [
                (2, ["我是 Karl，一个法国摄影师", "住在法国西部的尼奥尔"]),
                (3, ["夏天，很多法国人会去", "诺曼底和布列塔尼的海边"]),
                (4, ["这里的海和南法", "蓝色的地中海完全不同："]),
                (5, ["潮汐很大，雾说来就来，", "海岸上一座座灯塔守着航道"]),
                (6, ["这组照片从格朗维尔出发，", "到只能坐船登岛的肖塞群岛，", "再到圣米歇尔山和圣马洛"]),
                (7, ["圣米歇尔山所在的海湾，", "潮差是欧洲最大的之一，"]),
                (8, ["涨潮时山会变成一座岛"]),
            ],
            "lecon": ("法语小课堂", [("le phare", "灯塔"), ("la marée", "潮汐")]),
        },
        "fr": {
            "couverture": ("Normandie et Bretagne", "Brume, phares, Mont-Saint-Michel",
                           "Granville · Chausey · Saint-Malo", "8 photos · gratuites sur Pexels"),
            "plans": [
                (2, "Sur les côtes de Normandie et de Bretagne, rien à voir avec la Méditerranée bleue du Sud :"),
                (3, "les marées y sont immenses, la brume arrive sans prévenir, et les phares veillent sur les passes."),
                (4, "Ces photos partent de Granville, passent par les îles Chausey, accessibles seulement en bateau,"),
                (5, "puis vont jusqu'au Mont-Saint-Michel et à Saint-Malo."),
                (6, "La baie du Mont connaît l'un des plus grands marnages d'Europe :"),
                (7, "à marée haute, le Mont redevient une île."),
                (8, None),
            ],
        },
        "en": {
            "couverture": ("A French photographer's coast", "Mist, lighthouses, Mont-Saint-Michel",
                           "Granville · Chausey · Saint-Malo", "8 photos · free on Pexels"),
            "plans": [
                (2, "I'm Karl, a French photographer. I live in Niort, in western France."),
                (3, "In summer, many French people head for the coasts of Normandy and Brittany."),
                (4, "Nothing like the blue Mediterranean of the south:"),
                (5, "the tides are huge, the mist rolls in without warning, and lighthouses watch over the channels."),
                (6, "These photos start in Granville, stop at the Chausey Islands, reachable only by boat, and go on to Mont-Saint-Michel and Saint-Malo."),
                (7, "The bay of Mont-Saint-Michel has one of the largest tidal ranges in Europe:"),
                (8, "at high tide, the Mont becomes an island again."),
            ],
            "lecon": ("French lesson", [("le phare", "the lighthouse · from Pharos, in ancient Alexandria"),
                                     ("la marée", "the tide")]),
        },
    },
    {
        "cle": "04-roadtrip",
        "photos": {1: 39564913, 2: 39670623, 3: 39241472, 4: 39423921, 5: 39423922, 6: 39212543,
                   7: 39208847, 8: 39386271, 9: 39236039},
        "fond_lecon": 8,  # la photo 9 est arrivée après les cartes
        "fichier": "4 - Road trip d'août",
        "musique": M + "chopin-grande-valse-op18.mp3",  # chinois et anglais
        "musique_fr": M + "lfm-roller-fever.mp3",  # français
        "zh": {
            "couverture": C + "04-roadtrip-01.jpg", "fin": C + "04-roadtrip-09.jpg",
            "plans": [
                (1, ["我是 Karl，一个法国摄影师", "今年8月10日，我和未婚妻 Maëlle", "从尼奥尔开车出发，", "用十天走了一个大环线"]),
                (2, ["第一站是阿斯图里亚斯的希洪。", "我们在城里慢慢走，", "去了宏伟的劳动大学", "（Universidad Laboral）"]),
                (3, ["接着在加利西亚待了几天：", "8月12日的日全食，"]),
                (9, ["当晚山顶上的金色日落，", "还有里瓦德奥的“大教堂海滩”"]),
                (5, ["然后是巴斯克地区：", "坐地铁进毕尔巴鄂逛古城，", "吃 churros 蘸热巧克力，", "看古根海姆美术馆门口的大狗 Puppy"]),
                (6, ["回到法国，", "我们在贝阿恩停了两晚"]),
                (7, ["参观了圣地亚哥朝圣之路上的", "L'Hôpital-Saint-Blaise 教堂，", "它是联合国教科文组织世界遗产"]),
                (8, ["最后一站是波尔多的葡萄酒城"]),
            ],
            "lecon": ("法语小课堂", [("les vacances", ["假期。", "法国人把暑假叫作 les grandes vacances，“大假期”"]),
                                  ("un aoûtien", "八月去度假的人（août 就是八月）")]),
        },
        "fr": {
            "couverture": ("Road trip, août 2026", "Vers le nord de\nl'Espagne, retour\npar la France",
                           "Asturies · Galice · Pays basque · Béarn · Bordeaux", "8 photos · gratuites sur Pexels"),
            "plans": [
                (1, "Le 10 août, Maëlle et moi sommes partis de Niort en voiture, pour une grande boucle de dix jours."),
                (2, "Première étape : Gijón, dans les Asturies. Nous avons marché dans la ville, visité l'immense Universidad Laboral."),
                (3, "Puis quelques jours en Galice : l'éclipse totale du 12 août,"),
                (9, "le coucher de soleil doré du soir même, sur les hauteurs, et la plage des Cathédrales à Ribadeo."),
                (5, "Ensuite le Pays basque : le métro jusqu'à Bilbao, des churros trempés dans le chocolat chaud, et Puppy, le grand chien fleuri du Guggenheim."),
                (6, "De retour en France, deux nuits en Béarn"),
                (7, "et la visite de l'église de L'Hôpital-Saint-Blaise, sur le chemin de Saint-Jacques-de-Compostelle, inscrite au patrimoine mondial de l'UNESCO."),
                (8, "Dernière étape : la Cité du Vin, à Bordeaux."),
            ],
        },
        "en": {
            "couverture": ("A French photographer's August", "North to Spain,\nback through France",
                           "Asturias · Galicia · Basque Country · Béarn · Bordeaux", "8 photos · free on Pexels"),
            "plans": [
                (1, "I'm Karl, a French photographer. On 10 August, my fiancée Maëlle and I drove out of Niort for a ten-day loop."),
                (2, "First stop: Gijón, in Asturias. We walked around the city and visited the vast Universidad Laboral."),
                (3, "Then a few days in Galicia: the total eclipse of 12 August,"),
                (9, "a golden sunset that same evening, up on the heights, and the Cathedrals beach at Ribadeo."),
                (5, "Next, the Basque Country: the metro into Bilbao, churros dipped in hot chocolate, and Puppy, the giant flower dog at the Guggenheim."),
                (6, "Back in France, two nights in the Béarn"),
                (7, "and a visit to the church of L'Hôpital-Saint-Blaise, on the Way of St James, a UNESCO World Heritage site."),
                (8, "Last stop: the Cité du Vin, in Bordeaux."),
            ],
            "lecon": ("French lesson", [("les vacances", "the holidays · summer is “les grandes vacances”"),
                                     ("un aoûtien", "someone who goes on holiday in August (août)")]),
        },
    },
    {
        "cle": "05-bordeaux",
        "photos": {1: 39376205, 2: 39386271, 3: 39386274, 4: 39386273, 5: 39386272, 6: 39376206,
                   7: 10369144},
        "fichier": "5 - Bordeaux",
        "musique": M + "chopin-valse-op64-3.mp3",  # chinois et anglais
        "musique_fr": M + "lfm-chillin-with-a-drink.mp3",  # français
        "zh": {
            "couverture": C + "05-bordeaux-01.jpg", "fin": C + "05-bordeaux-09.jpg",
            "plans": [
                (2, ["我是 Karl，一个法国摄影师", "八月公路旅行的回程，", "我们特意绕道波尔多"]),
                (3, ["我和未婚妻 Maëlle", "参观了葡萄酒城（La Cité du Vin）"]),
                (4, ["梅花广场上的两座喷泉，", "分别歌颂“共和国的胜利”", "和“协和的胜利”"]),
                (5, ["下面的喷泉里，", "青铜骏马在水花中奔腾", "1943年德占时期，铜像被拆下准备熔毁，", "幸免于难，1983年才重回原位"]),
                (6, ["高柱顶上，", "自由女神挣断了锁链"]),
                (7, ["波尔多还有一种小甜点：", "可露丽（cannelé），外壳焦糖色、脆脆的，", "里面软软的，带着朗姆酒和香草的香气"]),
            ],
            "lecon": ("法语小课堂", [("le cannelé", ["可露丽。cannelé 的意思是“有凹槽的”，", "名字来自它带凹槽的模具"]),
                                  ("la dégustation", ["品鉴。品尝葡萄酒就叫 une dégustation de vin"]),
                                  ("Santé !", ["干杯！法国人碰杯时要看着对方的眼睛，", "据说不然会倒霉七年"])]),
        },
        "fr": {
            "couverture": ("Bordeaux", "Dernière étape\ndu road trip",
                           "Cité du Vin · place des Quinconces · cannelés", "7 photos · gratuites sur Pexels"),
            "plans": [
                (2, "Au retour de notre road trip d'août, nous sommes passés exprès par Bordeaux."),
                (3, "Avec Maëlle, nous avons visité la Cité du Vin."),
                (4, "Place des Quinconces, les fontaines célèbrent le Triomphe de la République et celui de la Concorde."),
                (5, "En bas, les chevaux de bronze galopent dans les éclaboussures. Déposés en 1943 pour être fondus au profit de l'occupant, ils ont été épargnés et n'ont retrouvé leur place qu'en 1983."),
                (6, "Au sommet de la colonne, la Liberté brise ses chaînes."),
                (7, "Bordeaux a aussi son petit gâteau : le cannelé, à la croûte caramélisée et croustillante, moelleux à l'intérieur, parfumé au rhum et à la vanille."),
            ],
        },
        "en": {
            "couverture": ("A French photographer's Bordeaux", "The last stop\nof the road trip",
                           "Cité du Vin · Place des Quinconces · cannelés", "7 photos · free on Pexels"),
            "plans": [
                (2, "I'm Karl, a French photographer. On the way back from our August road trip, we made a point of stopping in Bordeaux."),
                (3, "With my fiancée Maëlle, we visited the Cité du Vin, devoted to the history and cultures of wine."),
                (4, "On the Place des Quinconces, the fountains celebrate the Triumph of the Republic and the Triumph of Concord."),
                (5, "Below, bronze horses gallop through the spray. Taken down in 1943 to be melted for the occupying forces, they were spared and only returned in 1983."),
                (6, "At the top of the column, Liberty breaks her chains."),
                (7, "Bordeaux also has its own little cake: the cannelé, with a crisp caramelised crust, soft inside, flavoured with rum and vanilla."),
            ],
            "lecon": ("French lesson", [("le cannelé", "“fluted”, after its mould"),
                                     ("la dégustation", "tasting · une dégustation de vin"),
                                     ("Santé !", "cheers! Look each other in the eye, or it's seven years of bad luck")]),
        },
    },
]

FIN = {
    "en": ("French photographer · landscapes", "Free photos, even for commercial use",
           "Search on Pexels", "Save this post to find these images again"),
    "fr": ("Photographe · paysages", "Photos gratuites, même à usage commercial",
           "Cherchez sur Pexels", "Enregistrez pour retrouver ces images"),
}

DOSSIERS = {"zh": "Chinois (RedNote)", "fr": "Français", "en": "Anglais"}

# Musiques : adresse de téléchargement et crédit (repris dans « Musiques et licences »).
# Avant d'en ajouter une, lire reseaux/README.md, « Vidéos diaporama des carrousels ».
LFM = ("Loyalty Freak Music, album « %s » (%s) : dédié au domaine public (CC0), utilisable "
       "même commercialement, sans mention obligatoire. %s")
MUSOPEN = "Enregistrement Musopen, dédié au domaine public (CC0). https://archive.org/details/musopen-chopin"
MUSIQUES = {
    "vivaldi-printemps-harrison.mp3": {
        "url": archive("The_Four_Seasons_Vivaldi-10361",
                       "John_Harrison_with_the_Wichita_State_University_Chamber_Players_-_01_-_Spring_Mvt_1_Allegro.mp3"),
        "credit": "Antonio Vivaldi, Les Quatre Saisons, « Le Printemps », 1er mouvement (Allegro). John "
                  "Harrison (violon) et le Wichita State University Chamber Players, sous licence CC BY-SA 3.0 : "
                  "citer l'enregistrement, et la vidéo qui l'utilise reste sous la même licence (CC BY-SA 3.0). "
                  "https://archive.org/details/The_Four_Seasons_Vivaldi-10361"},
    "macleod-thatched-villagers.mp3": {
        "url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Thatched%20Villagers.mp3",
        "credit": "« Thatched Villagers », Kevin MacLeod (incompetech.com), sous licence CC BY 4.0 : citer "
                  "« Thatched Villagers » Kevin MacLeod (incompetech.com), Licensed under Creative Commons: "
                  "By Attribution 4.0 License. https://incompetech.com"},
    "chopin-nocturne-op9-2.mp3": {
        "url": archive("musopen-chopin", "Nocturne Op. 9 no. 2 in E flat major.mp3"),
        "credit": "Frédéric Chopin, Nocturne op. 9 n° 2 en mi bémol majeur. Enregistrement Musopen, « The "
                  "Complete Chopin Collection », dédié au domaine public (CC0). https://archive.org/details/musopen-chopin"},
    "bach-prelude-1-ishizaka.mp3": {
        "url": archive("bach-well-tempered-clavier-book-1",
                       "Kimiko Ishizaka - Bach- Well-Tempered Clavier, Book 1 - 01 Prelude No. 1 in C major, BWV 846.mp3"),
        "credit": "Jean-Sébastien Bach, Prélude n° 1 en do majeur, BWV 846 (Le Clavier bien tempéré, livre 1). "
                  "Kimiko Ishizaka, « The Open Well-Tempered Clavier », placé dans le domaine public. "
                  "https://archive.org/details/bach-well-tempered-clavier-book-1"},
    "chopin-prelude-op28-15.mp3": {
        "url": archive("musopen-chopin", "Prelude Op. 28 no. 15.mp3"),
        "credit": "Frédéric Chopin, Prélude op. 28 n° 15 « La Goutte d'eau ». " + MUSOPEN},
    "chopin-grande-valse-op18.mp3": {
        "url": archive("musopen-chopin", "Grande Valse Brilliante Op.18 In E flat major.mp3"),
        "credit": "Frédéric Chopin, Grande valse brillante op. 18 en mi bémol majeur. " + MUSOPEN},
    "chopin-valse-op64-3.mp3": {
        "url": archive("musopen-chopin", "Waltz no.8 - Op.64 no.3_ Ab-major.mp3"),
        "credit": "Frédéric Chopin, Valse op. 64 n° 3 en la bémol majeur. " + MUSOPEN},
    "lfm-soft-as-a-dry-pillow.mp3": {
        "url": archive("loyalty-freak-music-chill-for-real",
                       "Loyalty Freak Music - CHILL FOR REAL ! - 05 Soft as a dry pillow.mp3"),
        "credit": "« Soft as a dry pillow ». " + LFM % (
            "CHILL FOR REAL !", "2023", "https://archive.org/details/loyalty-freak-music-chill-for-real")},
    "lfm-happy-sadie.mp3": {
        "url": archive("loyalty-freak-music-chill-for-real",
                       "Loyalty Freak Music - CHILL FOR REAL ! - 02 Happy Sadie.mp3"),
        "credit": "« Happy Sadie ». " + LFM % (
            "CHILL FOR REAL !", "2023", "https://archive.org/details/loyalty-freak-music-chill-for-real")},
    "lfm-sweet-sun.mp3": {
        "url": archive("LoyaltyFreakMusicPOSITIVEATTITUDE20170920175908839",
                       "Loyalty_Freak_Music_-_04_-_Sweet_Sun.mp3"),
        "credit": "« Sweet Sun ». " + LFM % (
            "POSITIVE ATTITUDE !", "2017",
            "https://archive.org/details/LoyaltyFreakMusicPOSITIVEATTITUDE20170920175908839")},
    "lfm-roller-fever.mp3": {
        "url": archive("LoyaltyFreakMusic-ROLLERDISCODANCEDANCE",
                       "Loyalty Freak Music - ROLLER DISCO DANCE DANCE - 01 Roller Fever.mp3"),
        "credit": "« Roller Fever ». " + LFM % (
            "ROLLER DISCO DANCE DANCE", "2019", "https://archive.org/details/LoyaltyFreakMusic-ROLLERDISCODANCEDANCE")},
    "lfm-chillin-with-a-drink.mp3": {
        "url": archive("LoyaltyFreakMusicTOCHILLANDSTAYAWAKE20170923132621469",
                       "Loyalty_Freak_Music_-_03_-_Chillin_with_a_drink_at_the_club.mp3"),
        "credit": "« Chillin' with a drink at the club ». " + LFM % (
            "TO CHILL AND STAY AWAKE", "2017",
            "https://archive.org/details/LoyaltyFreakMusicTOCHILLANDSTAYAWAKE20170923132621469")},
}
