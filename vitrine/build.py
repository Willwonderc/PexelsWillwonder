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
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
SORTIE = RACINE / "_site"
FICHES = ICI / "donnees" / "fiches.json"
PHOTOGRAPHE = 28489473
LICENCE = "https://www.pexels.com/license/"
AUJOURDHUI = datetime.now(timezone.utc).date().isoformat()

TEXTES = {
    "fr": {
        "accueil": "Photographies de Karl Forterre",
        "galeries": "Galeries",
        "a_propos": "À propos",
        "autre_langue": "English",
        "themes": "Thèmes",
        "lieux": "Lieux",
        "recentes": "Dernières photos",
        "une_photo": "1 photo",
        "n_photos": "{n} photos",
        "telecharger": "Télécharger gratuitement sur Pexels",
        "credit": "Photo de Karl Forterre, sous licence Pexels : utilisation libre et gratuite.",
        "numero": "Pexels n° {id}",
        "mots": "Mots-clés",
        "dans": "Dans les galeries :",
        "meme_galerie": "Dans la même galerie",
        "precedente": "Photo précédente",
        "suivante": "Photo suivante",
        "flux": "Flux RSS",
        "flux_galerie": "Flux RSS de la galerie",
        "suffixe": "Photo de Karl Forterre, libre de droits, à télécharger gratuitement sur Pexels.",
        "introuvable": "Page introuvable",
        "introuvable_texte": "Cette page n'existe pas ou plus.",
        "retour": "Retour à l'accueil",
        "profil": "Profil Pexels",
        "evitement": "Aller au contenu",
        "menu": "Navigation principale",
        "suivre": "Suivre sur Pexels",
        "voir_pexels": "Voir cette photo sur Pexels",
        "locale": "fr_FR",
    },
    "en": {
        "accueil": "Photographs by Karl Forterre",
        "galeries": "Galleries",
        "a_propos": "About",
        "autre_langue": "Français",
        "themes": "Themes",
        "lieux": "Places",
        "recentes": "Latest photos",
        "une_photo": "1 photo",
        "n_photos": "{n} photos",
        "telecharger": "Free download on Pexels",
        "credit": "Photo by Karl Forterre, under the Pexels license: free to use.",
        "numero": "Pexels no. {id}",
        "mots": "Keywords",
        "dans": "In the galleries:",
        "meme_galerie": "From the same gallery",
        "precedente": "Previous photo",
        "suivante": "Next photo",
        "flux": "RSS feed",
        "flux_galerie": "Gallery RSS feed",
        "suffixe": "Photo by Karl Forterre, royalty-free, free to download on Pexels.",
        "introuvable": "Page not found",
        "introuvable_texte": "This page does not exist, or no longer does.",
        "retour": "Back to the home page",
        "profil": "Pexels profile",
        "evitement": "Skip to content",
        "menu": "Main navigation",
        "suivre": "Follow on Pexels",
        "voir_pexels": "See this photo on Pexels",
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


def liste_mots(texte):
    return [m.strip() for m in (texte or "").split(",") if m.strip()]


# ---------------------------------------------------------------- données


def lire_ini(nom):
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(ICI / nom, encoding="utf-8")
    return conf


def lire_photos():
    ids = []
    for ligne in (ICI / "photos.txt").read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        trouves = nombres(ligne)
        if trouves and trouves[-1] not in ids:
            ids.append(trouves[-1])
    return ids


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
            "photo": f"/photo/{cle}/",
            "apropos": "/about/" if en else "/a-propos/",
            "flux": "/feed.xml" if en else "/flux.xml",
            "flux_galerie": f"/galleries/{cle}/feed.xml" if en else f"/galeries/{cle}/flux.xml",
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
        f'<a class="carreau" href="{adr.chemin(langue, "photo", photo["id"])}" '
        f'style="--r:{ratio:.3f};background-color:{e(photo["couleur"])}">'
        f'<img src="{url_image(photo, 600)}" srcset="{srcset(photo, (300, 600, 900, 1300))}" '
        f'sizes="(max-width: 640px) 60vw, 30vw" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(photo["titre"][langue])}" loading="lazy" decoding="async"></a>'
    )


def grille(photos, langue, adr):
    return '<div class="grille">' + "".join(carreau(p, langue, adr) for p in photos) + "</div>"


def carte_galerie(galerie, langue, adr):
    p = galerie["couverture"]
    return (
        f'<a class="galerie" href="{adr.chemin(langue, "galerie", galerie["cle"])}">'
        f'<span class="galerie-image" style="background-color:{e(p["couleur"])}">'
        f'<img src="{url_image(p, 800)}" srcset="{srcset(p, (400, 800, 1200))}" '
        f'sizes="(max-width: 640px) 92vw, 30vw" alt="" loading="lazy" decoding="async"></span>'
        f'<span class="galerie-titre">{e(galerie["titre"][langue])}</span>'
        f'<span class="galerie-nombre">{nombre_photos(len(galerie["photos"]), langue)}</span></a>'
    )


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


def jsonld(donnees):
    texte = json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{texte}</script>'


class Gabarit:
    """Enveloppe commune à toutes les pages."""

    def __init__(self, reglages, adr):
        self.site = reglages["site"]
        self.adr = adr
        style = (ICI / "statique" / "style.css").read_bytes()
        self.version = hashlib.md5(style).hexdigest()[:8]

    def statique(self, nom):
        return f"{self.adr.base}/statique/{nom}"

    def page(self, langue, *, titre, description, chemins, contenu, image=None, donnees=None,
             flux=None, classe="", titre_complet=False):
        t = TEXTES[langue]
        autre = "en" if langue == "fr" else "fr"
        adr = self.adr
        nom = self.site.get("nom", "Karl Forterre")
        titre_page = titre if titre_complet else f"{titre} — {nom}"
        url = adr.absolue(chemins[langue])
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
            f'<link rel="icon" href="{self.statique("favicon.svg")}" type="image/svg+xml">',
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
        entete = (
            f'<a class="evitement" href="#contenu">{t["evitement"]}</a>'
            f'<header class="entete"><a class="marque" href="{adr.chemin(langue, "accueil")}">{e(nom)}</a>'
            f'<nav class="menu" aria-label="{t["menu"]}">'
            f'<a href="{adr.chemin(langue, "galeries")}">{t["galeries"]}</a>'
            f'<a href="{adr.chemin(langue, "apropos")}">{t["a_propos"]}</a>'
            f'<a href="{chemins[autre]}" hreflang="{autre}" lang="{autre}">{TEXTES[langue]["autre_langue"]}</a>'
            f'<a class="suivre" href="{e(self.site.get("profil_pexels", ""))}" data-goatcounter-click="suivre-pexels">{t["suivre"]}</a>'
            f"</nav></header>"
        )
        annee = datetime.now(timezone.utc).year
        pied = (
            '<footer class="pied">'
            '<p><a href="https://www.pexels.com">Photos provided by Pexels</a></p>'
            f'<p>© {annee} {e(nom)} · <a href="{e(self.site.get("profil_pexels", ""))}">{t["profil"]}</a>'
            f' · <a href="{e(self.site.get("site_personnel", ""))}">{e(urlparse(self.site.get("site_personnel", "")).netloc)}</a>'
            f' · <a href="{adr.chemin(langue, "flux")}">{t["flux"]}</a></p>'
            "</footer>"
        )
        return (
            f'<!doctype html>\n<html lang="{langue}"><head>' + "".join(tete) + "</head>"
            f'<body class="{classe}">{entete}<main id="contenu">{contenu}</main>{pied}</body></html>\n'
        )


# ---------------------------------------------------------------- pages


def ecrire(chemin, texte):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")


def page_accueil(g, reglages, photos, galeries, langue):
    adr = g.adr
    t = TEXTES[langue]
    accroche = reglages["accueil"].get(f"accroche_{langue}", "")
    contenu = (
        f'<section class="ouverture"><h1>{t["accueil"]}</h1><p class="accroche">{e(accroche)}</p></section>'
        + cartes(galeries, langue, adr, "theme")
        + cartes(galeries, langue, adr, "lieu")
        + f'<section class="bloc"><h2 class="surtitre">{t["recentes"]}</h2>{grille(photos[:30], langue, adr)}</section>'
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
                   image=photos[0] if photos else None, donnees=donnees, classe="accueil", titre_complet=True)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galeries(g, galeries, langue):
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
                   image=galeries[0]["couverture"] if galeries else None)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galerie(g, galerie, langue):
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
                   contenu=contenu, image=galerie["couverture"], donnees=donnees, flux=flux)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_photo(g, photo, langue, precedente, suivante, galeries_photo):
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
    if galeries_photo:
        liens = ", ".join(
            f'<a href="{adr.chemin(langue, "galerie", gal["cle"])}">{e(gal["titre"][langue])}</a>' for gal in galeries_photo
        )
        dans = f'<p class="dans">{t["dans"]} {liens}</p>'
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
    contenu = (
        f'<article class="photo"><figure class="cliche" style="--r:{ratio:.3f}">'
        f'<a href="{e(photo["page"])}" title="{t["voir_pexels"]}" data-goatcounter-click="pexels-image-{photo["id"]}">'
        f'<img src="{url_image(photo, 1600)}" srcset="{srcset(photo, (800, 1200, 1600, 2200, 3000))}" '
        f'sizes="(max-width: 1440px) 100vw, 1440px" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(titre)}" fetchpriority="high" style="background-color:{e(photo["couleur"])}"></a></figure>'
        f'<div class="legende"><h1>{e(titre)}</h1>'
        f'<p><a class="bouton" href="{e(photo["page"])}" data-goatcounter-click="pexels-{photo["id"]}" '
        f'data-goatcounter-title="{e(titre)}">{t["telecharger"]}</a></p>'
        f'<p class="credit">{t["credit"]} <span class="numero">{t["numero"].format(id=photo["id"])}</span></p>'
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
                   image=photo, donnees=donnees, classe="page-photo")
    ecrire(adr.fichier(chemins[langue]), texte)


def page_a_propos(g, reglages, langue):
    adr = g.adr
    t = TEXTES[langue]
    texte_brut = reglages["a-propos"].get(f"texte_{langue}", "")
    paragraphes = [p.strip() for p in re.split(r"\n\s*\n", texte_brut) if p.strip()]
    liens = (
        f'<ul class="liens"><li><a href="{e(g.site.get("profil_pexels", ""))}">{t["profil"]}</a></li>'
        f'<li><a href="{e(g.site.get("site_personnel", ""))}">{e(urlparse(g.site.get("site_personnel", "")).netloc)}</a></li></ul>'
    )
    contenu = (
        f'<section class="ouverture texte"><h1>{t["a_propos"]}</h1>'
        + "".join(f"<p>{e(p)}</p>" for p in paragraphes)
        + liens + "</section>"
    )
    chemins = {l: adr.chemin(l, "apropos") for l in ("fr", "en")}
    texte = g.page(langue, titre=t["a_propos"], description=paragraphes[0] if paragraphes else t["a_propos"],
                   chemins=chemins, contenu=contenu)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_introuvable(g):
    adr = g.adr
    contenu = "".join(
        f'<section class="ouverture texte" lang="{l}"><h1>{TEXTES[l]["introuvable"]}</h1>'
        f'<p>{TEXTES[l]["introuvable_texte"]} <a href="{adr.chemin(l, "accueil")}">{TEXTES[l]["retour"]}</a></p></section>'
        for l in ("fr", "en")
    )
    chemins = {l: adr.chemin(l, "accueil") for l in ("fr", "en")}
    texte = g.page("fr", titre=TEXTES["fr"]["introuvable"], description=TEXTES["fr"]["introuvable_texte"],
                   chemins=chemins, contenu=contenu)
    ecrire(SORTIE / "404.html", texte.replace("<head>", '<head><meta name="robots" content="noindex">', 1))


# ---------------------------------------------------------------- flux, plan du site


def date_rss(jour):
    moment = datetime.fromisoformat(jour).replace(hour=12, tzinfo=timezone.utc)
    return email.utils.format_datetime(moment)


def ecrire_flux(adr, langue, titre, description, page, chemin_flux, photos, nombre=30):
    t = TEXTES[langue]
    articles = []
    for p in photos[:nombre]:
        lien = adr.absolue(adr.chemin(langue, "photo", p["id"]))
        titre_photo = p["titre"][langue]
        image = url_image(p, 1200)
        corps = f'<p><img src="{e(image)}" alt="{e(titre_photo)}"></p><p>{e(titre_photo)}. {e(t["suffixe"])}</p>'
        articles.append(
            f"<item><title>{e(titre_photo)}</title><link>{lien}</link>"
            f'<guid isPermaLink="true">{lien}</guid><pubDate>{date_rss(p["vue_le"])}</pubDate>'
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


def ecrire_plan(adr, photos, galeries):
    entrees = []

    def ajouter(chemins, image=None):
        for langue in ("fr", "en"):
            bloc = f"<url><loc>{adr.absolue(chemins[langue])}</loc>"
            for autre in ("fr", "en"):
                bloc += f'<xhtml:link rel="alternate" hreflang="{autre}" href="{adr.absolue(chemins[autre])}"/>'
            if image:
                bloc += f"<image:image><image:loc>{e(image)}</image:loc></image:image>"
            entrees.append(bloc + "</url>")

    for genre in ("accueil", "galeries", "apropos"):
        ajouter({l: adr.chemin(l, genre) for l in ("fr", "en")})
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
    adr = Adresses(reglages["site"]["adresse"])
    flux_max = int(reglages["site"].get("flux_max", "12") or 12)

    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    shutil.copytree(ICI / "statique", SORTIE / "statique")
    g = Gabarit(reglages, adr)
    par_photo = {p["id"]: [gal for gal in galeries if p in gal["photos"]] for p in photos}
    for langue in ("fr", "en"):
        page_accueil(g, reglages, photos, galeries, langue)
        page_galeries(g, galeries, langue)
        page_a_propos(g, reglages, langue)
        for gal in galeries:
            page_galerie(g, gal, langue)
            ecrire_flux(adr, langue, f'{gal["titre"][langue]} — {g.site.get("nom", "")}',
                        gal["description"][langue], adr.chemin(langue, "galerie", gal["cle"]),
                        adr.chemin(langue, "flux_galerie", gal["cle"]), gal["photos"], flux_max)
        for rang, p in enumerate(photos):
            precedente = photos[rang - 1] if rang > 0 else None
            suivante = photos[rang + 1] if rang + 1 < len(photos) else None
            page_photo(g, p, langue, precedente, suivante, par_photo[p["id"]])
        ecrire_flux(adr, langue, TEXTES[langue]["accueil"], reglages["accueil"].get(f"accroche_{langue}", ""),
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux"), photos)
    page_introuvable(g)
    ecrire_plan(adr, photos, galeries)
    print(f"{len(photos)} photos publiées ({sans_titre} en attente d'un titre), {len(galeries)} galeries :")
    for gal in galeries:
        print(f"  {gal['cle']} : {len(gal['photos'])} photos")


if __name__ == "__main__":
    main()
