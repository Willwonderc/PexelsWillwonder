#!/usr/bin/env python3
"""Construit le site de photographe de Karl Forterre.

1. Lit la liste des photos : vitrine/photos.txt.
2. Complète les fiches Pexels (vitrine/donnees/fiches.json) grâce à l'API, si la
   variable d'environnement PEXELS_API_KEY est définie.
3. Ajoute les parutions du jour au journal des flux Pinterest
   (vitrine/donnees/parutions.json).
4. Écrit le site statique dans le dossier _site/, avec les fichiers llms.txt pour les
   assistants IA.
5. Compare chaque page au journal des pages (vitrine/donnees/pages.json) : la date de
   sa dernière modification va dans le plan du site, et les pages nouvelles, modifiées
   ou supprimées sont à signaler aux moteurs de recherche par IndexNow.

Options :
  --fiches-seulement       ne fait que l'étape 2
  --max-appels N           nombre maximum d'appels à l'API (180 par défaut)
  --enregistrer-parutions  enregistre le journal (tâche de nuit) ; sans cette option,
                           les parutions du jour servent aux flux sans être enregistrées
  --indexnow               enregistre le journal des pages et prépare la liste des pages
                           à signaler, _indexnow/envoi.json (tâche de nuit)
  --envoyer-indexnow       envoie cette liste à IndexNow, une fois le site en ligne
                           (tâche de nuit), et ne fait rien d'autre
  --enregistrer-historique enregistre l'historique du tableau de bord (relevés Pexels et
                           semaines de GoatCounter, tâche de nuit)

Le tableau de bord (/tableau-de-bord/, non référencé) lit les relevés de releves/ et, si la
variable d'environnement GOATCOUNTER_JETON contient une clé d'API, les chiffres de GoatCounter.
À côté, /tableau-de-bord/publications.json liste pour Telepex, l'application Mac de Karl, les
publications à faire à la main (reseaux/publications/).
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
from collections import Counter
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
SORTIE = RACINE / "_site"
FICHES = ICI / "donnees" / "fiches.json"
PARUTIONS = ICI / "donnees" / "parutions.json"
PAGES = ICI / "donnees" / "pages.json"
# Pages à signaler par IndexNow, préparées par la construction et envoyées une fois le
# site en ligne (hors du site publié). Bing les transmet aux autres moteurs du protocole
# (Yandex, Seznam, Naver, Yep, Amazon…) et, contrairement à api.indexnow.org, refuse
# clairement une clé qu'il ne trouve pas.
ENVOI_INDEXNOW = RACINE / "_indexnow" / "envoi.json"
INDEXNOW = "https://www.bing.com/indexnow"
AUTRES = "autres-photos"  # flux des photos rangées dans aucune galerie
PHOTOGRAPHE = 28489473
LICENCE = "https://www.pexels.com/license/"
AUJOURDHUI = datetime.now(timezone.utc).date().isoformat()
HEBERGEUR = "GitHub, Inc."
HEBERGEUR_ADRESSE = {
    "fr": "88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis",
    "en": "88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, United States",
    "zh": "88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, 美国",
}
HEBERGEUR_TELEPHONE = "+1 877 448 4820"
# Langues du site : le bouton de l'en-tête passe de l'une à la suivante, et la dernière
# ramène à la première. Sans traduction, les pages chinoises reprennent l'anglais.
LANGUES = ("fr", "en", "zh")
SUIVANTE = {"fr": "en", "en": "zh", "zh": "fr"}
HREFLANG = {"fr": "fr", "en": "en", "zh": "zh-Hans"}
# Langues qui ont leurs flux RSS (Pinterest, bloqué en Chine, n'en lit pas d'autres).
LANGUES_FLUX = ("fr", "en")

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
        "recit_photographe": "Le récit du photographe",
        "lecon_francais": "Petit cours de français",
        "utiliser": "Utiliser mes photos",
        "mentions": "Mentions légales",
        "confidentialite": "Confidentialité",
        "faq": "Questions fréquentes",
        "faq_intro": "Licence, téléchargement, crédit, lieux, auteur : les réponses aux questions les plus "
                     "courantes sur les photos de Karl Forterre.",
        "contact": "Contact",
        "lieux_photographies": "Lieux photographiés",
        "materiel": "Matériel",
        "usages_galerie": "Utilisées dans des projets",
        "usages_ligne": "Utilisées sur {sites}",
        "usages_intro": "Pexels m'a signalé ces usages de mes photos. Ce n'est qu'une petite partie : "
                        "Pexels ne signale pas chaque téléchargement.",
        "usage_par": "Utilisée par {qui}{date}.",
        "campagne": "la campagne « {nom} »",
        "usage_photo": "Utilisée sur {sites}, d'après Pexels{date}.",
        "usages_source": "D'après Pexels",
        "campagne_court": "Campagne",
        "guillemets": "« {nom} »",
        "voir_usages": "Voir les {n}\u00a0photos et leurs usages",
        "voir_usage": "Voir la photo et ses usages",
        "voir_photo": "Voir la photo",
        "liste_et": "et",
        "auteur": "Aussi auteur",
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
        "autre_langue": "中文",
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
        "recit_photographe": "The photographer's story",
        "lecon_francais": "A little French lesson",
        "utiliser": "Use my photos",
        "mentions": "Legal notice",
        "confidentialite": "Privacy",
        "faq": "Frequently asked questions",
        "faq_intro": "License, downloads, credit, places, the photographer: answers to the most common "
                     "questions about Karl Forterre's photos.",
        "contact": "Contact",
        "lieux_photographies": "Places photographed",
        "materiel": "Equipment",
        "usages_galerie": "Used in projects",
        "usages_ligne": "Used on {sites}",
        "usages_intro": "Pexels notified me of these uses of my photos. This is only a small part: "
                        "Pexels does not report every download.",
        "usage_par": "Used by {qui}{date}.",
        "campagne": "the “{nom}” campaign",
        "usage_photo": "Used on {sites}, according to Pexels{date}.",
        "usages_source": "According to Pexels",
        "campagne_court": "Campaign",
        "guillemets": "“{nom}”",
        "voir_usages": "See the {n}\u00a0photos and their uses",
        "voir_usage": "See the photo and its uses",
        "voir_photo": "See the photo",
        "liste_et": "and",
        "auteur": "Also a writer",
        "visionneuse": "Photo viewer",
        "fermer": "Close",
        "locale": "en_US",
    },
    "zh": {
        "accueil": "Karl Forterre 摄影作品",
        "galeries": "图库",
        "series": "专题",
        "selection": "精选",
        "a_propos": "关于",
        "autre_langue": "Français",
        "themes": "主题",
        "lieux": "地点",
        "recentes": "最新照片",
        "une_photo": "1\u00a0张照片",
        "n_photos": "{n}\u00a0张照片",
        "telecharger": "在 Pexels 免费下载",
        "credit": "摄影：Karl Forterre，采用 {licence}：可免费自由使用。",
        "licence": "Pexels 许可协议",
        "numero": "Pexels 编号 {id}",
        "mots": "关键词",
        "dans": "所属图库：",
        "dans_serie": "所属专题：",
        "proches": "相似照片",
        "a_propos_galerie": "关于本图库",
        "couleurs": "颜色",
        "couleurs_photo": "颜色：",
        "couleur_description": "Karl Forterre 的{titre}，按主色调排列：免版税，可在 Pexels 免费下载。",
        "accueil_court": "首页",
        "ariane": "导航路径",
        "precedente": "上一张",
        "suivante": "下一张",
        "flux": "RSS 订阅",
        "flux_galerie": "图库 RSS 订阅",
        "autres_photos": "Karl Forterre 的更多照片",
        "suffixe": "摄影：Karl Forterre，免版税，可在 Pexels 免费下载。",
        "introuvable": "页面不存在",
        "introuvable_texte": "该页面不存在或已被删除。",
        "retour": "返回首页",
        "profil": "Pexels 主页",
        "evitement": "跳到正文",
        "menu": "主导航",
        "suivre": "在 Pexels 关注",
        "voir_pexels": "在 Pexels 查看这张照片",
        "voir_galeries": "浏览图库",
        "preuve": "在 Pexels 上已获 {vues} 次浏览、{telechargements} 次下载",
        "preuve_vues": "在 Pexels 上已获 {vues} 次浏览",
        "rappel": "这里的所有照片都可以在 Pexels 免费下载。"
                  "在 Pexels 关注 Karl Forterre，第一时间看到新作品。",
        "series_intro": "每个专题讲述一个地方或一个时刻：先是几段背景故事，再是照片，全部可在 Pexels 免费下载。",
        "galeries_intro": "按主题和地点整理的照片，全部可在 Pexels 免费下载。",
        "titre_serie": "{titre}：免版税照片",
        "autres_series": "更多专题",
        "recit_photographe": "摄影师手记",
        "lecon_francais": "法语小课堂",
        "utiliser": "使用我的照片",
        "mentions": "法律声明",
        "confidentialite": "隐私政策",
        "faq": "常见问题",
        "faq_intro": "许可协议、下载、署名、拍摄地点与摄影师：关于 Karl Forterre 照片的常见问题解答。",
        "contact": "联系方式",
        "lieux_photographies": "拍摄地点",
        "materiel": "器材",
        "usages_galerie": "项目中使用的照片",
        "usages_ligne": "曾被 {sites} 使用",
        "usages_intro": "Pexels 通知了我以下这些照片的使用情况。这只是其中一小部分：Pexels 并不通报每一次下载。",
        "usage_par": "这张照片曾被{qui}使用{date}。",
        "campagne": "“{nom}”竞选活动",
        "usage_photo": "据 Pexels 通知，这张照片曾被 {sites} 使用{date}。",
        "usages_source": "据 Pexels 通知",
        "campagne_court": "竞选活动",
        "guillemets": "“{nom}”",
        "voir_usages": "查看这 {n} 张照片及其使用情况",
        "voir_usage": "查看这张照片及其使用情况",
        "voir_photo": "查看照片",
        "liste_et": "和",
        "auteur": "作家身份",
        "visionneuse": "照片浏览器",
        "fermer": "关闭",
        "locale": "zh_CN",
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


# Descriptions des pages (balise description, que Google affiche sous le titre) : entre
# ces deux longueurs, et deux fois plus courtes en chinois, qui dit autant en moins de
# caractères. En deçà du minimum, une description passe pour trop courte.
LONGUEUR_DESCRIPTION = {"fr": (140, 160), "en": (140, 160), "zh": (70, 80)}
DESCRIPTION_COURTE = {"fr": 70, "en": 70, "zh": 35}


def resume(texte, langue):
    """Début d'un texte ramené à la longueur d'une description : coupé à la fin d'une
    phrase quand elle tombe entre les deux longueurs, sinon à la fin d'un mot (en chinois,
    après un signe de ponctuation), avec des points de suspension."""
    court, long = LONGUEUR_DESCRIPTION.get(langue, LONGUEUR_DESCRIPTION["en"])
    texte = re.sub(r"\s*\n\s*", " ", texte).strip()
    if len(texte) <= long:
        return texte
    if langue == "zh":
        extrait = texte[:long]
        for signes, suite in (("。！？", None), ("，；：、", "…"), (" ", "…")):
            fin = max(extrait.rfind(s) for s in signes)
            if fin + 1 >= court:
                return extrait[:fin + 1] if suite is None else extrait[:fin].rstrip(" ·") + suite
        return texte[:long - 1] + "…"
    extrait = texte[:long + 1]
    fin = max(extrait.rfind(s) for s in (". ", "! ", "? "))
    if fin + 1 >= court:
        return texte[:fin + 1]
    return texte[:long - 1].rsplit(" ", 1)[0].rstrip(" ,;:—") + "…"


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


def pexels(adresse, langue):
    """Lien vers Pexels dans la langue de la page : Pexels sert son interface en chinois
    simplifié sous www.pexels.com/zh-cn/ (pages de photo, profil, licence)."""
    debut = "https://www.pexels.com/"
    if langue == "zh" and adresse.startswith(debut) and not adresse.startswith(debut + "zh-cn/"):
        return debut + "zh-cn/" + adresse[len(debut):]
    return adresse


def traduit(reglage, champ, langue, defaut=""):
    """Champ « champ_langue » d'un réglage ; sans traduction chinoise, l'anglais, et sans
    anglais, le français."""
    for l in dict.fromkeys((langue, "en", "fr")):
        valeur = (reglage.get(f"{champ}_{l}") or "").strip()
        if valeur:
            return valeur
    return defaut


def lecon_francais(reglage, langue):
    """Petit cours de français d'une série (réglages francais_en, francais_zh) : pages
    anglaises et chinoises seulement, jamais les françaises ; sans traduction chinoise,
    l'anglais. Une ligne par mot, « mot français = explication » ; une ligne sans « = »
    prolonge l'explication précédente. Rend [(mot, explication)]."""
    if langue == "fr":
        return []
    texte = ""
    for l in dict.fromkeys((langue, "en")):
        texte = (reglage.get(f"francais_{l}") or "").strip()
        if texte:
            break
    mots = []
    for ligne in texte.splitlines():
        mot, egal, sens = ligne.partition("=")
        if egal and mot.strip():
            mots.append([" ".join(mot.split()), " ".join(sens.split())])
        elif ligne.strip() and mots:
            mots[-1][1] = f'{mots[-1][1]} {" ".join(ligne.split())}'.strip()
    return [(mot, sens) for mot, sens in mots if sens]


def chiffre(n, langue):
    """878500 → « 878 500 » en français (espace fine insécable), « 878,500 » en anglais."""
    texte = f"{n:,}"
    return texte.replace(",", " ") if langue == "fr" else texte


# ---------------------------------------------------------------- données


def lire_ini(nom):
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(ICI / nom, encoding="utf-8")
    return conf


def lire_usages():
    """Usages de photos par d'autres sites (usages.csv), tels que Pexels les signale :
    {numéro: [{"site", "type", "page", "date"}]}, dans l'ordre du fichier. Type « site » : un
    site web (« utilisée sur … ») ; « campagne » : une campagne (« utilisée par … »)."""
    chemin = ICI / "usages.csv"
    usages = {}
    for ligne in lire_csv(chemin) if chemin.exists() else []:
        numero, site = (ligne.get("photo") or "").strip(), (ligne.get("site") or "").strip()
        if numero.isdigit() and site:
            usages.setdefault(int(numero), []).append({
                "site": site, "type": (ligne.get("type") or "").strip().lower() or "site",
                "page": (ligne.get("page") or "").strip(),
                "date": (ligne.get("signale_le") or "").strip()})
    return usages


def lire_reseaux():
    """Profils de la rubrique [reseaux] de site.ini : [(nom, adresse)], dans l'ordre du
    fichier, les noms avec leurs majuscules (« Bluesky », « LinkedIn »)."""
    conf = configparser.ConfigParser(interpolation=None)
    conf.optionxform = str
    conf.read(ICI / "site.ini", encoding="utf-8")
    if not conf.has_section("reseaux"):
        return []
    return [(nom.strip(), adresse.strip()) for nom, adresse in conf.items("reseaux") if adresse.strip()]


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


def lire_libelles(nom):
    """Libellés d'une liste : le commentaire qui suit le numéro, jusqu'au tiret long.
    Ceux de selection.txt servent de titres courts, en français, dans le carrousel du
    site d'auteur (apercu.json)."""
    chemin = ICI / nom
    libelles = {}
    if not chemin.exists():
        return libelles
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        mots = ligne.split(maxsplit=1)
        if len(mots) < 2 or mots[0].startswith("#"):
            continue
        trouves = nombres(mots[0])
        libelle = mots[1].split(" — ")[0].strip()
        if trouves and libelle and trouves[-1] not in libelles:
            libelles[trouves[-1]] = libelle
    return libelles


def lire_photos():
    return lire_liste("photos.txt")


def lire_csv(chemin):
    # utf-8-sig : un CSV enregistré par Excel commence par un BOM, qui changerait sinon le
    # nom de la première colonne (« photo » deviendrait illisible).
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def lire_traductions(langue):
    """Titres et mots-clés traduits d'une langue : donnees/textes-<langue>.csv, colonnes
    photo, titre_<langue>, mots_cles_<langue>."""
    traductions = {}
    chemin = ICI / "donnees" / f"textes-{langue}.csv"
    if chemin.exists():
        for ligne in lire_csv(chemin):
            cle = (ligne.get("photo") or "").strip()
            if cle.isdigit():
                traductions[int(cle)] = {"titre": (ligne.get(f"titre_{langue}") or "").strip(),
                                         "mots": ligne.get(f"mots_cles_{langue}", "")}
    return traductions


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

# Fautes de frappe des mots-clés saisis sur Pexels, qui ne permet plus de les corriger :
# elles sont redressées à la lecture des fiches de suivi (pages du site, hashtags).
CORRECTIONS_MOTS = {
    "abbaye du mont-saint-micheal": "abbaye du mont-saint-michel",
    "backgound": "background",
    "backgroud": "background",
    "center-val de loire": "centre-val de loire",
    "chesse": "cheese",
    "cineamtic": "cinematic",
    "confidant": "confident",
    "headsho": "headshot",
    "ladnmark": "landmark",
    "landmamrk": "landmark",
    "organnic": "organic",
    "turquois": "turquoise",
    "vegitable": "vegetable",
    "vertial": "vertical",
}


def corriger_mots(mots):
    """Mots-clés corrigés d'après CORRECTIONS_MOTS, sans doublons."""
    resultat, vus = [], set()
    for mot in mots:
        mot = CORRECTIONS_MOTS.get(mot.lower(), mot)
        if mot.lower() not in vus:
            vus.add(mot.lower())
            resultat.append(mot)
    return resultat


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
            if (ligne.get("import") or "").strip():
                fiche["import"] = ligne["import"].strip()
            mots = corriger_mots(m for m in liste_mots(ligne.get("mots_cles")) if not ILLISIBLE.search(m))
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


def assembler_photos(ids, fiches, anglais, francais, suivi=None, chinois=None):
    """Photos publiées : fiche Pexels, titres et mots-clés de l'atelier, et, d'après la fiche
    de suivi, vues et mots-clés Pexels. Ces derniers servent à composer les galeries et à
    trouver les photos proches ; une douzaine s'affiche quand l'atelier n'en a pas donné."""
    suivi = suivi or {}
    chinois = chinois or {}
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
        zh = chinois.get(pid, {})
        titre_en = en.get("titre") or titre_pexels(fiche.get("texte"))
        if not titre_en:
            sans_titre += 1
            continue
        mots_pexels = suivi.get(pid, {}).get("mots", [])
        mots_en = liste_mots(en.get("mots"))
        mots_fr = liste_mots(fr.get("mots"))
        mots_zh = liste_mots(zh.get("mots"))
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
            "jour": suivi.get(pid, {}).get("import", ""),
            "titre": {"en": titre_en, "fr": fr.get("titre") or titre_en, "zh": zh.get("titre") or titre_en},
            # Sans mots-clés traduits, les pages française et chinoise affichent les mots anglais.
            "mots": {"en": affiches, "fr": mots_fr or affiches, "zh": mots_zh or affiches},
            "langue_mots": {"en": "en", "fr": "fr" if mots_fr else "en", "zh": "zh" if mots_zh else "en"},
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
        galeries.append({
            "cle": cle,
            "type": reglage.get("type", "theme").strip(),
            "titre": {l: traduit(reglage, "titre", l, cle) for l in LANGUES},
            "description": {l: traduit(reglage, "description", l) for l in LANGUES},
            "texte": {l: paragraphes(traduit(reglage, "texte", l)) for l in LANGUES},
            "photos": membres,
            "couverture": couverture,
            "bandeau": photo_bandeau(reglage, membres, couverture),
            "anciennes": liste_mots(reglage.get("anciennes")),
        })
    return galeries


def composer_series(conf, photos, minimum):
    """Séries racontées de series.ini : photos dans l'ordre donné, textes en trois langues,
    récit du photographe et, pour les pages anglaises et chinoises, petit cours de français."""
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
        champs = {champ: {l: traduit(reglage, champ, l, cle if champ == "titre" else "") for l in LANGUES}
                  for champ in ("titre", "lieu", "date")}
        series.append({
            "cle": cle,
            **champs,
            "texte": {l: paragraphes(traduit(reglage, "texte", l)) for l in LANGUES},
            "recit": {l: paragraphes(traduit(reglage, "recit", l)) for l in LANGUES},
            "francais": {l: lecon_francais(reglage, l) for l in LANGUES},
            "photos": membres,
            "couverture": couverture,
            "bandeau": photo_bandeau(reglage, membres, couverture),
        })
    return series


# Pages par couleur, d'après la couleur moyenne que Pexels donne pour chaque photo.
COULEURS = (
    {"cle": {"fr": "bleu", "en": "blue", "zh": "blue"}, "nom": {"fr": "Bleu", "en": "Blue", "zh": "蓝色"},
     "titre": {"fr": "Photos bleues", "en": "Blue photos", "zh": "蓝色调照片"}, "pastille": "#3d6ea6"},
    {"cle": {"fr": "vert", "en": "green", "zh": "green"}, "nom": {"fr": "Vert", "en": "Green", "zh": "绿色"},
     "titre": {"fr": "Photos vertes", "en": "Green photos", "zh": "绿色调照片"}, "pastille": "#4c7a3b"},
    {"cle": {"fr": "jaune-orange", "en": "yellow-orange", "zh": "yellow-orange"},
     "nom": {"fr": "Jaune et orange", "en": "Yellow and orange", "zh": "黄色与橙色"},
     "titre": {"fr": "Photos jaunes et orange", "en": "Yellow and orange photos", "zh": "黄橙色调照片"},
     "pastille": "#d99130"},
    {"cle": {"fr": "rouge-rose", "en": "red-pink", "zh": "red-pink"},
     "nom": {"fr": "Rouge et rose", "en": "Red and pink", "zh": "红色与粉色"},
     "titre": {"fr": "Photos rouges et roses", "en": "Red and pink photos", "zh": "红粉色调照片"}, "pastille": "#b84552"},
    {"cle": {"fr": "tons-sombres", "en": "dark-tones", "zh": "dark-tones"},
     "nom": {"fr": "Tons sombres", "en": "Dark tones", "zh": "暗色调"},
     "titre": {"fr": "Photos aux tons sombres", "en": "Dark-toned photos", "zh": "暗色调照片"}, "pastille": "#1c1c21"},
    {"cle": {"fr": "tons-clairs", "en": "light-tones", "zh": "light-tones"},
     "nom": {"fr": "Tons clairs", "en": "Light tones", "zh": "亮色调"},
     "titre": {"fr": "Photos aux tons clairs", "en": "Light-toned photos", "zh": "亮色调照片"}, "pastille": "#ebe6dc"},
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
        # Mots pris dans le même ordre à chaque construction, et scores arrondis : sans quoi
        # les arrondis de calcul changeraient d'une nuit à l'autre l'ordre des photos à égalité,
        # et la page paraîtrait modifiée (plan du site, IndexNow).
        for cle in sorted(p["cles"]):
            for autre in index[cle] if cle in poids else ():
                score[autre] = score.get(autre, 0) + poids[cle]
        for gal in par_photo[p["id"]]:
            for autre in membres[gal["cle"]]:
                score[autre] = score.get(autre, 0) + 2
        score.pop(p["id"], None)
        meilleures = sorted(score, key=lambda i: (-round(score[i], 6), -par_id[i]["vues"], -i))[:nombre]
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
        # Pages anglaises sous /en/, chinoises sous /zh/ (mêmes adresses qu'en anglais).
        en = langue != "fr"
        debut = self.base + ("" if langue == "fr" else f"/{langue}")
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
            "faq": "/faq/" if en else "/questions-frequentes/",
            # Présentation du site pour les assistants IA (llmstxt.org), une par langue.
            "llms": "/llms.txt",
            "llms_complet": "/llms-full.txt",
            "flux": "/feed.xml" if en else "/flux.xml",
            "flux_galerie": f"/galleries/{cle}/feed.xml" if en else f"/galeries/{cle}/flux.xml",
            "flux_autres": "/more-photos/feed.xml" if en else "/autres-photos/flux.xml",
            # Tableau de bord, page non référencée, en français seulement.
            "tableau": "/tableau-de-bord/",
            "compteur": "/tableau-de-bord/compteur.json",
            # Publications à faire à la main, pour Telepex, et leurs images.
            "publications": "/tableau-de-bord/publications.json",
            "publication": f"/tableau-de-bord/publications/{cle}/",
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
        f'<a class="carreau" href="{adr.chemin(langue, "photo", photo["id"])}" data-pexels="{e(pexels(photo["page"], langue))}" '
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


MOIS = {
    "fr": ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
           "octobre", "novembre", "décembre"),
    "en": ("January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December"),
}


def mois_annee(jour, langue):
    """« janvier 2026 », « January 2026 », « 2026 年 1 月 »."""
    d = date.fromisoformat(jour)
    return f"{d.year} 年 {d.month} 月" if langue == "zh" else f"{MOIS[langue][d.month - 1]} {d.year}"


def entre_parentheses(texte, langue):
    return f"（{texte}）" if langue == "zh" else f" ({texte})"


def enumeration(elements, langue):
    """« a, b et c » ; en chinois « a、b 和 c », sans espace entre deux mots chinois
    (« 摄影师和作家 ») mais avec une espace à côté d'un mot latin (« CNN.com 和 … »)."""
    if len(elements) < 2:
        return "".join(elements)
    if langue != "zh":
        return ", ".join(elements[:-1]) + f' {TEXTES[langue]["liste_et"]} ' + elements[-1]
    debut, fin = "、".join(elements[:-1]), elements[-1]

    def latin(texte, bout):
        texte = re.sub(r"<[^>]+>", "", texte)
        return bool(texte) and texte[bout].isascii()

    return (debut + (" " if latin(debut, -1) else "") + TEXTES[langue]["liste_et"]
            + (" " if latin(fin, 0) else "") + fin)


def designation(usage, langue):
    """Nom affiché d'un usage : le site (lien vers la page exacte s'il est connu), ou
    « la campagne « … » »."""
    nom = e(usage["site"])
    if usage["type"] == "campagne":
        nom = TEXTES[langue]["campagne"].format(nom=nom)
    return f'<a href="{e(usage["page"])}">{nom}</a>' if usage["page"] else nom


def phrases_usages(usages, langue):
    """« Utilisée sur CNN.com …, d'après Pexels (janvier 2026). » et « Utilisée par … »."""
    t = TEXTES[langue]
    sites = [u for u in usages if u["type"] == "site"]
    autres = [u for u in usages if u["type"] != "site"]
    phrases = []
    if sites:
        phrases.append(t["usage_photo"].format(sites=enumeration([designation(u, langue) for u in sites], langue),
                                               date=date_usages(sites, langue)))
    if autres:
        phrases.append(t["usage_par"].format(qui=enumeration([designation(u, langue) for u in autres], langue),
                                             date=date_usages(autres, langue)))
    return " ".join(phrases)


def date_usages(usages, langue):
    """Mois du dernier signalement, entre parenthèses, ou rien."""
    dates = [u["date"] for u in usages if u["date"]]
    return entre_parentheses(mois_annee(max(dates), langue), langue) if dates else ""


def ligne_usages(g, langue, classe="preuve"):
    """« Utilisées sur CNN.com, … », lien vers la page des photos utilisées ; sans classe
    dans le pied de page de l'accueil, dont elle prend l'allure discrète."""
    sites = list(dict.fromkeys(u["site"] for usages in g.usages.values() for u in usages if u["type"] == "site"))
    if not sites:
        return ""
    texte = TEXTES[langue]["usages_ligne"].format(sites=enumeration(sites, langue))
    attribut = f' class="{classe}"' if classe else ""
    return f'<p{attribut}><a href="{g.adr.chemin(langue, "galerie", CLE_USAGES)}">{e(texte)}</a></p>'


def preuve_sociale(preuve, langue):
    """« 878 500 vues et 3 950 téléchargements sur Pexels », d'après les relevés."""
    t = TEXTES[langue]
    if preuve["vues"] and preuve["telechargements"]:
        return t["preuve"].format(vues=chiffre(preuve["vues"], langue),
                                  telechargements=chiffre(preuve["telechargements"], langue))
    if preuve["vues"]:
        return t["preuve_vues"].format(vues=chiffre(preuve["vues"], langue))
    return ""


# Tirage de la rubrique « Sélection » de l'accueil, à chaque visite : autant de photos que
# la sélection fixe, prises au hasard parmi les plus vues sur Pexels, au plus deux d'un même
# jour d'import (une même sortie), pour varier les sujets. Placé juste après la grille, le
# script la remplace avant que ses images, chargées à la demande, ne partent ; sans
# JavaScript, la sélection fixe de selection.txt reste affichée.
TIRAGE_JS = """(function () {
  var source = document.getElementById("tirage-selection");
  var grille = document.querySelector("#selection .grille");
  if (!source || !grille || !window.JSON) return;
  var photos = JSON.parse(source.textContent), n = grille.children.length;
  for (var i = photos.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1)), x = photos[i];
    photos[i] = photos[j];
    photos[j] = x;
  }
  var parJour = {}, choix = [];
  for (var k = 0; k < photos.length && choix.length < n; k++) {
    var jour = photos[k].g;
    if ((parJour[jour] || 0) < 2) {
      parJour[jour] = (parJour[jour] || 0) + 1;
      choix.push(photos[k]);
    }
  }
  if (choix.length < n) return;
  var largeurs = [300, 600, 900, 1300], morceau = document.createDocumentFragment();
  choix.forEach(function (p) {
    var lien = document.createElement("a"), img = document.createElement("img");
    var base = p.i + "?auto=compress&cs=tinysrgb&w=";
    lien.className = "carreau";
    lien.href = p.h;
    lien.setAttribute("data-pexels", p.x);
    lien.style.setProperty("--r", p.r);
    lien.style.backgroundColor = p.c;
    img.loading = "lazy";
    img.decoding = "async";
    img.width = p.l;
    img.height = p.u;
    img.alt = p.t;
    img.sizes = "(max-width: 640px) 60vw, 30vw";
    img.srcset = largeurs.map(function (l) { return base + l + " " + l + "w"; }).join(", ");
    img.src = base + 600;
    lien.appendChild(img);
    morceau.appendChild(lien);
  });
  while (grille.firstChild) grille.removeChild(grille.firstChild);
  grille.appendChild(morceau);
})();"""


def tirage_selection(g, photos, nombre, langue):
    """Données et script du tirage de la « Sélection » (TIRAGE_JS) : les « nombre » photos
    les plus vues sur Pexels, avec ce qu'il faut pour en faire des vignettes."""
    adr = g.adr
    plus_vues = [p for p in sorted(photos, key=lambda p: (-p["vues"], -p["id"])) if p["vues"]][:nombre]
    donnees = [{
        "h": adr.chemin(langue, "photo", p["id"]),
        "x": pexels(p["page"], langue),
        "r": f'{p["largeur"] / p["hauteur"]:.3f}',
        "c": p["couleur"],
        "i": p["image"],
        "l": p["largeur"],
        "u": p["hauteur"],
        "t": p["titre"][langue],
        "g": p.get("jour") or str(p["id"]),
    } for p in plus_vues]
    texte = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="tirage-selection">{texte}</script><script>{TIRAGE_JS}</script>'


def rappel(g, langue, usages=True):
    """Rappel « Suivre sur Pexels » en fin de galerie, de série et de page ; « usages » :
    avec la ligne qui mène aux photos utilisées dans des projets (sauf sur cette page)."""
    t = TEXTES[langue]
    preuve = preuve_sociale(g.preuve, langue)
    return (
        f'<aside class="rappel"><p>{t["rappel"]}</p>'
        f'<p><a class="bouton" href="{e(pexels(g.site.get("profil_pexels", ""), langue))}" '
        f'data-goatcounter-click="suivre-pexels-fin">{t["suivre"]}</a></p>'
        + (f'<p class="preuve">{e(preuve)}</p>' if preuve else "")
        + (ligne_usages(g, langue) if usages else "")
        + "</aside>"
    )


def jsonld(donnees):
    texte = json.dumps(donnees, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{texte}</script>'


def profils(g):
    """Adresses qui désignent l'auteur ailleurs : profil Pexels, site d'auteur, réseaux de
    la rubrique [reseaux] et autres profils de la rubrique [personne] (Wikidata…)."""
    p = g.reglages["personne"] if g.reglages.has_section("personne") else {}
    adresses = [g.site.get("profil_pexels", ""), site_auteur(g), *(a for _, a in g.reseaux),
                *liste_mots(p.get("profils"))]
    return list(dict.fromkeys(a.strip() for a in adresses if a.strip()))


def site_auteur(g):
    adresse = g.site.get("site_personnel", "").strip()
    return adresse.rstrip("/") + "/" if adresse else ""


def personne(g, langue, complete=False):
    """L'auteur dans les données structurées (schema.org Person). Son identifiant (@id),
    le même que dans les données de karlforterre.fr, fait des deux sites, du profil Pexels
    et des réseaux une seule et même personne pour les moteurs et les assistants IA.
    « complete » : la fiche entière (accueil, À propos) ; sinon une référence."""
    p = g.reglages["personne"] if g.reglages.has_section("personne") else {}
    fiche = {"@type": "Person"}
    if (p.get("identifiant") or "").strip():
        fiche["@id"] = p["identifiant"].strip()
    fiche["name"] = g.site.get("nom", "Karl Forterre")
    if site_auteur(g):
        fiche["url"] = site_auteur(g)
    if not complete:
        return fiche
    for champ, cle in (("givenName", "prenom"), ("familyName", "nom_de_famille"), ("image", "portrait")):
        if (p.get(cle) or "").strip():
            fiche[champ] = p[cle].strip()
    metiers = liste_mots(traduit(p, "metier", langue))
    if metiers:
        fiche["jobTitle"] = metiers if len(metiers) > 1 else metiers[0]
    presentation = paragraphes(traduit(g.reglages["a-propos"], "texte", langue))
    if presentation:
        fiche["description"] = presentation[0]
    contact = g.reglages["mentions"].get("contact", "").strip() if g.reglages.has_section("mentions") else ""
    if contact:
        fiche["email"] = f"mailto:{contact}"
    lieu = traduit(p, "lieu", langue)
    if lieu:
        fiche["homeLocation"] = {"@type": "Place", "name": lieu}
    if (p.get("nationalite") or "").strip():
        fiche["nationality"] = {"@type": "Country", "name": p["nationalite"].strip()}
    if (p.get("formation") or "").strip():
        fiche["alumniOf"] = {"@type": "CollegeOrUniversity", "name": p["formation"].strip()}
    domaines = liste_mots(traduit(p, "domaines", langue))
    if domaines:
        fiche["knowsAbout"] = domaines
    fiche["sameAs"] = profils(g)
    return fiche


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
        self.reseaux = lire_reseaux()
        self.usages = {}
        empreinte = hashlib.md5()
        for nom in ("style.css", "site.js"):
            empreinte.update((ICI / "statique" / nom).read_bytes())
        self.version = empreinte.hexdigest()[:8]

    def statique(self, nom):
        return f"{self.adr.base}/statique/{nom}"

    def visionneuse(self, langue):
        """Visionneuse plein écran, remplie par statique/site.js au clic sur une vignette."""
        t = TEXTES[langue]
        profil = e(pexels(self.site.get("profil_pexels", ""), langue))
        return (
            f'<dialog class="visionneuse" aria-label="{t["visionneuse"]}">'
            f'<div class="v-cadre"><a class="v-image" href="{profil}" '
            f'title="{t["voir_pexels"]}" data-goatcounter-click="pexels-image">'
            '<img class="v-apercu" alt=""><img class="v-grande" alt=""></a></div>'
            '<div class="v-barre"><p class="v-titre"><a href=""></a></p>'
            f'<p><a class="bouton v-pexels" href="{profil}" '
            f'data-goatcounter-click="pexels">{t["telecharger"]}</a></p></div>'
            '<p class="v-rang" aria-live="polite"></p>'
            f'<button type="button" class="v-bouton v-precedente" aria-label="{t["precedente"]}">{icone("precedente")}</button>'
            f'<button type="button" class="v-bouton v-suivante" aria-label="{t["suivante"]}">{icone("suivante")}</button>'
            f'<button type="button" class="v-bouton v-fermer" aria-label="{t["fermer"]}">{icone("fermer")}</button>'
            "</dialog>"
        )

    def page(self, langue, *, titre, description, chemins, contenu, image=None, donnees=None,
             flux=None, classe="", titre_complet=False, series=True, prive=(), pied_haut=""):
        """« prive » : feuilles de style et scripts d'une page non référencée (le tableau de
        bord), qui n'a ni indexation, ni traductions, ni compteur GoatCounter. « pied_haut » :
        paragraphe placé en tête du pied de page (les usages, sur l'accueil)."""
        t = TEXTES[langue]
        autre = SUIVANTE[langue]
        adr = self.adr
        nom = self.site.get("nom", "Karl Forterre")
        titre_page = titre if titre_complet else f"{titre} — {nom}"
        url = adr.absolue(chemins[langue])
        profil = e(pexels(self.site.get("profil_pexels", ""), langue))
        if prive:
            tete = self.tete_privee(titre_page, prive)
        else:
            tete = self.tete(langue, titre, titre_page, description, chemins, url, image, donnees, flux)

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
            + ("" if prive else
               f'<a class="langue" href="{chemins[autre]}" hreflang="{HREFLANG[autre]}" lang="{HREFLANG[autre]}">'
               f'{t["autre_langue"]}</a>')
            + f'<a class="suivre" href="{profil}" data-goatcounter-click="suivre-pexels">{t["suivre"]}</a>'
            f"</nav></header>"
        )
        annee = datetime.now(timezone.utc).year
        pied = (
            '<footer class="pied">'
            + pied_haut
            + f'<p><a href="{pexels("https://www.pexels.com/", langue)}">Photos provided by Pexels</a></p>'
            f'<p><a href="{adr.chemin(langue, "utiliser")}">{t["utiliser"]}</a>'
            f' · <a href="{adr.chemin(langue, "faq")}">{t["faq"]}</a>'
            f' · <a href="{adr.chemin(langue, "mentions")}">{t["mentions"]}</a>'
            f' · <a href="{adr.chemin(langue, "confidentialite")}">{t["confidentialite"]}</a></p>'
            f'<p>© {annee} {e(nom)} · <a href="{profil}">{t["profil"]}</a>'
            f' · <a href="{e(self.site.get("site_personnel", ""))}">{e(urlparse(self.site.get("site_personnel", "")).netloc)}</a>'
            + "".join(f' · <a rel="me" href="{e(adresse)}">{e(nom)}</a>' for nom, adresse in self.reseaux)
            + (f' · <a href="{adr.chemin(langue, "flux")}">{t["flux"]}</a>' if langue in LANGUES_FLUX else "")
            + "</p></footer>"
        )
        visionneuse = self.visionneuse(langue) if 'class="grille' in contenu else ""
        return (
            f'<!doctype html>\n<html lang="{HREFLANG[langue]}"><head>' + "".join(tete) + "</head>"
            f'<body class="{classe}">{entete}<main id="contenu">{contenu}</main>{pied}{visionneuse}</body></html>\n'
        )

    def tete_privee(self, titre_page, fichiers):
        """En-tête d'une page non référencée : ni moteurs, ni traductions, ni GoatCounter, qui
        compterait les visites de Karl."""
        def version(nom):
            return hashlib.md5((ICI / "statique" / nom).read_bytes()).hexdigest()[:8]

        return [
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{e(titre_page)}</title>",
            '<meta name="robots" content="noindex, nofollow">',
            f'<link rel="preload" href="{self.statique("archivo.woff2")}" as="font" type="font/woff2" crossorigin>',
            f'<link rel="stylesheet" href="{self.statique("style.css")}?v={self.version}">',
            *(f'<link rel="stylesheet" href="{self.statique(nom)}?v={version(nom)}">'
              for nom in fichiers if nom.endswith(".css")),
            *(f'<script src="{self.statique(nom)}?v={version(nom)}" defer></script>'
              for nom in fichiers if nom.endswith(".js")),
            f'<link rel="icon" href="{self.statique("favicon.svg")}" type="image/svg+xml">',
            f'<link rel="apple-touch-icon" href="{self.statique("icone-180.png")}">',
        ]

    def tete(self, langue, titre, titre_page, description, chemins, url, image, donnees, flux):
        t = TEXTES[langue]
        adr = self.adr
        nom = self.site.get("nom", "Karl Forterre")
        tete = [
            f'<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{e(titre_page)}</title>",
            f'<meta name="description" content="{e(resume(description, langue))}">',
            f'<link rel="canonical" href="{url}">',
            *(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{adr.absolue(chemins[l])}">' for l in LANGUES),
            f'<link rel="alternate" hreflang="x-default" href="{adr.absolue(chemins["fr"])}">',
            f'<meta http-equiv="content-language" content="{HREFLANG[langue]}">',
            f'<meta property="og:site_name" content="{e(nom)}">',
            f'<meta property="og:type" content="website">',
            f'<meta property="og:locale" content="{t["locale"]}">',
            f'<meta property="og:title" content="{e(titre)}">',
            f'<meta property="og:description" content="{e(resume(description, langue))}">',
            f'<meta property="og:url" content="{url}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<link rel="preload" href="{self.statique("archivo.woff2")}" as="font" type="font/woff2" crossorigin>',
            f'<link rel="stylesheet" href="{self.statique("style.css")}?v={self.version}">',
            f'<script src="{self.statique("site.js")}?v={self.version}" defer></script>',
            f'<link rel="icon" href="{self.statique("favicon.svg")}" type="image/svg+xml">',
            f'<link rel="apple-touch-icon" href="{self.statique("icone-180.png")}">',
            # Présentation du site pour les assistants IA (llms.txt de la langue de la page).
            f'<link rel="describedby" href="{adr.chemin(langue, "llms")}" type="text/markdown">',
        ]
        if langue in LANGUES_FLUX:
            tete.append(f'<link rel="alternate" type="application/rss+xml" title="{e(t["flux"])}" '
                        f'href="{flux or adr.chemin(langue, "flux")}">')
        if image:
            tete += [
                f'<meta property="og:image" content="{url_image(image, 1200)}">',
                f'<meta property="og:image:alt" content="{e(image["titre"][langue])}">',
            ]
        for _, adresse in self.reseaux:
            tete.append(f'<link rel="me" href="{e(adresse)}">')
        if self.site.get("google_verification", "").strip():
            tete.append(f'<meta name="google-site-verification" content="{e(self.site["google_verification"].strip())}">')
        if self.site.get("bing_verification", "").strip():
            tete.append(f'<meta name="msvalidate.01" content="{e(self.site["bing_verification"].strip())}">')
        if self.site.get("pinterest_verification", "").strip():
            tete.append(f'<meta name="p:domain_verify" content="{e(self.site["pinterest_verification"].strip())}">')
        code = self.site.get("goatcounter", "").strip()
        if code:
            tete.append(f'<script data-goatcounter="https://{e(code)}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>')
        for bloc in donnees or []:
            tete.append(jsonld(bloc))
        return tete


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
    accroche = traduit(g.reglages["accueil"], "accroche", langue)
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
        f'<a class="bouton bouton-contour" href="{e(pexels(g.site.get("profil_pexels", ""), langue))}" '
        f'data-goatcounter-click="suivre-pexels-accueil">{t["suivre"]}</a></p>'
        + (f'<p class="preuve">{e(preuve)}</p>' if preuve else "")
        + "</div></section>"
    )


def page_accueil(g, photos, galeries, series, selection, ouverture, langue):
    adr = g.adr
    t = TEXTES[langue]
    accroche = traduit(g.reglages["accueil"], "accroche", langue)
    # Titre et description pour les moteurs (réglages titre_* et description_* de
    # [accueil]) ; à défaut, le titre du site et l'accroche.
    titre = traduit(g.reglages["accueil"], "titre", langue, t["accueil"])
    description = traduit(g.reglages["accueil"], "description", langue, accroche)
    tirage = entier(g.reglages["accueil"].get("tirage"))
    rubrique_selection = ""
    if selection:
        rubrique_selection = (
            f'<section class="bloc" id="selection"><h2 class="surtitre">{t["selection"]}</h2>'
            + grille(selection, langue, adr)
            + (tirage_selection(g, photos, tirage, langue) if tirage else "")
            + "</section>"
        )
    contenu = (
        ouverture_accueil(g, ouverture, langue)
        + '<div class="enveloppe">'
        + rubrique_selection
        + cartes_series(series, langue, adr)
        + cartes(galeries, langue, adr, "theme")
        + cartes(galeries, langue, adr, "lieu")
        + f'<section class="bloc"><h2 class="surtitre">{t["recentes"]}</h2>{grille(photos[:12], langue, adr)}</section>'
        + "</div>"
    )
    nom = g.site.get("nom", "Karl Forterre")
    auteur = personne(g, langue, complete=True)
    reference = {"@id": auteur["@id"]} if "@id" in auteur else auteur
    site = {
        "@type": "WebSite",
        "@id": adr.absolue(adr.chemin("fr", "accueil")) + "#site",
        "name": nom,
        "alternateName": t["accueil"],
        "description": description,
        "url": adr.absolue(adr.chemin(langue, "accueil")),
        "inLanguage": HREFLANG[langue],
        "author": reference,
        "publisher": reference,
    }
    donnees = [{"@context": "https://schema.org", "@graph": [site, auteur] if "@id" in auteur else [site]}]
    chemins = {l: adr.chemin(l, "accueil") for l in LANGUES}
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=(ouverture or photos or [None])[0], donnees=donnees,
                   classe="accueil sur-photo" if ouverture else "accueil",
                   titre_complet=True, series=bool(series), pied_haut=ligne_usages(g, langue, classe=""))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_galeries(g, galeries, series, couleurs, langue, par_id=None):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "galeries") for l in LANGUES}
    ariane, donnees_ariane = fil_ariane(adr, langue, [], (t["galeries"], chemins[langue]))
    index = index_usages(g, par_id or {}, langue)
    suite = (cartes(galeries, langue, adr, "theme") + cartes(galeries, langue, adr, "lieu")
             + pastilles(couleurs, galeries, langue, adr))
    if galeries:
        contenu = (bandeau(g, bandeau_index(galeries), langue, t["galeries"], e(t["galeries_intro"]), ariane)
                   + index + f'<div class="enveloppe">{suite}</div>')
    else:
        contenu = f'<section class="ouverture">{ariane}<h1>{t["galeries"]}</h1></section>' + index + suite
    description = " · ".join(gal["titre"][langue] for gal in galeries)
    texte = g.page(langue, titre=t["galeries"], description=description, chemins=chemins, contenu=contenu,
                   image=galeries[0]["couverture"] if galeries else None, donnees=[donnees_ariane],
                   series=bool(series), classe="sur-photo" if galeries else "")
    ecrire(adr.fichier(chemins[langue]), texte)


# Page des photos utilisées dans des projets, rangée parmi les galeries.
CLE_USAGES = "photos-utilisees"


def nom_usage(usage, langue, coupure=True):
    """Nom d'un usage écrit en grand : le site, ou la campagne entre guillemets.
    « coupure » : un nom trop long pour la ligne passe à la ligne avant son extension
    (« TheFreeDictionary / .com »)."""
    if usage["type"] == "campagne":
        return e(TEXTES[langue]["guillemets"].format(nom=usage["site"]))
    debut, point, fin = usage["site"].rpartition(".")
    return f"{e(debut)}<wbr>.{e(fin)}" if coupure and point and debut else e(usage["site"])


def cadrage(photo):
    """Partie gardée d'une photo recadrée : le centre d'une photo en largeur, le haut d'une
    photo en hauteur, où se trouve le plus souvent le sujet."""
    return "50% 50%" if en_largeur(photo) else "50% 25%"


def index_usages(g, par_id, langue):
    """Rubrique de la page des galeries, sur fond noir : une bande par photo utilisée, avec
    le nom du site ou de la campagne en très grand, lien vers la page de la photo. Quand
    plusieurs l'ont utilisée, leurs noms partagent la bande : statique/site.js les y fait
    défiler comme au générique (sans lui, ils s'y suivent l'un sous l'autre). Au survol ou au
    clavier, la photo remplit la rubrique : statique/site.js ne la charge qu'au premier
    passage (modèle <template>). Sur un écran tactile ou étroit, chaque bande a sa vignette."""
    utilisees = [(par_id[i], u) for i, u in g.usages.items() if i in par_id]
    if not utilisees:
        return ""
    t = TEXTES[langue]
    adr = g.adr
    lignes = []
    for p, usages in utilisees:
        fond = (f'<img src="{url_image(p, 1600)}" srcset="{srcset(p, (1200, 1600, 2200))}" '
                f'sizes="(min-width: 1800px) 100vw, 50vw" '
                f'width="{p["largeur"]}" height="{p["hauteur"]}" alt="" decoding="async">')
        campagnes = all(u["type"] == "campagne" for u in usages)
        titre = e(p["titre"][langue])
        infos = f'{e(t["campagne_court"])} · {titre}' if campagnes else titre
        # Mois du signalement : une fois s'il est le même pour toute la bande, sinon celui
        # de chaque nom, qui alterne avec lui ; « Campagne » le précède dans une bande mêlée.
        quand = [" · ".join(([t["campagne_court"]] if u["type"] == "campagne" and not campagnes else [])
                            + ([mois_annee(u["date"], langue)] if u["date"] else []))
                 for u in usages]
        if len(set(quand)) == 1:
            quand = quand[:1]
        noms = " ".join(f"<span>{nom_usage(u, langue)}</span>" for u in usages)
        mois = "".join(f"<span>{e(q)}</span>" for q in quand)
        lignes.append(
            f'<li><a class="index-ligne" href="{adr.chemin(langue, "photo", p["id"])}" '
            f'style="--pos:{cadrage(p)};--c:{e(p["couleur"])}">'
            f'<span class="index-fond"><template>{fond}</template></span>'
            f'<span class="index-vignette"><img src="{url_image(p, 240)}" width="{p["largeur"]}" '
            f'height="{p["hauteur"]}" alt="" loading="lazy" decoding="async"></span>'
            f'<span class="index-nom">{noms}</span>'
            f'<span class="index-infos"><span class="index-titre">{infos}</span>'
            + (f'<span class="index-quand">{mois}</span>' if any(quand) else "")
            + "</span></a></li>"
        )
    n = len(utilisees)
    suite = t["voir_usages"].format(n=n) if n > 1 else t["voir_usage"]
    return (
        '<section class="index-usages" aria-labelledby="titre-usages"><div class="enveloppe">'
        f'<div class="index-tete"><h2 class="surtitre" id="titre-usages">{e(t["usages_galerie"])}</h2>'
        f'<p class="index-note">{e(t["usages_source"])} · {nombre_photos(n, langue)}</p></div>'
        f'<ol class="index-liste">{"".join(lignes)}</ol>'
        f'<p class="index-suite"><a href="{adr.chemin(langue, "galerie", CLE_USAGES)}">{e(suite)} →</a></p>'
        "</div></section>"
    )


def salle(p, usages, rang, total, langue, adr):
    """Une photo de l'exposition des photos utilisées : l'image entière d'un côté, son
    cartel de l'autre (noms des sites en grand, titre, usages d'après Pexels, lien vers sa
    page). Une photo sur deux passe à droite ; une lueur reprend sa couleur moyenne."""
    t = TEXTES[langue]
    lien = adr.chemin(langue, "photo", p["id"])
    classes = "salle" + (" salle-inverse" if rang % 2 == 0 else "") + ("" if en_largeur(p) else " salle-portrait")
    tailles = "(max-width: 640px) 92vw, " + ("56vw" if en_largeur(p) else "40vw")
    noms = "".join(f"<span>{nom_usage(u, langue)}</span>" for u in usages)
    return (
        f'<section class="{classes}" id="photo-{p["id"]}" style="--c:{e(p["couleur"])}">'
        f'<figure class="salle-oeuvre"><a href="{lien}">'
        f'<img src="{url_image(p, 1600)}" srcset="{srcset(p, (800, 1200, 1600, 2200, 3000))}" sizes="{tailles}" '
        f'width="{p["largeur"]}" height="{p["hauteur"]}" alt="{e(p["titre"][langue])}" loading="lazy" '
        f'decoding="async" style="background-color:{e(p["couleur"])}"></a></figure>'
        '<div class="salle-cartel">'
        f'<p class="salle-rang">{rang} / {total}</p>'
        f'<h2 class="salle-noms">{noms}</h2>'
        f'<p class="salle-titre">{e(p["titre"][langue])}</p>'
        f'<p class="salle-usages">{phrases_usages(usages, langue)}</p>'
        f'<p class="salle-lien"><a href="{lien}">{t["voir_photo"]} →</a></p>'
        "</div></section>"
    )


def accrochee(p, usages, rang, langue):
    """Une photo accrochée au mur de l'ouverture de l'exposition, entière, avec son petit
    cartel (les noms des sites, le mois du signalement) ; elle mène à sa salle, plus bas
    dans la page."""
    noms = " · ".join(nom_usage(u, langue, coupure=False) for u in usages)
    dates = [u["date"] for u in usages if u["date"]]
    tailles = "(max-width: 640px) 46vw, " + ("26vw" if en_largeur(p) else "12vw")
    return (
        f'<a class="accrochee" href="#photo-{p["id"]}" '
        f'style="--r:{p["largeur"] / p["hauteur"]:.3f};--pos:{cadrage(p)};--i:{rang - 1}">'
        f'<img src="{url_image(p, 800)}" srcset="{srcset(p, (400, 800, 1200))}" sizes="{tailles}" '
        f'width="{p["largeur"]}" height="{p["hauteur"]}" alt="{e(p["titre"][langue])}" decoding="async" '
        f'style="background-color:{e(p["couleur"])}">'
        f'<span class="accrochee-cartel"><span class="accrochee-noms">{noms}</span>'
        + (f'<span class="accrochee-date">{mois_annee(max(dates), langue)}</span>' if dates else "")
        + "</span></a>"
    )


def page_usages(g, par_id, series, langue):
    """Page des photos utilisées dans des projets, présentée comme une exposition : à
    l'ouverture, les photos accrochées côte à côte sur un mur noir, chacune menant à sa
    salle ; puis une photo par écran, entière, avec son cartel."""
    adr = g.adr
    t = TEXTES[langue]
    utilisees = [(par_id[i], u) for i, u in g.usages.items() if i in par_id]
    if not utilisees:
        return
    chemins = {l: adr.chemin(l, "galerie", CLE_USAGES) for l in LANGUES}
    titre = t["usages_galerie"]
    ariane, donnees_ariane = fil_ariane(adr, langue, [(t["galeries"], adr.chemin(langue, "galeries"))],
                                        (titre, chemins[langue]))
    photos = [p for p, _ in utilisees]
    mur = "".join(accrochee(p, u, rang, langue) for rang, (p, u) in enumerate(utilisees, 1))
    contenu = (
        f'<section class="salle-ouverture">{ariane}<h1>{e(titre)}</h1>'
        f'<div class="accrochage">{mur}</div>'
        f'<p class="accroche">{e(t["usages_intro"])} <span class="nombre">{nombre_photos(len(photos), langue)}</span></p>'
        "</section>"
        + "".join(salle(p, u, rang, len(utilisees), langue, adr) for rang, (p, u) in enumerate(utilisees, 1))
        + f'<div class="enveloppe">{rappel(g, langue, usages=False)}</div>'
    )
    auteur = personne(g, langue)
    reference = {"@id": auteur["@id"]} if "@id" in auteur else auteur
    nom = g.site.get("nom", "Karl Forterre")
    donnees = [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": titre,
        "description": t["usages_intro"],
        "url": adr.absolue(chemins[langue]),
        "inLanguage": HREFLANG[langue],
        "author": auteur,
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(photos),
            "itemListElement": [{
                "@type": "ListItem",
                "position": rang,
                "item": {
                    "@type": "ImageObject",
                    "name": p["titre"][langue],
                    "url": adr.absolue(adr.chemin(langue, "photo", p["id"])),
                    "contentUrl": p["image"],
                    "creator": reference,
                    "creditText": f"{nom} / Pexels",
                    "license": LICENCE,
                    "acquireLicensePage": pexels(p["page"], langue),
                },
            } for rang, p in enumerate(photos, 1)],
        },
    }, donnees_ariane]
    texte = g.page(langue, titre=titre, description=t["usages_intro"], chemins=chemins, contenu=contenu,
                   image=photos[0], donnees=donnees, series=bool(series), classe="sur-photo exposition")
    ecrire(adr.fichier(chemins[langue]), texte)


def ecrire_renvois(g, galeries, langue):
    """Pages de renvoi des anciennes adresses d'une galerie (réglage « anciennes ») dans
    une langue : elles mènent aussitôt à la nouvelle adresse et la donnent pour adresse de
    référence. Elles restent hors du plan du site et du journal des pages."""
    adr = g.adr
    actuelles = {gal["cle"] for gal in galeries}
    for gal in galeries:
        for ancienne in gal["anciennes"]:
            if ancienne in actuelles:
                continue
            nouvelle = adr.chemin(langue, "galerie", gal["cle"])
            titre = e(f'{gal["titre"][langue]} — {g.site.get("nom", "Karl Forterre")}')
            ecrire(adr.fichier(adr.chemin(langue, "galerie", ancienne)),
                   f'<!doctype html>\n<html lang="{HREFLANG[langue]}"><head><meta charset="utf-8">'
                   f"<title>{titre}</title>"
                   f'<link rel="canonical" href="{e(adr.absolue(nouvelle))}">'
                   f'<meta http-equiv="refresh" content="0; url={e(nouvelle)}">'
                   f'</head><body><p><a href="{e(nouvelle)}">{titre}</a></p></body></html>\n')


def page_galerie(g, galerie, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "galerie", galerie["cle"]) for l in LANGUES}
    flux = adr.chemin(langue, "flux_galerie", galerie["cle"])
    description = galerie["description"][langue] or galerie["titre"][langue]
    ariane, donnees_ariane = fil_ariane(adr, langue, [(t["galeries"], adr.chemin(langue, "galeries"))],
                                        (galerie["titre"][langue], chemins[langue]))
    texte_galerie = galerie["texte"][langue]
    accroche = f'{e(description)} <span class="nombre">{nombre_photos(len(galerie["photos"]), langue)}</span>'
    # Pour les moteurs : le début du texte de la galerie, plus parlant que la ligne courte.
    if texte_galerie:
        description = resume(" ".join(texte_galerie), langue)
    contenu = (
        bandeau(g, galerie["bandeau"], langue, galerie["titre"][langue], accroche, ariane)
        + '<div class="enveloppe">'
        + grille(galerie["photos"], langue, adr)
        + (f'<section class="texte galerie-texte"><h2 class="surtitre">{t["a_propos_galerie"]}</h2>'
           + "".join(f"<p>{e(para)}</p>" for para in texte_galerie) + "</section>" if texte_galerie else "")
        + (f'<p class="flux-lien"><a href="{flux}">{t["flux_galerie"]}</a></p>' if langue in LANGUES_FLUX else "")
        + rappel(g, langue)
        + "</div>"
    )
    donnees = [{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": galerie["titre"][langue],
        "description": description,
        "url": adr.absolue(chemins[langue]),
        "inLanguage": HREFLANG[langue],
        "author": personne(g, langue),
    }, donnees_ariane]
    texte = g.page(langue, titre=galerie["titre"][langue], description=description, chemins=chemins,
                   contenu=contenu, image=galerie["couverture"], donnees=donnees, flux=flux, series=bool(series),
                   classe="sur-photo")
    ecrire(adr.fichier(chemins[langue]), texte)


def page_couleur(g, couleur, couleurs, galeries, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "couleur", couleur["cle"][l]) for l in LANGUES}
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
        "inLanguage": HREFLANG[langue],
        "author": personne(g, langue),
    }, donnees_ariane]
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=couleur["couverture"], donnees=donnees, series=bool(series))
    ecrire(adr.fichier(chemins[langue]), texte)


def page_series(g, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    chemins = {l: adr.chemin(l, "series") for l in LANGUES}
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
    chemins = {l: adr.chemin(l, "serie", serie["cle"]) for l in LANGUES}
    titre = serie["titre"][langue]
    texte_serie = serie["texte"][langue]
    recit = serie["recit"][langue]
    lecon = serie["francais"][langue]
    description = texte_serie[0] if texte_serie else titre
    ariane, donnees_ariane = fil_ariane(adr, langue, [(t["series"], adr.chemin(langue, "series"))], (titre, chemins[langue]))
    # Avant les photos : le texte (chapeau, puis paragraphes), le récit du photographe et,
    # sur les pages anglaises et chinoises seulement, le petit cours de français.
    corps = (
        (f'<p class="chapeau">{e(texte_serie[0])}</p>' + "".join(f"<p>{e(p)}</p>" for p in texte_serie[1:])
         if texte_serie else "")
        + (f'<section class="serie-recit"><h2 class="surtitre">{e(t["recit_photographe"])}</h2>'
           + "".join(f"<p>{e(p)}</p>" for p in recit) + "</section>" if recit else "")
        + (f'<section class="lecon"><h2 class="surtitre">{e(t["lecon_francais"])}</h2><dl>'
           + "".join(f'<div><dt lang="fr">{e(mot)}</dt><dd>{e(sens)}</dd></div>' for mot, sens in lecon)
           + "</dl></section>" if lecon else "")
    )
    contenu = (
        bandeau(g, serie["bandeau"], langue, titre, e(infos_serie(serie, langue)), ariane, plein_ecran=True)
        + '<div class="enveloppe">'
        + (f'<div class="texte serie-texte">{corps}</div>' if corps else "")
        + grille(serie["photos"], langue, adr, grand=True)
        + rappel(g, langue)
        + cartes_series(series, langue, adr, titre=t["autres_series"], sauf=serie)
        + "</div>"
    )
    donnees = [{
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": titre,
        "description": tronquer(description, 300),
        "url": adr.absolue(chemins[langue]),
        "inLanguage": HREFLANG[langue],
        "image": url_image(serie["couverture"], 1200),
        "author": personne(g, langue),
        **({"contentLocation": {"@type": "Place", "name": serie["lieu"][langue]}} if serie["lieu"][langue] else {}),
    }, donnees_ariane]
    texte = g.page(langue, titre=t["titre_serie"].format(titre=titre), description=description, chemins=chemins,
                   contenu=contenu, image=serie["couverture"], donnees=donnees, classe="sur-photo recit")
    ecrire(adr.fichier(chemins[langue]), texte)


def descriptions_photos(photos):
    """Description de la page de chaque photo, par langue : son titre et la phrase de
    crédit. Quand plusieurs photos portent le même titre, ou que la description serait
    trop courte, les trois premiers mots-clés la complètent, puis au besoin le numéro
    Pexels : chaque page garde une description à elle."""
    resultat = {}
    for langue in LANGUES:
        t = TEXTES[langue]
        repetes = {titre for titre, n in Counter(p["titre"][langue] for p in photos).items() if n > 1}
        descriptions, details = {}, {}
        for p in photos:
            titre = p["titre"][langue]
            simple = f"{titre}. {t['suffixe']}"
            details[p["id"]] = ", ".join([m for m in p["mots"][langue] if plier(m) != plier(titre)][:3])
            besoin = titre in repetes or len(simple) < DESCRIPTION_COURTE[langue]
            descriptions[p["id"]] = (f"{titre} ({details[p['id']]}). {t['suffixe']}"
                                     if besoin and details[p["id"]] else simple)
        doubles = {d for d, n in Counter(descriptions.values()).items() if n > 1}
        for p in photos:
            if descriptions[p["id"]] in doubles:
                numero = t["numero"].format(id=p["id"])
                detail = f"{details[p['id']]}, {numero}" if details[p["id"]] else numero
                descriptions[p["id"]] = f"{p['titre'][langue]} ({detail}). {t['suffixe']}"
        resultat[langue] = descriptions
    return resultat


def page_photo(g, photo, langue, precedente, suivante, galeries_photo, series_photo, avec_series, proches,
               couleurs_photo):
    adr = g.adr
    t = TEXTES[langue]
    titre = photo["titre"][langue]
    description = g.descriptions_photos[langue][photo["id"]]
    chemins = {l: adr.chemin(l, "photo", photo["id"]) for l in LANGUES}
    ratio = photo["largeur"] / photo["hauteur"]
    page_pexels = pexels(photo["page"], langue)
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
    usages = g.usages.get(photo["id"], [])
    usage = f'<p class="usage">{phrases_usages(usages, langue)}</p>' if usages else ""
    contenu = (
        f'<article class="photo"><figure class="cliche" style="--r:{ratio:.3f}">'
        f'<a href="{e(page_pexels)}" title="{t["voir_pexels"]}" data-goatcounter-click="pexels-image-{photo["id"]}">'
        f'<img src="{url_image(photo, 1600)}" srcset="{srcset(photo, (800, 1200, 1600, 2200, 3000))}" '
        f'sizes="(max-width: 1440px) 100vw, 1440px" width="{photo["largeur"]}" height="{photo["hauteur"]}" '
        f'alt="{e(titre)}" fetchpriority="high" style="background-color:{e(photo["couleur"])}"></a></figure>'
        f'<div class="legende">{ariane}<h1>{e(titre)}</h1>'
        f'<p><a class="bouton" href="{e(page_pexels)}" data-goatcounter-click="pexels-{photo["id"]}" '
        f'data-goatcounter-title="{e(titre)}">{t["telecharger"]}</a></p>{usage}'
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
        "inLanguage": HREFLANG[langue],
        "creator": personne(g, langue),
        "creditText": f"{nom} / Pexels",
        "copyrightNotice": nom,
        "license": LICENCE,
        "acquireLicensePage": page_pexels,
        **({"keywords": ", ".join(mots)} if mots else {}),
        # Lieu : la galerie de lieu de la photo, quand elle en a une.
        **({"contentLocation": {"@type": "Place", "name": parente["titre"][langue]}}
           if parente and parente["type"] == "lieu" else {}),
    }, donnees_ariane]
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=photo, donnees=donnees, classe="page-photo", series=avec_series)
    ecrire(adr.fichier(chemins[langue]), texte)


def page_texte(g, langue, genre, titre, description, corps, avec_series, image=None, donnees=()):
    """Page de texte simple (À propos, Utiliser mes photos, questions fréquentes, pages
    légales). « donnees » : données structurées propres à la page, avant le fil d'Ariane."""
    adr = g.adr
    chemins = {l: adr.chemin(l, genre) for l in LANGUES}
    ariane, donnees_ariane = fil_ariane(adr, langue, [], (titre, chemins[langue]))
    contenu = f'<section class="ouverture texte">{ariane}<h1>{e(titre)}</h1>{corps}</section>'
    texte = g.page(langue, titre=titre, description=description, chemins=chemins, contenu=contenu,
                   image=image, donnees=[*donnees, donnees_ariane], series=avec_series)
    ecrire(adr.fichier(chemins[langue]), texte)


def courriel(g):
    adresse = g.reglages["mentions"].get("contact", "").strip() if g.reglages.has_section("mentions") else ""
    return f'<a href="mailto:{e(adresse)}">{e(adresse)}</a>' if adresse else ""


def page_a_propos(g, par_id, galeries, series, langue):
    adr = g.adr
    t = TEXTES[langue]
    reglage = g.reglages["a-propos"]
    textes = paragraphes(traduit(reglage, "texte", langue))
    corps = "".join(f"<p>{e(p)}</p>" for p in textes)
    portrait = next((par_id[i] for i in nombres(reglage.get("portrait")) if i in par_id), None)
    materiel = paragraphes(traduit(reglage, "materiel", langue))
    if materiel:
        corps += f'<h2>{t["materiel"]}</h2>' + "".join(f"<p>{e(p)}</p>" for p in materiel)
    auteur = paragraphes(traduit(reglage, "auteur", langue))
    site_auteur = g.site.get("site_personnel", "")
    if auteur:
        corps += (f'<h2>{t["auteur"]}</h2>' + "".join(f"<p>{e(p)}</p>" for p in auteur)
                  + (f'<p><a href="{e(site_auteur)}">{e(urlparse(site_auteur).netloc)}</a></p>' if site_auteur else ""))
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
        + f'<li><a href="{e(pexels(g.site.get("profil_pexels", ""), langue))}">{t["profil"]}</a></li>'
        f'<li><a href="{e(g.site.get("site_personnel", ""))}">{e(urlparse(g.site.get("site_personnel", "")).netloc)}</a></li>'
        f'<li><a href="{adr.chemin(langue, "faq")}">{t["faq"]}</a></li></ul>'
    )
    if portrait:
        corps = (f'<figure class="portrait"><img src="{url_image(portrait, 800)}" '
                 f'srcset="{srcset(portrait, (400, 800, 1200))}" sizes="(max-width: 640px) 92vw, 420px" '
                 f'width="{portrait["largeur"]}" height="{portrait["hauteur"]}" alt="{e(portrait["titre"][langue])}"></figure>'
                 + corps)
    # Page de profil de l'auteur (schema.org ProfilePage), avec sa fiche entière.
    profil = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "name": t["a_propos"],
        "url": adr.absolue(adr.chemin(langue, "apropos")),
        "inLanguage": HREFLANG[langue],
        "mainEntity": personne(g, langue, complete=True),
    }
    page_texte(g, langue, "apropos", t["a_propos"], textes[0] if textes else t["a_propos"],
               corps + rappel(g, langue), bool(series), image=portrait, donnees=[profil])


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
    "zh": {
        "intro": "本站所有照片都发布在 Pexels 上。无需注册即可免费下载，并可自由使用，包括商业用途。",
        "etapes_titre": "如何下载照片",
        "etapes": [
            "在本站打开照片页面。",
            "点击「在 Pexels 免费下载」。",
            "在 Pexels 页面点击免费下载按钮，并按需选择尺寸：全分辨率原图或较小的版本。",
        ],
        "permis_titre": "Pexels 许可协议允许",
        "permis": [
            "免费使用照片，无论个人用途还是商业用途。",
            "修改照片：裁剪、修图、添加文字。",
            "将照片用于网站、博客、应用、网店、电子报或演示文稿。",
            "将照片用于广告或营销活动。",
            "将照片印在传单、明信片、书籍或杂志上。",
            "在社交媒体上分享照片。",
        ],
        "interdit_titre": "Pexels 许可协议不允许",
        "interdit": [
            "以贬损或冒犯的方式展示照片中可辨认的人物。",
            "未经修改直接出售照片，例如制成海报、印刷品或印在商品上出售。",
            "暗示照片中的人物或品牌为您的产品背书。",
            "在其他图片素材网站或壁纸网站上传播或转售这些照片。",
            "将照片用作商标、标志或商号。",
        ],
        "credit_titre": "注明作者",
        "credit": "这不是必须的，但我们非常感谢您注明：「摄影：Karl Forterre / Pexels」，最好附上照片页面的链接。",
        "officiel": "一切以{lien}为准。",
        "officiel_lien": "Pexels 许可协议官方文本",
        "contact": "如需印刷、委托拍摄或其他用途，请写信至 {courriel}。",
    },
}


def page_utiliser(g, series, langue):
    t = TEXTES[langue]
    x = LICENCE_PEXELS[langue]

    def puces(elements, balise="ul"):
        return f"<{balise}>" + "".join(f"<li>{e(el)}</li>" for el in elements) + f"</{balise}>"

    contact = courriel(g)
    officiel = x["officiel"].format(lien=f'<a href="{pexels(LICENCE, langue)}">{x["officiel_lien"]}</a>')
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
        lignes.append({"fr": "SIRET : ", "en": "SIRET number: ", "zh": "SIRET 编号："}[langue] + e(m["siret"].strip()))
    contact = courriel(g)
    if contact:
        lignes.append(t["contact"] + {"fr": " : ", "en": ": ", "zh": "："}[langue] + contact)
    utiliser = f'<a href="{adr.chemin(langue, "utiliser")}">{t["utiliser"]}</a>'
    confidentialite = f'<a href="{adr.chemin(langue, "confidentialite")}">{t["confidentialite"]}</a>'
    telephone = {"fr": "Téléphone : ", "en": "Phone: ", "zh": "电话："}[langue] + HEBERGEUR_TELEPHONE
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
    elif langue == "zh":
        corps = (
            f"<h2>网站发布者</h2><p>{'<br>'.join(lignes)}</p>"
            f"<p>发布负责人：{e(editeur)}。</p>"
            f"<h2>网站托管</h2>{hebergeur}"
            "<h2>照片与内容</h2>"
            f"<p>所有照片均为 {e(editeur)} 的作品，发布在 Pexels 上，本站图片也由 Pexels 提供，"
            f"可依照 Pexels 许可协议使用，详见{utiliser}。KF’ 标志和本站文字的版权归 {e(editeur)} 所有。</p>"
            f"<h2>个人数据</h2><p>请参阅{confidentialite}。</p>"
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
    description = {"fr": f"Mentions légales du site de photographie de {editeur} : éditeur, hébergement "
                         "par GitHub Pages, droits sur les photos publiées sur Pexels et sur les textes.",
                   "en": f"Legal notice for {editeur}'s photography website: publisher, hosting by GitHub Pages, "
                         "and rights to the photos published on Pexels and to the texts.",
                   "zh": f"{editeur} 摄影网站的法律声明：发布者、GitHub Pages 托管，以及 Pexels 上照片与网站文字的权利。"}[langue]
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
    elif langue == "zh":
        audience = (
            "<p>本站使用 GoatCounter 统计访问量，这是一款不使用 Cookie 的网站统计工具。GoatCounter 只保存汇总数据："
            "浏览的页面、来源网站、浏览器、操作系统、屏幕尺寸和国家或地区。您的 IP 地址从不被记录，"
            "它只会与浏览器信息一起，在内存中用于几小时内识别同一次访问。前往 Pexels 的点击也以同样方式统计。"
            '<a href="https://www.goatcounter.com/help/privacy">GoatCounter 隐私政策</a>（英文）。</p>'
            if goatcounter else "<p>本站不统计访问量。</p>"
        )
        corps = (
            '<p class="accroche">本站不设置任何统计或广告 Cookie，也不收集任何个人数据，因此没有 Cookie 同意横幅。</p>'
            f"<h2>访问统计</h2>{audience}"
            "<h2>网站托管</h2><p>本站由 GitHub Pages 托管。和所有托管服务一样，GitHub 出于服务安全的需要，"
            "会在日志中记录访客的 IP 地址："
            '<a href="https://docs.github.com/zh/site-policy/privacy-policies/github-general-privacy-statement">'
            "GitHub 隐私声明</a>。</p>"
            "<h2>照片</h2><p>图片直接从 Pexels 的服务器加载，因此 Pexels 会收到您浏览器的 IP 地址。为 Pexels 分发图片的 "
            "Cloudflare 可能会设置用于服务安全的技术性 Cookie："
            '<a href="https://www.pexels.com/zh-cn/privacy-policy/">Pexels 隐私政策</a>。'
            "指向 Pexels 和其他网站的链接会带您进入各自有其规则的服务。</p>"
            + (f"<h2>您的权利</h2><p>如对您的数据有任何疑问，请写信至 {contact}。</p>" if contact else "")
        )
        description = "隐私政策：无广告 Cookie，不收集个人数据，访问统计不使用 Cookie。"
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


# Questions fréquentes (questions.ini) : liens [texte](adresse) et champs {nom}.
MOTIF_REPONSE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)|\{(\w+)\}")


def adresse_lien(g, langue, cible, absolue):
    """Adresse d'un lien des questions fréquentes : complète (https://…, mailto:…), le
    profil Pexels (« pexels ») ou une page du site dans la langue de la page (« utiliser »,
    « galerie:pyrenees », « apropos#usages »…). None si la page n'existe pas."""
    if re.match(r"(https?:|mailto:)", cible):
        return pexels(cible, langue)
    page, _, ancre = cible.partition("#")
    if page == "pexels":
        adresse = pexels(g.site.get("profil_pexels", ""), langue)
    else:
        genre, _, cle = page.partition(":")
        try:
            adresse = g.adr.chemin(langue, genre, cle or None)
        except KeyError:
            print(f"Questions fréquentes : lien « {cible} » inconnu, laissé sans lien.")
            return None
        adresse = g.adr.absolue(adresse) if absolue else adresse
    return adresse + (f"#{ancre}" if ancre else "")


def lire_questions(g, langue, photos, galeries, series, markdown=False):
    """Questions fréquentes de questions.ini, dans une langue : [(identifiant, question,
    paragraphes de la réponse)]. Réponses en HTML (liens relatifs), ou en Markdown aux
    adresses complètes pour llms.txt. Une question qui fait appel à une liste vide (aucun
    usage signalé, par exemple) est laissée de côté."""
    conf = lire_ini("questions.ini")

    def echapper(texte):
        # Texte courant : les apostrophes restent lisibles, dans la page comme dans ses données.
        return texte if markdown else html.escape(texte, quote=False)

    def lien(texte, adresse):
        if markdown:
            return f"[{texte}]({adresse})" if adresse else texte
        return f'<a href="{e(adresse)}">{echapper(texte)}</a>' if adresse else echapper(texte)

    def lien_page(texte, genre, cle=None):
        chemin = g.adr.chemin(langue, genre, cle)
        return lien(texte, g.adr.absolue(chemin) if markdown else chemin)

    sites = list(dict.fromkeys(u["site"] for usages in g.usages.values() for u in usages if u["type"] == "site"))
    valeurs = {
        "photos": chiffre(len(photos), langue),
        "galeries": chiffre(len(galeries), langue),
        "vues": chiffre(g.preuve["vues"], langue) if g.preuve["vues"] else "",
        "telechargements": chiffre(g.preuve["telechargements"], langue) if g.preuve["telechargements"] else "",
        "lieux": enumeration([lien_page(gal["titre"][langue], "galerie", gal["cle"])
                              for gal in galeries if gal["type"] == "lieu"], langue),
        "series": enumeration([lien_page(s["titre"][langue], "serie", s["cle"]) for s in series], langue),
        "sites": enumeration([echapper(s) for s in sites], langue),
    }

    def rendre(texte):
        morceaux, fin = [], 0
        for m in MOTIF_REPONSE.finditer(texte):
            morceaux.append(echapper(texte[fin:m.start()]))
            if m.group(1):
                morceaux.append(lien(m.group(1), adresse_lien(g, langue, m.group(2), markdown)))
            elif m.group(3) in valeurs:
                morceaux.append(valeurs[m.group(3)])
            else:
                morceaux.append(echapper(m.group(0)))
            fin = m.end()
        morceaux.append(echapper(texte[fin:]))
        return "".join(morceaux)

    questions = []
    for cle in conf.sections():
        question = traduit(conf[cle], "question", langue)
        reponse = traduit(conf[cle], "reponse", langue)
        if not question or not reponse or any(valeurs.get(nom) == "" for nom in re.findall(r"\{(\w+)\}", reponse)):
            continue
        questions.append((cle, question, [rendre(p) for p in paragraphes(reponse)]))
    return questions


def page_questions(g, photos, galeries, series, langue):
    """Questions fréquentes, avec leurs données structurées FAQPage."""
    t = TEXTES[langue]
    questions = lire_questions(g, langue, photos, galeries, series)
    if not questions:
        return False
    corps = f'<p class="accroche">{e(t["faq_intro"])}</p>' + "".join(
        f'<h2 id="{e(cle)}">{html.escape(question, quote=False)}</h2>' + "".join(f"<p>{p}</p>" for p in reponse)
        for cle, question, reponse in questions
    )
    # Dans les données structurées, les liens de la réponse ont leur adresse complète.
    absolues = re.compile(r'href="(/[^"]*)"')
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "name": t["faq"],
        "url": g.adr.absolue(g.adr.chemin(langue, "faq")),
        "inLanguage": HREFLANG[langue],
        "mainEntity": [{
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": absolues.sub(
                lambda m: f'href="{g.adr.absolue(m.group(1))}"', "".join(f"<p>{p}</p>" for p in reponse))},
        } for _, question, reponse in questions],
    }
    page_texte(g, langue, "faq", t["faq"], t["faq_intro"], corps + rappel(g, langue), bool(series), donnees=[faq])
    return True


def page_introuvable(g, series):
    adr = g.adr
    contenu = "".join(
        f'<section class="ouverture texte" lang="{HREFLANG[l]}"><h1>{TEXTES[l]["introuvable"]}</h1>'
        f'<p>{TEXTES[l]["introuvable_texte"]} <a href="{adr.chemin(l, "accueil")}">{TEXTES[l]["retour"]}</a></p></section>'
        for l in LANGUES
    )
    chemins = {l: adr.chemin(l, "accueil") for l in LANGUES}
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


def ecrire_apercu(g, photos, galeries, series, selection, libelles, par_photo, par_serie):
    """Aperçu du site photo (apercu.json), lu par le site d'auteur karlforterre.fr pour sa
    section Photographie : sélection, séries, galeries, dernières photos et chiffres
    Pexels, en français. Le site d'auteur dépend de ce format : le garder."""
    adr = g.adr

    def lien(genre, cle, titre):
        return {"titre": titre, "page": adr.absolue(adr.chemin("fr", genre, cle))}

    def fiche(p, avec_liens=False):
        donnees = {
            "id": p["id"],
            "titre": libelles.get(p["id"]) or p["titre"]["fr"],
            "page": adr.absolue(adr.chemin("fr", "photo", p["id"])),
            "pexels": p["page"],
            "image": p["image"],
            "largeur": p["largeur"],
            "hauteur": p["hauteur"],
            "couleur": p["couleur"],
        }
        if avec_liens:
            serie = next(iter(par_serie.get(p["id"], [])), None)
            galeries_photo = par_photo.get(p["id"], [])
            galerie = next((gal for gal in galeries_photo if gal["type"] == "lieu"), None) or next(iter(galeries_photo), None)
            if serie:
                donnees["serie"] = lien("serie", serie["cle"], serie["titre"]["fr"])
            if galerie:
                donnees["galerie"] = lien("galerie", galerie["cle"], galerie["titre"]["fr"])
        return donnees

    apercu = {
        "site": adr.absolue(adr.chemin("fr", "accueil")),
        "mis_a_jour": AUJOURDHUI,
        "chiffres": {
            "photos": len(photos),
            "galeries": len(galeries),
            "series": len(series),
            "vues_pexels": g.preuve["vues"],
            "telechargements_pexels": g.preuve["telechargements"],
        },
        "pages": {
            "galeries": adr.absolue(adr.chemin("fr", "galeries")),
            "series": adr.absolue(adr.chemin("fr", "series")),
            "profil_pexels": g.site.get("profil_pexels", ""),
            **({"usages": adr.absolue(adr.chemin("fr", "galerie", CLE_USAGES))} if g.usages else {}),
        },
        "selection": [fiche(p, avec_liens=True) for p in selection],
        "series": [{**lien("serie", s["cle"], s["titre"]["fr"]), "cle": s["cle"], "lieu": s["lieu"]["fr"],
                    "date": s["date"]["fr"], "photos": len(s["photos"]), "couverture": fiche(s["bandeau"])}
                   for s in series],
        "galeries": [{**lien("galerie", gal["cle"], gal["titre"]["fr"]), "cle": gal["cle"], "type": gal["type"],
                      "description": gal["description"]["fr"], "photos": len(gal["photos"]),
                      "couverture": fiche(gal["bandeau"])}
                     for gal in galeries],
        "recentes": [fiche(p) for p in photos[:12]],
        "usages": [{**fiche(p), "sites": [u["site"] for u in g.usages[p["id"]]],
                    "types": [u["type"] for u in g.usages[p["id"]]],
                    "signale_le": max((u["date"] for u in g.usages[p["id"]]), default="")}
                   for p in photos if p["id"] in g.usages],
    }
    ecrire(adr.fichier(f"{adr.base}/apercu.json"), json.dumps(apercu, ensure_ascii=False, indent=1) + "\n")


def pages_du_plan(adr, photos, galeries, series, couleurs, avec_faq, usages=False):
    """Pages du plan du site : [(chemins dans chaque langue, image)]."""
    entrees = []
    genres = (["accueil", "galeries"] + (["series"] if series else [])
              + ["apropos", "utiliser"] + (["faq"] if avec_faq else []) + ["mentions", "confidentialite"])
    for genre in genres:
        entrees.append(({l: adr.chemin(l, genre) for l in LANGUES}, None))
    for serie in series:
        entrees.append(({l: adr.chemin(l, "serie", serie["cle"]) for l in LANGUES}, None))
    for gal in galeries:
        entrees.append(({l: adr.chemin(l, "galerie", gal["cle"]) for l in LANGUES}, None))
    if usages:
        entrees.append(({l: adr.chemin(l, "galerie", CLE_USAGES) for l in LANGUES}, None))
    for couleur in couleurs:
        entrees.append(({l: adr.chemin(l, "couleur", couleur["cle"][l]) for l in LANGUES}, None))
    for p in photos:
        entrees.append(({l: adr.chemin(l, "photo", p["id"]) for l in LANGUES}, p["image"]))
    return entrees


def ecrire_plan(adr, entrees, journal):
    """Plan du site : chaque page, ses traductions, son image et la date de sa dernière
    modification d'après le journal des pages (lastmod, que Bing et Google lisent pour
    savoir quoi relire)."""
    blocs = []
    for chemins, image in entrees:
        for langue in LANGUES:
            bloc = f"<url><loc>{adr.absolue(chemins[langue])}</loc>"
            if chemins[langue] in journal:
                bloc += f"<lastmod>{journal[chemins[langue]][1]}</lastmod>"
            for autre in LANGUES:
                bloc += f'<xhtml:link rel="alternate" hreflang="{HREFLANG[autre]}" href="{adr.absolue(chemins[autre])}"/>'
            if image:
                bloc += f"<image:image><image:loc>{e(image)}</image:loc></image:image>"
            blocs.append(bloc + "</url>")
    texte = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
        'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">'
        + "".join(blocs) + "</urlset>\n"
    )
    ecrire(SORTIE / "sitemap.xml", texte)
    racine = adr.absolue(adr.base + "/")
    # Tous les robots sont les bienvenus, ceux des moteurs comme ceux des assistants IA
    # (OAI-SearchBot, Claude-SearchBot, PerplexityBot…) : llms.txt leur présente le site.
    ecrire(SORTIE / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {racine}sitemap.xml\n"
                                  f"# Présentation pour les assistants IA : {racine}llms.txt\n")


# ---------------------------------------------------------------- journal des pages, IndexNow


def empreinte(fichier):
    """Empreinte de ce qui compte dans une page : titre, description, données structurées
    et contenu principal. L'en-tête, le pied de page et la version des feuilles de style
    n'y entrent pas : ils changent sans que la page change vraiment."""
    texte = fichier.read_text(encoding="utf-8")
    morceaux = re.findall(r'<title>.*?</title>|<meta name="description"[^>]*>'
                          r'|<script type="application/ld\+json">.*?</script>|<main\b.*?</main>', texte, flags=re.S)
    return hashlib.sha1("".join(morceaux).encode("utf-8")).hexdigest()[:12]


def charger_pages():
    if PAGES.exists():
        return json.loads(PAGES.read_text(encoding="utf-8"))
    return {}


def enregistrer_pages(journal):
    """Une page par ligne : adresse, empreinte, date de dernière modification."""
    lignes = [f" {json.dumps(chemin, ensure_ascii=False)}: {json.dumps(valeur)}"
              for chemin, valeur in sorted(journal.items())]
    PAGES.write_text("{\n" + ",\n".join(lignes) + "\n}\n", encoding="utf-8")


def suivre_pages(adr, entrees, jour):
    """Compare les pages construites au journal des pages (donnees/pages.json). Renvoie le
    journal à jour, où chaque page garde la date de sa dernière modification réelle, et
    les adresses à signaler : pages nouvelles, modifiées, ou supprimées depuis."""
    ancien = charger_pages()
    journal, signaler = {}, []
    for chemins, _ in entrees:
        for chemin in chemins.values():
            valeur = empreinte(adr.fichier(chemin))
            if chemin in ancien and ancien[chemin][0] == valeur:
                journal[chemin] = ancien[chemin]
            else:
                journal[chemin] = [valeur, jour]
                signaler.append(adr.absolue(chemin))
    signaler += [adr.absolue(chemin) for chemin in ancien if chemin not in journal]
    return journal, signaler


def cle_indexnow(reglages):
    """Clé IndexNow de site.ini : de 8 à 128 lettres, chiffres ou tirets."""
    cle = reglages["site"].get("indexnow", "").strip()
    if cle and not re.fullmatch(r"[A-Za-z0-9-]{8,128}", cle):
        print(f"Clé IndexNow « {cle} » invalide (8 à 128 lettres, chiffres ou tirets) : rien ne sera signalé.")
        return ""
    return cle


def preparer_indexnow(adr, cle, signaler):
    """Écrit la liste des pages à signaler (_indexnow/envoi.json), que la tâche de nuit
    envoie une fois le site en ligne : avant, les moteurs trouveraient l'ancienne page."""
    ENVOI_INDEXNOW.parent.mkdir(parents=True, exist_ok=True)
    envoi = {"host": urlparse(adr.origine).netloc, "key": cle,
             "keyLocation": adr.absolue(f"{adr.base}/{cle}.txt"), "urlList": signaler if cle else []}
    ENVOI_INDEXNOW.write_text(json.dumps(envoi, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# Réponses d'IndexNow (https://www.indexnow.org/documentation).
REPONSES_INDEXNOW = {
    200: "adresses reçues",
    202: "adresses reçues, clé en cours de vérification",
    400: "requête mal formée",
    403: "clé refusée : le fichier de clé n'est pas en ligne ou ne correspond pas à la clé",
    422: "adresses refusées : elles n'appartiennent pas au site, ou la clé ne correspond pas",
    429: "trop de requêtes : envoi pris pour un abus, à reprendre plus tard",
}

# Au premier envoi avec une clé, Bing lit d'abord le fichier de clé et refuse l'envoi en
# attendant (403, « SiteVerificationNotCompleted »). Attentes avant chaque nouvel essai,
# en secondes : une vingtaine de minutes en tout.
ATTENTES_VERIFICATION = (60, 120, 300, 600)


def envoyer_indexnow():
    """Envoie à IndexNow la liste préparée par la construction, par lots de 10 000
    adresses au plus. Renvoie le code de sortie : 1 si IndexNow refuse l'envoi (clé ou
    adresses), 0 sinon ; une panne passagère ne fait qu'un avertissement. Tant que Bing
    vérifie la clé, l'envoi est repris après une attente (ATTENTES_VERIFICATION). Après un
    refus pour excès (429), IndexNow demande d'attendre au moins dix minutes : pas de
    nouvel essai."""
    if not ENVOI_INDEXNOW.exists():
        print("IndexNow : aucune liste préparée (build.py --indexnow), rien à signaler.")
        return 0
    envoi = json.loads(ENVOI_INDEXNOW.read_text(encoding="utf-8"))
    adresses = envoi.get("urlList", [])
    if not envoi.get("key") or not adresses:
        print("IndexNow : aucune page nouvelle, modifiée ou supprimée à signaler.")
        return 0
    sortie = 0
    for debut in range(0, len(adresses), 10000):
        lot = adresses[debut:debut + 10000]
        corps = json.dumps({**envoi, "urlList": lot}).encode("utf-8")
        pannes = verifications = 0
        while True:
            code, detail = None, ""
            requete = urllib.request.Request(INDEXNOW, data=corps, method="POST", headers={
                "Content-Type": "application/json; charset=utf-8", "User-Agent": "site-karl-forterre"})
            try:
                with urllib.request.urlopen(requete, timeout=60) as reponse:
                    code = reponse.status
            except urllib.error.HTTPError as erreur:
                code, detail = erreur.code, erreur.read().decode("utf-8", "replace")[:300]
            except OSError as erreur:
                code, detail = None, str(erreur)
            if (code == 403 and "SiteVerificationNotCompleted" in detail
                    and verifications < len(ATTENTES_VERIFICATION)):
                attente = ATTENTES_VERIFICATION[verifications]
                verifications += 1
                print(f"IndexNow : Bing vérifie encore la clé ; nouvel essai dans {attente // 60} min.")
                time.sleep(attente)
            elif (code is None or code >= 500) and pannes < 2:
                pannes += 1
                time.sleep(30 * pannes)
            else:
                break
        explication = REPONSES_INDEXNOW.get(code, detail or "pas de réponse")
        print(f"IndexNow : {len(lot)} pages signalées, réponse {code or '—'} ({explication}).")
        if code in (400, 403, 422):
            if detail:
                print(f"  Détail : {detail}")
            sortie = 1
    return sortie


# ---------------------------------------------------------------- tableau de bord

# Page non référencée (/tableau-de-bord/) qui suit, semaine après semaine, les relevés de
# releves/ (Pexels, par Telepex ou à la main ; Pinterest ; assistants IA) et GoatCounter.
HISTORIQUE = ICI / "donnees" / "historique.json"
DEPOT = "https://github.com/Willwonderc/PexelsWillwonder"
# La fiche du 24 septembre 2026 n'a pas de colonne « releve » : Telepex l'ajoute à chaque
# relevé depuis la session T.
RELEVE_INITIAL = "2026-09-24T12:42:00+02:00"
# Relevés photo par photo gardés dans l'historique, un par semaine : de quoi calculer les
# gains de la semaine et du mois (quatre semaines).
SEMAINES_GARDEES = 5
# Jours avant de rappeler un relevé en retard.
RETARD_SEMAINE = 8
RETARD_MOIS = 35
GOATCOUNTER_DEBUT = date(2026, 9, 28)  # premier jour compté, un lundi
GOATCOUNTER_API = "https://{code}.goatcounter.com/api/v0"
# Semaines relues au plus à chaque passage ; les semaines finies restent dans l'historique.
GOATCOUNTER_SEMAINES = 8
# Clics vers Pexels : bouton et image de chaque photo (« pexels-<numéro> »,
# « pexels-image-<numéro> ») et boutons « Suivre sur Pexels » (vitrine/README.md).
CLIC_PHOTO = re.compile(r"^pexels(?:-image)?(?:-(\d+))?$")
CLIC_SUIVRE = re.compile(r"^suivre-pexels")
# Provenance des visites, d'après le nom du site d'origine que donne GoatCounter. Les
# assistants IA d'abord : gemini.google.com n'est pas une visite venue de Google.
PROVENANCES = (
    ("Assistants IA", ("chatgpt", "openai", "perplexity", "copilot", "gemini", "claude.ai")),
    ("Google", ("google",)),
    ("Bing", ("bing",)),
    ("Pinterest", ("pinterest", "pin.it")),
    ("Bluesky", ("bsky",)),
    ("Mastodon et Pixelfed", ("mastodon", "pixelfed")),
    ("Instagram", ("instagram",)),
    ("Facebook", ("facebook", "fb.com")),
    ("karlforterre.fr", ("karlforterre.fr",)),
    ("Pexels", ("pexels",)),
)
MOIS_COURTS = ("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.",
               "nov.", "déc.")


def nombre_ou_rien(texte):
    """Nombre d'un relevé, ou None pour une case vide : une valeur inconnue n'est pas zéro."""
    chiffres = re.sub(r"\D", "", texte or "")
    return int(chiffres) if chiffres else None


def moment(texte):
    """Date et heure d'un relevé (ISO 8601) ; sans fuseau, en UTC."""
    quand = datetime.fromisoformat(texte.strip().replace("Z", "+00:00"))
    return quand if quand.tzinfo else quand.replace(tzinfo=timezone.utc)


def lundi(jour):
    return jour - timedelta(days=jour.weekday())


def date_fr(jour, courte=False, annee=False):
    """« 1er octobre 2026 », « 24 septembre 2026 » ; courte : « 24 sept. », ou « 24 sept. 2026 »
    avec l'année, pour les tableaux."""
    if courte:
        return f"{jour.day} {MOIS_COURTS[jour.month - 1]}" + (f" {jour.year}" if annee else "")
    return f"{'1er' if jour.day == 1 else jour.day} {MOIS['fr'][jour.month - 1]} {jour.year}"


def valeur(n):
    return "—" if n is None else chiffre(n, "fr")


def ecart(n):
    """« +1 234 », « −56 » ou « 0 » ; vide si l'écart est inconnu."""
    if n is None:
        return ""
    return ("+" if n > 0 else "−" if n < 0 else "") + chiffre(abs(n), "fr")


def lire_releve_photos():
    """Dernier relevé photo par photo (releves/suivi-pexels.csv, que Telepex remplace à chaque
    relevé) : sa date et, pour chaque photo, statut, vues, téléchargements, J'aime…"""
    chemin = RACINE / "releves" / "suivi-pexels.csv"
    if not chemin.exists():
        return None
    lignes = lire_csv(chemin)
    quand = next((l["releve"].strip() for l in lignes if (l.get("releve") or "").strip()), RELEVE_INITIAL)
    photos = {}
    for ligne in lignes:
        cle = (ligne.get("photo") or "").strip()
        if not cle.isdigit():
            continue
        titre = (ligne.get("titre") or "").strip()
        photos[int(cle)] = {
            "retenue": (ligne.get("moderation") or "").strip() == "retenue",
            "import": (ligne.get("import") or "").strip(),
            "vues": nombre_ou_rien(ligne.get("vues")),
            "telechargements": nombre_ou_rien(ligne.get("telechargements")),
            "jaime": nombre_ou_rien(ligne.get("jaime")),
            "evenement": (ligne.get("evenement") or "").strip() == "oui",
            # La fiche du 24 septembre reprend « Free stock photo of… » pour les photos sans titre.
            "titre": "" if titre.lower().startswith("free stock photo") else titre,
            "mots": [m for m in liste_mots(ligne.get("mots_cles")) if not ILLISIBLE.search(m)],
        }
    return {"date": quand, "photos": photos}


def totaux_releve(releve):
    photos = list(releve["photos"].values())

    def somme(cle):
        connues = [p[cle] for p in photos if p[cle] is not None]
        return sum(connues) if connues else None

    return {"vues": somme("vues"), "telechargements": somme("telechargements"), "jaime": somme("jaime"),
            "photos": len(photos), "retenues": sum(p["retenue"] for p in photos),
            "evenements": sum(p["evenement"] for p in photos)}


def lire_releves_dates(nom, colonnes):
    """Relevés datés de releves/ (vues-pexels.csv, pinterest.csv) : une ligne par jour, du plus
    ancien au plus récent ; la dernière ligne d'un même jour l'emporte."""
    chemin = RACINE / "releves" / nom
    par_jour = {}
    for ligne in lire_csv(chemin) if chemin.exists() else []:
        try:
            jour = date.fromisoformat((ligne.get("date") or "").strip())
        except ValueError:
            continue
        par_jour[jour] = {"date": jour, **{c: nombre_ou_rien(ligne.get(c)) for c in colonnes},
                          "remarque": (ligne.get("remarque") or "").strip()}
    return [par_jour[j] for j in sorted(par_jour)]


def lire_assistants():
    """Réponses des assistants IA (releves/assistants-ia.csv), regroupées par date de relevé."""
    chemin = RACINE / "releves" / "assistants-ia.csv"
    par_jour = {}
    for ligne in lire_csv(chemin) if chemin.exists() else []:
        try:
            jour = date.fromisoformat((ligne.get("date") or "").strip())
        except ValueError:
            continue
        releve = par_jour.setdefault(jour, {"date": jour, "reponses": 0, "citent": 0, "assistants": set()})
        releve["reponses"] += 1
        releve["citent"] += (ligne.get("cite") or "").strip().lower() == "oui"
        releve["assistants"].add((ligne.get("assistant") or "").strip())
    return [par_jour[j] for j in sorted(par_jour)]


def charger_historique():
    historique = json.loads(HISTORIQUE.read_text(encoding="utf-8")) if HISTORIQUE.exists() else {}
    for cle in ("releves", "semaines", "goatcounter"):
        historique.setdefault(cle, {})
    return historique


def enregistrer_historique(historique):
    texte = json.dumps(historique, ensure_ascii=False, indent=1, sort_keys=True)
    # Une photo par ligne : [vues, téléchargements, J'aime, retenue].
    texte = re.sub(r"\[\s+([^\[\]{}]*?)\s+\]",
                   lambda m: "[" + ", ".join(v.strip() for v in m.group(1).split(",")) + "]", texte)
    HISTORIQUE.write_text(texte + "\n", encoding="utf-8")


def completer_historique(historique, releve):
    """Ajoute le relevé photo par photo à l'historique : ses totaux, et les chiffres de chaque
    photo pour sa semaine, où le dernier relevé de la semaine l'emporte. Seules les
    SEMAINES_GARDEES dernières semaines gardent leurs chiffres photo par photo."""
    if not releve:
        return
    historique["releves"][releve["date"]] = totaux_releve(releve)
    semaine = lundi(moment(releve["date"]).date()).isoformat()
    deja = historique["semaines"].get(semaine)
    if not deja or moment(deja["releve"]) <= moment(releve["date"]):
        historique["semaines"][semaine] = {
            "releve": releve["date"],
            "photos": {str(pid): [p["vues"], p["telechargements"], p["jaime"], int(p["retenue"])]
                       for pid, p in sorted(releve["photos"].items())},
        }
    for cle in sorted(historique["semaines"])[:-SEMAINES_GARDEES]:
        del historique["semaines"][cle]


def references(historique, releve):
    """Relevés photo par photo de la semaine précédente et d'il y a quatre semaines, qui
    servent aux gains ; None tant qu'il n'y en a pas."""
    semaine = lundi(moment(releve["date"]).date())
    anciennes = sorted(k for k in historique["semaines"] if date.fromisoformat(k) < semaine)
    mois = [k for k in anciennes if date.fromisoformat(k) <= semaine - timedelta(weeks=4)]
    return (historique["semaines"][anciennes[-1]] if anciennes else None,
            historique["semaines"][mois[-1]] if mois else None)


def gain(pid, rang, actuel, reference):
    """Écart d'un chiffre depuis un relevé de référence (rang : 0 vues, 1 téléchargements,
    2 J'aime) ; None s'il est inconnu d'un côté ou de l'autre."""
    ancien = reference["photos"].get(str(pid)) if reference else None
    if actuel is None or not ancien or ancien[rang] is None:
        return None
    return actuel - ancien[rang]


# GoatCounter : visites et clics vers Pexels, par son API (clé du secret GOATCOUNTER_JETON).


class GoatCounterErreur(Exception):
    pass


def appel_goatcounter(base, jeton, chemin, **parametres):
    """Un appel à l'API de GoatCounter, 4 par seconde au plus. La clé ne part que dans l'en-tête
    Authorization : elle n'apparaît ni dans l'adresse ni dans les messages d'erreur."""
    requete = urllib.request.Request(f"{base}{chemin}?{urlencode(parametres)}", headers={
        "Authorization": f"Bearer {jeton}",
        "Content-Type": "application/json",
        "User-Agent": "photos.karlforterre.fr (tableau de bord)",
    })
    time.sleep(0.3)
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return json.load(reponse)
    except urllib.error.HTTPError as erreur:
        if erreur.code in (401, 403):
            raise GoatCounterErreur("GoatCounter refuse la clé du secret GOATCOUNTER_JETON : fausse, révoquée "
                                    "ou sans le droit de lire les statistiques.") from None
        raise GoatCounterErreur(f"GoatCounter a répondu par l'erreur {erreur.code}.") from None
    except (urllib.error.URLError, OSError, ValueError):
        raise GoatCounterErreur("GoatCounter n'a pas répondu.") from None


def heure_utc(quand):
    """Moment arrondi à l'heure, au format attendu par GoatCounter."""
    return quand.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:00:00Z")


def chemins_vus(base, jeton, debut, fin, lots=10):
    """Pages et événements vus entre deux moments, avec leur nombre de visiteurs (par lots de
    100, les chemins déjà reçus exclus du lot suivant)."""
    vus, exclus = [], []
    for _ in range(lots):
        parametres = {"start": heure_utc(debut), "end": heure_utc(fin), "limit": 100}
        if exclus:
            parametres["exclude_paths"] = ",".join(map(str, exclus))
        reponse = appel_goatcounter(base, jeton, "/stats/hits", **parametres)
        lot = reponse.get("hits") or []
        vus += lot
        exclus += [h["path_id"] for h in lot if "path_id" in h]
        if not reponse.get("more") or not lot:
            break
    return vus


def clics(vus):
    """Clics vers Pexels : sur les photos (bouton ou image) et sur « Suivre sur Pexels »."""
    def compte(motif):
        return sum(h.get("count", 0) for h in vus if h.get("event") and motif.match(h.get("path", "")))
    return compte(CLIC_PHOTO), compte(CLIC_SUIVRE)


def visites(base, jeton, debut, fin):
    """Visiteurs des pages, sans les clics comptés comme événements."""
    total = appel_goatcounter(base, jeton, "/stats/total", start=heure_utc(debut), end=heure_utc(fin))
    return max(0, (total.get("total") or 0) - (total.get("total_events") or 0))


def famille(nom):
    nom = nom.lower()
    if not nom:
        return "Accès direct ou inconnu"
    if nom.startswith("photos.karlforterre.fr"):
        return None  # navigation à l'intérieur du site
    return next((libelle for libelle, motifs in PROVENANCES if any(m in nom for m in motifs)), "Autres sites")


def provenance(base, jeton, debut, fin):
    """Sites d'où viennent les visites, regroupés par famille (Google, Pinterest…)."""
    reponse = appel_goatcounter(base, jeton, "/stats/toprefs", start=heure_utc(debut), end=heure_utc(fin),
                                limit=100)
    familles = {}
    for site in reponse.get("stats") or []:
        libelle = famille(site.get("name") or "")
        if libelle:
            familles[libelle] = familles.get(libelle, 0) + (site.get("count") or 0)
    return sorted(familles.items(), key=lambda f: -f[1])


def lire_goatcounter(code, jeton, journal, maintenant):
    """Chiffres de GoatCounter. Semaine par semaine depuis GOATCOUNTER_DEBUT : les semaines
    finies restent dans le journal, la semaine en cours est relue à chaque passage. Puis les
    7 derniers jours : pages les plus vues, photos les plus cliquées, provenance. Lève
    GoatCounterErreur ; le journal garde les semaines déjà lues."""
    base = GOATCOUNTER_API.format(code=code)
    maintenant = maintenant.replace(minute=0, second=0, microsecond=0)
    semaines = journal.setdefault("semaines", {})
    lundis, jour = [], GOATCOUNTER_DEBUT
    while jour <= maintenant.date():
        lundis.append(jour)
        jour += timedelta(days=7)
    a_lire = [l for l in lundis if not semaines.get(l.isoformat(), {}).get("complete")]
    for l in a_lire[-GOATCOUNTER_SEMAINES:]:
        debut = datetime.combine(l, datetime.min.time(), timezone.utc)
        fin = min(debut + timedelta(days=7), maintenant)
        if fin <= debut:
            semaines[l.isoformat()] = {"visites": 0, "clics_photos": 0, "clics_suivre": 0, "complete": False}
            continue
        photos, suivre = clics(chemins_vus(base, jeton, debut, fin))
        semaines[l.isoformat()] = {"visites": visites(base, jeton, debut, fin), "clics_photos": photos,
                                   "clics_suivre": suivre, "complete": fin == debut + timedelta(days=7)}
    debut = maintenant - timedelta(days=7)
    vus = chemins_vus(base, jeton, debut, maintenant)
    photos, suivre = clics(vus)
    par_photo = {}
    for h in vus:
        trouve = CLIC_PHOTO.match(h.get("path", ""))
        if h.get("event") and trouve and trouve.group(1):
            par_photo[int(trouve.group(1))] = par_photo.get(int(trouve.group(1)), 0) + (h.get("count") or 0)
    pages = sorted((h for h in vus if not h.get("event")), key=lambda h: -(h.get("count") or 0))[:10]
    return {
        "visites": visites(base, jeton, debut, maintenant),
        "clics_photos": photos,
        "clics_suivre": suivre,
        "photos": sorted(par_photo.items(), key=lambda p: (-p[1], -p[0]))[:10],
        "pages": [(h.get("path", ""), h.get("title") or "", h.get("count") or 0) for h in pages],
        "provenance": provenance(base, jeton, debut, maintenant),
        "provenance_debut": provenance(base, jeton, datetime.combine(GOATCOUNTER_DEBUT, datetime.min.time(),
                                                                     timezone.utc), maintenant),
    }


# Courbes et colonnes en SVG, tracées ici sans bibliothèque. Une série par graphique, traits
# fins, graduations rondes, valeur de la dernière mesure ; statique/tableau.js ajoute le
# survol et le clavier, et chaque graphique a son tableau de chiffres à côté.


def graduations(bas, haut, nombre=4):
    """Graduations rondes (1, 2 ou 5 × 10ⁿ) qui couvrent l'intervalle [bas, haut]."""
    if haut <= bas:
        haut = bas + 1
    brut = (haut - bas) / nombre
    puissance = 10 ** math.floor(math.log10(brut))
    pas = max(1, round(next(m * puissance for m in (1, 2, 5, 10) if m * puissance >= brut)))
    debut = int(bas // pas * pas)
    return [debut + i * pas for i in range(math.ceil((haut - debut) / pas) + 1)]


def graphe(titre, points, colonnes=False, note=""):
    """points : [(date, nombre)] du plus ancien au plus récent. colonnes : totaux par semaine,
    depuis zéro ; sinon une courbe, dont l'échelle suit les valeurs."""
    points = [(jour, n) for jour, n in points if n is not None]
    if not points:
        return ""
    largeur, hauteur, gauche, droite, haut, bas = 640, 220, 60, 76, 14, 28
    zone_l, zone_h = largeur - gauche - droite, hauteur - haut - bas
    nombres = [n for _, n in points]
    if colonnes:
        echelle = graduations(0, max(max(nombres), 1))
    else:
        mini, maxi = min(nombres), max(nombres)
        jeu = (maxi - mini) * .15 or max(1, maxi * .005)
        echelle = graduations(max(0, mini - jeu), maxi + jeu)
    y0, y1 = echelle[0], echelle[-1]

    def y(n):
        return haut + zone_h * (1 - (n - y0) / (y1 - y0))

    if colonnes:
        pas = zone_l / len(points)
        xs = [gauche + pas * (i + .5) for i in range(len(points))]
    elif len(points) == 1:
        xs = [gauche + zone_l]
    else:
        etendue = (points[-1][0] - points[0][0]).days or 1
        xs = [gauche + zone_l * (jour - points[0][0]).days / etendue for jour, _ in points]
    elements = []
    for g in echelle:
        elements.append(f'<line class="tb-grille" x1="{gauche}" x2="{largeur - droite}" y1="{y(g):.1f}" y2="{y(g):.1f}"/>'
                        f'<text class="tb-axe" x="{gauche - 8}" y="{y(g) + 4:.1f}" text-anchor="end">{chiffre(g, "fr")}</text>')
    etiquettes = {0, len(points) - 1} if len(points) < 12 or not colonnes else {0, len(points) // 2, len(points) - 1}
    for i in sorted(etiquettes):
        ancre = "middle" if colonnes else ("start" if i == 0 and len(points) > 1 else "end")
        elements.append(f'<text class="tb-axe" x="{xs[i]:.1f}" y="{hauteur - 8}" text-anchor="{ancre}">'
                        f'{date_fr(points[i][0], courte=True)}</text>')
    if colonnes:
        epaisseur = min(24, pas * .6)
        for x, (_, n) in zip(xs, points):
            gx, dx, haut_c, base = x - epaisseur / 2, x + epaisseur / 2, y(n), y(0)
            r = min(4, base - haut_c, epaisseur / 2)
            elements.append(f'<path class="tb-colonne" d="M{gx:.1f},{base:.1f}V{haut_c + r:.1f}'
                            f'Q{gx:.1f},{haut_c:.1f} {gx + r:.1f},{haut_c:.1f}H{dx - r:.1f}'
                            f'Q{dx:.1f},{haut_c:.1f} {dx:.1f},{haut_c + r:.1f}V{base:.1f}Z"/>')
        derniere = (xs[-1], y(nombres[-1]) - 8, "middle")
    else:
        trace = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y(n):.1f}" for i, (x, (_, n)) in enumerate(zip(xs, points)))
        elements.append(f'<path class="tb-ligne" d="{trace}"/>'
                        f'<line class="tb-reticule" x1="0" x2="0" y1="{haut}" y2="{haut + zone_h}"/>'
                        f'<circle class="tb-point" cx="{xs[-1]:.1f}" cy="{y(nombres[-1]):.1f}" r="5"/>')
        derniere = (xs[-1] + 10, y(nombres[-1]) + 4, "start")
    elements.append(f'<text class="tb-valeur" x="{derniere[0]:.1f}" y="{derniere[1]:.1f}" '
                    f'text-anchor="{derniere[2]}">{chiffre(nombres[-1], "fr")}</text>')
    donnees = [[round(x, 1), round(y(n), 1), date_fr(jour), chiffre(n, "fr")] for x, (jour, n) in zip(xs, points)]
    resume_ = f"{titre} : {chiffre(nombres[-1], 'fr')} au {date_fr(points[-1][0])}"
    return (
        f'<figure class="tb-graphe{" tb-colonnes" if colonnes else ""}" tabindex="0" '
        f'data-points="{e(json.dumps(donnees, ensure_ascii=False))}">'
        f'<figcaption>{e(titre)}{f"<span>{e(note)}</span>" if note else ""}</figcaption>'
        f'<svg viewBox="0 0 {largeur} {hauteur}" role="img" aria-label="{e(resume_)}">{"".join(elements)}</svg>'
        '<p class="tb-bulle" hidden><strong></strong><span></span></p></figure>'
    )


def tableau_chiffres(entetes, lignes, classe=""):
    """Tableau simple. En tête d'un en-tête : « # » pour une colonne de nombres, « ~ » pour une
    colonne masquée sur les petits écrans."""
    def attribut(t):
        classes = " ".join(c for c, marque in (("n", "#"), ("tb-facultatif", "~")) if marque in t[:2])
        return f' class="{classes}"' if classes else ""

    tete = "".join(f'<th scope="col"{attribut(t)}>{e(t.lstrip("#~"))}</th>' for t in entetes)
    corps = "".join(
        "<tr>" + "".join(f'<td{attribut(t)}>{c}</td>' for t, c in zip(entetes, ligne)) + "</tr>"
        for ligne in lignes)
    return f'<div class="tb-defile"><table class="tb-table {classe}"><thead><tr>{tete}</tr></thead><tbody>{corps}</tbody></table></div>'


def tuile(libelle, nombre, detail="", heros=False):
    precision = f'<p class="tb-detail">{detail}</p>' if detail else ""
    return (f'<div class="tb-tuile{" tb-heros" if heros else ""}"><p class="tb-libelle">{e(libelle)}</p>'
            f'<p class="tb-nombre">{valeur(nombre)}</p>{precision}</div>')


def depuis(n, jour):
    """« +1 234 depuis le 24 septembre 2026 » ; vide si l'écart est inconnu."""
    return f"{ecart(n)} depuis le {date_fr(jour)}" if n is not None else ""


def lien_depot(chemin, texte):
    return f'<a href="{DEPOT}/{chemin}">{e(texte)}</a>'


def titre_photo(pid, releve_photo, par_id):
    if pid in par_id:
        return par_id[pid]["titre"]["fr"]
    return (releve_photo or {}).get("titre") or "Sans titre"


def page_tableau(g, releve, historique, gc, erreur_gc, par_id, fiches, maintenant):
    """Tableau de bord : page française non référencée, et compteur de la barre des menus du Mac."""
    adr = g.adr
    chemin = adr.chemin("fr", "tableau")
    code = g.site.get("goatcounter", "").strip()
    vues_pexels = lire_releves_dates("vues-pexels.csv", ("vues", "photos", "abonnes"))
    pinterest = lire_releves_dates("pinterest.csv", ("impressions", "engagements", "clics_sortants",
                                                     "enregistrements", "abonnes"))
    assistants = lire_assistants()
    releves = sorted(((moment(q), t) for q, t in historique["releves"].items()), key=lambda r: r[0])
    rappels = []

    def en_retard(jour, jours, quoi, comment):
        if jour is None:
            rappels.append(f"Aucun relevé {quoi} pour l'instant : {comment}")
        elif (maintenant.date() - jour).days > jours:
            rappels.append(f"Le dernier relevé {quoi} date du {date_fr(jour)} : {comment}")

    # Pexels : totaux du profil, et relevé photo par photo.
    derniere_vue = next((l for l in reversed(vues_pexels) if l["vues"] is not None), None)
    abonnes = next((l for l in reversed(vues_pexels) if l["abonnes"] is not None), None)
    en_retard(derniere_vue["date"] if derniere_vue else None, RETARD_SEMAINE, "des vues Pexels",
              "Telepex l'envoie à chaque relevé ; sinon, "
              + lien_depot("edit/main/releves/vues-pexels.csv", "noter une ligne dans vues-pexels.csv") + ".")
    tuiles, detail_vues, vue_precedente = [], "", None
    if derniere_vue:
        avant = [l for l in vues_pexels if l["vues"] is not None and l["date"] < derniere_vue["date"]]
        if avant:
            vue_precedente = avant[-1]
            detail_vues = depuis(derniere_vue["vues"] - vue_precedente["vues"], vue_precedente["date"])
        tuiles.append(tuile("Vues sur Pexels", derniere_vue["vues"],
                            detail_vues or f"relevé du {date_fr(derniere_vue['date'])}", heros=True))
    if abonnes:
        tuiles.append(tuile("Abonnés", abonnes["abonnes"], f"relevé du {date_fr(abonnes['date'])}"))
    if releves:
        (quand, totaux), precedent = releves[-1], (releves[-2] if len(releves) > 1 else None)
        for libelle, cle in (("Téléchargements", "telechargements"), ("J'aime", "jaime"),
                             ("Photos retenues", "retenues")):
            detail = (depuis(totaux[cle] - precedent[1][cle], precedent[0].date())
                      if precedent and totaux[cle] is not None and precedent[1][cle] is not None
                      else f"relevé du {date_fr(quand.date())}")
            tuiles.append(tuile(libelle, totaux[cle], detail))
    en_retard(moment(releve["date"]).date() if releve else None, RETARD_SEMAINE, "photo par photo",
              "Telepex l'envoie après chaque scan (session T).")

    # Semaine après semaine : la dernière valeur connue de chaque semaine.
    semaines = {}
    for l in vues_pexels:
        s = semaines.setdefault(lundi(l["date"]), {})
        s.update({k: l[k] for k in ("vues", "abonnes") if l[k] is not None})
    for quand, totaux in releves:
        s = semaines.setdefault(lundi(quand.date()), {})
        s.update({k: totaux[k] for k in ("telechargements", "jaime", "retenues") if totaux[k] is not None})
    lignes_semaines, precedente = [], {}
    for s in sorted(semaines):
        v = semaines[s]
        lignes_semaines.append([
            date_fr(s, courte=True, annee=True),
            valeur(v.get("vues")) + (f' <span class="tb-ecart">{ecart(v["vues"] - precedente["vues"])}</span>'
                                     if "vues" in v and "vues" in precedente else ""),
            valeur(v.get("abonnes")),
            valeur(v.get("telechargements")) + (
                f' <span class="tb-ecart">{ecart(v["telechargements"] - precedente["telechargements"])}</span>'
                if "telechargements" in v and "telechargements" in precedente else ""),
            valeur(v.get("jaime")),
            valeur(v.get("retenues")),
        ])
        precedente = {**precedente, **v}
    graphes_pexels = (
        graphe("Vues sur Pexels", [(l["date"], l["vues"]) for l in vues_pexels])
        + graphe("Téléchargements", [(q.date(), t["telechargements"]) for q, t in releves],
                 note="" if len(releves) > 1 else "un seul relevé pour l'instant")
    )
    section_pexels = (
        '<section class="tb-section" id="pexels" aria-labelledby="t-pexels"><h2 id="t-pexels">Pexels</h2>'
        f'<div class="tb-tuiles">{"".join(tuiles)}</div><div class="tb-graphes">{graphes_pexels}</div>'
        '<h3>Semaine après semaine</h3>'
        + tableau_chiffres(["Semaine du", "#Vues", "#Abonnés", "#Téléchargements", "~#J'aime", "~#Retenues"],
                           list(reversed(lignes_semaines)))
        + "</section>"
    )

    # Photos : les plus vues, les nouvelles retenues, et toutes, comme dans Telepex.
    section_photos = ""
    if releve:
        semaine, mois = references(historique, releve)
        photos = releve["photos"]
        gains = {pid: gain(pid, 0, p["vues"], semaine) for pid, p in photos.items()}
        ref = f"depuis le relevé du {date_fr(moment(semaine['releve']).date())}" if semaine else ""

        def vignette(pid, taille=64):
            fiche = fiches.get(str(pid)) or {}
            image = fiche.get("image") or f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"
            return (f'<img src="{e(image)}?auto=compress&amp;cs=tinysrgb&amp;w={taille * 2}" width="{taille}" '
                    f'height="{round(taille * .75)}" alt="" loading="lazy" decoding="async">')

        def lien(pid):
            titre = titre_photo(pid, photos.get(pid), par_id)
            cible = adr.chemin("fr", "photo", pid) if pid in par_id else f"https://www.pexels.com/photo/{pid}/"
            return f'<a href="{e(cible)}">{e(titre)}</a>'

        classees = sorted(photos, key=lambda pid: (-(photos[pid]["vues"] or -1), -pid))
        meilleures = [[vignette(pid), lien(pid), valeur(photos[pid]["vues"]), ecart(gains[pid]) or "—",
                       valeur(photos[pid]["telechargements"]), "retenue" if photos[pid]["retenue"] else "refusée"]
                      for pid in classees[:10]]
        if semaine:
            nouvelles = [pid for pid, p in photos.items()
                         if p["retenue"] and not (semaine["photos"].get(str(pid)) or [0, 0, 0, 0])[3]]
            bloc_nouvelles = (
                f'<p>{len(nouvelles)} {"photo retenue" if len(nouvelles) == 1 else "photos retenues"} {ref}'
                + (" : " + ", ".join(lien(pid) for pid in sorted(nouvelles, reverse=True)) if nouvelles else "")
                + ".</p>")
        else:
            bloc_nouvelles = "<p>Les photos nouvellement retenues par la modération apparaîtront au relevé suivant.</p>"
        rangees = []
        for pid in classees:
            p = photos[pid]
            mots = " ".join(p["mots"][:12])
            recherche = plier(f"{titre_photo(pid, p, par_id)} {p['titre']} {pid} {mots}")
            jour = p["import"].replace("-", "")
            etat = ("r" if p["retenue"] else "x") + (" e" if p["evenement"] else "")
            try:
                importee = date_fr(date.fromisoformat(p["import"]))
            except ValueError:
                importee = ""
            rangees.append(
                f'<tr class="{etat}" data-v="{p["vues"] if p["vues"] is not None else -1}" '
                f'data-g="{gains[pid] if gains[pid] is not None else -1}" '
                f'data-t="{p["telechargements"] if p["telechargements"] is not None else -1}" '
                f'data-j="{p["jaime"] if p["jaime"] is not None else -1}" data-d="{jour or 0}" '
                f'data-s="{e(recherche)}">'
                f'<td class="tb-vignette">{vignette(pid, 48)}</td>'
                f'<td>{lien(pid)}<span class="tb-sous">n° {pid} · {"retenue" if p["retenue"] else "refusée"}'
                f'{" · événement marquant" if p["evenement"] else ""}</span></td>'
                f'<td class="n">{valeur(p["vues"])}</td><td class="n tb-facultatif">{ecart(gains[pid]) or "—"}</td>'
                f'<td class="n">{valeur(p["telechargements"])}</td><td class="n tb-facultatif">{valeur(p["jaime"])}</td>'
                f'<td class="tb-facultatif">{importee}</td>'
                f'<td class="tb-facultatif"><a href="https://www.pexels.com/photo/{pid}/">Pexels</a></td></tr>')
        section_photos = (
            '<section class="tb-section" id="photos" aria-labelledby="t-photos"><h2 id="t-photos">Photos</h2>'
            f'<p class="tb-doux">Relevé du {date_fr(moment(releve["date"]).date())}'
            f'{" ; gains " + ref if ref else " ; les gains apparaîtront au relevé de la semaine prochaine"}.</p>'
            '<h3>Les dix plus vues</h3>'
            + tableau_chiffres(["Photo", "Titre", "#Vues", "#Gain de la semaine", "~#Téléchargements", "~Modération"],
                               meilleures, "tb-meilleures")
            + '<h3>Nouvelles photos retenues</h3>' + bloc_nouvelles
            + '<h3 id="toutes">Toutes les photos</h3>'
            '<form class="tb-filtres" hidden role="search" aria-label="Chercher dans les photos">'
            '<label>Chercher <input type="search" name="texte" placeholder="Titre, mot-clé ou numéro"></label>'
            '<label>Afficher <select name="filtre"><option value="">toutes</option>'
            '<option value="r">retenues</option><option value="x">refusées</option>'
            '<option value="e">événements marquants</option></select></label>'
            '<label>Trier par <select name="tri"><option value="v">vues</option><option value="g">gain de la semaine</option>'
            '<option value="t">téléchargements</option><option value="j">J\'aime</option>'
            '<option value="d">date d\'import, récentes d\'abord</option>'
            '<option value="-d">date d\'import, anciennes d\'abord</option></select></label>'
            f'<output name="compte">{chiffre(len(rangees), "fr")} photos</output></form>'
            '<div class="tb-defile"><table class="tb-table tb-photos"><thead><tr><th scope="col">Photo</th>'
            '<th scope="col">Titre</th><th scope="col" class="n">Vues</th><th scope="col" class="n tb-facultatif">Gain</th>'
            '<th scope="col" class="n">Téléch.</th><th scope="col" class="n tb-facultatif">J\'aime</th>'
            '<th scope="col" class="tb-facultatif">Import</th><th scope="col" class="tb-facultatif">Lien</th></tr></thead>'
            f'<tbody>{"".join(rangees)}</tbody></table></div></section>'
        )

    # Site photo : GoatCounter.
    semaines_gc = sorted(historique["goatcounter"].get("semaines", {}).items())
    if gc or semaines_gc:
        blocs = []
        if erreur_gc:
            blocs.append(f'<p class="tb-alerte">{e(erreur_gc)} Chiffres du dernier passage réussi.</p>')
        if gc:
            blocs.append('<div class="tb-tuiles">'
                         + tuile("Visites, 7 derniers jours", gc["visites"])
                         + tuile("Clics vers les photos sur Pexels", gc["clics_photos"], "7 derniers jours")
                         + tuile("Clics « Suivre sur Pexels »", gc["clics_suivre"], "7 derniers jours") + "</div>")
        if semaines_gc:
            blocs.append('<div class="tb-graphes">'
                         + graphe("Visites par semaine", [(date.fromisoformat(s), v["visites"]) for s, v in semaines_gc],
                                  colonnes=True, note="semaine en cours incomplète")
                         + graphe("Clics vers Pexels par semaine",
                                  [(date.fromisoformat(s), v["clics_photos"] + v["clics_suivre"]) for s, v in semaines_gc],
                                  colonnes=True) + "</div>")
            blocs.append('<h3>Semaine après semaine</h3>' + tableau_chiffres(
                ["Semaine du", "#Visites", "#Clics vers les photos", "#Clics « Suivre »"],
                [[date_fr(date.fromisoformat(s), courte=True, annee=True) + ("" if v.get("complete") else " (en cours)"),
                  valeur(v["visites"]),
                  valeur(v["clics_photos"]), valeur(v["clics_suivre"])] for s, v in reversed(semaines_gc)]))
        if gc:
            blocs.append('<div class="tb-colonnes-texte"><div><h3>Provenance, 7 derniers jours</h3>'
                         + tableau_chiffres(["Venues de", "#Visites"], [[e(f), valeur(n)] for f, n in gc["provenance"]])
                         + '</div><div><h3>Provenance depuis le 28 septembre</h3>'
                         + tableau_chiffres(["Venues de", "#Visites"],
                                            [[e(f), valeur(n)] for f, n in gc["provenance_debut"]]) + "</div></div>")
            blocs.append('<h3>Photos les plus cliquées vers Pexels, 7 derniers jours</h3>' + (
                tableau_chiffres(["Titre", "#Clics"], [[e(titre_photo(pid, (releve or {}).get("photos", {}).get(pid), par_id))
                                                        + f' <span class="tb-sous">n° {pid}</span>', valeur(n)]
                                                       for pid, n in gc["photos"]])
                if gc["photos"] else "<p>Aucun clic cette semaine.</p>"))
            blocs.append('<h3>Pages les plus vues, 7 derniers jours</h3>' + tableau_chiffres(
                ["Page", "#Visites"], [[f'<a href="{e(p)}">{e(t or p)}</a>', valeur(n)] for p, t, n in gc["pages"]]))
        section_site = ('<section class="tb-section" id="site" aria-labelledby="t-site"><h2 id="t-site">Site photo</h2>'
                        + "".join(blocs) + "</section>")
    else:
        rappels.append(e(erreur_gc) if erreur_gc else (
            "GoatCounter n'est pas encore relié au tableau de bord : il lui faut une clé d'API en lecture seule, "
            "rangée dans le secret GOATCOUNTER_JETON du dépôt (" + lien_depot("blob/main/releves/README.md", "mode d'emploi")
            + ")."))
        section_site = ('<section class="tb-section" id="site" aria-labelledby="t-site"><h2 id="t-site">Site photo</h2>'
                        f'<p>Les visites et les clics vers Pexels s\'affichent ici dès que GoatCounter est relié ; '
                        f'en attendant, ils se lisent sur <a href="https://{e(code)}.goatcounter.com">{e(code)}.goatcounter.com</a>.</p>'
                        "</section>")

    # Pinterest, relevé à la main chaque semaine.
    derniere_p = pinterest[-1]["date"] if pinterest else None
    en_retard(derniere_p, RETARD_SEMAINE, "Pinterest",
              lien_depot("edit/main/releves/pinterest.csv", "noter une ligne dans pinterest.csv")
              + ", avec les chiffres des 7 derniers jours de Statistiques → Vue d'ensemble.")
    if pinterest:
        section_pinterest = (
            '<div class="tb-graphes">'
            + graphe("Impressions", [(l["date"], l["impressions"]) for l in pinterest])
            + graphe("Clics sortants", [(l["date"], l["clics_sortants"]) for l in pinterest]) + "</div>"
            + tableau_chiffres(["Relevé du", "#Impressions", "~#Engagements", "#Clics sortants", "~#Enregistrements",
                                "~#Abonnés", "~Remarque"],
                               [[date_fr(l["date"], courte=True, annee=True), valeur(l["impressions"]),
                                 valeur(l["engagements"]),
                                 valeur(l["clics_sortants"]), valeur(l["enregistrements"]), valeur(l["abonnes"]),
                                 e(l["remarque"])] for l in reversed(pinterest)]))
    else:
        section_pinterest = ("<p>Aucun relevé pour l'instant. Chaque semaine, "
                             + lien_depot("edit/main/releves/pinterest.csv", "une ligne dans pinterest.csv")
                             + " : les chiffres des 7 derniers jours de Statistiques → Vue d'ensemble.</p>")

    # Assistants IA, relevé chaque mois.
    en_retard(assistants[-1]["date"] if assistants else None, RETARD_MOIS, "des assistants IA",
              lien_depot("edit/main/releves/assistants-ia.csv", "les questions du mois dans assistants-ia.csv") + ".")
    section_ia = (tableau_chiffres(["Relevé du", "#Réponses", "#Citent le site", "~Assistants"],
                                   [[date_fr(r["date"], courte=True, annee=True), valeur(r["reponses"]),
                                     valeur(r["citent"]),
                                     e(", ".join(sorted(a for a in r["assistants"] if a)))] for r in reversed(assistants)])
                  if assistants else "<p>Aucun relevé pour l'instant : une fois par mois, les mêmes questions aux "
                  "assistants, notées dans " + lien_depot("edit/main/releves/assistants-ia.csv", "assistants-ia.csv") + ".</p>")

    detail = [
        (f"https://{code}.goatcounter.com", "GoatCounter : visites et clics, en détail") if code else None,
        ("https://analytics.pinterest.com/", "Statistiques Pinterest"),
        ("https://search.google.com/search-console", "Google Search Console : apparitions et clics dans Google"),
        ("https://www.bing.com/webmasters", "Bing Webmaster Tools : Bing et Copilot"),
        (g.site.get("profil_pexels", ""), "Profil Pexels"),
        (f"{DEPOT}/tree/main/releves", "Les relevés sur GitHub"),
    ]
    maj = maintenant.astimezone(timezone.utc)
    contenu = (
        '<div class="tableau">'
        '<section class="ouverture tb-tete"><p class="surtitre">Page non référencée</p><h1>Tableau de bord</h1>'
        f'<p class="accroche">Mis à jour le {date_fr(maj.date())} à {maj:%H} h {maj:%M} (UTC), chaque nuit et après '
        "chaque relevé. Les chiffres Pexels viennent des relevés de Telepex ou notés à la main ; rien n'est relevé "
        "sur pexels.com par le site.</p>"
        + (f'<ul class="tb-rappels" aria-label="Relevés à faire">{"".join(f"<li>{r}</li>" for r in rappels)}</ul>'
           if rappels else "")
        + '<nav class="tb-sommaire" aria-label="Sections"><a href="#pexels">Pexels</a>'
        + ('<a href="#photos">Photos</a><a href="#toutes">Toutes les photos</a>' if releve else "")
        + '<a href="#site">Site photo</a><a href="#pinterest">Pinterest</a><a href="#ia">Assistants IA</a>'
        '<a href="#detail">Détail</a></nav></section>'
        + section_pexels + section_photos + section_site
        + '<section class="tb-section" id="pinterest" aria-labelledby="t-pinterest"><h2 id="t-pinterest">Pinterest</h2>'
        + section_pinterest + "</section>"
        + '<section class="tb-section" id="ia" aria-labelledby="t-ia"><h2 id="t-ia">Assistants IA</h2>'
        + section_ia + "</section>"
        + '<section class="tb-section" id="detail" aria-labelledby="t-detail"><h2 id="t-detail">Pour le détail</h2><ul>'
        + "".join(f'<li><a href="{e(url)}">{e(texte)}</a></li>' for url, texte in filter(None, detail))
        + "</ul></section></div>"
    )
    chemins = {l: chemin for l in LANGUES}
    ecrire(adr.fichier(chemin), g.page("fr", titre="Tableau de bord", description="", chemins=chemins,
                                       contenu=contenu, classe="page-tableau", prive=("tableau.css", "tableau.js")))

    # Compteur de la barre des menus du Mac (releves/barre-des-menus/) : les derniers chiffres,
    # relus toutes les heures.
    totaux = releves[-1][1] if releves else {}
    compteur = {
        "mis_a_jour": maj.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pexels": {
            "vues": derniere_vue["vues"] if derniere_vue else None,
            "vues_releve": derniere_vue["date"].isoformat() if derniere_vue else None,
            # Écart des vues depuis le relevé précédent, et sa date.
            "vues_gain": derniere_vue["vues"] - vue_precedente["vues"] if vue_precedente else None,
            "vues_gain_depuis": vue_precedente["date"].isoformat() if vue_precedente else None,
            "abonnes": abonnes["abonnes"] if abonnes else None,
            "telechargements": totaux.get("telechargements"),
            "jaime": totaux.get("jaime"),
            "retenues": totaux.get("retenues"),
            "releve": releves[-1][0].isoformat() if releves else None,
        },
        "site_7_jours": ({"visites": gc["visites"], "clics_pexels": gc["clics_photos"] + gc["clics_suivre"]}
                         if gc else None),
    }
    ecrire(adr.fichier(adr.chemin("fr", "compteur")), json.dumps(compteur, ensure_ascii=False, indent=1) + "\n")
    return rappels


# ---------------------------------------------------------------- publications à la main, pour Telepex

# Publications que Karl fait à la main (RedNote, Facebook), préparées en session dans
# reseaux/publications/<id>/ : publication.json et ses images (format : reseaux/README.md).
# L'onglet « Publications » de Telepex, son application Mac, les lit dans
# /tableau-de-bord/publications.json ; quand Karl en valide une, Telepex ajoute une ligne à
# reseaux/publications-validees.csv, et la publication n'est plus proposée. Rien que de
# public : ces textes et ces images sont faits pour être publiés.
PUBLICATIONS = RACINE / "reseaux" / "publications"
VALIDEES = RACINE / "reseaux" / "publications-validees.csv"
RESEAUX_TELEPEX = ("rednote", "facebook")
VALIDEES_GARDEES = 30  # jours pendant lesquels une publication validée reste dans la liste
ANNULATION = "telepex annulation"  # remarque d'une validation annulée dans Telepex
# Nom des vidéos de chaque langue, tel que l'écrit reseaux/videos/fabrique.py.
SUFFIXE_VIDEO = {"zh": "chinois", "fr": "français", "en": "anglais"}


def lire_validees():
    """Date de validation de chaque publication, d'après le journal que tient Telepex, lu dans
    l'ordre du fichier : la dernière ligne d'un id l'emporte, et une ligne « Telepex
    annulation » remet la publication à faire. Les vidéos validées hors de la liste y ont
    aussi leurs lignes, sans dossier dans reseaux/publications/ : elles ne servent pas ici."""
    validees = {}
    for ligne in lire_csv(VALIDEES) if VALIDEES.exists() else []:
        ident, jour = (ligne.get("id") or "").strip(), (ligne.get("date") or "").strip()
        if ident and (ligne.get("remarque") or "").strip().lower() == ANNULATION:
            validees.pop(ident, None)
        elif ident and jour:
            validees[ident] = jour
    return validees


def publication_telepex(adr, dossier, validees):
    """Une publication au format que lit Telepex, ou None si elle est incomplète. Ses images
    sont publiées tant qu'elle reste à faire."""
    pub = json.loads((dossier / "publication.json").read_text(encoding="utf-8"))
    textes = [t for t in pub.get("textes") or [] if isinstance(t, dict) and (t.get("texte") or "").strip()]
    titres = [t["texte"] for t in textes if (t.get("nom") or "").lower().startswith("titre")]
    corps = [t["texte"] for t in textes if not (t.get("nom") or "").lower().startswith("titre")]
    ident, langue = pub.get("id"), pub.get("langue")
    if not (isinstance(ident, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ident)
            and pub.get("reseau") in RESEAUX_TELEPEX and corps):
        return None
    validee = validees.get(ident)
    entree = {"id": ident, "reseau": pub["reseau"], "langue": langue}
    if titres:
        entree["titre"] = titres[0]
    entree["texte"] = corps[0]
    traduction = [t.get("texte") for t in (pub.get("traduction") or {}).get("textes") or []
                  if isinstance(t, dict) and (t.get("texte") or "").strip()]
    if traduction:
        entree["traduction"] = "\n\n".join(traduction)
    entree["hashtags"] = list(dict.fromkeys(re.findall(r"#[^\s#]+", corps[0])))
    # Images du dossier seulement, et rien d'autre : tout ce qui est copié ici devient public.
    noms = [Path(nom) for nom in pub.get("images") or []]
    if any(nom.is_absolute() or ".." in nom.parts or nom.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp")
           or not (dossier / nom).is_file() for nom in noms):
        return None
    sources = [dossier / nom for nom in noms]
    entree["images"] = []
    for rang, source in enumerate([] if validee else sources, 1):
        chemin = f"{adr.chemin('fr', 'publication', ident)}{rang:02d}{source.suffix.lower()}"
        adr.fichier(chemin).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, adr.fichier(chemin))
        entree["images"].append({"url": adr.absolue(chemin), "nom": chemin.rsplit("/", 1)[1]})
    if pub.get("carrousel") and langue in SUFFIXE_VIDEO:
        entree["video"] = f"{pub['carrousel']} ({SUFFIXE_VIDEO[langue]}).mp4"
    for cle, champ in (("conseil", "heure_conseillee"), ("prevue", "date_prevue")):
        if pub.get(champ):
            entree[cle] = pub[champ]
    # Repris tels quels quand la publication les a : le pas à pas, où Telepex accroche ses
    # boutons d'après quelques mots (reseaux/README.md), la forme, le sujet et le carrousel.
    etapes = pub.get("etapes")
    if isinstance(etapes, list) and etapes and all(isinstance(e, str) and e.strip() for e in etapes):
        entree["etapes"] = etapes
    for champ in ("forme", "sujet", "carrousel"):
        if isinstance(pub.get(champ), str) and pub[champ].strip():
            entree[champ] = pub[champ]
    entree["validee"] = validee
    return entree


def ecrire_publications(adr, maintenant):
    """/tableau-de-bord/publications.json : les publications à faire, par date prévue, puis
    celles validées depuis moins de VALIDEES_GARDEES jours. Rend (à faire, validées, écartées)."""
    validees = lire_validees()
    limite = (maintenant - timedelta(days=VALIDEES_GARDEES)).date().isoformat()
    liste, ecartees = [], []
    for dossier in sorted(PUBLICATIONS.iterdir()) if PUBLICATIONS.is_dir() else []:
        if not (dossier / "publication.json").is_file():
            continue
        try:
            entree = publication_telepex(adr, dossier, validees)
        except (OSError, ValueError, TypeError, AttributeError):
            entree = None
        if entree is None:
            ecartees.append(dossier.name)
        elif not entree["validee"] or entree["validee"][:10] >= limite:
            liste.append(entree)
    liste.sort(key=lambda p: (bool(p["validee"]), p.get("prevue") or "9999-12-31", p["id"]))
    ecrire(adr.fichier(adr.chemin("fr", "publications")), json.dumps(
        {"genere": maintenant.strftime("%Y-%m-%dT%H:%M:%SZ"), "publications": liste},
        ensure_ascii=False, indent=1) + "\n")
    a_faire = sum(1 for p in liste if not p["validee"])
    return a_faire, len(liste) - a_faire, ecartees


# ---------------------------------------------------------------- llms.txt, pour les assistants IA


LLMS = {
    "fr": {
        "titre": "Karl Forterre — photographies libres de droits",
        "compte": "{photos} photos, en {series} séries et {galeries} galeries.",
        "auteur": "{nom} : {metiers}{lieu}. Site d'auteur : {site}",
        "licence": "Licence : licence Pexels. Usage gratuit, personnel ou commercial, sans inscription ni "
                   "obligation de crédit ; il est interdit de vendre une photo telle quelle ou de la "
                   "redistribuer sur une autre banque d'images. Texte officiel : {licence}",
        "credit": "Crédit conseillé : « Photo : {nom} / Pexels », avec un lien vers la page de la photo.",
        "pages_photos": "Chaque photo a sa page sur ce site, dont l'adresse finit par son numéro Pexels (par "
                        "exemple {exemple}) : elle mène à sa page Pexels, où la photo se télécharge en pleine "
                        "définition.",
        "usages": "Photos utilisées notamment par {sites}, d'après Pexels.",
        "langues": "Langues : français{fr}, anglais{en}, chinois simplifié{zh}.",
        "principales": "Pages principales",
        "lieux": "Galeries par lieu",
        "themes": "Galeries par thème",
        "donnees": "Données",
        "complet": "Toutes les photos : titre, galeries, mots-clés et adresse de chacune",
        "complet_titre": "toutes les photos",
        "apercu": "Sélection, séries, galeries et chiffres, en JSON",
        "plan": "Plan du site, avec les traductions de chaque page",
        "flux": "Dernières photos, en RSS",
        "auteur_titre": "L'auteur",
        "autres_langues": "Autres langues",
        "photos_titre": "Photos",
        "numero": "Pexels n° {id}",
        "dans": "galeries : {galeries}",
        "mots": "mots-clés : {mots}",
    },
    "en": {
        "titre": "Karl Forterre — royalty-free photographs",
        "compte": "{photos} photos, in {series} series and {galeries} galleries.",
        "auteur": "{nom}: {metiers}{lieu}. Author website: {site}",
        "licence": "License: the Pexels license. Free to use, for personal or commercial purposes, with no "
                   "account and no attribution required; selling an unaltered copy of a photo or redistributing "
                   "it on another stock photo platform is not allowed. Official text: {licence}",
        "credit": "Suggested credit: “Photo: {nom} / Pexels”, with a link to the photo's page.",
        "pages_photos": "Each photo has its own page on this site, whose address ends with its Pexels ID (for "
                        "example {exemple}); it leads to the photo's Pexels page, where the full-resolution file "
                        "can be downloaded.",
        "usages": "Photos used by {sites}, among others, according to Pexels.",
        "langues": "Languages: French{fr}, English{en}, Simplified Chinese{zh}.",
        "principales": "Main pages",
        "lieux": "Galleries by place",
        "themes": "Galleries by theme",
        "donnees": "Data",
        "complet": "Every photo: title, galleries, keywords and address",
        "complet_titre": "every photo",
        "apercu": "Selection, series, galleries and figures, as JSON",
        "plan": "Sitemap, with the translations of each page",
        "flux": "Latest photos, as RSS",
        "auteur_titre": "The photographer",
        "autres_langues": "Other languages",
        "photos_titre": "Photos",
        "numero": "Pexels no. {id}",
        "dans": "galleries: {galeries}",
        "mots": "keywords: {mots}",
    },
    "zh": {
        "titre": "Karl Forterre — 免版税摄影作品",
        "compte": "共 {photos} 张照片，分为 {series} 个专题和 {galeries} 个图库。",
        "auteur": "{nom}：{metiers}{lieu}。个人网站：{site}",
        "licence": "许可协议：Pexels 许可协议。可免费用于个人或商业用途，无需注册，也不强制署名；不得原样出售照片，"
                   "也不得在其他图片素材网站上转发。官方文本：{licence}",
        "credit": "建议署名：「摄影：{nom} / Pexels」，并附上照片页面的链接。",
        "pages_photos": "每张照片在本站都有自己的页面，网址以其 Pexels 编号结尾（例如 {exemple}），"
                        "页面链接到该照片的 Pexels 页面，可在那里下载原图。",
        "usages": "据 Pexels 通知，这些照片曾被 {sites} 等网站使用。",
        "langues": "语言：法语{fr}，英语{en}，简体中文{zh}。",
        "principales": "主要页面",
        "lieux": "按地点分类的图库",
        "themes": "按主题分类的图库",
        "donnees": "数据",
        "complet": "全部照片：每张照片的标题、图库、关键词和链接",
        "complet_titre": "全部照片",
        "apercu": "精选、专题、图库与统计数据（JSON）",
        "plan": "网站地图，含每个页面的各语言版本",
        "flux": "最新照片（RSS）",
        "auteur_titre": "关于摄影师",
        "autres_langues": "其他语言",
        "photos_titre": "照片",
        "numero": "Pexels 编号 {id}",
        "dans": "图库：{galeries}",
        "mots": "关键词：{mots}",
    },
}


def une_ligne(texte):
    return " ".join(str(texte).split())


def ecrire_llms(g, photos, galeries, series, couleurs, selection, par_photo, langue):
    """llms.txt (llmstxt.org) : le site présenté aux assistants IA, en Markdown, dans une
    langue. llms-full.txt y ajoute les réponses entières et la liste de toutes les photos.
    Pages françaises : /llms.txt ; anglaises : /en/llms.txt ; chinoises : /zh/llms.txt."""
    adr = g.adr
    t, x = TEXTES[langue], LLMS[langue]
    nom = g.site.get("nom", "Karl Forterre")
    p = g.reglages["personne"] if g.reglages.has_section("personne") else {}

    def url(genre, cle=None, l=langue):
        return adr.absolue(adr.chemin(l, genre, cle))

    presentation = paragraphes(traduit(g.reglages["a-propos"], "texte", langue))
    resume = ("" if langue == "zh" else " ").join([
        traduit(g.reglages["accueil"], "accroche", langue), *presentation[:1],
        x["compte"].format(photos=chiffre(len(photos), langue), series=len(series), galeries=len(galeries))])
    metiers = liste_mots(traduit(p, "metier", langue))
    lieu = traduit(p, "lieu", langue)
    sites = list(dict.fromkeys(u["site"] for usages in g.usages.values() for u in usages if u["type"] == "site"))
    preuve = preuve_sociale(g.preuve, langue)
    point = "。" if langue == "zh" else "."
    exemple = (selection or photos or [{"id": 0}])[0]["id"]
    faits = [
        x["auteur"].format(nom=nom, metiers=enumeration(metiers, langue) if metiers else "",
                           lieu=entre_parentheses(lieu, langue) if lieu else "", site=site_auteur(g)),
        x["licence"].format(licence=pexels(LICENCE, langue)),
        x["credit"].format(nom=nom),
        x["pages_photos"].format(exemple=url("photo", exemple)),
        *([preuve + point] if preuve else []),
        *([x["usages"].format(sites=enumeration(sites, langue))] if sites else []),
        x["langues"].format(**{l: entre_parentheses(url("accueil", l=l), langue) for l in LANGUES}),
    ]
    tete = [f"# {x['titre']}", "", f"> {une_ligne(resume)}", "", *(f"- {une_ligne(f)}" for f in faits)]

    def section(titre, lignes):
        return ["", f"## {titre}", "", *lignes] if lignes else []

    principales = [
        f"- [{t['accueil_court']}]({url('accueil')}): {une_ligne(traduit(g.reglages['accueil'], 'accroche', langue))}",
        f"- [{t['faq']}]({url('faq')}): {t['faq_intro']}",
        f"- [{t['utiliser']}]({url('utiliser')}): {LICENCE_PEXELS[langue]['intro']}",
        f"- [{t['a_propos']}]({url('apropos')}): {une_ligne(presentation[0]) if presentation else nom}",
        *([f"- [{t['series']}]({url('series')}): {t['series_intro']}"] if series else []),
        f"- [{t['galeries']}]({url('galeries')}): {t['galeries_intro']}",
        *([f"- [{t['usages_galerie']}]({url('galerie', CLE_USAGES)}): {t['usages_intro']}"] if g.usages else []),
    ]
    lignes_series = [
        f"- [{s['titre'][langue]}]({url('serie', s['cle'])}): {infos_serie(s, langue)}"
        + (f". {tronquer(s['texte'][langue][0], 300)}" if s["texte"][langue] else "")
        for s in series
    ]

    def lignes_galeries(genre):
        return [f"- [{gal['titre'][langue]}]({url('galerie', gal['cle'])}): "
                + une_ligne(" ".join(filter(None, [gal["description"][langue],
                                                   entre_parentheses(nombre_photos(len(gal["photos"]), langue), langue)])))
                for gal in galeries if gal["type"] == genre]

    questions = lire_questions(g, langue, photos, galeries, series, markdown=True)
    lignes_questions = [f"- [{question}]({url('faq')}#{cle}): {une_ligne(' '.join(reponse))}"
                        for cle, question, reponse in questions]
    lignes_selection = [f"- [{ph['titre'][langue]}]({url('photo', ph['id'])}): {x['numero'].format(id=ph['id'])}"
                        for ph in selection]
    auteur = paragraphes(traduit(g.reglages["a-propos"], "auteur", langue))
    lignes_auteur = ([f"- [{urlparse(site_auteur(g)).netloc}]({site_auteur(g)}): {une_ligne(' '.join(auteur))}"]
                     if site_auteur(g) and auteur else [])
    lignes_auteur += [f"- [{t['profil']}]({pexels(g.site.get('profil_pexels', ''), langue)})"]
    lignes_auteur += [f"- [{nom_reseau}]({adresse})" for nom_reseau, adresse in g.reseaux]
    lignes_donnees = [
        f"- [llms-full.txt]({url('llms_complet')}): {x['complet']}",
        f"- [apercu.json]({adr.absolue(adr.base + '/apercu.json')}): {x['apercu']}",
        f"- [sitemap.xml]({adr.absolue(adr.base + '/sitemap.xml')}): {x['plan']}",
        *([f"- [{t['flux']}]({url('flux')}): {x['flux']}"] if langue in LANGUES_FLUX else []),
    ]
    facultatif = [f"- [{c['titre'][langue]}]({url('couleur', c['cle'][langue])}): "
                  f"{nombre_photos(len(c['photos']), langue)}" for c in couleurs]
    facultatif += [f"- [llms.txt ({HREFLANG[l]})]({url('llms', l=l)}): {x['autres_langues']}"
                   for l in LANGUES if l != langue]
    corps = (tete + section(x["principales"], principales) + section(t["series"], lignes_series)
             + section(x["lieux"], lignes_galeries("lieu")) + section(x["themes"], lignes_galeries("theme"))
             + section(t["faq"], lignes_questions) + section(t["selection"], lignes_selection)
             + section(x["auteur_titre"], lignes_auteur) + section(x["donnees"], lignes_donnees)
             + section("Optional", facultatif))
    ecrire(adr.fichier(adr.chemin(langue, "llms")), "\n".join(corps) + "\n")

    # llms-full.txt : les réponses entières et chaque photo, de la plus récente à la plus ancienne.
    reponses = [f"### {question}\n\n" + "\n\n".join(reponse) for _, question, reponse in questions]
    lignes_photos = []
    for ph in photos:
        details = [x["numero"].format(id=ph["id"]), f"{ph['largeur']} × {ph['hauteur']} px"]
        if par_photo[ph["id"]]:
            details.append(x["dans"].format(galeries=", ".join(gal["titre"][langue] for gal in par_photo[ph["id"]])))
        if ph["mots"][langue]:
            details.append(x["mots"].format(mots=", ".join(ph["mots"][langue])))
        lignes_photos.append(f"- [{une_ligne(ph['titre'][langue])}]({url('photo', ph['id'])}): " + " · ".join(details))
    complet = ([f"# {x['titre']} — {x['complet_titre']}", "", f"> {une_ligne(resume)}", "",
                *(f"- {une_ligne(f)}" for f in faits)]
               + (["", f"## {t['faq']}", "", *reponses] if reponses else [])
               + ["", f"## {x['photos_titre']}", "", *lignes_photos])
    ecrire(adr.fichier(adr.chemin(langue, "llms_complet")), "\n".join(complet) + "\n")


# ---------------------------------------------------------------- programme


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("--fiches-seulement", action="store_true")
    options.add_argument("--max-appels", type=int, default=180)
    options.add_argument("--enregistrer-parutions", action="store_true")
    options.add_argument("--indexnow", action="store_true")
    options.add_argument("--envoyer-indexnow", action="store_true")
    options.add_argument("--enregistrer-historique", action="store_true")
    args = options.parse_args()
    if args.envoyer_indexnow:
        raise SystemExit(envoyer_indexnow())

    ids = lire_photos()
    fiches = charger_fiches()
    lues = completer_fiches(ids, fiches, args.max_appels)
    manquantes = sum(1 for i in ids if str(i) not in fiches)
    print(f"{len(ids)} photos listées, {lues} fiches lues sur Pexels, {manquantes} encore à lire.")
    if args.fiches_seulement:
        return

    reglages = lire_ini("site.ini")
    anglais, francais = lire_textes()
    photos, sans_titre = assembler_photos(ids, fiches, anglais, francais, lire_suivi(), lire_traductions("zh"))
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
    publiees = {p["id"] for p in photos}
    g.usages = {i: u for i, u in lire_usages().items() if i in publiees}
    par_photo = {p["id"]: [gal for gal in galeries if p in gal["photos"]] for p in photos}
    par_serie = {p["id"]: [s for s in series if p in s["photos"]] for p in photos}
    par_couleur = {p["id"]: [c for c in couleurs if p in c["photos"]] for p in photos}
    proches = photos_proches(photos, par_photo)
    avec_series = bool(series)
    g.descriptions_photos = descriptions_photos(photos)
    for langue in LANGUES:
        page_accueil(g, photos, galeries, series, selection, ouverture, langue)
        page_galeries(g, galeries, series, couleurs, langue, par_id)
        page_usages(g, par_id, series, langue)
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
        avec_faq = page_questions(g, photos, galeries, series, langue)
        for gal in galeries:
            page_galerie(g, gal, series, langue)
        ecrire_renvois(g, galeries, langue)
        for rang, p in enumerate(photos):
            precedente = photos[rang - 1] if rang > 0 else None
            suivante = photos[rang + 1] if rang + 1 < len(photos) else None
            page_photo(g, p, langue, precedente, suivante, par_photo[p["id"]], par_serie[p["id"]], avec_series,
                       proches[p["id"]], par_couleur[p["id"]])
    # Flux RSS en français et en anglais seulement : Pinterest, qui les lit, est bloqué en Chine.
    for langue in LANGUES_FLUX:
        for gal in galeries:
            ecrire_flux(adr, langue, f'{gal["titre"][langue]} — {g.site.get("nom", "")}',
                        gal["description"][langue], adr.chemin(langue, "galerie", gal["cle"]),
                        adr.chemin(langue, "flux_galerie", gal["cle"]),
                        parutions_flux(journal.get(gal["cle"], {}), par_id, r["flux_max"]))
        ecrire_flux(adr, langue, TEXTES[langue]["accueil"], reglages["accueil"].get(f"accroche_{langue}", ""),
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux"), [(p, p["vue_le"]) for p in photos[:30]])
        ecrire_flux(adr, langue, TEXTES[langue]["autres_photos"], TEXTES[langue]["suffixe"],
                    adr.chemin(langue, "accueil"), adr.chemin(langue, "flux_autres"),
                    parutions_flux(journal.get(AUTRES, {}), par_id, r["flux_max"]))
    page_introuvable(g, series)
    for langue in LANGUES:
        ecrire_llms(g, photos, galeries, series, couleurs, selection, par_photo, langue)
    entrees = pages_du_plan(adr, photos, galeries, series, couleurs, avec_faq, usages=bool(g.usages))
    journal_pages, signaler = suivre_pages(adr, entrees, AUJOURDHUI)
    ecrire_plan(adr, entrees, journal_pages)
    ecrire_apercu(g, photos, galeries, series, selection, lire_libelles("selection.txt"), par_photo, par_serie)
    # Tableau de bord (page non référencée) et compteur de la barre des menus du Mac.
    maintenant = datetime.now(timezone.utc)
    releve = lire_releve_photos()
    historique = charger_historique()
    completer_historique(historique, releve)
    gc, erreur_gc = None, None
    jeton = os.environ.get("GOATCOUNTER_JETON", "").strip()
    code_gc = reglages["site"].get("goatcounter", "").strip()
    if jeton and code_gc:
        try:
            gc = lire_goatcounter(code_gc, jeton, historique["goatcounter"], maintenant)
        except GoatCounterErreur as erreur:
            erreur_gc = str(erreur)
    if args.enregistrer_historique:
        enregistrer_historique(historique)
    rappels = page_tableau(g, releve, historique, gc, erreur_gc, par_id, fiches, maintenant)
    a_faire, validees, ecartees = ecrire_publications(adr, maintenant)
    # IndexNow : la clé, publique, est publiée à la racine du site ; les moteurs y vérifient
    # que les pages signalées viennent bien du propriétaire du site.
    cle = cle_indexnow(reglages)
    if cle:
        ecrire(adr.fichier(f"{adr.base}/{cle}.txt"), cle)
    if args.indexnow:
        enregistrer_pages(journal_pages)
        preparer_indexnow(adr, cle, signaler)
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
    print(f"Aperçu pour karlforterre.fr (apercu.json) : {len(selection)} photos de la sélection, "
          f"{len(series)} séries, {len(galeries)} galeries.")
    attente = sum(1 for cle, membres, _ in flux for p in membres if str(p["id"]) not in journal.get(cle, {}))
    print(f"Pinterest : {du_jour} parutions ajoutées aujourd'hui, {attente} en attente dans les files"
          + ("." if args.enregistrer_parutions else " (journal non enregistré)."))
    etat_gc = ("relié" if gc else erreur_gc if erreur_gc else
               "non relié (pas de clé GOATCOUNTER_JETON)" if not jeton else "non relié (pas de code dans site.ini)")
    print(f"Tableau de bord : relevé photo par photo du "
          f"{releve['date'] if releve else '(aucun)'}, GoatCounter {etat_gc}, {len(rappels)} rappel(s)"
          + (" ; historique enregistré." if args.enregistrer_historique else " (historique non enregistré)."))
    print(f"Publications pour Telepex : {a_faire} à faire, {validees} validée(s) depuis moins de "
          f"{VALIDEES_GARDEES} jours" + (f" ; laissées de côté (illisibles, incomplètes, ou ni RedNote ni "
                                        f"Facebook) : {', '.join(ecartees)}." if ecartees else "."))
    print(f"Assistants IA : llms.txt et llms-full.txt en {len(LANGUES)} langues"
          + (", questions fréquentes." if avec_faq else "."))
    print(f"Pages : {len(journal_pages)} au plan du site, {len(signaler)} nouvelles, modifiées ou supprimées"
          + (" : à signaler par IndexNow (_indexnow/envoi.json)." if args.indexnow and cle
             else " (IndexNow : pas de clé dans site.ini)." if args.indexnow
             else " (journal non enregistré)."))


if __name__ == "__main__":
    main()
