#!/usr/bin/env python3
"""Prépare les fichiers d'import d'épingles pour Pinterest et prévoit le calendrier des flux.

  python3 pinterest/epingles.py --essai        une épingle par galerie : crée les tableaux
  python3 pinterest/epingles.py --calendrier   épingles par flux et date de la dernière

Chaque épingle mène à la page Pexels de sa photo ; l'image est donnée par son adresse
directe, terminée par .jpeg, comme le demande l'aide de Pinterest. Les fichiers sont écrits dans
pinterest/imports/, au format du modèle d'import de Pinterest.
"""

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "vitrine"))
import build  # noqa: E402

COLONNES = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]


def charger():
    reglages = build.lire_ini("site.ini")
    anglais, francais = build.lire_textes()
    photos, _ = build.assembler_photos(build.lire_photos(), build.charger_fiches(), anglais, francais, build.lire_suivi())
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


def calendrier(photos, galeries):
    """Simule le journal des parutions nuit après nuit, sans nouvelle photo : nombre de
    photos de chaque flux, déjà parues, et date prévue de la dernière épingle."""
    r = build.reglages_pinterest(build.lire_ini("site.ini"))
    flux = build.flux_pinterest(galeries, photos, r)
    journal = build.charger_parutions()
    parues = {cle: sum(1 for p in membres if str(p["id"]) in journal.get(cle, {})) for cle, membres, _ in flux}
    jour = date.fromisoformat(build.AUJOURDHUI)
    par_jour = {}
    while True:
        par_jour[jour] = build.completer_parutions(journal, flux, jour.isoformat(), r["depuis"], r["par_flux"], r["plafond"])
        if all(str(p["id"]) in journal.get(cle, {}) for cle, membres, _ in flux for p in membres):
            break
        jour += timedelta(days=1)
    titres = {g["cle"]: g["titre"]["en"] for g in galeries}
    titres[build.AUTRES] = "Photos by Karl Forterre"
    print("| Tableau | Photos | Déjà parues | Dernière épingle |")
    print("|---|---|---|---|")
    for cle, membres, _ in flux:
        dates = [journal[cle][str(p["id"])] for p in membres]
        print(f"| {titres[cle]} | {len(membres)} | {parues[cle]} | {max(dates) if dates else '—'} |")
    premiers = ", ".join(f"{j.isoformat()} : {n}" for j, n in list(par_jour.items())[:5])
    print(f"\nÉpingles ajoutées les premiers jours : {premiers}.")
    print(f"Plus haut : {max(par_jour.values())} en un jour ; dernière épingle du fonds : {jour.isoformat()}.")


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("--essai", action="store_true", help="une épingle par galerie, pour créer les tableaux")
    options.add_argument("--calendrier", action="store_true", help="calendrier prévu des flux Pinterest")
    args = options.parse_args()
    photos, galeries = charger()
    if args.essai:
        ecrire("essai-2-une-epingle-par-galerie.csv", [epingle(g["couverture"], g["titre"]["en"]) for g in galeries])
    elif args.calendrier:
        calendrier(photos, galeries)
    else:
        options.print_help()


if __name__ == "__main__":
    main()
