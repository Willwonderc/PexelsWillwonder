#!/usr/bin/env python3
"""Construit le site de photographe de Karl Forterre.

1. Lit la liste des photos : vitrine/photos.txt.
2. Complète les fiches Pexels (vitrine/donnees/fiches.json) grâce à l'API, si la
   variable d'environnement PEXELS_API_KEY est définie.
3. Ajoute les parutions du jour au journal des flux Pinterest
   (vitrine/donnees/parutions.json).
4. Écrit le site statique dans le dossier _site/.

Options :
  --fiches-seulement       ne fait que l'étape 2
  --max-appels N           nombre maximum d'appels à l'API (180 par défaut)
  --enregistrer-parutions  enregistre le journal (tâche de nuit) ; sans cette option,
                           les parutions du jour servent aux flux sans être enregistrées
"""

import argparse
import colorsys
import configparser
import csv
import email.utils
import hashlib
import html
import json
import math
import os
import re
import shutil
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
SORTIE = RACINE / "_site"
FICHES = ICI / "donnees" / "fiches.json"
PARUTIONS = ICI / "donnees" / "parutions.json"
AUTRES = "autres-photos"  # flux des photos rangées dans aucune galerie
PHOTOGRAPHE = 28489473
LICENCE = "https://www.pexels.com/license/"
AUJOURDHUI = datetime.now(timezone.utc).date().isoformat()
HEBERGEUR = "GitHub, Inc."
HEBERGEUR_ADRESSE = {
    "fr": "88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis",
    "en": "88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, United States",
}
HEBERGEUR_TELEPHONE = "+1 877 448 4820"

TEXTES = {
    "fr": {
        "accueil": "Photographies de Karl Forterre",
        "galeries": "Galeries",
        "series": "Séries",
        "selection": "Sélection",
        "a_propos": "À propos",
        "autre_langue": "English",
        "themes": "Thèmes",
        "lieux": "Lieux",
        "recentes": "Dernières photos",
        "une_photo": "1\u00a0photo",
        "n_photos": "{n}\u00a0photos",
        "telecharger": "Télécharger gratuitement sur Pexels",
        "credit": "Photo de Karl Forterre, sous {licence} : utilisation libre et gratuite.",
        "licence": "licence Pexels",
        "numero": "Pexels n° {id}",
        "mots": "Mots-clés",
        "dans": "Dans les galeries :",
        "dans_serie": "Dans la série :",
        "proches": "Photos proches",
        "a_propos_galerie": "À propos de cette galerie",
        "couleurs": "Couleurs",
        "couleurs_photo": "Couleurs :",
        "couleur_description": "{titre} de Karl Forterre, rangées d'après leur couleur dominante : "
                               "libres de droits, à télécharger gratuitement sur Pexels.",
        "accueil_court": "Accueil",
        "ariane": "Fil d'Ariane",
        "precedente": "Photo précédente",
        "suivante": "Photo suivante",
        "flux": "Flux RSS",
        "flux_galerie": "Flux RSS de la galerie",
        "autres_photos": "Autres photos de Karl Forterre",
        "suffixe": "Photo de Karl Forterre, libre de droits, à télécharger gratuitement sur Pexels.",
        "introuvable": "Page introuvable",
        "introuvable_texte": "Cette page n'existe pas ou plus.",
        "retour": "Retour à l'accueil",
        "profil": "Profil Pexels",
        "evitement": "Aller au contenu",
        "menu": "Navigation principale",
        "suivre": "Suivre sur Pexels",
        "voir_pexels": "Voir cette photo sur Pexels",
        "voir_galeries": "Voir les galeries",
        "preuve": "{vues} vues et {telechargements} téléchargements sur Pexels",
        "preuve_vues": "{vues} vues sur Pexels",
        "rappel": "Toutes ces photos se téléchargent gratuitement sur Pexels. "
                  "Suivez-y Karl Forterre pour découvrir les nouvelles en premier.",
        "series_intro": "Chaque série raconte un lieu ou un moment : quelques lignes d'histoire, "
                        "puis les photos, toutes à télécharger gratuitement sur Pexels.",
        "galeries_intro": "Les photos rangées par thème et par lieu, toutes à télécharger gratuitement sur Pexels.",
        "titre_serie": "{titre} : photos libres de droits",
        "autres_series": "Autres séries",
        "utiliser": "Utiliser mes photos",
        "mentions": "Mentions légales",
        "confidentialite": "Confidentialité",
        "contact": "Contact",
        "lieux_photographies": "Lieux photographiés",
        "materiel": "Matériel",
        "visionneuse": "Visionneuse",
        "fermer": "Fermer",
        "locale": "fr_FR",
    },
    "en": {
        "accueil": "Photographs by Karl Forterre",
        "galeries": "Galleries",
        "series": "Series",
        "selection": "Selection",
        "a_propos": "About",
        "autre_langue": "Français",
        "themes": "Themes",
        "lieux": "Places",
        "recentes": "Latest photos",
        "une_photo": "1\u00a0photo",
        "n_photos": "{n}\u00a0photos",
        "telecharger": "Free download on Pexels",
        "credit": "Photo by Karl Forterre, under the {licence}: free to use.",
        "licence": "Pexels license",
        "numero": "Pexels no. {id}",
        "mots": "Keywords",
        "dans": "In the galleries:",
        "dans_serie": "In the series:",
        "proches": "Similar photos",
        "a_propos_galerie": "About this gallery",
        "couleurs": "Colors",
        "couleurs_photo": "Colors:",
        "couleur_description": "{titre} by Karl Forterre, sorted by their dominant color: "
                               "royalty-free, free to download on Pexels.",
        "accueil_court": "Home",
        "ariane": "Breadcrumb",
        "precedente": "Previous photo",
        "suivante": "Next photo",
        "flux": "RSS feed",
        "flux_galerie": "Gallery RSS feed",
        "autres_photos": "More photos by Karl Forterre",
        "suffixe": "Photo by Karl Forterre, royalty-free, free to download on Pexels.",
        "introuvable": "Page not found",
        "introuvable_texte": "This page does not exist, or no longer does.",
        "retour": "Back to the home page",
        "profil": "Pexels profile",
        "evitement": "Skip to content",
        "menu": "Main navigation",
        "suivre": "Follow on Pexels",
        "voir_pexels": "See this photo on Pexels",
        "voir_galeries": "See the galleries",
        "preuve": "{vues} views and {telechargements} downloads on Pexels",
        "preuve_vues": "{vues} views on Pexels",
        "rappel": "All these photos are free to download on Pexels. "
                  "Follow Karl Forterre there to see new ones first.",
        "series_intro": "Each series tells the story of a place or a moment: a few lines of background, "
                        "then the photos, all free to download on Pexels.",
        "galeries_intro": "Photos arranged by theme and by place, all free to download on Pexels.",
        "titre_serie": "{titre}: royalty-free photos",
        "autres_series": "More series",
        "utiliser": "Use my photos",
        "mentions": "Legal notice",
        "confidentialite": "Privacy",
        "contact": "Contact",
        "lieux_photographies": "Places photographed",
        "materiel": "Equipment",
        "visionneuse": "Photo viewer",
        "fermer": "Close",
        "locale": "en_US",
    },
}


def e(texte):
    return html.escape(str(texte), quote=True)


def plier(texte):
    """Minuscules sans accents, pour comparer des mots."""
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


def tronquer(texte, n=160):
    return texte if len(texte) <= n else texte[: n - 1].rsplit(" ", 1)[0] + "…"


def nombres(texte):
    return [int(n) for n in re.findall(r"\d{4,}", texte or "")]


def entier(texte):
    """Nombre écrit dans un relevé, avec ou sans espaces : 0 s'il n'y en a pas."""
    chiffres = re.sub(r"\D", "", texte or "")
    return int(chiffres) if chiffres else 0


def liste_mots(texte):
    return [m.strip() for m in (texte or "").split(",") if m.strip()]


def paragraphes(texte):
    """Paragraphes d'un texte de réglage, séparés par une ligne vide."""
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", texte or "") if p.strip()]


def chiffre(n, langue):
    """878500 → « 878 500 » en français (espace fine insécable), « 878,500 » en anglais."""
    texte = f"{n:,}"
    return texte.replace(",", " ") if langue == "fr" else texte


# ---------------------------------------------------------------- données


def lire_ini(nom):
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(ICI / nom, encoding="utf-8")
    return conf


def lire_liste(nom):
    """Numéros Pexels d'une liste : un lien ou un numéro en début de ligne, suivi au
    besoin d'un commentaire. Les lignes qui commencent par # sont ignorées."""
    chemin = ICI / nom
    ids = []
    if not chemin.exists():
        return ids
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        mots = ligne.split()
        if not mots or mots[0].startswith("#"):
            continue
        trouves = nombres(mots[0])
        if trouves and trouves[-1] not in ids:
            ids.append(trouves[-1])
    return ids


def lire_photos():
    return lire_liste("photos.txt")


def lire_csv(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def lire_textes():
    """Titres et mots-clés anglais (atelier/resultats) et français (donnees/textes-fr.csv)."""
    anglais, francais = {}, {}
    for chemin in sorted((RACINE / "atelier" / "resultats").glob("*.csv")):
        for ligne in lire_csv(chemin):
            cle = (ligne.get("photo") or "").strip()
            if cle.isdigit() and (ligne.get("titre") or "").strip():
                anglais[int(cle)] = {"titre": ligne["titre"].strip(), "mots": ligne.get("mots_cles", "")}
    chemin = ICI / "donnees" / "textes-fr.csv"
    if chemin.exists():
        for ligne in lire_csv(chemin):
            cle = (ligne.get("photo") or "").strip()
            if cle.isdigit():
                francais[int(cle)] = {"titre": (ligne.get("titre_fr") or "").strip(), "mots": ligne.get("mots_cles_fr", "")}
    return anglais, francais


# Mots-clés mal encodés dans l'export de la fiche de suivi (« apÃ ro » pour « apéro »).
ILLISIBLE = re.compile("[ÃÂ]|â€|\ufffd")


def lire_suivi():
    """Fiches de suivi (releves/suivi-*.csv) : vues et mots-clés Pexels de chaque photo.

    Vues : le plus haut relevé. Mots-clés : ceux de la fiche la plus récente, c'est-à-dire
    celle qui totalise le plus de vues, sans les mots mal encodés.
    """
    fichiers = [lire_csv(chemin) for chemin in (RACINE / "releves").glob("suivi-*.csv")]
    suivi = {}
    for lignes in sorted(fichiers, key=lambda lignes: sum(entier(l.get("vues")) for l in lignes)):
        for ligne in lignes:
            cle = (ligne.get("photo") or "").strip()
            if not cle.isdigit():
                continue
            fiche = suivi.setdefault(int(cle), {"vues": 0, "mots": []})
            fiche["vues"] = max(fiche["vues"], entier(ligne.get("vues")))
            mots = [m for m in liste_mots(ligne.get("mots_cles")) if not ILLISIBLE.search(m)]
            if mots:
                fiche["mots"] = mots
    return suivi


def lire_releves():
    """Derniers chiffres des relevés (dossier releves/) : vues et téléchargements Pexels.

    Vues : la ligne la plus récente de vues-pexels.csv, ou le total d'une fiche de suivi
    s'il est plus élevé. Téléchargements : le total de la fiche de suivi la plus récente,
    c'est-à-dire la plus élevée, puisque ces chiffres ne font que croître.
    """
    dossier = RACINE / "releves"
    vues = telechargements = 0
    chemin = dossier / "vues-pexels.csv"
    if chemin.exists():
        lignes = [l for l in lire_csv(chemin) if entier(l.get("vues"))]
        if lignes:
            vues = entier(max(lignes, key=lambda l: (l.get("date") or "").strip())["vues"])
    for chemin in sorted(dossier.glob("suivi-*.csv")):
        lignes = lire_csv(chemin)
        vues = max(vues, sum(entier(l.get("vues")) for l in lignes))
        telechargements = max(telechargements, sum(entier(l.get("telechargements")) for l in lignes))
    return {"vues": vues, "telechargements": telechargements}


def charger_fiches():
    if FICHES.exists():
        return json.loads(FICHES.read_text(encoding="utf-8"))
    return {}


def enregistrer_fiches(fiches):
    FICHES.parent.mkdir(parents=True, exist_ok=True)
    triees = {cle: fiches[cle] for cle in sorted(fiches, key=int)}
    FICHES.write_text(json.dumps(triees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def completer_fiches(ids, fiches, max_appels):
    """Lit sur l'API Pexels les fiches manquantes, dans la limite de max_appels."""
    manquantes = [i for i in ids if str(i) not in fiches]
    cle = os.environ.get("PEXELS_API_KEY", "").strip()
    if not manquantes or max_appels <= 0:
        return 0
    if not cle:
        print(f"{len(manquantes)} fiches manquantes, mais PEXELS_API_KEY n'est pas définie.")
        return 0
    lues = 0
    for pid in manquantes[:max_appels]:
        requete = urllib.request.Request(
            f"https://api.pexels.com/v1/photos/{pid}",
            headers={"Authorization": cle, "User-Agent": "site-karl-forterre"},
        )
        try:
            with urllib.request.urlopen(requete, timeout=30) as reponse:
                p = json.load(reponse)
        except urllib.error.HTTPError as erreur:
            if erreur.code == 429:
                print("Limite horaire de l'API atteinte : la suite au prochain passage.")
                break
            if erreur.code == 404:
                fiches[str(pid)] = {"introuvable": True, "vue_le": AUJOURDHUI}
            else:
                print(f"Photo {pid} : erreur {erreur.code}.")
            continue
        except OSError as erreur:
            print(f"Photo {pid} : {erreur}.")
            continue
        fiches[str(pid)] = {
            "largeur": p["width"],
            "hauteur": p["height"],
            "texte": p.get("alt") or "",
            "page": p["url"],
            "image": p["src"]["original"],
            "couleur": p.get("avg_color") or "",
            "photographe": p.get("photographer_id"),
            "vue_le": AUJOURDHUI,
        }
        lues += 1
        time.sleep(0.25)
    enregistrer_fiches(fiches)
    return lues


def titre_pexels(texte):
    """Texte alternatif de Pexels, sauf s'il est vide ou automatique."""
    texte = (texte or "").strip().rstrip(".").strip()
    if not texte or texte.lower().startswith("free stock photo"):
        return ""
    return texte


def cle_mot(mot):
    """Forme de comparaison d'un mot-clé : sans accents, sans majuscules ni pluriel."""
    mot = " ".join(plier(mot).split())
    return mot[:-1] if len(mot) > 3 and mot.endswith("s") and not mot.endswith("ss") else mot


# Mots d'ambiance, affichés après les mots plus concrets quand il faut choisir.
MOTS_VAGUES = frozenset(map(cle_mot, (
    "beautiful, beauty, beautiful wallpaper, breathtaking, bright, calm, charming, cute, dazzling, "
    "elegant, gentle, handsome, harmonious design, harmony, idyllic, impressive, inspiration, lovely, "
    "lush, majestic, mood, moody, natural beauty, peace, peaceful, picturesque, pretty, quiet moment, "
    "relaxation, relaxing, scenic, serene, serenity, simple, soothing, stunning, tranquil, tranquility, "
    "vastness, vivid colors, wonderful").split(", ")))


def choisir_mots(mots, titre, frequence, nombre=12):
    """Mots-clés Pexels affichés sur la page d'une photo : ceux du titre d'abord, puis les
    plus répandus dans l'ensemble des photos, les mots d'ambiance en dernier."""
    titre = plier(titre)
    uniques = {}
    for mot in mots:
        uniques.setdefault(cle_mot(mot), mot)

    def rang(cle):
        return (not re.search(r"\b" + re.escape(cle), titre), cle in MOTS_VAGUES, -frequence[cle], cle)

    return [uniques[cle] for cle in sorted(uniques, key=rang)][:nombre]


def assembler_photos(ids, fiches, anglais, francais, suivi=None):
    """Photos publiées : fiche Pexels, titres et mots-clés de l'atelier, et, d'après la fiche
    de suivi, vues et mots-clés Pexels. Ces derniers servent à composer les galeries et à
    trouver les photos proches ; une douzaine s'affiche quand l'atelier n'en a pas donné."""
    suivi = suivi or {}
    frequence = {}
    for pid in ids:
        for cle in {cle_mot(m) for m in suivi.get(pid, {}).get("mots", [])}:
            frequence[cle] = frequence.get(cle, 0) + 1
    photos, sans_titre = [], 0
    for pid in ids:
        fiche = fiches.get(str(pid))
        if not fiche or fiche.get("introuvable") or fiche.get("photographe") != PHOTOGRAPHE:
            continue
        en = anglais.get(pid, {})
        fr = francais.get(pid, {})
        titre_en = en.get("titre") or titre_pexels(fiche.get("texte"))
        if not titre_en:
            sans_titre += 1
            continue
        mots_pexels = suivi.get(pid, {}).get("mots", [])
        mots_en = liste_mots(en.get("mots"))
        mots_fr = liste_mots(fr.get("mots"))
        affiches = mots_en or choisir_mots(mots_pexels, titre_en, frequence)
        photos.append({
            "id": pid,
            "largeur": fiche["largeur"],
            "hauteur": fiche["hauteur"],
            "page": fiche["page"],
            "image": fiche["image"],
            "couleur": fiche.get("couleur") or "#8a8a8a",
            "vue_le": fiche.get("vue_le") or AUJOURDHUI,
            "vues": suivi.get(pid, {}).get("vues", 0),
            "titre": {"en": titre_en, "fr": fr.get("titre") or titre_en},
            # Sans mots-clés français, la page française affiche les mots anglais.
            "mots": {"en": affiches, "fr": mots_fr or affiches},
            "langue_mots": {"en": "en", "fr": "fr" if mots_fr else "en"},
            "cles": {cle_mot(m) for m in mots_en + mots_pexels},
            "recherche": plier(" ".join([titre_en, en.get("mots", ""), fiche.get("texte", ""), ", ".join(mots_pexels)])),
        })
    photos.sort(key=lambda p: -p["id"])
    return photos, sans_titre


def en_largeur(photo):
    return photo["largeur"] > photo["hauteur"]


def photo_bandeau(reglage, membres, couverture):
    """Photo affichée en bandeau derrière le titre : réglage « bandeau », sinon la
    couverture si elle est en largeur, sinon la première photo en largeur."""
    choix = nombres(reglage.get("bandeau"))
    return (next((p for p in membres if p["id"] in choix), None)
            or (couverture if en_largeur(couverture) else next((p for p in membres if en_largeur(p)), couverture)))


def composer_galeries(conf, photos, minimum):
    galeries = []
    for cle in conf.sections():
        reglage = conf[cle]
        mots = [plier(m) for m in liste_mots(reglage.get("mots"))]
        motif = re.compile(r"\b(?:" + "|".join(re.escape(m) for m in mots) + r")s?\b") if mots else None
        ajouter = set(nombres(reglage.get("ajouter")))
        retirer = set(nombres(reglage.get("retirer")))
        membres = [
            p for p in photos
            if p["id"] not in retirer and (p["id"] in ajouter or (motif and motif.search(p["recherche"])))
        ]
        if len(membres) < minimum:
            continue
        couverture = next((p for p in membres if p["id"] in nombres(reglage.get("couverture"))), membres[0])
        titre_fr = reglage.get("titre_fr", cle)
        description_fr = reglage.get("description_fr", "")
        texte_fr = paragraphes(reglage.get("texte_fr"))
        galeries.append({
            "cle": cle,
            "type": reglage.get("type", "theme").strip(),
            "titre": {"fr": titre_fr, "en": reglage.get("titre_en", titre_fr)},
            "description": {"fr": description_fr, "en": reglage.get("description_en", description_fr)},
            "texte": {"fr": texte_fr, "en": paragraphes(reglage.get("texte_en")) or texte_fr},
            "photos": membres,
            "couverture": couverture,
            "bandeau": photo_bandeau(reglage, membres, couverture),
        })
    return galeries


def composer_series(conf, photos, minimum):
    """Séries racontées de series.ini : photos dans l'ordre donné, textes bilingues."""
    par_id = {p["id"]: p for p in photos}
    series = []
    for cle in conf.sections():
        reglage = conf[cle]
        membres = []
        for pid in nombres(reglage.get("photos")):
            if pid in par_id and par_id[pid] not in membres:
                membres.append(par_id[pid])
        if len(membres) < minimum:
            continue
        couverture = next((p for p in membres if p["id"] in nombres(reglage.get("couverture"))), membres[0])
        champs = {}
        for champ in ("titre", "lieu", "date"):
            fr = reglage.get(f"{champ}_fr", cle if champ == "titre" else "").strip()
            champs[champ] = {"fr": fr, "en": reglage.get(f"{champ}_en", "").strip() or fr}
        texte_fr = paragraphes(reglage.get("texte_fr"))
        series.append({
            "cle": cle,
            **champs,
            "texte": {"fr": texte_fr, "en": paragraphes(reglage.get("texte_en")) or texte_fr},
            "photos": membres,
            "couverture": couverture,
            "bandeau": photo_bandeau(reglage, membres, couverture),
        })
    return series


# Pages par couleur, d'après la couleur moyenne que Pexels donne pour chaque photo.
COULEURS = (
    {"cle": {"fr": "bleu", "en": "blue"}, "nom": {"fr": "Bleu", "en": "Blue"},
     "titre": {"fr": "Photos bleues", "en": "Blue photos"}, "pastille": "#3d6ea6"},
    {"cle": {"fr": "vert", "en": "green"}, "nom": {"fr": "Vert", "en": "Green"},
     "titre": {"fr": "Photos vertes", "en": "Green photos"}, "pastille": "#4c7a3b"},
    {"cle": {"fr": "jaune-orange", "en": "yellow-orange"}, "nom": {"fr": "Jaune et orange", "en": "Yellow and orange"},
     "titre": {"fr": "Photos jaunes et orange", "en": "Yellow and orange photos"}, "pastille": "#d99130"},
    {"cle": {"fr": "rouge-rose", "en": "red-pink"}, "nom": {"fr": "Rouge et rose", "en": "Red and pink"},
     "titre": {"fr": "Photos rouges et roses", "en": "Red and pink photos"}, "pastille": "#b84552"},
    {"cle": {"fr": "tons-sombres", "en": "dark-tones"}, "nom": {"fr": "Tons sombres", "en": "Dark tones"},
     "titre": {"fr": "Photos aux tons sombres", "en": "Dark-toned photos"}, "pastille": "#1c1c21"},
    {"cle": {"fr": "tons-clairs", "en": "light-tones"}, "nom": {"fr": "Tons clairs", "en": "Light tones"},
     "titre": {"fr": "Photos aux tons clairs", "en": "Light-toned photos"}, "pastille": "#ebe6dc"},
)


def teintes(couleur):
    """Pages de couleur d'une photo, d'après sa couleur moyenne (#rrvvbb) : une teinte si
    elle est assez marquée, et un ton si elle est assez foncée ou assez pâle."""
    try:
        r, v, b = (int(couleur[i:i + 2], 16) / 255 for i in (1, 3, 5))
    except ValueError:
        return []
    teinte, clarte, _ = colorsys.rgb_to_hls(r, v, b)
    choix = []
    if max(r, v, b) - min(r, v, b) >= 0.08:
        degres = teinte * 360
        choix.append("jaune-orange" if 15 <= degres < 70 else "vert" if degres < 165
                     else "bleu" if degres < 260 else "rouge-rose")
    if clarte < 0.25:
        choix.append("tons-sombres")
    elif clarte > 0.7:
        choix.append("tons-clairs")
    return choix


def composer_couleurs(photos, minimum):
    couleurs = []
    for c in COULEURS:
        membres = [p for p in photos if c["cle"]["fr"] in teintes(p["couleur"])]
        if len(membres) >= minimum:
            couleurs.append({**c, "photos": membres, "couverture": membres[0]})
    return couleurs


def photos_proches(photos, par_photo, nombre=8):
    """Pour chaque photo, celles qui partagent le plus de mots-clés avec elle. Un mot compte
    d'autant plus qu'il est rare (log du nombre de photos sur le nombre de photos qui le
    portent) ; les mots portés par plus d'une photo sur quatre sont ignorés. Chaque galerie
    en commun ajoute 2."""
    n = len(photos)
    index = {}
    for p in photos:
        for cle in p["cles"]:
            index.setdefault(cle, []).append(p["id"])
    poids = {cle: math.log(n / len(ids)) for cle, ids in index.items() if len(ids) <= n / 4}
    membres = {}
    for p in photos:
        for gal in par_photo[p["id"]]:
            membres.setdefault(gal["cle"], []).append(p["id"])
    par_id = {p["id"]: p for p in photos}
    proches = {}
    for p in photos:
        score = {}
        for cle in p["cles"]:
            for autre in index[cle] if cle in poids else ():
                score[autre] = score.get(autre, 0) + poids[cle]
        for gal in par_photo[p["id"]]:
            for autre in membres[gal["cle"]]:
                score[autre] = score.get(autre, 0) + 2
        score.pop(p["id"], None)
        meilleures = sorted(score, key=lambda i: (-score[i], -par_id[i]["vues"], -i))[:nombre]
        proches[p["id"]] = [par_id[i] for i in meilleures]
    return proches


def photos_ouverture(reglages, par_id, selection):
    """Photos qui défilent sur l'accueil : réglage « ouverture », sinon les premières
    photos en format paysage de la sélection."""
    choisies = [par_id[i] for i in nombres(reglages["accueil"].get("ouverture")) if i in par_id]
    if not choisies:
        choisies = [p for p in selection if en_largeur(p)][:6]
    return choisies[:8] or selection[:1]


# ---------------------------------------------------------------- adresses


class Adresses:
    def __init__(self, adresse):
        u = urlparse(adresse.strip().rstrip("/"))
        self.origine = f"{u.scheme}://{u.netloc}"
        self.base = u.path.rstrip("/")

    def chemin(self, langue, genre, cle=None):
        en = langue == "en"
        debut = self.base + ("/en" if en else "")
        chemins = {
            "accueil": "/",
            "galeries": "/galleries/" if en else "/galeries/",
            "galerie": f"/galleries/{cle}/" if en else f"/galeries/{cle}/",
            "couleur": f"/colors/{cle}/" if en else f"/couleurs/{cle}/",
            "series": "/series/",
            "serie": f"/series/{cle}/",
            "photo": f"/photo/{cle}/",
            "apropos": "/about/" if en else "/a-propos/",
            "utiliser": "/use-my-photos/" if en else "/utiliser-mes-photos/",
            "mentions": "/legal-notice/" if en else "/mentions-legales/",
            "confidentialite": "/privacy/" if en else "/confidentialite/",
            "flux": "/feed.xml" if en else "/flux.xml",
            "flux_galerie": f"/galleries/{cle}/feed.xml" if en else f"/galeries/{cle}/flux.xml",
            "flux_autres": "/more-photos/feed.xml" if en else "/autres-photos/flux.xml",
        }
        return debut + chemins[genre]

    def absolue(self, chemin):
        return self.origine + chemin

    def fichier(self, chemin):
        relatif = chemin[len(self.base):].lstrip("/")
        return SORTIE / (relatif + "index.html" if relatif.endswith("/") or not relatif else relatif)


# ---------------------------------------------------------------- morceaux de page


def url_image(photo, largeur):
    return f"{photo['image']}?auto=compress&cs=tinysrgb&w={largeur}"


def srcset(photo, largeurs):
    return ", ".join(f"{url_image(photo, l)} {l}w" for l in largeurs)


def nombre_photos(n, langue):
    return TEXTES[langue]["une_photo"] if n == 1 else TEXTES[langue]["n_photos"].format(n=n)


def carreau(photo, langue, adr, grand=False):
    ratio = photo["largeur"] / photo["hauteur"]
    largeurs, tailles = (((600, 900, 1300, 1800), "(max-width: 640px) 100vw, 50vw") if grand
                         else ((300, 600, 900, 1300), "(max-width: 640px) 60vw, 30vw"))
    return (
        f'<a class="carreau" href="{adr.chemin(langue, "photo", photo["id"])}" data-pexels="{e(photo["page"])}" '
        f'style="--r:{ratio:.3f};background-color:{e(photo["couleur"])}">'
        f'<img src="{url_image(photo, 900 if grand else 600)}" srcset="{srcset(photo, largeurs)}" '
        f'sizes="{tailles}" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(photo["titre"][langue])}" loading="lazy" decoding="async"></a>'
    )


def grille(photos, langue, adr, grand=False):
    """Grille justifiée de vignettes ; « grand » : photos plus grandes et plus espacées
    (séries)."""
    return (f'<div class="grille{" grandes" if grand else ""}">'
            + "".join(carreau(p, langue, adr, grand) for p in photos) + "</div>")


def carte(lien, photo, titre, infos):
    """Carte d'une galerie ou d'une série : photo de couverture, titre et précisions."""
    return (
        f'<a class="galerie" href="{lien}">'
        f'<span class="galerie-image" style="background-color:{e(photo["couleur"])}">'
        f'<img src="{url_image(photo, 800)}" srcset="{srcset(photo, (400, 800, 1200))}" '
        f'sizes="(max-width: 640px) 92vw, 30vw" alt="" loading="lazy" decoding="async"></span>'
        f'<span class="galerie-titre">{e(titre)}</span>'
        f'<span class="galerie-nombre">{e(infos)}</span></a>'
    )


def carte_galerie(galerie, langue, adr):
    return carte(adr.chemin(langue, "galerie", galerie["cle"]), galerie["couverture"],
                 galerie["titre"][langue], nombre_photos(len(galerie["photos"]), langue))


def infos_serie(serie, langue):
    morceaux = (serie["lieu"][langue], serie["date"][langue], nombre_photos(len(serie["photos"]), langue))
    return " · ".join(m for m in morceaux if m)


def carte_serie(serie, langue, adr):
    return carte(adr.chemin(langue, "serie", serie["cle"]), serie["couverture"],
                 serie["titre"][langue], infos_serie(serie, langue))


def cartes(galeries, langue, adr, genre):
    choisies = [g for g in galeries if g["type"] == genre]
    if not choisies:
        return ""
    titre = TEXTES[langue]["themes" if genre == "theme" else "lieux"]
    return (
        f'<section class="bloc"><h2 class="surtitre">{titre}</h2><div class="galeries">'
        + "".join(carte_galerie(g, langue, adr) for g in choisies)
        + "</div></section>"
    )


def cartes_series(series, langue, adr, titre=None, sauf=None):
    choisies = [s for s in series if s is not sauf]
    if not choisies:
        return ""
    return (
        f'<section class="bloc"><h2 class="surtitre">{titre or TEXTES[langue]["series"]}</h2><div class="galeries">'
        + "".join(carte_serie(s, langue, adr) for s in choisies)
        + "</div></section>"
    )


def preuve_sociale(preuve, langue):
    """« 878 500 vues et 3 950 téléchargements sur Pexels », d'après les relevés."""
    t = TEXTES[langue]
    if preuve["vues"] and preuve["telechargements"]:
        return t["preuve"].format(vues=chiffre(preuve["vues"], langue),
                                  telechargements=chiffre(preuve["telechargements"], langue))
    if preuve["vues"]:
        return t["preuve_vues"].format(vues=chiffre(preuve["vues"], langue))
    return ""


def rappel(g, langue):
    """Rappel « Suivre sur Pexels » en fin de galerie, de série et de page."""
    t = TEXTES[langue]
    preuve = preuve_sociale(g.preuve, langue)
    return (
        f'<aside class="rappel"><p>{t["rappel"]}</p>'
        f'<p><a class="bouton" href="{e(g.site.get("profil_pexels", ""))}" '
        f'data-goatcounter-click="suivre-pexels-fin">{t["suivre"]}</a></p>'
        + (f'<p class="preuve">{e(preuve)}</p>' if preuve else "")
        + "</aside>"
    )


def jsonld(donnees):
    texte = json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{texte}</script>'


def fil_ariane(adr, langue, parents, courante):
    """Fil d'Ariane : liens vers l'accueil et les pages parentes (« parents » : liste de
    (nom, chemin)), et données structurées BreadcrumbList, page courante comprise."""
    t = TEXTES[langue]
    etapes = [(t["accueil_court"], adr.chemin(langue, "accueil"))] + parents
    visible = (
        f'<nav class="ariane" aria-label="{t["ariane"]}"><ol>'
        + "".join(f'<li><a href="{chemin}">{e(nom)}</a></li>' for nom, chemin in etapes)
        + "</ol></nav>"
    )
    donnees = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": rang, "name": nom, "item": adr.absolue(chemin)}
            for rang, (nom, chemin) in enumerate(etapes + [courante], 1)
        ],
    }
    return visible, donnees


def pastilles(couleurs, galeries, langue, adr, courante=None):
    """Liens vers les pages de couleur, chacun avec sa pastille ; le noir et blanc mène à
    sa galerie."""
    t = TEXTES[langue]
    liens = [(adr.chemin(langue, "couleur", c["cle"][langue]), c["nom"][langue], f'background:{c["pastille"]}',
              len(c["photos"]), c is courante) for c in couleurs]
    noir_et_blanc = next((gal for gal in galeries if gal["cle"] == "noir-et-blanc"), None)
    if noir_et_blanc:
        liens.append((adr.chemin(langue, "galerie", noir_et_blanc["cle"]), noir_et_blanc["titre"][langue],
                      "background:linear-gradient(135deg,#161616 50%,#f2f2f2 50%)", len(noir_et_blanc["photos"]), False))
    if not liens:
        return ""
    return (
        f'<section class="bloc"><h2 class="surtitre">{t["couleurs"]}</h2><ul class="couleurs">'
        + "".join(
            f'<li><a href="{lien}"' + (' aria-current="page"' if actuelle else "") + '>'
            f'<span class="pastille" style="{style}"></span>{e(nom)} <span class="compte">{n}</span></a></li>'
            for lien, nom, style, n, actuelle in liens
        )
        + "</ul></section>"
    )


ICONES = {
    "precedente": '<path d="M15 4.5 7.5 12l7.5 7.5"/>',
    "suivante": '<path d="M9 4.5 16.5 12 9 19.5"/>',
    "fermer": '<path d="M5.5 5.5l13 13M18.5 5.5l-13 13"/>',
}


def icone(nom):
    return (
        '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" fill="none" '
        f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round">{ICONES[nom]}</svg>'
    )


class Gabarit:
    """Enveloppe commune à toutes les pages."""

    def __init__(self, reglages, adr, preuve):
        self.reglages = reglages
        self.site = reglages["site"]
        self.adr = adr
        self.preuve = preuve
        empreinte = hashlib.md5()
        for nom in ("style.css", "site.js"):
            empreinte.update((ICI / "statique" / nom).read_bytes())
        self.version = empreinte.hexdigest()[:8]

    def statique(self, nom):
        return f"{self.adr.base}/statique/{nom}"

    def visionneuse(self, langue):
        """Visionneuse plein écran, remplie par statique/site.js au clic sur une vignette."""
        t = TEXTES[langue]
        return (
            f'<dialog class="visionneuse" aria-label="{t["visionneuse"]}">'
            f'<div class="v-cadre"><a class="v-image" href="{e(self.site.get("profil_pexels", ""))}" '
            f'title="{t["voir_pexels"]}" data-goatcounter-click="pexels-image">'
            '<img class="v-apercu" alt=""><img class="v-grande" alt=""></a></div>'
            '<div class="v-barre"><p class="v-titre"><a href=""></a></p>'
            f'<p><a class="bouton v-pexels" href="{e(self.site.get("profil_pexels", ""))}" '
            f'data-goatcounter-click="pexels">{t["telecharger"]}</a></p></div>'
            '<p class="v-rang" aria-live="polite"></p>'
            f'<button type="button" class="v-bouton v-precedente" aria-label="{t["precedente"]}">{icone("precedente")}</button>'
            f'<button type="button" class="v-bouton v-suivante" aria-label="{t["suivante"]}">{icone("suivante")}</button>'
            f'<button type="button" class="v-bouton v-fermer" aria-label="{t["fermer"]}">{icone("fermer")}</button>'
            "</dialog>"
        )

    def page(self, langue, *, titre, description, chemins, contenu, image=None, donnees=None,
             flux=None, classe="", titre_complet=False, series=True):
        t = TEXTES[langue]
        autre = "en" if langue == "fr" else "fr"
        adr = self.adr
        nom = self.site.get("nom", "Karl Forterre")
        titre_page = titre if titre_complet else f"{titre} — {nom}"
        url = adr.absolue(chemins[langue])
        profil = e(self.site.get("profil_pexels", ""))
        tete = [
            f'<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{e(titre_page)}</title>",
            f'<meta name="description" content="{e(tronquer(description))}">',
            f'<link rel="canonical" href="{url}">',
            f'<link rel="alternate" hreflang="fr" href="{adr.absolue(chemins["fr"])}">',
            f'<link rel="alternate" hreflang="en" href="{adr.absolue(chemins["en"])}">',
            f'<link rel="alternate" hreflang="x-default" href="{adr.absolue(chemins["fr"])}">',
            f'<meta property="og:site_name" content="{e(nom)}">',
            f'<meta property="og:type" content="website">',
            f'<meta property="og:locale" content="{t["locale"]}">',
            f'<meta property="og:title" content="{e(titre)}">',
            f'<meta property="og:description" content="{e(tronquer(description))}">',
            f'<meta property="og:url" content="{url}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<link rel="preload" href="{self.statique("archivo.woff2")}" as="font" type="font/woff2" crossorigin>',
            f'<link rel="stylesheet" href="{self.statique("style.css")}?v={self.version}">',
            f'<script src="{self.statique("site.js")}?v={self.version}" defer></script>',
            f'<link rel="icon" href="{self.statique("favicon.svg")}" type="image/svg+xml">',
            f'<link rel="apple-touch-icon" href="{self.statique("icone-180.png")}">',
            f'<link rel="alternate" type="application/rss+xml" title="{e(t["flux"])}" '
            f'href="{flux or adr.chemin(langue, "flux")}">',
        ]
        if image:
            tete += [
                f'<meta property="og:image" content="{url_image(image, 1200)}">',
                f'<meta property="og:image:alt" content="{e(image["titre"][langue])}">',
            ]
        if self.site.get("google_verification", "").strip():
            tete.append(f'<meta name="google-site-verification" content="{e(self.site["google_verification"].strip())}">')
        if self.site.get("pinterest_verification", "").strip():
            tete.append(f'<meta name="p:domain_verify" content="{e(self.site["pinterest_verification"].strip())}">')
        code = self.site.get("goatcounter", "").strip()
        if code:
            tete.append(f'<script data-goatcounter="https://{e(code)}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>')
        for bloc in donnees or []:
            tete.append(jsonld(bloc))

        def lien_menu(genre, texte):
            chemin = adr.chemin(langue, genre)
            courant = ' aria-current="page"' if chemin == chemins[langue] else ""
            return f'<a href="{chemin}"{courant}>{texte}</a>'

        entete = (
            f'<a class="evitement" href="#contenu">{t["evitement"]}</a>'
            f'<header class="entete"><a class="marque" href="{adr.chemin(langue, "accueil")}">'
            f'<span class="logo" aria-hidden="true"></span>{e(nom)}</a>'
            f'<nav class="menu" aria-label="{t["menu"]}">'
            + (lien_menu("series", t["series"]) if series else "")
            + lien_menu("galeries", t["galeries"])
            + lien_menu("apropos", t["a_propos"])
            + f'<a href="{chemins[autre]}" hreflang="{autre}" lang="{autre}">{TEXTES[langue]["autre_langue"]}</a>'
            f'<a class="suivre" href="{profil}" data-goatcounter-click="suivre-pexels">{t["suivre"]}</a>'
            f"</nav></header>"
        )
        annee = datetime.now(timezone.utc).year
        pied = (
            '<footer class="pied">'
            '<p><a href="https://www.pexels.com">Photos provided by Pexels</a></p>'
            f'<p><a href="{adr.chemin(langue, "utiliser")}">{t["utiliser"]}</a>'
            f' · <a href="{adr.chemin(langue, "mentions")}">{t["mentions"]}</a>'
            f' · <a href="{adr.chemin(langue, "confidentialite")}">{t["confidentialite"]}</a></p>'
            f'<p>© {annee} {e(nom)} · <a href="{profil}">{t["profil"]}</a>'
            f' · <a href="{e(self.site.get("site_personnel", ""))}">{e(urlparse(self.site.get("site_personnel", "")).netloc)}</a>'
            f' · <a href="{adr.chemin(langue, "flux")}">{t["flux"]}</a></p>'
            "</footer>"
        )
        visionneuse = self.visionneuse(langue) if 'class="grille' in contenu else ""
        return (
            f'<!doctype html>\n<html lang="{langue}"><head>' + "".join(tete) + "</head>"
            f'<body class="{classe}">{entete}<main id="contenu">{contenu}</main>{pied}{visionneuse}</body></html>\n'
        )


# ---------------------------------------------------------------- pages


def ecrire(chemin, texte):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")


def url_recadree(photo, largeur, hauteur):
    return f"{photo['image']}?auto=compress&cs=tinysrgb&fit=crop&w={largeur}&h={hauteur}"


def diapo(photo, langue, adr, premiere, bandeau=False):
    """Une photo de l'accueil plein écran, ou du bandeau d'une série ou d'une galerie.
    Sur un écran en hauteur, Pexels fournit directement l'image recadrée, bien plus
    légère que l'image entière."""
    hauteur = 4 / 3 if bandeau else 1.75
    portrait = ", ".join(f"{url_recadree(photo, l, round(l * hauteur))} {l}w" for l in (600, 900, 1200))
    ratio = photo["largeur"] / photo["hauteur"]
    priorite = ' fetchpriority="high"' if premiere else ""
    tailles = ("100vw", "100vw") if bandeau else (
        "(max-aspect-ratio: 4/7) 57vh, 100vw",
        f'(max-aspect-ratio: {photo["largeur"]}/{photo["hauteur"]}) {ratio * 100:.0f}vh, 100vw',
    )
    return (
        f'<figure class="diapo{" visible" if premiere else ""}" style="background-color:{e(photo["couleur"])}">'
        f'<picture><source media="(max-aspect-ratio: 4/5)" srcset="{portrait}" sizes="{tailles[0]}">'
        f'<img src="{url_image(photo, 1600)}" srcset="{srcset(photo, (1200, 1600, 2200, 3000))}" '
        f'sizes="{tailles[1]}" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(photo["titre"][langue])}"{priorite}>'
        f'</picture><figcaption><a href="{adr.chemin(langue, "photo", photo["id"])}">'
        f'{e(photo["titre"][langue])}</a></figcaption></figure>'
    )


def bandeau(g, photo, langue, titre, accroche="", surtitre="", plein_ecran=False, centre=False):
    """En-tête d'une série ou d'une galerie : une grande photo derrière le titre.
    « accroche » et « surtitre » (le fil d'Ariane) sont du HTML déjà échappé.
    « plein_ecran » : ouverture sur tout l'écran, titre au centre (séries)."""
    classes = "plein centre" if plein_ecran else "plein bandeau" + (" centre" if centre else "")
    return (
        f'<section class="{classes}"><div class="defile">'
        f'{diapo(photo, langue, g.adr, True, bandeau=not plein_ecran)}</div>'
        f'<div class="plein-texte">{surtitre}<h1>{e(titre)}</h1>'
        + (f'<p class="accroche">{accroche}</p>' if accroche else "")
        + "</div></section>"
    )


def bandeau_index(elements):
    """Photo du bandeau d'une page d'index : le premier bandeau en largeur."""
    return next((x["bandeau"] for x in elements if en_largeur(x["bandeau"])), elements[0]["bandeau"])


def ouverture_accueil(g, photos, langue):
    """Ouverture plein écran : fondu lent entre quelques photos, nom, accroche,
    bouton « Voir les galeries » et « Suivre sur Pexels » avec la preuve sociale."""
    adr = g.adr
    t = TEXTES[langue]
    accroche = g.reglages["accueil"].get(f"accroche_{langue}", "")
    if not photos:
        return f'<section class="ouverture"><h1>{t["accueil"]}</h1><p class="accroche">{e(accroche)}</p></section>'
    preuve = preuve_sociale(g.preuve, langue)
    diapos = diapo(photos[0], langue, adr, True) + "".join(
        f"<template>{diapo(p, langue, adr, False)}</template>" for p in photos[1:]
    )
    return (
        f'<section class="plein"><div class="defile">{diapos}</div>'
        f'<div class="plein-texte"><h1>{t["accueil"]}</h1><p class="accroche">{e(accroche)}</p>'
        f'<p class="actions"><a class="bouton" href="{adr.chemin(langue, "galeries")}">{t["voir_galeries"]}</a>'
        f'<a class="bouton bouton-contour" href="{e(g.site.get("profil_pexels", ""))}" '
        f'data-goatcounter-click="suivre-pexels-accueil">{t["suivre"]}</a></p>'
        + (f'<p class="preuve">{e(preuve)}</p>' if preuve else "")
        + "</div></section>"
    )


def page_accueil(g, photos, galeries, series, selection, ouverture, langue):
    adr = g.adr
    t = TEXTES[langue]
    accroche = g.reglages["accueil"].get(f"accroche_{langue}", "")
    contenu = (
        ouverture_accueil(g, ouverture, langue)
        + '<div class="enveloppe">'
        + (f'<section class="bloc" id="selection"><h2 class="surtitre">{t["selection"]}</h2>'
           f"{grille(selection, langue, adr)}</section>" if selection else "")
        + cartes_series(series, langue, adr)
        + cartes(galeries, langue, adr, "theme")
        + cartes(galeries, langue, adr, "lieu")
        + f'<section class="bloc"><h2 class="surtitre">{t["recentes"]}</h2>{grille(photos[:12], langue, adr)}</section>'
        + "</div>"
    )
    nom = g.site.get("nom", "Karl Forterre")
    donnees = [{
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": nom,
        "url": adr.absolue(adr.chemin(langue, "accueil")),
        "inLanguage": langue,
        "author": {"@type": "Person", "name": nom,
                   "sameAs": [g.site.get("profil_pexels", ""), g.site.get("site_personnel", "")]},
    }]
    chemins = {l: adr.chemin(l, "accueil") for l in ("fr", "en")}
    texte = g.page(langue, titre=f'{t["accueil"]}', description=accroche, chemins=chemins, contenu=contenu,
                   image=(ouverture or photos or [None])[0], donnees=donnees,
                   classe="accueil sur-photo" if ouverture else "accueil",
                   titre_complet=True, series=bool(series))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galeries(g, galeries, series, couleurs, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "galeries") for l in ("fr", "en")}
    ariane, donnees_ariane = fil_ariane(adr, langue, [], (t["galeries"], chemins[langue]))
    suite = (cartes(galeries, langue, adr, "theme") + cartes(galeries, langue, adr, "lieu")
             + pastilles(couleurs, galeries, langue, adr))
    if galeries:
        contenu = (bandeau(g, bandeau_index(galeries), langue, t["galeries"], e(t["galeries_intro"]), ariane)
                   + f'<div class="enveloppe">{suite}</div>')
    else:
        contenu = f'<section class="ouverture">{ariane}<h1>{t["galeries"]}</h1></section>' + suite
    description = " · ".join(gal["titre"][langue] for gal in galeries)
    texte = g.page(langue, titre=t["galeries"], description=description, chemins=chemins, contenu=contenu,
                   image=galeries[0]["couverture"] if galeries else None, donnees=[donnees_ariane],
                   series=bool(series), classe="sur-photo" if galeries else "")
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galerie(g, galerie, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "galerie", galerie["cle"]) for l in ("fr", "en")}
    flux = adr.chemin(langue, "flux_galerie", galerie["cle"])
    description = galerie["description"][langue] or galerie["titre"][langue]
    ariane, donnees_ariane = fil_ariane(adr, langue, [(t["galeries"], adr.chemin(langue, "galeries"))],
                                        (galerie["titre"][langue], chemins[langue]))
    texte_galerie = galerie["texte"][langue]
    accroche = f'{e(description)} <span class="nombre">{nombre_photos(len(galerie["photos"]), langue)}</span>'
    contenu = (
        bandeau(g, galerie["bandeau"], langue, galerie["titre"][langue], accroche, ariane)
        + '<div class="enveloppe">'
        + grille(galerie["photos"], langue, adr)
        + (f'<section class="texte galerie-texte"><h2 class="surtitre">{t["a_propos_galerie"]}</h2>'
           + "".join(f"<p>{e(para)}</p>" for para in texte_galerie) + "</section>" if texte_galerie else "")
        + f'<p class="flux-lien"><a href="{flux}">{t["flux_galerie"]}</a></p>'
        + rappel(g, langue)
        + "</div>"
    )
    donnees = [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": galerie["titre"][langue],
        "description": description,
        "url": adr.absolue(chemins[langue]),
        "inLanguage": langue,
    }, donnees_ariane]
    texte = g.page(langue, titre=galerie["titre"][langue], description=description, chemins=chemins,
                   contenu=contenu, image=galerie["couverture"], donnees=donnees, flux=flux, series=bool(series),
                   classe="sur-photo")
    ecrire(adr.fichier(chemins[langue]), texte)


def page_couleur(g, couleur, couleurs, galeries, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "couleur", couleur["cle"][l]) for l in ("fr", "en")}
    titre = couleur["titre"][langue]
    description = t["couleur_description"].format(titre=titre)
    ariane, donnees_ariane = fil_ariane(adr, langue, [(t["galeries"], adr.chemin(langue, "galeries"))],
                                        (titre, chemins[langue]))
    contenu = (
        f'<header class="ouverture">{ariane}<h1>{e(titre)}</h1>'
        f'<p class="accroche">{e(description)} <span class="nombre">{nombre_photos(len(couleur["photos"]), langue)}</span></p>'
        f"</header>"
        + grille(couleur["photos"], langue, adr)
        + pastilles(couleurs, galeries, langue, adr, courante=couleur)
        + rappel(g, langue)
    )
    donnees = [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": titre,
        "description": description,
        "url": adr.absolue(chemins[langue]),
        "inLanguage": langue,
    }, donnees_ariane]
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=couleur["couverture"], donnees=donnees, series=bool(series))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_series(g, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "series") for l in ("fr", "en")}
    ariane, donnees_ariane = fil_ariane(adr, langue, [], (t["series"], chemins[langue]))
    contenu = (
        bandeau(g, bandeau_index(series), langue, t["series"], e(t["series_intro"]), ariane, centre=True)
        + '<div class="enveloppe"><div class="galeries">' + "".join(carte_serie(s, langue, adr) for s in series)
        + "</div>" + rappel(g, langue) + "</div>"
    )
    texte = g.page(langue, titre=t["series"], description=t["series_intro"], chemins=chemins, contenu=contenu,
                   image=series[0]["couverture"], donnees=[donnees_ariane], classe="sur-photo")
    ecrire(adr.fichier(chemins[langue]), texte)


def page_serie(g, serie, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "serie", serie["cle"]) for l in ("fr", "en")}
    titre = serie["titre"][langue]
    texte_serie = serie["texte"][langue]
    description = texte_serie[0] if texte_serie else titre
    ariane, donnees_ariane = fil_ariane(adr, langue, [(t["series"], adr.chemin(langue, "series"))], (titre, chemins[langue]))
    contenu = (
        bandeau(g, serie["bandeau"], langue, titre, e(infos_serie(serie, langue)), ariane, plein_ecran=True)
        + '<div class="enveloppe">'
        + (f'<div class="texte serie-texte"><p class="chapeau">{e(texte_serie[0])}</p>'
           + "".join(f"<p>{e(p)}</p>" for p in texte_serie[1:]) + "</div>" if texte_serie else "")
        + grille(serie["photos"], langue, adr, grand=True)
        + rappel(g, langue)
        + cartes_series(series, langue, adr, titre=t["autres_series"], sauf=serie)
        + "</div>"
    )
    nom = g.site.get("nom", "Karl Forterre")
    donnees = [{
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": titre,
        "description": tronquer(description, 300),
        "url": adr.absolue(chemins[langue]),
        "inLanguage": langue,
        "image": url_image(serie["couverture"], 1200),
        "author": {"@type": "Person", "name": nom, "url": g.site.get("profil_pexels", "")},
        **({"contentLocation": {"@type": "Place", "name": serie["lieu"][langue]}} if serie["lieu"][langue] else {}),
    }, donnees_ariane]
    texte = g.page(langue, titre=t["titre_serie"].format(titre=titre), description=description, chemins=chemins,
                   contenu=contenu, image=serie["couverture"], donnees=donnees, classe="sur-photo recit")
    ecrire(adr.fichier(chemins[langue]), texte)


def page_photo(g, photo, langue, precedente, suivante, galeries_photo, series_photo, avec_series, proches,
               couleurs_photo):
    adr = g.adr
    t = TEXTES[langue]
    titre = photo["titre"][langue]
    description = f"{titre}. {t['suffixe']}"
    chemins = {l: adr.chemin(l, "photo", photo["id"]) for l in ("fr", "en")}
    ratio = photo["largeur"] / photo["hauteur"]
    mots = photo["mots"][langue]
    langue_mots = photo["langue_mots"][langue]
    liste = (
        f'<ul class="mots" aria-label="{t["mots"]}"' + (f' lang="{langue_mots}"' if langue_mots != langue else "")
        + ">" + "".join(f"<li>{e(m)}</li>" for m in mots) + "</ul>"
        if mots else ""
    )
    dans = ""
    if series_photo:
        liens = ", ".join(
            f'<a href="{adr.chemin(langue, "serie", s["cle"])}">{e(s["titre"][langue])}</a>' for s in series_photo
        )
        dans += f'<p class="dans">{t["dans_serie"]} {liens}</p>'
    if galeries_photo:
        liens = ", ".join(
            f'<a href="{adr.chemin(langue, "galerie", gal["cle"])}">{e(gal["titre"][langue])}</a>' for gal in galeries_photo
        )
        dans += f'<p class="dans">{t["dans"]} {liens}</p>'
    if couleurs_photo:
        liens = ", ".join(
            f'<a href="{adr.chemin(langue, "couleur", c["cle"][langue])}">{e(c["nom"][langue])}</a>' for c in couleurs_photo
        )
        dans += f'<p class="dans">{t["couleurs_photo"]} {liens}</p>'
    suite = '<nav class="suite">'
    if precedente:
        suite += f'<a rel="prev" href="{adr.chemin(langue, "photo", precedente["id"])}">← {t["precedente"]}</a>'
    if suivante:
        suite += f'<a rel="next" href="{adr.chemin(langue, "photo", suivante["id"])}">{t["suivante"]} →</a>'
    suite += "</nav>"
    voisines = (
        f'<section class="bloc"><h2 class="surtitre">{t["proches"]}</h2>{grille(proches, langue, adr)}</section>'
        if proches else ""
    )
    # Fil d'Ariane : la galerie de lieu de la photo, sinon sa première galerie.
    parente = next((gal for gal in galeries_photo if gal["type"] == "lieu"), (galeries_photo or [None])[0])
    parents = [(t["galeries"], adr.chemin(langue, "galeries")),
               (parente["titre"][langue], adr.chemin(langue, "galerie", parente["cle"]))] if parente else []
    ariane, donnees_ariane = fil_ariane(adr, langue, parents, (titre, chemins[langue]))
    licence = f'<a href="{adr.chemin(langue, "utiliser")}">{t["licence"]}</a>'
    contenu = (
        f'<article class="photo"><figure class="cliche" style="--r:{ratio:.3f}">'
        f'<a href="{e(photo["page"])}" title="{t["voir_pexels"]}" data-goatcounter-click="pexels-image-{photo["id"]}">'
        f'<img src="{url_image(photo, 1600)}" srcset="{srcset(photo, (800, 1200, 1600, 2200, 3000))}" '
        f'sizes="(max-width: 1440px) 100vw, 1440px" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(titre)}" fetchpriority="high" style="background-color:{e(photo["couleur"])}"></a></figure>'
        f'<div class="legende">{ariane}<h1>{e(titre)}</h1>'
        f'<p><a class="bouton" href="{e(photo["page"])}" data-goatcounter-click="pexels-{photo["id"]}" '
        f'data-goatcounter-title="{e(titre)}">{t["telecharger"]}</a></p>'
        f'<p class="credit">{t["credit"].format(licence=licence)} '
        f'<span class="numero">{t["numero"].format(id=photo["id"])}</span></p>'
        f"{liste}{dans}</div>{suite}</article>{voisines}"
    )
    nom = g.site.get("nom", "Karl Forterre")
    donnees = [{
        "@context": "https://schema.org",
        "@type": "ImageObject",
        "name": titre,
        "description": description,
        "url": adr.absolue(chemins[langue]),
        "contentUrl": photo["image"],
        "thumbnailUrl": url_image(photo, 800),
        "width": photo["largeur"],
        "height": photo["hauteur"],
        "encodingFormat": "image/jpeg",
        "inLanguage": langue,
        "creator": {"@type": "Person", "name": nom, "url": g.site.get("profil_pexels", "")},
        "creditText": f"{nom} / Pexels",
        "copyrightNotice": nom,
        "license": LICENCE,
        "acquireLicensePage": photo["page"],
        **({"keywords": ", ".join(mots)} if mots else {}),
    }, donnees_ariane]
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=photo, donnees=donnees, classe="page-photo", series=avec_series)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_texte(g, langue, genre, titre, description, corps, avec_series, image=None):
    """Page de texte simple (À propos, Utiliser mes photos, pages légales)."""
    adr = g.adr
    chemins = {l: adr.chemin(l, genre) for l in ("fr", "en")}
    ariane, donnees_ariane = fil_ariane(adr, langue, [], (titre, chemins[langue]))
    contenu = f'<section class="ouverture texte">{ariane}<h1>{e(titre)}</h1>{corps}</section>'
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=image, donnees=[donnees_ariane], series=avec_series)
    ecrire(adr.fichier(chemins[langue]), texte)


def courriel(g):
    adresse = g.reglages["mentions"].get("contact", "").strip() if g.reglages.has_section("mentions") else ""
    return f'<a href="mailto:{e(adresse)}">{e(adresse)}</a>' if adresse else ""


def page_a_propos(g, par_id, galeries, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    reglage = g.reglages["a-propos"]
    textes = paragraphes(reglage.get(f"texte_{langue}", ""))
    corps = "".join(f"<p>{e(p)}</p>" for p in textes)
    portrait = next((par_id[i] for i in nombres(reglage.get("portrait")) if i in par_id), None)
    materiel = paragraphes(reglage.get(f"materiel_{langue}", ""))
    if materiel:
        corps += f'<h2>{t["materiel"]}</h2>' + "".join(f"<p>{e(p)}</p>" for p in materiel)
    liens_series = [f'<a href="{adr.chemin(langue, "serie", s["cle"])}">{e(s["titre"][langue])}</a>' for s in series]
    if liens_series:
        corps += f'<h2>{t["series"]}</h2><p>' + " · ".join(liens_series) + "</p>"
    lieux = [f'<a href="{adr.chemin(langue, "galerie", gal["cle"])}">{e(gal["titre"][langue])}</a>'
             for gal in galeries if gal["type"] == "lieu"]
    if lieux:
        corps += f'<h2>{t["lieux_photographies"]}</h2><p>' + " · ".join(lieux) + "</p>"
    contact = courriel(g)
    corps += (
        f'<h2>{t["contact"]}</h2><ul class="liens">'
        + (f"<li>{contact}</li>" if contact else "")
        + f'<li><a href="{e(g.site.get("profil_pexels", ""))}">{t["profil"]}</a></li>'
        f'<li><a href="{e(g.site.get("site_personnel", ""))}">{e(urlparse(g.site.get("site_personnel", "")).netloc)}</a></li></ul>'
    )
    if portrait:
        corps = (f'<figure class="portrait"><img src="{url_image(portrait, 800)}" '
                 f'srcset="{srcset(portrait, (400, 800, 1200))}" sizes="(max-width: 640px) 92vw, 420px" '
                 f'width="{portrait["largeur"]}" height="{portrait["hauteur"]}" alt="{e(portrait["titre"][langue])}"></figure>'
                 + corps)
    page_texte(g, langue, "apropos", t["a_propos"], textes[0] if textes else t["a_propos"],
               corps + rappel(g, langue), bool(series), image=portrait)


LICENCE_PEXELS = {
    "fr": {
        "intro": "Toutes les photos de ce site sont publiées sur Pexels. Elles se téléchargent gratuitement, "
                 "sans inscription, et s'utilisent librement, y compris pour un usage commercial.",
        "etapes_titre": "Télécharger une photo",
        "etapes": [
            "Ouvrez la page de la photo sur ce site.",
            "Cliquez sur « Télécharger gratuitement sur Pexels ».",
            "Sur Pexels, cliquez sur le bouton de téléchargement gratuit et choisissez, si besoin, la taille : "
            "l'original en pleine définition ou une version plus légère.",
        ],
        "permis_titre": "Ce que la licence Pexels permet",
        "permis": [
            "Utiliser les photos gratuitement, pour un usage personnel ou commercial.",
            "Les modifier : recadrer, retoucher, ajouter du texte.",
            "Les publier sur un site, un blog, une application, une boutique en ligne, une lettre "
            "d'information ou dans une présentation.",
            "Les utiliser dans une publicité ou une campagne de communication.",
            "Les imprimer sur des flyers, des cartes postales, des livres ou des magazines.",
            "Les partager sur les réseaux sociaux.",
        ],
        "interdit_titre": "Ce qu'elle ne permet pas",
        "interdit": [
            "Montrer une personne reconnaissable sous un jour dégradant ou offensant.",
            "Vendre une photo telle quelle, sans l'avoir modifiée, par exemple en poster, en tirage ou sur un objet.",
            "Laisser croire qu'une personne ou une marque visible sur la photo recommande votre produit.",
            "Diffuser ou revendre les photos sur une autre banque d'images ou un site de fonds d'écran.",
            "Utiliser une photo comme marque, logo ou nom commercial.",
        ],
        "credit_titre": "Créditer l'auteur",
        "credit": "Ce n'est pas obligatoire, mais toujours apprécié : « Photo : Karl Forterre / Pexels », "
                  "avec si possible un lien vers la page de la photo.",
        "officiel": "Seul le {lien} fait foi.",
        "officiel_lien": "texte officiel de la licence Pexels",
        "contact": "Pour un tirage, une commande ou une autre utilisation, écrivez à {courriel}.",
    },
    "en": {
        "intro": "All the photos on this site are published on Pexels. They can be downloaded for free, "
                 "without an account, and used freely, including for commercial purposes.",
        "etapes_titre": "Downloading a photo",
        "etapes": [
            "Open the photo's page on this site.",
            "Click “Free download on Pexels”.",
            "On Pexels, click the free download button and, if needed, choose the size: "
            "the full-resolution original or a lighter version.",
        ],
        "permis_titre": "What the Pexels license allows",
        "permis": [
            "Using the photos for free, for personal or commercial purposes.",
            "Modifying them: cropping, editing, adding text.",
            "Publishing them on a website, a blog, an app, an online shop, a newsletter or in a presentation.",
            "Using them in advertising or a marketing campaign.",
            "Printing them on flyers, postcards, books or magazines.",
            "Sharing them on social media.",
        ],
        "interdit_titre": "What it does not allow",
        "interdit": [
            "Showing an identifiable person in a bad light or in an offensive way.",
            "Selling an unaltered copy of a photo, for example as a poster, a print or on a product.",
            "Implying that a person or brand shown in the photo endorses your product.",
            "Redistributing or selling the photos on another stock photo or wallpaper platform.",
            "Using a photo as a trademark, logo or business name.",
        ],
        "credit_titre": "Crediting the photographer",
        "credit": "It is not required, but always appreciated: “Photo: Karl Forterre / Pexels”, "
                  "ideally with a link to the photo's page.",
        "officiel": "Only the {lien} is legally binding.",
        "officiel_lien": "official text of the Pexels license",
        "contact": "For a print, a commission or any other use, write to {courriel}.",
    },
}


def page_utiliser(g, series, langue):
    t = TEXTES[langue]
    x = LICENCE_PEXELS[langue]

    def puces(elements, balise="ul"):
        return f"<{balise}>" + "".join(f"<li>{e(el)}</li>" for el in elements) + f"</{balise}>"

    contact = courriel(g)
    officiel = x["officiel"].format(lien=f'<a href="{LICENCE}">{x["officiel_lien"]}</a>')
    corps = (
        f'<p class="accroche">{e(x["intro"])}</p>'
        f'<h2>{x["etapes_titre"]}</h2>{puces(x["etapes"], "ol")}'
        f'<h2>{x["permis_titre"]}</h2>{puces(x["permis"])}'
        f'<h2>{x["interdit_titre"]}</h2>{puces(x["interdit"])}'
        f'<h2>{x["credit_titre"]}</h2><p>{e(x["credit"])}</p>'
        f"<p>{officiel}"
        + (f' {x["contact"].format(courriel=contact)}' if contact else "")
        + "</p>" + rappel(g, langue)
    )
    page_texte(g, langue, "utiliser", t["utiliser"], x["intro"], corps, bool(series))


def page_mentions(g, series, langue):
    t = TEXTES[langue]
    adr = g.adr
    m = g.reglages["mentions"] if g.reglages.has_section("mentions") else {}
    editeur = (m.get("editeur") or g.site.get("nom", "Karl Forterre")).strip()
    lignes = [e(editeur)]
    for champ in ("adresse_postale", "telephone"):
        if (m.get(champ) or "").strip():
            lignes.append(e(m[champ].strip()))
    if (m.get("siret") or "").strip():
        lignes.append(f"SIRET : {e(m['siret'].strip())}" if langue == "fr" else f"SIRET number: {e(m['siret'].strip())}")
    contact = courriel(g)
    if contact:
        lignes.append(f"{t['contact']} : {contact}" if langue == "fr" else f"{t['contact']}: {contact}")
    utiliser = f'<a href="{adr.chemin(langue, "utiliser")}">{t["utiliser"]}</a>'
    confidentialite = f'<a href="{adr.chemin(langue, "confidentialite")}">{t["confidentialite"]}</a>'
    telephone = f"Téléphone : {HEBERGEUR_TELEPHONE}" if langue == "fr" else f"Phone: {HEBERGEUR_TELEPHONE}"
    hebergeur = (
        f"<p>{HEBERGEUR} (GitHub Pages)<br>{HEBERGEUR_ADRESSE[langue]}<br>{telephone}<br>"
        '<a href="https://github.com">github.com</a></p>'
    )
    if langue == "fr":
        corps = (
            f"<h2>Éditeur</h2><p>{'<br>'.join(lignes)}</p>"
            f"<p>Directeur de la publication : {e(editeur)}.</p>"
            f"<h2>Hébergement</h2>{hebergeur}"
            "<h2>Photos et contenus</h2>"
            f"<p>Les photos sont l'œuvre de {e(editeur)}. Elles sont publiées sur Pexels, qui fournit les images "
            f"du site, et s'utilisent selon la licence Pexels : voir {utiliser}. Le logo KF’ et les textes du site "
            f"restent la propriété de {e(editeur)}.</p>"
            f"<h2>Données personnelles</h2><p>Voir la page {confidentialite}.</p>"
        )
    else:
        corps = (
            f"<h2>Publisher</h2><p>{'<br>'.join(lignes)}</p>"
            f"<p>Publication director: {e(editeur)}.</p>"
            f"<h2>Hosting</h2>{hebergeur}"
            "<h2>Photos and content</h2>"
            f"<p>The photos are the work of {e(editeur)}. They are published on Pexels, which provides the site's "
            f"images, and may be used under the Pexels license: see {utiliser}. The KF’ logo and the texts of the "
            f"site remain the property of {e(editeur)}.</p>"
            f"<h2>Personal data</h2><p>See the {confidentialite} page.</p>"
        )
    description = (f"Mentions légales du site de {editeur} : éditeur et hébergeur." if langue == "fr"
                   else f"Legal notice for {editeur}'s website: publisher and host.")
    page_texte(g, langue, "mentions", t["mentions"], description, corps, bool(series))


def page_confidentialite(g, series, langue):
    t = TEXTES[langue]
    contact = courriel(g)
    goatcounter = bool(g.site.get("goatcounter", "").strip())
    if langue == "fr":
        audience = (
            "<p>Le site compte ses visites avec GoatCounter, un outil de mesure d'audience sans cookies. "
            "GoatCounter ne conserve que des chiffres d'ensemble : pages vues, site de provenance, navigateur, "
            "système, taille d'écran et pays. Votre adresse IP n'est jamais enregistrée : elle sert seulement, "
            "avec votre navigateur, à reconnaître une même visite pendant quelques heures, en mémoire. Les clics "
            "vers Pexels sont comptés de la même façon. "
            '<a href="https://www.goatcounter.com/help/privacy">Politique de confidentialité de GoatCounter</a>.</p>'
            if goatcounter else "<p>Le site ne mesure pas son audience.</p>"
        )
        corps = (
            '<p class="accroche">Ce site ne dépose aucun cookie de mesure d\'audience ni de publicité et ne '
            "demande aucune donnée personnelle : il n'affiche donc pas de bandeau de consentement.</p>"
            f"<h2>Mesure d'audience</h2>{audience}"
            "<h2>Hébergement</h2><p>Le site est hébergé par GitHub Pages. Comme tout hébergeur, GitHub enregistre "
            "l'adresse IP des visiteurs dans ses journaux, pour la sécurité du service : "
            '<a href="https://docs.github.com/fr/site-policy/privacy-policies/github-general-privacy-statement">'
            "déclaration de confidentialité de GitHub</a>.</p>"
            "<h2>Photos</h2><p>Les images sont chargées directement depuis les serveurs de Pexels, qui reçoivent "
            "donc l'adresse IP de votre navigateur. Cloudflare, qui les diffuse pour Pexels, peut déposer des "
            "cookies techniques qui servent à la sécurité du service : "
            '<a href="https://www.pexels.com/privacy-policy/">politique de confidentialité de Pexels</a>. '
            "Les liens vers Pexels et vers d'autres sites mènent à des services qui ont leurs propres règles.</p>"
            + (f"<h2>Vos droits</h2><p>Pour toute question sur vos données, écrivez à {contact}.</p>" if contact else "")
        )
        description = "Confidentialité : ni cookies publicitaires ni données personnelles, mesure d'audience sans cookies."
    else:
        audience = (
            "<p>The site counts its visits with GoatCounter, a cookie-free web analytics tool. GoatCounter only "
            "keeps aggregate figures: pages viewed, referring site, browser, operating system, screen size and "
            "country. Your IP address is never stored: together with your browser, it is only used to recognise "
            "the same visit for a few hours, in memory. Clicks through to Pexels are counted in the same way. "
            '<a href="https://www.goatcounter.com/help/privacy">GoatCounter privacy policy</a>.</p>'
            if goatcounter else "<p>The site does not measure its audience.</p>"
        )
        corps = (
            '<p class="accroche">This site sets no analytics or advertising cookies and asks for no personal data, '
            "which is why it shows no consent banner.</p>"
            f"<h2>Analytics</h2>{audience}"
            "<h2>Hosting</h2><p>The site is hosted by GitHub Pages. Like any host, GitHub logs visitors' IP "
            "addresses for the security of the service: "
            '<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">'
            "GitHub privacy statement</a>.</p>"
            "<h2>Photos</h2><p>Images are loaded directly from Pexels' servers, which therefore receive your "
            "browser's IP address. Cloudflare, which delivers them for Pexels, may set technical cookies used for "
            'the security of the service: <a href="https://www.pexels.com/privacy-policy/">Pexels privacy policy</a>. '
            "Links to Pexels and other sites lead to services with their own rules.</p>"
            + (f"<h2>Your rights</h2><p>For any question about your data, write to {contact}.</p>" if contact else "")
        )
        description = "Privacy: no advertising cookies, no personal data, cookie-free analytics."
    page_texte(g, langue, "confidentialite", t["confidentialite"], description, corps, bool(series))


def page_introuvable(g, series):
    adr = g.adr
    contenu = "".join(
        f'<section class="ouverture texte" lang="{l}"><h1>{TEXTES[l]["introuvable"]}</h1>'
        f'<p>{TEXTES[l]["introuvable_texte"]} <a href="{adr.chemin(l, "accueil")}">{TEXTES[l]["retour"]}</a></p></section>'
        for l in ("fr", "en")
    )
    chemins = {l: adr.chemin(l, "accueil") for l in ("fr", "en")}
    texte = g.page("fr", titre=TEXTES["fr"]["introuvable"], description=TEXTES["fr"]["introuvable_texte"],
                   chemins=chemins, contenu=contenu, series=bool(series))
    ecrire(SORTIE / "404.html", texte.replace("<head>", '<head><meta name="robots" content="noindex">', 1))


# ---------------------------------------------------------------- flux, plan du site


def date_rss(jour):
    moment = datetime.fromisoformat(jour).replace(hour=12, tzinfo=timezone.utc)
    return email.utils.format_datetime(moment)


def charger_parutions(jour=None):
    """Journal des parutions Pinterest (donnees/parutions.json) : pour chaque flux, les
    photos parues et leur date, dans l'ordre de parution. Une date postérieure au jour
    (aujourd'hui par défaut) n'est pas une parution : elle est oubliée."""
    jour = jour or AUJOURDHUI
    if not PARUTIONS.exists():
        return {}
    journal = json.loads(PARUTIONS.read_text(encoding="utf-8"))
    return {flux: {pid: date_parution for pid, date_parution in parues.items() if date_parution <= jour}
            for flux, parues in journal.items()}


def enregistrer_parutions(journal):
    PARUTIONS.write_text(json.dumps(journal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def completer_parutions(journal, flux, jour, depuis, par_flux, plafond):
    """Ajoute au journal les parutions du jour et renvoie leur nombre.

    « flux » : liste de (clé, photos, rythme), par ordre de priorité. Une photo ne paraît
    qu'une fois dans un flux : une photo ajoutée à une galerie ou reclassée entre dans sa
    file, sans jamais être sautée ni republiée. Les nouvelles photos (vues après « depuis »)
    passent en tête ; le fonds suit, des photos les plus vues aux moins vues, au rythme du
    flux. Un flux qui démarre reçoit d'abord « par_flux » photos, et jamais plus par jour ;
    tous les flux ensemble, pas plus de « plafond » par jour.
    """
    total = sum(1 for parues in journal.values() for d in parues.values() if d == jour)
    recentes = {str(p["id"]) for _, photos, _ in flux for p in photos if p["vue_le"] > depuis}
    files = []
    for cle, photos, rythme in flux:
        parues = journal.get(cle, {})
        attente = [p for p in photos if str(p["id"]) not in parues]
        files.append({
            "cle": cle,
            "rythme": rythme,
            "avant": sum(1 for d in parues.values() if d < jour),
            "du_jour": sum(1 for d in parues.values() if d == jour),
            "fonds_du_jour": sum(1 for pid, d in parues.items() if d == jour and pid not in recentes),
            "nouvelles": sorted((p for p in attente if p["vue_le"] > depuis), key=lambda p: (p["vue_le"], p["id"])),
            "fonds": sorted((p for p in attente if p["vue_le"] <= depuis), key=lambda p: (-p["vues"], -p["id"])),
        })
    ajoutees = 0

    def publier(f, p):
        nonlocal total, ajoutees
        journal.setdefault(f["cle"], {})[str(p["id"])] = jour
        f["du_jour"] += 1
        total += 1
        ajoutees += 1

    for f in files:
        while f["nouvelles"] and f["du_jour"] < par_flux and total < plafond:
            publier(f, f["nouvelles"].pop(0))
    for f in files:
        quota = max(f["rythme"], par_flux - f["avant"]) - f["fonds_du_jour"]
        while quota > 0 and f["fonds"] and f["du_jour"] < par_flux and total < plafond:
            publier(f, f["fonds"].pop(0))
            quota -= 1
    return ajoutees


def reglages_pinterest(reglages):
    """Réglages des flux Pinterest (rubrique [site] de site.ini)."""
    site = reglages["site"]
    flux_max = int(site.get("flux_max", "12") or 12)
    return {
        "flux_max": flux_max,
        "par_flux": max(1, flux_max // 2),
        "depuis": site.get("fonds_date", AUJOURDHUI).strip() or AUJOURDHUI,
        "par_jour": int(site.get("epingles_par_jour", "1") or 1),
        "par_jour_autres": int(site.get("epingles_par_jour_autres", "3") or 3),
        "plafond": int(site.get("epingles_max_par_jour", "200") or 200),
    }


def flux_pinterest(galeries, photos, r):
    """Flux reliés à Pinterest, par ordre de priorité : un par galerie, puis celui des
    photos rangées dans aucune galerie."""
    rangees = {p["id"] for gal in galeries for p in gal["photos"]}
    return ([(gal["cle"], gal["photos"], r["par_jour"]) for gal in galeries]
            + [(AUTRES, [p for p in photos if p["id"] not in rangees], r["par_jour_autres"])])


def parutions_flux(parues, par_id, taille):
    """Les « taille » dernières parutions d'un flux, de la plus récente à la plus ancienne.
    Une photo retirée du site en disparaît, sans qu'une plus ancienne reparaisse."""
    dernieres = list(parues.items())[-taille:]
    return [(par_id[int(pid)], d) for pid, d in reversed(dernieres) if int(pid) in par_id]


def ecrire_flux(adr, langue, titre, description, page, chemin_flux, selection):
    t = TEXTES[langue]
    articles = []
    for p, jour in selection:
        lien = adr.absolue(adr.chemin(langue, "photo", p["id"]))
        titre_photo = p["titre"][langue]
        image = url_image(p, 1200)
        corps = f'<p><img src="{e(image)}" alt="{e(titre_photo)}"></p><p>{e(titre_photo)}. {e(t["suffixe"])}</p>'
        articles.append(
            f"<item><title>{e(titre_photo)}</title><link>{lien}</link>"
            f'<guid isPermaLink="true">{lien}</guid><pubDate>{date_rss(jour)}</pubDate>'
            f"<description>{e(corps)}</description>"
            f'<enclosure url="{e(image)}" type="image/jpeg" length="0"/>'
            f'<media:content url="{e(image)}" medium="image" type="image/jpeg"/></item>'
        )
    texte = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">'
        f"<channel><title>{e(titre)}</title><link>{adr.absolue(page)}</link>"
        f"<description>{e(description)}</description><language>{langue}</language>"
        f'<atom:link href="{adr.absolue(chemin_flux)}" rel="self" type="application/rss+xml"/>'
        + "".join(articles) + "</channel></rss>\n"
    )
    ecrire(SORTIE / chemin_flux[len(adr.base):].lstrip("/"), texte)


def ecrire_plan(adr, photos, galeries, series, couleurs):
    entrees = []

    def ajouter(chemins, image=None):
        for langue in ("fr", "en"):
            bloc = f"<url><loc>{adr.absolue(chemins[langue])}</loc>"
            for autre in ("fr", "en"):
                bloc += f'<xhtml:link rel="alternate" hreflang="{autre}" href="{adr.absolue(chemins[autre])}"/>'
            if image:
                bloc += f"<image:image><image:loc>{e(image)}</image:loc></image:image>"
            entrees.append(bloc + "</url>")

    genres = ["accueil", "galeries"] + (["series"] if series else []) + ["apropos", "utiliser", "mentions", "confidentialite"]
    for genre in genres:
        ajouter({l: adr.chemin(l, genre) for l in ("fr", "en")})
    for serie in series:
        ajouter({l: adr.chemin(l, "serie", serie["cle"]) for l in ("fr", "en")})
    for gal in galeries:
        ajouter({l: adr.chemin(l, "galerie", gal["cle"]) for l in ("fr", "en")})
    for couleur in couleurs:
        ajouter({l: adr.chemin(l, "couleur", couleur["cle"][l]) for l in ("fr", "en")})
    for p in photos:
        ajouter({l: adr.chemin(l, "photo", p["id"]) for l in ("fr", "en")}, image=p["image"])
    texte = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
        + "".join(entrees) + "</urlset>\n"
    )
    ecrire(SORTIE / "sitemap.xml", texte)
    racine = adr.absolue(adr.base + "/")
    ecrire(SORTIE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {racine}sitemap.xml\n")


# ---------------------------------------------------------------- programme


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("--fiches-seulement", action="store_true")
    options.add_argument("--max-appels", type=int, default=180)
    options.add_argument("--enregistrer-parutions", action="store_true")
    args = options.parse_args()

    ids = lire_photos()
    fiches = charger_fiches()
    lues = completer_fiches(ids, fiches, args.max_appels)
    manquantes = sum(1 for i in ids if str(i) not in fiches)
    print(f"{len(ids)} photos listées, {lues} fiches lues sur Pexels, {manquantes} encore à lire.")
    if args.fiches_seulement:
        return

    reglages = lire_ini("site.ini")
    anglais, francais = lire_textes()
    photos, sans_titre = assembler_photos(ids, fiches, anglais, francais, lire_suivi())
    minimum = int(reglages["site"].get("galerie_min", "4") or 4)
    galeries = composer_galeries(lire_ini("galeries.ini"), photos, minimum)
    series = composer_series(lire_ini("series.ini"), photos, minimum)
    couleurs = composer_couleurs(photos, minimum)
    par_id = {p["id"]: p for p in photos}
    choix = lire_liste("selection.txt")
    selection = [par_id[i] for i in choix if i in par_id]
    ouverture = photos_ouverture(reglages, par_id, selection or photos)
    preuve = lire_releves()
    adr = Adresses(reglages["site"]["adresse"])
    r = reglages_pinterest(reglages)
    journal = charger_parutions()
    flux = flux_pinterest(galeries, photos, r)
    du_jour = completer_parutions(journal, flux, AUJOURDHUI, r["depuis"], r["par_flux"], r["plafond"])
    if args.enregistrer_parutions:
        enregistrer_parutions(journal)

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    shutil.copytree(ICI / "statique", SORTIE / "statique")
    g = Gabarit(reglages, adr, preuve)
    par_photo = {p["id"]: [gal for gal in galeries if p in gal["photos"]] for p in photos}
    par_serie = {p["id"]: [s for s in series if p in s["photos"]] for p in photos}
    par_couleur = {p["id"]: [c for c in couleurs if p in c["photos"]] for p in photos}
    proches = photos_proches(photos, par_photo)
    avec_series = bool(series)
    for langue in ("fr", "en"):
        page_accueil(g, photos, galeries, series, selection, ouverture, langue)
        page_galeries(g, galeries, series, couleurs, langue)
        for couleur in couleurs:
            page_couleur(g, couleur, couleurs, galeries, series, langue)
        if series:
            page_series(g, series, langue)
        for serie in series:
            page_serie(g, serie, series, langue)
        page_a_propos(g, par_id, galeries, series, langue)
        page_utiliser(g, series, langue)
        page_mentions(g, series, langue)
        page_confidentialite(g, series, langue)
        for gal in galeries:
            page_galerie(g, gal, series, langue)
            ecrire_flux(adr, langue, f'{gal["titre"][langue]} — {g.site.get("nom", "")}',
                        gal["description"][langue], adr.chemin(langue, "galerie", gal["cle"]),
                        adr.chemin(langue, "flux_galerie", gal["cle"]),
                        parutions_flux(journal.get(gal["cle"], {}), par_id, r["flux_max"]))
        for rang, p in enumerate(photos):
            precedente = photos[rang - 1] if rang > 0 else None
            suivante = photos[rang + 1] if rang + 1 < len(photos) else None
            page_photo(g, p, langue, precedente, suivante, par_photo[p["id"]], par_serie[p["id"]], avec_series,
                       proches[p["id"]], par_couleur[p["id"]])
        ecrire_flux(adr, langue, TEXTES[langue]["accueil"], reglages["accueil"].get(f"accroche_{langue}", ""),
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux"), [(p, p["vue_le"]) for p in photos[:30]])
        ecrire_flux(adr, langue, TEXTES[langue]["autres_photos"], TEXTES[langue]["suffixe"],
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux_autres"),
                    parutions_flux(journal.get(AUTRES, {}), par_id, r["flux_max"]))
    page_introuvable(g, series)
    ecrire_plan(adr, photos, galeries, series, couleurs)
    print(f"{len(photos)} photos publiées ({sans_titre} en attente d'un titre), {len(galeries)} galeries :")
    for gal in galeries:
        print(f"  {gal['cle']} : {len(gal['photos'])} photos")
    hors = [p["id"] for p in photos if not par_photo[p["id"]]]
    if hors:
        print(f"Dans aucune galerie ({len(hors)}, flux « More photos ») : {', '.join(map(str, hors))}.")
    print(f"{len(couleurs)} pages de couleur : " + ", ".join(f'{c["cle"]["fr"]} ({len(c["photos"])})' for c in couleurs) + ".")
    print(f"{len(series)} séries :")
    for serie in series:
        print(f"  {serie['cle']} : {len(serie['photos'])} photos")
    absentes = [i for i in choix if i not in par_id]
    print(f"Sélection : {len(selection)} photos" + (f" (non publiées : {', '.join(map(str, absentes))})" if absentes else "")
          + f", {len(ouverture)} à l'ouverture de l'accueil.")
    print(f"Relevés : {preuve['vues']} vues et {preuve['telechargements']} téléchargements sur Pexels.")
    attente = sum(1 for cle, membres, _ in flux for p in membres if str(p["id"]) not in journal.get(cle, {}))
    print(f"Pinterest : {du_jour} parutions ajoutées aujourd'hui, {attente} en attente dans les files"
          + ("." if args.enregistrer_parutions else " (journal non enregistré)."))


if __name__ == "__main__":
    main()
