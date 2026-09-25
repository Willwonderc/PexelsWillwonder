#!/usr/bin/env python3
"""Construit le site de photographe de Karl Forterre.

1. Lit la liste des photos : vitrine/photos.txt.
2. Complète les fiches Pexels (vitrine/donnees/fiches.json) grâce à l'API, si la
   variable d'environnement PEXELS_API_KEY est définie.
3. Écrit le site statique dans le dossier _site/.

Options :
  --fiches-seulement   ne fait que l'étape 2
  --max-appels N       nombre maximum d'appels à l'API (180 par défaut)
"""

import argparse
import configparser
import csv
import email.utils
import hashlib
import html
import json
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
        "une_photo": "1 photo",
        "n_photos": "{n} photos",
        "telecharger": "Télécharger gratuitement sur Pexels",
        "credit": "Photo de Karl Forterre, sous {licence} : utilisation libre et gratuite.",
        "licence": "licence Pexels",
        "numero": "Pexels n° {id}",
        "mots": "Mots-clés",
        "dans": "Dans les galeries :",
        "dans_serie": "Dans la série :",
        "meme_galerie": "Dans la même galerie",
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
        "une_photo": "1 photo",
        "n_photos": "{n} photos",
        "telecharger": "Free download on Pexels",
        "credit": "Photo by Karl Forterre, under the {licence}: free to use.",
        "licence": "Pexels license",
        "numero": "Pexels no. {id}",
        "mots": "Keywords",
        "dans": "In the galleries:",
        "dans_serie": "In the series:",
        "meme_galerie": "From the same gallery",
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


def assembler_photos(ids, fiches, anglais, francais):
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
        photos.append({
            "id": pid,
            "largeur": fiche["largeur"],
            "hauteur": fiche["hauteur"],
            "page": fiche["page"],
            "image": fiche["image"],
            "couleur": fiche.get("couleur") or "#8a8a8a",
            "vue_le": fiche.get("vue_le") or AUJOURDHUI,
            "titre": {"en": titre_en, "fr": fr.get("titre") or titre_en},
            "mots": {"en": liste_mots(en.get("mots")), "fr": liste_mots(fr.get("mots"))},
            "recherche": plier(" ".join([titre_en, en.get("mots", ""), fiche.get("texte", "")])),
        })
    photos.sort(key=lambda p: -p["id"])
    return photos, sans_titre


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
        galeries.append({
            "cle": cle,
            "type": reglage.get("type", "theme").strip(),
            "titre": {"fr": titre_fr, "en": reglage.get("titre_en", titre_fr)},
            "description": {"fr": description_fr, "en": reglage.get("description_en", description_fr)},
            "photos": membres,
            "couverture": couverture,
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
        })
    return series


def photos_ouverture(reglages, par_id, selection):
    """Photos qui défilent sur l'accueil : réglage « ouverture », sinon les premières
    photos en format paysage de la sélection."""
    choisies = [par_id[i] for i in nombres(reglages["accueil"].get("ouverture")) if i in par_id]
    if not choisies:
        choisies = [p for p in selection if p["largeur"] > p["hauteur"]][:6]
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


def carreau(photo, langue, adr):
    ratio = photo["largeur"] / photo["hauteur"]
    return (
        f'<a class="carreau" href="{adr.chemin(langue, "photo", photo["id"])}" data-pexels="{e(photo["page"])}" '
        f'style="--r:{ratio:.3f};background-color:{e(photo["couleur"])}">'
        f'<img src="{url_image(photo, 600)}" srcset="{srcset(photo, (300, 600, 900, 1300))}" '
        f'sizes="(max-width: 640px) 60vw, 30vw" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(photo["titre"][langue])}" loading="lazy" decoding="async"></a>'
    )


def grille(photos, langue, adr):
    return '<div class="grille">' + "".join(carreau(p, langue, adr) for p in photos) + "</div>"


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
        visionneuse = self.visionneuse(langue) if 'class="grille"' in contenu else ""
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


def diapo(photo, langue, adr, premiere):
    """Une photo de l'accueil plein écran. Sur un écran en hauteur, Pexels fournit
    directement l'image recadrée, bien plus légère que l'image entière."""
    portrait = ", ".join(f"{url_recadree(photo, l, round(l * 1.75))} {l}w" for l in (600, 900, 1200))
    ratio = photo["largeur"] / photo["hauteur"]
    priorite = ' fetchpriority="high"' if premiere else ""
    return (
        f'<figure class="diapo{" visible" if premiere else ""}" style="background-color:{e(photo["couleur"])}">'
        f'<picture><source media="(max-aspect-ratio: 4/5)" srcset="{portrait}" '
        f'sizes="(max-aspect-ratio: 4/7) 57vh, 100vw">'
        f'<img src="{url_image(photo, 1600)}" srcset="{srcset(photo, (1200, 1600, 2200, 3000))}" '
        f'sizes="(max-aspect-ratio: {photo["largeur"]}/{photo["hauteur"]}) {ratio * 100:.0f}vh, 100vw" '
        f'width="{photo["largeur"]}" height="{photo["hauteur"]}" alt="{e(photo["titre"][langue])}"{priorite}>'
        f'</picture><figcaption><a href="{adr.chemin(langue, "photo", photo["id"])}">'
        f'{e(photo["titre"][langue])}</a></figcaption></figure>'
    )


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
                   image=(ouverture or photos or [None])[0], donnees=donnees, classe="accueil",
                   titre_complet=True, series=bool(series))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galeries(g, galeries, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    contenu = (
        f'<section class="ouverture"><h1>{t["galeries"]}</h1></section>'
        + cartes(galeries, langue, adr, "theme")
        + cartes(galeries, langue, adr, "lieu")
    )
    chemins = {l: adr.chemin(l, "galeries") for l in ("fr", "en")}
    description = " · ".join(gal["titre"][langue] for gal in galeries)
    texte = g.page(langue, titre=t["galeries"], description=description, chemins=chemins, contenu=contenu,
                   image=galeries[0]["couverture"] if galeries else None, series=bool(series))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galerie(g, galerie, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "galerie", galerie["cle"]) for l in ("fr", "en")}
    flux = adr.chemin(langue, "flux_galerie", galerie["cle"])
    description = galerie["description"][langue] or galerie["titre"][langue]
    contenu = (
        f'<header class="ouverture"><p class="surtitre"><a href="{adr.chemin(langue, "galeries")}">{t["galeries"]}</a></p>'
        f'<h1>{e(galerie["titre"][langue])}</h1>'
        f'<p class="accroche">{e(description)} <span class="nombre">{nombre_photos(len(galerie["photos"]), langue)}</span></p>'
        f"</header>"
        + grille(galerie["photos"], langue, adr)
        + f'<p class="flux-lien"><a href="{flux}">{t["flux_galerie"]}</a></p>'
        + rappel(g, langue)
    )
    donnees = [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": galerie["titre"][langue],
        "description": description,
        "url": adr.absolue(chemins[langue]),
        "inLanguage": langue,
    }]
    texte = g.page(langue, titre=galerie["titre"][langue], description=description, chemins=chemins,
                   contenu=contenu, image=galerie["couverture"], donnees=donnees, flux=flux, series=bool(series))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_series(g, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "series") for l in ("fr", "en")}
    contenu = (
        f'<section class="ouverture"><h1>{t["series"]}</h1><p class="accroche">{t["series_intro"]}</p></section>'
        '<div class="galeries">' + "".join(carte_serie(s, langue, adr) for s in series) + "</div>"
        + rappel(g, langue)
    )
    texte = g.page(langue, titre=t["series"], description=t["series_intro"], chemins=chemins, contenu=contenu,
                   image=series[0]["couverture"])
    ecrire(adr.fichier(chemins[langue]), texte)


def page_serie(g, serie, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "serie", serie["cle"]) for l in ("fr", "en")}
    titre = serie["titre"][langue]
    texte_serie = serie["texte"][langue]
    description = texte_serie[0] if texte_serie else titre
    contenu = (
        f'<header class="ouverture"><p class="surtitre"><a href="{adr.chemin(langue, "series")}">{t["series"]}</a></p>'
        f'<h1>{e(titre)}</h1><p class="accroche">{e(infos_serie(serie, langue))}</p></header>'
        + (f'<div class="texte serie-texte">' + "".join(f"<p>{e(p)}</p>" for p in texte_serie) + "</div>"
           if texte_serie else "")
        + grille(serie["photos"], langue, adr)
        + rappel(g, langue)
        + cartes_series(series, langue, adr, titre=t["autres_series"], sauf=serie)
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
    }]
    texte = g.page(langue, titre=t["titre_serie"].format(titre=titre), description=description, chemins=chemins,
                   contenu=contenu, image=serie["couverture"], donnees=donnees)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_photo(g, photo, langue, precedente, suivante, galeries_photo, series_photo, avec_series):
    adr = g.adr
    t = TEXTES[langue]
    titre = photo["titre"][langue]
    description = f"{titre}. {t['suffixe']}"
    chemins = {l: adr.chemin(l, "photo", photo["id"]) for l in ("fr", "en")}
    ratio = photo["largeur"] / photo["hauteur"]
    mots = photo["mots"][langue]
    liste = (
        f'<ul class="mots" aria-label="{t["mots"]}">' + "".join(f"<li>{e(m)}</li>" for m in mots) + "</ul>"
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
    suite = '<nav class="suite">'
    if precedente:
        suite += f'<a rel="prev" href="{adr.chemin(langue, "photo", precedente["id"])}">← {t["precedente"]}</a>'
    if suivante:
        suite += f'<a rel="next" href="{adr.chemin(langue, "photo", suivante["id"])}">{t["suivante"]} →</a>'
    suite += "</nav>"
    voisines = ""
    if galeries_photo:
        gal = next((g for g in galeries_photo if g["type"] == "lieu"), galeries_photo[0])
        autres = [p for p in gal["photos"] if p["id"] != photo["id"]]
        rang = next((i for i, p in enumerate(gal["photos"]) if p["id"] == photo["id"]), 0)
        choix = (autres[rang:] + autres[:rang])[:8]
        if choix:
            voisines = (
                f'<section class="bloc"><h2 class="surtitre">{t["meme_galerie"]} · '
                f'<a href="{adr.chemin(langue, "galerie", gal["cle"])}">{e(gal["titre"][langue])}</a></h2>'
                f"{grille(choix, langue, adr)}</section>"
            )
    licence = f'<a href="{adr.chemin(langue, "utiliser")}">{t["licence"]}</a>'
    contenu = (
        f'<article class="photo"><figure class="cliche" style="--r:{ratio:.3f}">'
        f'<a href="{e(photo["page"])}" title="{t["voir_pexels"]}" data-goatcounter-click="pexels-image-{photo["id"]}">'
        f'<img src="{url_image(photo, 1600)}" srcset="{srcset(photo, (800, 1200, 1600, 2200, 3000))}" '
        f'sizes="(max-width: 1440px) 100vw, 1440px" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(titre)}" fetchpriority="high" style="background-color:{e(photo["couleur"])}"></a></figure>'
        f'<div class="legende"><h1>{e(titre)}</h1>'
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
    }]
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=photo, donnees=donnees, classe="page-photo", series=avec_series)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_texte(g, langue, genre, titre, description, corps, avec_series, image=None):
    """Page de texte simple (À propos, Utiliser mes photos, pages légales)."""
    adr = g.adr
    chemins = {l: adr.chemin(l, genre) for l in ("fr", "en")}
    contenu = f'<section class="ouverture texte"><h1>{e(titre)}</h1>{corps}</section>'
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=image, series=avec_series)
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


def selection_flux(photos, taille, par_jour, depuis):
    """Photos d'un flux, avec leur date de parution.

    Les photos vues après la date « depuis » y entrent aussitôt. Les autres, le fonds,
    y entrent peu à peu : les « taille » premières le jour même, puis « par_jour »
    de plus chaque jour. Le flux garde les « taille » dernières parues.
    """
    aujourdhui = date.fromisoformat(AUJOURDHUI)
    debut = date.fromisoformat(depuis)
    nouvelles = sorted((p for p in photos if p["vue_le"] > depuis), key=lambda p: (p["vue_le"], p["id"]), reverse=True)
    parues = []
    for rang, p in enumerate(p for p in photos if p["vue_le"] <= depuis):
        jour = debut + timedelta(days=0 if rang < taille else (rang - taille) // par_jour + 1)
        if jour > aujourdhui:
            break
        parues.append((p, jour.isoformat()))
    return [(p, p["vue_le"]) for p in nouvelles][:taille] + parues[::-1][:taille]


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


def ecrire_plan(adr, photos, galeries, series):
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
    photos, sans_titre = assembler_photos(ids, fiches, anglais, francais)
    minimum = int(reglages["site"].get("galerie_min", "4") or 4)
    galeries = composer_galeries(lire_ini("galeries.ini"), photos, minimum)
    series = composer_series(lire_ini("series.ini"), photos, minimum)
    par_id = {p["id"]: p for p in photos}
    choix = lire_liste("selection.txt")
    selection = [par_id[i] for i in choix if i in par_id]
    ouverture = photos_ouverture(reglages, par_id, selection or photos)
    preuve = lire_releves()
    adr = Adresses(reglages["site"]["adresse"])
    flux_max = int(reglages["site"].get("flux_max", "12") or 12)
    depuis = reglages["site"].get("fonds_date", AUJOURDHUI).strip() or AUJOURDHUI
    par_jour = int(reglages["site"].get("epingles_par_jour", "1") or 1)
    par_jour_autres = int(reglages["site"].get("epingles_par_jour_autres", "3") or 3)

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    shutil.copytree(ICI / "statique", SORTIE / "statique")
    g = Gabarit(reglages, adr, preuve)
    par_photo = {p["id"]: [gal for gal in galeries if p in gal["photos"]] for p in photos}
    par_serie = {p["id"]: [s for s in series if p in s["photos"]] for p in photos}
    avec_series = bool(series)
    for langue in ("fr", "en"):
        page_accueil(g, photos, galeries, series, selection, ouverture, langue)
        page_galeries(g, galeries, series, langue)
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
                        selection_flux(gal["photos"], flux_max, par_jour, depuis))
        for rang, p in enumerate(photos):
            precedente = photos[rang - 1] if rang > 0 else None
            suivante = photos[rang + 1] if rang + 1 < len(photos) else None
            page_photo(g, p, langue, precedente, suivante, par_photo[p["id"]], par_serie[p["id"]], avec_series)
        ecrire_flux(adr, langue, TEXTES[langue]["accueil"], reglages["accueil"].get(f"accroche_{langue}", ""),
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux"), [(p, p["vue_le"]) for p in photos[:30]])
        autres = [p for p in photos if not par_photo[p["id"]]]
        ecrire_flux(adr, langue, TEXTES[langue]["autres_photos"], TEXTES[langue]["suffixe"],
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux_autres"),
                    selection_flux(autres, flux_max, par_jour_autres, depuis))
    page_introuvable(g, series)
    ecrire_plan(adr, photos, galeries, series)
    print(f"{len(photos)} photos publiées ({sans_titre} en attente d'un titre), {len(galeries)} galeries :")
    for gal in galeries:
        print(f"  {gal['cle']} : {len(gal['photos'])} photos")
    print(f"{len(series)} séries :")
    for serie in series:
        print(f"  {serie['cle']} : {len(serie['photos'])} photos")
    absentes = [i for i in choix if i not in par_id]
    print(f"Sélection : {len(selection)} photos" + (f" (non publiées : {', '.join(map(str, absentes))})" if absentes else "")
          + f", {len(ouverture)} à l'ouverture de l'accueil.")
    print(f"Relevés : {preuve['vues']} vues et {preuve['telechargements']} téléchargements sur Pexels.")


if __name__ == "__main__":
    main()
