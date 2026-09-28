#!/usr/bin/env python3
"""Contrôle les publications à faire à la main, avant de les pousser sur main.

Chaque publication (carrousel RedNote, publication Facebook) a son dossier
reseaux/publications/<id>/ : publication.json et ses images. build.py en tire
/tableau-de-bord/publications.json, que lit l'onglet « Publications » de Telepex,
l'application Mac de Karl : images dans l'ordre, textes à copier, validation. Format :
reseaux/README.md, « Publications à la main, dans Telepex ».

  python3 reseaux/publications.py              contrôle toutes les publications
  python3 reseaux/publications.py DOSSIER…     contrôle ces dossiers seulement
"""

import argparse
import json
import os
import re
import struct
import sys
from datetime import date
from pathlib import Path

PUBLICATIONS = Path(__file__).resolve().parent / "publications"
RESEAUX = ("rednote", "facebook", "instagram", "youtube", "autre")
RESEAUX_TELEPEX = ("rednote", "facebook")
LANGUES = ("zh", "fr", "en")
FORMES = ("carrousel", "video", "texte")
CHAMPS = {"format", "id", "reseau", "langue", "forme", "sujet", "carrousel", "date_prevue",
          "heure_conseillee", "etapes", "images", "textes", "traduction"}
# RedNote : titre de 20 caractères, texte de 1 000 hashtags compris, un émoji comptant
# pour deux ; viser 950 (reseaux/README.md, « RedNote »).
REDNOTE_TITRE, REDNOTE_TEXTE, REDNOTE_VISE = 20, 1000, 950


def longueur_rednote(texte):
    n = 0
    for c in texte:
        o = ord(c)
        if c in "️‍":
            continue
        n += 2 if o >= 0x1F000 or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF else 1
    return n


def dimensions(chemin):
    """Largeur et hauteur d'un JPEG ou d'un PNG, None pour un autre fichier."""
    d = chemin.read_bytes()
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    if d[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(d):
        if d[i] != 0xFF:
            return None
        marqueur, taille = d[i + 1], struct.unpack(">H", d[i + 2:i + 4])[0]
        if 0xC0 <= marqueur <= 0xCF and marqueur not in (0xC4, 0xC8, 0xCC):
            hauteur, largeur = struct.unpack(">HH", d[i + 5:i + 9])
            return largeur, hauteur
        i += 2 + taille
    return None


def textes_valides(liste, ou, erreurs):
    if not isinstance(liste, list) or not liste:
        erreurs.append(f"{ou} : liste de textes vide ou absente")
        return []
    for t in liste:
        if not (isinstance(t, dict) and isinstance(t.get("nom"), str) and t["nom"].strip()
                and isinstance(t.get("texte"), str) and t["texte"].strip()):
            erreurs.append(f"{ou} : chaque texte a un « nom » et un « texte » non vides")
            return []
    return liste


def images_valides(liste, dossier, ou, erreurs, avis, rednote):
    if not isinstance(liste, list):
        erreurs.append(f"{ou} : « images » doit être une liste")
        return []
    for nom in liste:
        chemin = dossier / nom if isinstance(nom, str) else None
        if chemin is None or Path(nom).is_absolute() or ".." in Path(nom).parts or not chemin.is_file():
            erreurs.append(f"{ou} : image introuvable dans le dossier : {nom}")
            continue
        taille = dimensions(chemin)
        if taille is None:
            erreurs.append(f"{ou} : {nom} n'est ni un JPEG ni un PNG")
        elif rednote and taille[0] * 4 != taille[1] * 3:
            avis.append(f"{ou} : {nom} mesure {taille[0]} × {taille[1]}, pas 3:4")
    return [n for n in liste if isinstance(n, str)]


def verifier(dossier):
    """Contrôle une publication ; rend (publication, liste des fichiers, erreurs, avis)."""
    erreurs, avis = [], []
    try:
        pub = json.loads((dossier / "publication.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [], ["publication.json manque"], []
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return None, [], [f"publication.json illisible : {e}"], []
    if not isinstance(pub, dict):
        return None, [], ["publication.json doit contenir un objet"], []
    if pub.get("format") != 1:
        erreurs.append("« format » doit valoir 1")
    ident = pub.get("id")
    if not isinstance(ident, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident):
        erreurs.append("« id » : minuscules sans accents, chiffres et tirets")
    elif ident != dossier.name:
        avis.append(f"le dossier devrait porter le nom de l'« id » : {ident}")
    for champ, permis in (("reseau", RESEAUX), ("langue", LANGUES), ("forme", FORMES)):
        if pub.get(champ) not in permis:
            erreurs.append(f"« {champ} » : {', '.join(permis)}")
    if not isinstance(pub.get("sujet"), str) or not pub["sujet"].strip():
        erreurs.append("« sujet » manque")
    prevue = pub.get("date_prevue")
    if prevue is not None:
        try:
            date.fromisoformat(prevue)
        except (TypeError, ValueError):
            erreurs.append("« date_prevue » : AAAA-MM-JJ")
        if isinstance(ident, str) and isinstance(prevue, str) and not ident.startswith(prevue):
            avis.append("l'« id » commence d'ordinaire par la date prévue")
    for champ in sorted(set(pub) - CHAMPS):
        avis.append(f"champ inconnu : « {champ} »")
    if pub.get("reseau") in RESEAUX and pub["reseau"] not in RESEAUX_TELEPEX:
        avis.append("Telepex ne montre que les publications RedNote et Facebook")
    rednote = pub.get("reseau") == "rednote"
    fichiers = images_valides(pub.get("images", []), dossier, "images", erreurs, avis, rednote)
    if pub.get("forme") == "carrousel" and not fichiers:
        erreurs.append("un carrousel a au moins une image")
    if rednote and pub.get("forme") == "carrousel" and len(fichiers) != 9:
        avis.append(f"RedNote : {len(fichiers)} images, 9 d'ordinaire")
    textes = textes_valides(pub.get("textes"), "textes", erreurs)
    if textes and all(t["nom"].lower().startswith("titre") for t in textes):
        erreurs.append("« textes » : il faut un texte à publier en plus du titre")
    for t in textes:
        if rednote:
            n = longueur_rednote(t["texte"])
            limite = REDNOTE_TITRE if t["nom"].lower().startswith("titre") else REDNOTE_TEXTE
            if n > limite:
                erreurs.append(f"RedNote, « {t['nom']} » : {n} caractères, {limite} au plus")
            elif limite == REDNOTE_TEXTE and n > REDNOTE_VISE:
                avis.append(f"RedNote, « {t['nom']} » : {n} caractères, viser {REDNOTE_VISE}")
    trad = pub.get("traduction")
    if trad is not None:
        if not isinstance(trad, dict) or trad.get("langue") not in LANGUES:
            erreurs.append("« traduction » : un objet avec « langue » et « textes »")
        else:
            textes_valides(trad.get("textes"), "traduction", erreurs)
            fichiers += images_valides(trad.get("images", []), dossier, "traduction", erreurs, avis, False)
    etapes = pub.get("etapes", [])
    if not isinstance(etapes, list) or not all(isinstance(e, str) and e.strip() for e in etapes):
        erreurs.append("« etapes » : une liste de phrases")
    return pub, fichiers, erreurs, avis


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("dossiers", nargs="*", type=Path, metavar="DOSSIER")
    args = options.parse_args()
    dossiers = args.dossiers or sorted(d for d in PUBLICATIONS.iterdir() if d.is_dir())
    echecs = 0
    for dossier in dossiers:
        pub, fichiers, erreurs, avis = verifier(dossier)
        nom = os.path.relpath(dossier)
        for a in avis:
            print(f"{nom} : attention, {a}")
        if erreurs:
            echecs += 1
            for e in erreurs:
                print(f"{nom} : ERREUR, {e}")
            continue
        print(f"{nom} : publication valide ({len(fichiers)} images)")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
