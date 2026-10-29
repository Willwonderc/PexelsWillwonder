"""Assemble le fichier des cinq propositions : police, logo, données des photos, carte.

Usage : python3 docs/maquettes/panneau-wikipedia/assembler.py <fichier.html à écrire> [modèle]
(à écrire hors du dépôt, dans le dossier de travail de la session). Le modèle vaut
modele.html (les cinq propositions) ; retenu.html donne la version choisie par Karl.
"""
import base64, json, sys
from pathlib import Path
ici = Path(__file__).resolve().parent
depot = ici.parents[2]
statique = depot / "vitrine" / "statique"
modele = (ici / (sys.argv[2] if len(sys.argv) > 2 else "modele.html")).read_text(encoding="utf-8")
police = base64.b64encode((statique / "archivo.woff2").read_bytes()).decode()
logo = (statique / "logo.svg").read_text(encoding="utf-8").strip()
carte = json.loads((ici / "carte.json").read_text(encoding="utf-8"))
PHOTOS = [
    dict(id=39423921, lieu="Irun", region="Gipuzkoa, Pays basque", titre="Architecture classique de l'hôtel de ville d'Irun, au Pays basque espagnol",
         wiki="eu", article="Irungo Udala", partie="Udaletxea", legende="Irungo udaletxearen fatxada.", date="2026-10-28",
         fichier="Irun - hôtel de ville (Casa consistorial) - 2026.jpg"),
    dict(id=39228699, lieu="Gijón", region="Asturies", titre="La tour et l'église elliptique de l'Universidad Laboral de Gijón, en Espagne",
         wiki="ast", article="Universidá Llaboral de Xixón", partie="La torre", legende="La torre y la ilesia de la Universidá Llaboral.", date="2026-10-28",
         fichier="Gijón - Universidad Laboral, tour et église - 2026.jpg"),
    dict(id=39376205, lieu="Bordeaux", region="Gironde", titre="Majestueuse sculpture d'ange au monument aux Girondins, à Bordeaux, sous un ciel bleu",
         wiki="fr", article="Monument aux Girondins", partie="Description", legende="Le Génie de la Liberté brisant ses chaînes, au sommet de la colonne.", date="2026-10-28",
         fichier="Bordeaux - monument aux Girondins, Génie de la Liberté - 2026.jpg"),
    dict(id=13087478, lieu="Moyemont", region="Vosges", titre="Chemin de terre bordé d'arbres à Moyemont, un été idyllique",
         wiki="fr", article="Moyemont", partie="Géologie et relief", legende="Chemin de terre bordé d'arbres à Moyemont, en été.", date="2026-10-28",
         fichier="Moyemont - chemin bordé d'arbres - 2022.jpg"),
    dict(id=39182179, lieu="Buzy", region="Pyrénées-Atlantiques", titre="Un visiteur observe un dolmen préhistorique près de Pau, en noir et blanc",
         wiki="fr", article="Dolmen de Buzy", partie="Description", legende="La table de couverture en marbre gris, longue de 3,75 m, et ses orthostates.", date="2026-10-08",
         fichier="Buzy - dolmen - 2026.jpg"),
    dict(id=38279508, lieu="Niort", region="Deux-Sèvres", titre="Façade de la préfecture des Deux-Sèvres à Niort, drapeaux tricolores",
         wiki="fr", article="Hôtel de préfecture des Deux-Sèvres", partie="", legende="", date="2026-10-08",
         fichier="Niort - hôtel de préfecture des Deux-Sèvres - 2026.jpg"),
    dict(id=23414381, lieu="Niort", region="Deux-Sèvres", titre="Vue majestueuse des flèches néogothiques de l'église Saint-André au-dessus de Niort",
         wiki="fr", article="Église Saint-André de Niort", partie="Extérieur", legende="Les flèches jumelles dominent les toits de Niort.", date="2026-10-06",
         fichier="Niort - église Saint-André au-dessus de la ville - 2024.jpg"),
    dict(id=34894959, lieu="Îles Chausey", region="Manche", titre="Phare en granit à lanterne verte derrière les arbres aux îles Chausey, France",
         wiki="fr", article="Phare de Chausey", partie="Historique", legende="La tour carrée du phare, en granite de l'île, et sa lanterne.", date="2026-10-06",
         fichier="Îles Chausey - la tour du phare - 2025.jpg"),
]
fiches = json.loads((depot / "vitrine" / "donnees" / "fiches.json").read_text(encoding="utf-8"))
for p in PHOTOS:
    f = fiches[str(p["id"])]
    p.update(l=f["largeur"], h=f["hauteur"], couleur=f["couleur"])
html = (modele.replace("/*POLICE*/", police).replace("/*LOGO*/", logo)
        .replace("/*DONNEES*/", json.dumps(PHOTOS, ensure_ascii=False))
        .replace("/*CARTE*/", json.dumps(carte, ensure_ascii=False)))
Path(sys.argv[1]).write_text(html, encoding="utf-8")
print(len(html.encode()) // 1024, "Ko")
