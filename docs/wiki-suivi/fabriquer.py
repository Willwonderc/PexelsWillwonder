"""Suivi des photos de Karl dans Wikipédia (docs/wiki-route.md).

Outil de session, à relancer après chaque ajout : il lit les photos déjà dans un article
(vitrine/wikipedia.csv) et les pistes (pistes.csv, à côté de ce fichier), puis écrit :

- suivi-wikipedia.xlsx, le tableau de suivi (onglets Suivi, Bilan, À rassembler) ;
- vos-photos-dans-wikipedia.pdf, le même suivi à lire, en trois parties : les photos
  déposées (dans un article), refusées (retirées par un contributeur ou écartées d'avance)
  et à demander (prêtes, à vérifier, à identifier, en attente), avec leur vignette ;
- consigne-rassemblement.txt, la consigne que Karl colle dans Claude sur son Mac pour
  rassembler les originaux des photos prêtes avant de les verser sur Commons.

Il demande openpyxl (python3 -m pip install openpyxl), curl pour les vignettes et Chromium
pour le PDF (son chemin dans la variable CHROMIUM, sinon cherché sur la machine) : des
outils de session, absents du site lui-même. Les vignettes, gardées dans le dossier
temporaire de la machine, viennent de Pexels et, pour une photo seulement sur Commons, de
Commons (une demande par photo).

    python3 docs/wiki-suivi/fabriquer.py [--verifie-le AAAA-MM-JJ]

--verifie-le date le contrôle de la wiki route (chaque photo relue dans son article, étape 6 de
docs/wiki-route.md) : le PDF le dit. Sans lui, il n'affirme rien de tel.
"""

import base64
import csv
import glob
import hashlib
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent.parent

LANGUES = {"fr": "français", "en": "anglais", "es": "espagnol", "eu": "basque", "ast": "asturien",
           "it": "italien", "de": "allemand", "gl": "galicien", "ca": "catalan", "oc": "occitan",
           "br": "breton", "pt": "portugais"}
# Ordre d'affichage et couleur de chaque statut.
STATUTS = {
    "Prête": "FFF2CC",           # case préparée : verser la photo sur Commons, puis l'article
    "À vérifier": "DDEBF7",      # sujet identifié, article à vérifier par la session
    "À identifier": "EDE7F6",    # Karl doit dire ce que montre la photo
    "En attente": "F2F2F2",      # pas de place pour l'instant
    "Dans l'article": "E2EFDA",  # en ligne, et dans le panneau du site
    "Refusée": "F4CCCC",         # retirée d'un article par un autre contributeur : ne pas l'y remettre
    "Écartée": "FBE5D6",         # jamais proposée ; raison dans la colonne Remarques
}
APRES = ("Refusée", "Écartée")   # statuts rangés après les photos en ligne
POLICE = "Arial"
UA = "KarlForterre-session/1.0 (contact@karlforterre.fr)"
CACHE = Path(tempfile.gettempdir()) / "wiki-suivi-vignettes"
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]
# Nom local des fichiers et de la vignette dans la ligne de la photo (docs/wiki-route.md, étape 3).
PREFIXES = {"fr": "Fichier", "eu": "Fitxategi", "es": "Archivo", "gl": "Ficheiro", "ast": "Imaxe"}
VIGNETTES = {"fr": "vignette"}


def lire(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in ligne.items() if k} for ligne in csv.DictReader(f)]


def lien_article(wiki, article, section=""):
    base = f"https://{wiki}.wikipedia.org"
    if section != "":
        return f"{base}/w/index.php?title={quote(article.replace(' ', '_'))}&action=edit&section={section}"
    return f"{base}/wiki/{quote(article.replace(' ', '_'))}"


def lien_commons(fichier):
    return "https://commons.wikimedia.org/wiki/File:" + quote(fichier.replace(" ", "_"))


def lignes():
    titres = {l["photo"]: l["titre_fr"] for l in lire(RACINE / "vitrine" / "donnees" / "textes-fr.csv")}
    faites = []
    for w in lire(RACINE / "vitrine" / "wikipedia.csv"):
        faites.append({
            "photo": w["photo"], "sujet": titres.get(w["photo"]) or w.get("titre_fr") or w["fichier"],
            "statut": "Dans l'article", "wiki": w["wiki"], "article": w["article"],
            "partie": w["partie"] or "infobox", "legende": w["legende"], "fichier": w["fichier"],
            "date": w["ajoutee_le"], "section": "",
            "remarques": "" if w["photo"] else "Seulement sur Commons : le panneau mène à sa page Commons."})
    faites.sort(key=lambda l: l["date"], reverse=True)
    pistes = [dict(p, date="") for p in lire(ICI / "pistes.csv")]
    ordre = list(STATUTS)
    pistes.sort(key=lambda p: ordre.index(p["statut"]) if p["statut"] in ordre else len(ordre))
    avant = [p for p in pistes if p["statut"] not in APRES]
    return avant + faites + [p for p in pistes if p["statut"] in APRES]


def consigne(pretes):
    liste = "\n".join(f"- {p['photo']} → {p['fichier']}" for p in pretes)
    return f"""Je verse mes photos sur Wikimedia Commons. Rassemble les fichiers ORIGINAUX des photos ci-dessous dans le dossier ~/Downloads/Commons à verser/ (crée-le s'il n'existe pas).

Les photos (numéro Pexels → nom à donner au fichier) :
{liste}

Méthode :
1. Trouve où mon application Telepex garde ses données (par exemple dans ~/Library/Application Support/ ou ~/Library/Containers/, ou dans ses réglages) et lis-les sans rien y modifier. Pour chaque numéro Pexels, retrouve le fichier original sur mon Mac : son chemin ou son nom de fichier d'appareil. Si Telepex ne garde pas ce lien, cherche dans mes dossiers de photos d'après la date de publication et le titre que Telepex donne pour ce numéro, et montre-moi les fichiers candidats avant de choisir.
2. COPIE chaque original dans le dossier (ne déplace rien, ne supprime rien, ne modifie aucun fichier d'origine), en le renommant comme indiqué. Garde chaque fichier intact : pas de recadrage, pas de compression, métadonnées EXIF conservées.
3. Ne télécharge rien depuis Pexels et n'envoie rien sur Internet.
4. À la fin, donne-moi un tableau : numéro Pexels, nom du fichier copié, chemin de l'original, taille en pixels, date de prise de vue (exiftool -DateTimeOriginal), coordonnées GPS s'il y en a. Si l'année de prise de vue diffère de celle du nom, dis-le-moi. Signale chaque photo introuvable, avec les pistes essayées.
"""


def feuille_suivi(classeur, toutes):
    f = classeur.active
    f.title = "Suivi"
    entetes = ["N° Pexels", "Photo", "Statut", "Wikipédia", "Article", "Partie", "Légende",
               "Fichier sur Commons", "Ajoutée le", "Lien de modification", "Remarques"]
    largeurs = [12, 42, 14, 11, 30, 18, 42, 46, 12, 22, 60]
    f.append(entetes)
    for l in toutes:
        f.append([int(l["photo"]) if l["photo"].isdigit() else "", l["sujet"], l["statut"],
                  LANGUES.get(l["wiki"], l["wiki"]), l["article"], l["partie"], l["legende"], l["fichier"],
                  l["date"], "Modifier la partie" if l["statut"] == "Prête" and l["section"] != "" else "",
                  l["remarques"]])
        n = f.max_row
        if l["photo"].isdigit():
            f.cell(n, 1).hyperlink = f"https://www.pexels.com/photo/{l['photo']}/"
        if l["article"] and l["wiki"]:
            f.cell(n, 5).hyperlink = lien_article(l["wiki"], l["article"])
        if l["fichier"] and l["statut"] in ("Dans l'article", "En attente", "Refusée"):
            f.cell(n, 8).hyperlink = lien_commons(l["fichier"])
        if f.cell(n, 10).value:
            f.cell(n, 10).hyperlink = lien_article(l["wiki"], l["article"], l["section"])
        fond = PatternFill("solid", fgColor=STATUTS.get(l["statut"], "FFFFFF"))
        for c in range(1, len(entetes) + 1):
            cellule = f.cell(n, c)
            cellule.fill = fond
            cellule.alignment = Alignment(vertical="top", wrap_text=True)
            cellule.font = Font(name=POLICE, size=10, color="0563C1" if cellule.hyperlink else "000000",
                                underline="single" if cellule.hyperlink else None)
    trait = Side(style="thin", color="BFBFBF")
    for c, largeur in enumerate(largeurs, 1):
        f.column_dimensions[get_column_letter(c)].width = largeur
        tete = f.cell(1, c)
        tete.font = Font(name=POLICE, size=10, bold=True, color="FFFFFF")
        tete.fill = PatternFill("solid", fgColor="404040")
        tete.alignment = Alignment(vertical="center", wrap_text=True)
        tete.border = Border(bottom=trait)
    f.freeze_panes = "C2"
    f.auto_filter.ref = f"A1:{get_column_letter(len(entetes))}{f.max_row}"
    f.page_setup.orientation = "landscape"
    f.page_setup.fitToWidth, f.page_setup.fitToHeight = 1, 0
    f.sheet_properties.pageSetUpPr.fitToPage = True
    f.print_title_rows = "1:1"


def feuille_bilan(classeur, nombre):
    f = classeur.create_sheet("Bilan")
    f.append(["Statut", "Photos", "Ce que cela veut dire"])
    sens = {
        "Prête": "Case préparée : la photo est à verser sur Commons, puis à ajouter à l'article.",
        "À vérifier": "Sujet identifié : la session vérifie l'article et prépare la case.",
        "À identifier": "Karl doit dire ce que montre la photo.",
        "En attente": "Pas de bonne place pour l'instant.",
        "Dans l'article": "En ligne sur Wikipédia, et dans le panneau du site photo.",
        "Refusée": "Retirée d'un article par un autre contributeur : ne jamais l'y remettre (raison dans Remarques).",
        "Écartée": "Jamais proposée : raison dans la colonne Remarques de l'onglet Suivi.",
    }
    for statut, texte in sens.items():
        f.append([statut, f'=COUNTIF(Suivi!$C$2:$C${nombre + 1},A{f.max_row + 1})', texte])
    f.append(["Total", f"=SUM(B2:B{f.max_row})", "Lignes de l'onglet Suivi (une par photo et par article)."])
    f.append([])
    f.append([f"Mis à jour le {date.today().strftime('%d/%m/%Y')} à partir de vitrine/wikipedia.csv et "
              "docs/wiki-suivi/pistes.csv (dépôt PexelsWillwonder)."])
    for ligne in f.iter_rows():
        for cellule in ligne:
            cellule.font = Font(name=POLICE, size=10, bold=cellule.row == 1 or cellule.value == "Total")
            cellule.alignment = Alignment(vertical="top", wrap_text=True)
            if cellule.column == 1 and cellule.value in STATUTS:
                cellule.fill = PatternFill("solid", fgColor=STATUTS[cellule.value])
    for c, largeur in zip("ABC", (16, 10, 80)):
        f.column_dimensions[c].width = largeur


def feuille_rassembler(classeur, pretes, texte):
    f = classeur.create_sheet("À rassembler")
    f.append(["N° Pexels", "Nom du fichier à donner", "Wikipédia", "Article"])
    for p in pretes:
        f.append([int(p["photo"]), p["fichier"], LANGUES.get(p["wiki"], p["wiki"]), p["article"]])
        f.cell(f.max_row, 1).hyperlink = f"https://www.pexels.com/photo/{p['photo']}/"
    f.append([])
    f.append(["Consigne à coller dans Claude, sur le Mac, quand toutes les photos de la liste sont prêtes :"])
    debut = f.max_row + 1
    f.append([texte])
    f.merge_cells(start_row=debut, start_column=1, end_row=debut, end_column=4)
    f.row_dimensions[debut].height = 15 * (texte.count("\n") + 12)
    for ligne in f.iter_rows():
        for cellule in ligne:
            cellule.font = Font(name=POLICE, size=10, bold=cellule.row == 1,
                                color="0563C1" if cellule.hyperlink else "000000")
            cellule.alignment = Alignment(vertical="top", wrap_text=True)
    for c, largeur in zip("ABCD", (12, 60, 12, 40)):
        f.column_dimensions[c].width = largeur


# ---------------------------------------------------------------------------------------
# Le PDF « Vos photos dans Wikipédia »

def e(texte):
    return html.escape(str(texte), quote=True)


def date_fr(texte):
    try:
        d = date.fromisoformat(texte)
    except ValueError:
        return texte
    return f"{'1er' if d.day == 1 else d.day} {MOIS[d.month - 1]} {d.year}"


def fiches_pexels():
    """Adresse de l'image et taille de chaque photo, d'après le cache des fiches Pexels."""
    chemin = RACINE / "vitrine" / "donnees" / "fiches.json"
    fiches = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
    images = {k: v["image"] for k, v in fiches.items() if v.get("image")}
    tailles = {k: (v.get("largeur") or 4, v.get("hauteur") or 3) for k, v in fiches.items()}
    return images, tailles


def vignette(l, images, hauteur):
    """Vignette de la photo, en data: pour un PDF qui se suffit à lui-même ("" si introuvable)."""
    if l["photo"].isdigit():
        n = l["photo"]
        base = images.get(n) or f"https://images.pexels.com/photos/{n}/pexels-photo-{n}.jpeg"
        adresse = base + f"?auto=compress&cs=tinysrgb&h={hauteur}"
    elif l["fichier"]:
        adresse = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
                   + quote(l["fichier"].replace(" ", "_")) + "?width=250")  # une taille courante de Commons
    else:
        return ""
    CACHE.mkdir(exist_ok=True)
    nom = CACHE / (hashlib.sha1(adresse.encode()).hexdigest()[:20] + ".jpg")
    if not nom.exists() or nom.stat().st_size == 0:
        essai = subprocess.run(["curl", "-sS", "-L", "--fail", "--max-time", "30", "-A", UA,
                                "-o", str(nom), adresse], capture_output=True)
        time.sleep(1)
        if essai.returncode != 0:
            nom.unlink(missing_ok=True)
            print(f"  pas de vignette pour {l['photo'] or l['fichier']}")
            return ""
    return "data:image/jpeg;base64," + base64.b64encode(nom.read_bytes()).decode()


def ligne_photo(p, tailles):
    largeur, hauteur = tailles.get(p["photo"], (4, 3))
    options = [VIGNETTES.get(p["wiki"], "thumb")] + (["upright"] if hauteur > largeur else [])
    return f"[[{PREFIXES.get(p['wiki'], 'File')}:{p['fichier']}|{'|'.join(options)}|{p['legende']}]]"


def ou(l):
    """« Wikipédia en français · Article · Partie », l'article en lien."""
    if not l["wiki"]:
        return ""
    morceaux = [f"Wikipédia en {e(LANGUES.get(l['wiki'], l['wiki']))}"]
    if l["article"]:
        morceaux.append(f'<a href="{e(lien_article(l["wiki"], l["article"]))}">{e(l["article"])}</a>')
    if l["partie"]:
        morceaux.append(e(l["partie"]))
    return " · ".join(morceaux)


def carte(l, images, tailles, classe=""):
    # Deux fois la taille affichée, plus pour les photos à identifier.
    image = vignette(l, images, {"grande": 320, "petite": 120}.get(classe, 180))
    image = f'<img src="{image}" alt="">' if image else '<div class="sans-image">pas d’aperçu</div>'
    corps = [f'<p class="sujet">{e(l["sujet"])}</p>']
    if ou(l):
        corps.append(f'<p class="ou">{ou(l)}</p>')
    if l["legende"] and l["statut"] != "Prête":
        corps.append(f'<p class="legende">« {e(l["legende"])} »</p>')
    if l["statut"] == "Prête":
        corps.append('<p class="etiquette">Ligne de la photo (la case entière est redonnée le jour même) :</p>'
                     f'<p class="code">{e(ligne_photo(l, tailles))}</p>')
        if l["section"] != "":
            corps.append(f'<p class="detail"><a href="{e(lien_article(l["wiki"], l["article"], l["section"]))}">'
                         "Lien de modification de la partie</a></p>")
    details = []
    if l["fichier"]:
        if l["statut"] in ("Dans l'article", "Refusée", "En attente"):
            details.append(f'Commons : <a href="{e(lien_commons(l["fichier"]))}">{e(l["fichier"])}</a>')
        else:
            details.append(f"Nom à donner sur Commons : {e(l['fichier'])}")
    if l["date"]:
        details.append(f"ajoutée le {e(date_fr(l['date']))}")
    if l["photo"].isdigit():
        details.append(f'<a href="https://www.pexels.com/photo/{e(l["photo"])}/">Pexels n° {e(l["photo"])}</a>')
    if details:
        corps.append(f'<p class="detail">{" · ".join(details)}</p>')
    if l["remarques"]:
        corps.append(f'<p class="remarque">{e(l["remarques"])}</p>')
    return f'<div class="carte {classe}"><div class="image">{image}</div><div class="texte">{"".join(corps)}</div></div>'


STYLE = """
@font-face { font-family: "Archivo"; src: url("__POLICE__") format("woff2"); font-weight: 100 900; }
@page { size: A4; margin: 15mm 14mm 16mm; }
:root { --encre: #1d1d1b; --doux: #64625c; --trait: #dedad2; --lien: #0b57a0;
        --vert: #2e6b34; --vert-fond: #e2efda; --rouge: #a3261f; --rouge-fond: #f4cccc;
        --ambre: #8a6100; --ambre-fond: #fff2cc; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Archivo", "Inter", "DejaVu Sans", sans-serif; font-size: 9.6pt;
       line-height: 1.38; color: var(--encre); background: #fff; }
a { color: var(--lien); text-decoration: none; }
p { margin: 0; }
h1 { font-size: 27pt; font-weight: 800; letter-spacing: -0.015em; line-height: 1.05; margin: 0 0 5pt; }
.chapeau { color: var(--doux); font-size: 11pt; margin-bottom: 16pt; }
.bilan { display: grid; grid-template-columns: repeat(3, 1fr); gap: 9pt; margin-bottom: 14pt; }
.bilan a { color: inherit; display: block; border-radius: 7pt; padding: 11pt 12pt 12pt; }
.bilan .nombre { font-size: 30pt; font-weight: 800; line-height: 1; }
.bilan .nom { font-size: 12.5pt; font-weight: 700; margin: 3pt 0 4pt; }
.bilan .sens { font-size: 8.8pt; }
.bilan .deposees { background: var(--vert-fond); }
.bilan .refusees { background: var(--rouge-fond); }
.bilan .demander { background: var(--ambre-fond); }
.commons { font-size: 9pt; color: var(--doux); margin-bottom: 4pt; }
h2 { font-size: 18pt; font-weight: 800; margin: 0 0 4pt; padding-bottom: 4pt; border-bottom: 2.2pt solid; }
h2.deposees { color: var(--vert); }
h2.refusees { color: var(--rouge); break-before: page; }
h2.demander { color: var(--ambre); break-before: page; }
.partie { margin-top: 18pt; }
.intro { color: var(--doux); margin: 4pt 0 6pt; }
h3 { font-size: 12pt; font-weight: 700; margin: 14pt 0 3pt; break-after: avoid; }
h3 .compte { color: var(--doux); font-weight: 500; }
h3 + .intro { margin-top: 0; }
.carte { display: flex; gap: 10pt; padding: 7pt 0; border-top: 0.6pt solid var(--trait); break-inside: avoid; }
.carte .image { flex: none; width: 82pt; }
.carte img, .sans-image { display: block; width: 82pt; height: 64pt; object-fit: contain;
                          background: #f1efea; border-radius: 3pt; }
.sans-image { color: var(--doux); font-size: 7.5pt; text-align: center; padding-top: 26pt; }
.carte.grande .image, .carte.grande img, .carte.grande .sans-image { width: 150pt; height: 112pt; }
.carte.petite .image, .carte.petite img, .carte.petite .sans-image { width: 56pt; height: 44pt; }
.carte.petite .sans-image { padding-top: 16pt; }
.texte { flex: 1; min-width: 0; }
.sujet { font-weight: 700; font-size: 10.3pt; }
.ou { margin-top: 1pt; }
.legende { font-style: italic; margin-top: 2pt; }
.detail { font-size: 8.3pt; color: var(--doux); margin-top: 2pt; overflow-wrap: anywhere; }
.remarque { font-size: 8.8pt; margin-top: 3pt; padding: 3pt 6pt; border-left: 2pt solid var(--trait); }
.refusee .remarque { border-left-color: var(--rouge); background: #fbeeee; }
.etiquette { font-size: 8.3pt; color: var(--doux); margin-top: 3pt; }
.code { font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace; font-size: 7.8pt; background: #f3f1ec;
        padding: 3pt 5pt; margin-top: 1pt; border-radius: 3pt; overflow-wrap: anywhere; }
.ecartees { display: grid; grid-template-columns: 1fr 1fr; column-gap: 12pt; }
.consigne { break-inside: avoid; margin-top: 16pt; padding: 10pt 12pt; background: #f6f4ef; border-radius: 6pt; }
.consigne h3 { margin-top: 0; }
.consigne pre { white-space: pre-wrap; font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace;
                font-size: 7.6pt; line-height: 1.4; margin: 6pt 0 0; }
.pied { margin-top: 18pt; padding-top: 6pt; border-top: 0.6pt solid var(--trait); font-size: 8pt; color: var(--doux); }
"""

INTRO_DEMANDER = {
    "Prête": ("Prêtes à verser", "À faire par Karl : rassembler les originaux (consigne en fin de document), "
              "les verser sur Commons sous le nom indiqué, avec le modèle {{Permission pending}}, et ajouter ces "
              "noms au courriel d’autorisation ; puis demander à une session la case à coller, relue le jour même."),
    "À vérifier": ("À vérifier", "À faire par la session : lire l’article visé et trouver la partie dont le texte "
                   "parle de ce que montre la photo, sans doublon ni galerie pleine."),
    "À identifier": ("À identifier", "À faire par Karl : dire ce que montre la photo (commune, nom exact de "
                     "l’édifice)."),
    "En attente": ("En attente", "Rien à faire pour l’instant : pas de bonne place libre."),
}


def page(toutes, texte_consigne, verifie=""):
    images, tailles = fiches_pexels()
    par = {s: [l for l in toutes if l["statut"] == s] for s in STATUTS}
    deposees, refusees, ecartees = par["Dans l'article"], par["Refusée"], par["Écartée"]
    a_demander = [l for s in INTRO_DEMANDER for l in par[s]]
    articles = {(l["wiki"], l["article"]) for l in deposees}
    wikis = {l["wiki"] for l in deposees}
    sur_commons = {l["fichier"] for l in deposees} | {
        l["fichier"] for l in toutes if l["statut"] in ("Refusée", "En attente") and l["fichier"]}
    aujourd_hui = date_fr(date.today().isoformat())
    controle = f" ; toutes relues dans leur article le {e(date_fr(verifie))}" if verifie else ""

    def compte(n, un, plusieurs):
        return f"{n} {un if n == 1 else plusieurs}"

    morceaux = [f"""<h1>Vos photos dans Wikipédia</h1>
<p class="chapeau">Déposées, refusées, à demander · point au {aujourd_hui}</p>
<div class="bilan">
  <a class="deposees" href="#deposees"><div class="nombre">{len(deposees)}</div><div class="nom">Déposées</div>
    <div class="sens">Dans un article : {compte(len(articles), "article", "articles")},
    {compte(len(wikis), "Wikipédia", "Wikipédias")}. Aussi dans le panneau « Mes photos dans Wikipédia » du site photo.</div></a>
  <a class="refusees" href="#refusees"><div class="nombre">{len(refusees) + len(ecartees)}</div><div class="nom">Refusées</div>
    <div class="sens">{compte(len(refusees), "retirée", "retirées")} d’un article par un autre contributeur,
    {compte(len(ecartees), "écartée", "écartées")} d’avance (droits, doublons, personnes reconnaissables).</div></a>
  <a class="demander" href="#demander"><div class="nombre">{len(a_demander)}</div><div class="nom">À demander</div>
    <div class="sens">{len(par["Prête"])} prêtes à verser, {len(par["À vérifier"])} à vérifier,
    {len(par["À identifier"])} à identifier, {len(par["En attente"])} en attente.</div></a>
</div>
<p class="commons">{compte(len(sur_commons), "fichier versé", "fichiers versés")} sur Wikimedia Commons sous le compte
« Karl Forterre ». Mode d’emploi complet : docs/wiki-route.md (dépôt PexelsWillwonder).</p>"""]

    morceaux.append(f"""<section class="partie" id="deposees"><h2 class="deposees">Déposées</h2>
<p class="intro">En ligne dans un article, de la plus récente à la plus ancienne{controle}. Chacune est aussi dans le
panneau « Mes photos dans Wikipédia » du site photo, et la page de la photo cite l’article.</p>
{"".join(carte(l, images, tailles) for l in deposees)}</section>""")

    morceaux.append(f"""<section class="partie" id="refusees"><h2 class="refusees">Refusées</h2>
<h3>Retirées par Wikipédia <span class="compte">({len(refusees)})</span></h3>
<p class="intro">Une photo retirée par un autre contributeur ne se remet jamais dans le même article : ce serait
une guerre d’édition. On lit sa raison et on en tient compte pour les suivantes.</p>
{"".join(carte(l, images, tailles, "refusee") for l in refusees)}
<h3>Écartées d’avance <span class="compte">({len(ecartees)})</span></h3>
<p class="intro">Jamais proposées, pour la raison indiquée : droits (en France, pas de liberté de panorama pour les
œuvres et les bâtiments récents), doublons, personnes reconnaissables, image trop retouchée.</p>
<div class="ecartees">{"".join(carte(l, images, tailles, "petite") for l in ecartees)}</div></section>""")

    demander = ['<section class="partie" id="demander"><h2 class="demander">À demander</h2>'
                '<p class="intro">Les prochaines photos, et ce qu’il faut faire pour chacune.</p>']
    for statut, (titre, intro) in INTRO_DEMANDER.items():
        if not par[statut]:
            continue
        demander.append(f'<h3>{e(titre)} <span class="compte">({len(par[statut])})</span></h3>'
                        f'<p class="intro">{e(intro)}</p>')
        classe = "grande" if statut == "À identifier" else ""
        demander.extend(carte(l, images, tailles, classe) for l in par[statut])
    if par["Prête"]:
        demander.append('<div class="consigne"><h3>Consigne de rassemblement</h3>'
                        '<p class="intro">À coller dans Claude, sur le Mac, pour réunir les originaux des photos '
                        'prêtes (aussi dans consigne-rassemblement.txt et l’onglet « À rassembler » du '
                        f'tableau).</p><pre>{e(texte_consigne)}</pre></div>')
    demander.append("</section>")
    morceaux.append("".join(demander))
    morceaux.append(f"""<p class="pied">Écrit le {aujourd_hui} par docs/wiki-suivi/fabriquer.py, d’après
vitrine/wikipedia.csv et docs/wiki-suivi/pistes.csv (dépôt PexelsWillwonder). Vignettes : photos de Karl Forterre,
<a href="https://www.pexels.com">Photos provided by Pexels</a> ; la vue de face de l’hôtel de ville de Niort vient de
Wikimedia Commons.</p>""")
    corps = "".join(morceaux)
    # Espaces insécables de la typographie française, pour qu'aucune ligne ne commence par « : » ou « ».
    for avant, apres in (("« ", "«\u00a0"), (" »", "\u00a0»"), (" :", "\u00a0:"), (" ;", "\u202f;"),
                         ("n° ", "n°\u00a0")):
        corps = corps.replace(avant, apres)
    police = (RACINE / "vitrine" / "statique" / "archivo.woff2").as_uri()
    return ('<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Vos photos dans Wikipédia</title>'
            f'<style>{STYLE.replace("__POLICE__", police)}</style></head><body>{corps}</body></html>')


def chromium():
    if os.environ.get("CHROMIUM"):
        return os.environ["CHROMIUM"]
    for nom in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if shutil.which(nom):
            return shutil.which(nom)
    for motif in ("/opt/pw-browsers/chromium-*/chrome-linux64/chrome",
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium"):
        trouves = sorted(glob.glob(motif))
        if trouves:
            return trouves[-1]
    return None


def ecrire_pdf(contenu, sortie):
    navigateur = chromium()
    if not navigateur:
        print("Chromium introuvable (variable CHROMIUM) : PDF non écrit.")
        return False
    with tempfile.TemporaryDirectory() as dossier:
        source = Path(dossier) / "suivi.html"
        source.write_text(contenu, encoding="utf-8")
        subprocess.run([navigateur, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={sortie}", source.as_uri()],
                       check=True, capture_output=True, timeout=180)
    return True


def main():
    toutes = lignes()
    pretes = [l for l in toutes if l["statut"] == "Prête"]
    texte = consigne(pretes)
    classeur = Workbook()
    feuille_suivi(classeur, toutes)
    feuille_bilan(classeur, len(toutes))
    feuille_rassembler(classeur, pretes, texte)
    classeur.calculation.fullCalcOnLoad = True
    classeur.save(ICI / "suivi-wikipedia.xlsx")
    (ICI / "consigne-rassemblement.txt").write_text(texte, encoding="utf-8")
    verifie = sys.argv[sys.argv.index("--verifie-le") + 1] if "--verifie-le" in sys.argv else ""
    pdf = ecrire_pdf(page(toutes, texte, verifie), ICI / "vos-photos-dans-wikipedia.pdf")
    print(f"{len(toutes)} lignes, dont {len(pretes)} photos prêtes : suivi-wikipedia.xlsx, "
          f"consigne-rassemblement.txt{' et vos-photos-dans-wikipedia.pdf' if pdf else ''} écrits.")


if __name__ == "__main__":
    main()
