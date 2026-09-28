#!/usr/bin/env python3
"""Contrôle et ferme un paquet de publication pour Telepex.

Un paquet réunit une publication à faire à la main (carrousel RedNote, publication
Facebook, vidéo) : le fichier publication.json et ses images, dans un dossier. Telepex,
l'application Mac de Karl, l'affiche dans son onglet « Publications » : images dans
l'ordre, textes à copier, validation. Format : reseaux/README.md, « Paquets de
publication pour Telepex ». Les paquets ne vont jamais dans le dépôt.

  python3 reseaux/paquet.py DOSSIER [DOSSIER…]   contrôle chaque dossier et écrit
                                                publication-<id>.zip à côté
  python3 reseaux/paquet.py --verifier DOSSIER   contrôle seulement
"""

import argparse
import json
import re
import struct
import sys
import zipfile
from datetime import date
from pathlib import Path

RESEAUX = ("rednote", "facebook", "instagram", "youtube", "autre")
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
    """Contrôle le paquet ; rend (publication, liste des fichiers, erreurs, avis)."""
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
    rednote = pub.get("reseau") == "rednote"
    fichiers = images_valides(pub.get("images", []), dossier, "images", erreurs, avis, rednote)
    if pub.get("forme") == "carrousel" and not fichiers:
        erreurs.append("un carrousel a au moins une image")
    if rednote and pub.get("forme") == "carrousel" and len(fichiers) != 9:
        avis.append(f"RedNote : {len(fichiers)} images, 9 d'ordinaire")
    for t in textes_valides(pub.get("textes"), "textes", erreurs):
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


def fermer(dossier, pub, fichiers, sortie):
    nom = f"publication-{pub['id']}"
    zip_ = sortie / f"{nom}.zip"
    with zipfile.ZipFile(zip_, "w") as z:
        z.write(dossier / "publication.json", f"{nom}/publication.json", zipfile.ZIP_DEFLATED)
        for f in dict.fromkeys(fichiers):
            z.write(dossier / f, f"{nom}/{f}", zipfile.ZIP_STORED)
    return zip_


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("dossiers", nargs="+", type=Path, metavar="DOSSIER")
    options.add_argument("--verifier", action="store_true", help="contrôle sans écrire le zip")
    options.add_argument("--sortie", type=Path, help="dossier du zip (par défaut, à côté du dossier)")
    args = options.parse_args()
    echecs = 0
    for dossier in args.dossiers:
        pub, fichiers, erreurs, avis = verifier(dossier)
        for a in avis:
            print(f"{dossier} : attention, {a}")
        if erreurs:
            echecs += 1
            for e in erreurs:
                print(f"{dossier} : ERREUR, {e}")
            continue
        if args.verifier:
            print(f"{dossier} : paquet valide ({len(fichiers)} images)")
            continue
        zip_ = fermer(dossier, pub, fichiers, args.sortie or dossier.resolve().parent)
        print(f"{zip_} : {len(fichiers)} images, {zip_.stat().st_size / 1e6:.1f} Mo")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
