#!/usr/bin/env python3
"""Prépare les fichiers d'import d'épingles pour Pinterest.

  python3 pinterest/epingles.py --essai   une épingle par galerie : crée les tableaux

Chaque épingle mène à la page Pexels de sa photo ; l'image est donnée par son adresse
directe, terminée par .jpeg, comme le demande l'aide de Pinterest. Les fichiers sont écrits dans
pinterest/imports/, au format du modèle d'import de Pinterest.
"""

import argparse
import csv
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "vitrine"))
import build  # noqa: E402

COLONNES = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]


def charger():
    reglages = build.lire_ini("site.ini")
    anglais, francais = build.lire_textes()
    photos, _ = build.assembler_photos(build.lire_photos(), build.charger_fiches(), anglais, francais)
    minimum = int(reglages["site"].get("galerie_min", "4") or 4)
    return photos, build.composer_galeries(build.lire_ini("galeries.ini"), photos, minimum)


def epingle(photo, tableau, quand=""):
    titre = photo["titre"]["en"][:100]
    mots = photo["mots"]["en"][:10]
    description = f"{titre}. Royalty-free photo by Karl Forterre, free to download on Pexels."
    if mots:
        description += " " + ", ".join(mots) + "."
    return {
        "Title": titre,
        "Media URL": photo["image"],
        "Pinterest board": tableau,
        "Thumbnail": "",
        "Description": description[:500],
        "Link": photo["page"],
        "Publish date": quand,
        "Keywords": ", ".join(mots),
    }


def ecrire(nom, lignes):
    dossier = ICI / "imports"
    dossier.mkdir(exist_ok=True)
    with open(dossier / nom, "w", encoding="utf-8", newline="") as f:
        sortie = csv.DictWriter(f, fieldnames=COLONNES)
        sortie.writeheader()
        sortie.writerows(lignes)
    print(f"{dossier / nom} : {len(lignes)} épingles")


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("--essai", action="store_true", help="une épingle par galerie, pour créer les tableaux")
    args = options.parse_args()
    photos, galeries = charger()
    if args.essai:
        ecrire("essai-2-une-epingle-par-galerie.csv", [epingle(g["couverture"], g["titre"]["en"]) for g in galeries])
    else:
        options.print_help()


if __name__ == "__main__":
    main()
