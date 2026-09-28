"""Studio vidéo : les carrousels en vidéos rythmées, prêtes pour les réseaux sociaux.

    python3 reseaux/videos/studio.py preparer [filtre]      photos (4000 px), musiques, polices, analyses
    python3 reseaux/videos/studio.py planche [filtre]       planche et chronogramme, sans fabriquer la vidéo
    python3 reseaux/videos/studio.py videos [filtre] [options]
    python3 reseaux/videos/studio.py qualite [filtre]       contrôle qualité des vidéos déjà faites
    python3 reseaux/videos/studio.py couvertures [filtre]   couvertures 3:4 et 9:16

Options de « videos » : --formats=9x16,3x4 (par défaut ; 1x1 possible), --apercu (rapide,
une image sur trois, pour vérifier le montage), --hq (version haute qualité, en plus).
Le filtre retient les vidéos dont le nom « carrousel-langue » le contient : 04-roadtrip,
fr, 05-bordeaux-zh… Tout se passe dans reseaux/videos/travail/ (ignoré par git) ; les
vidéos sont dans travail/sortie/Studio/, rangées par langue. Textes, photos et musiques :
donnees.py. Mode d'emploi : README.md. L'ancien programme (fabrique.py) reste intact.
"""
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
TRAVAIL = os.path.join(ICI, "travail")
os.makedirs(TRAVAIL, exist_ok=True)
os.chdir(TRAVAIL)

import montage as V  # noqa: E402
import qualite as Q  # noqa: E402
import rythme as Ry  # noqa: E402
from diaporama import police_google  # noqa: E402
from donnees import CARROUSELS, DOSSIERS, FIN, MUSIQUES  # noqa: E402

LANGUES = ("zh", "fr", "en")
SUFFIXE = {"zh": "chinois", "fr": "français", "en": "anglais"}
SORTIE = "sortie/Studio/"
LOGO = os.path.join(ICI, "..", "..", "vitrine", "statique", "logo.svg")
POIDS_MAX = 29.5e6  # octets : 30 Mo au plus par fichier envoyé


def choisis(filtre, formats=("9x16",)):
    return [(c, l, f) for c in CARROUSELS for l in LANGUES for f in formats
            if not filtre or filtre in f"{c['cle']}-{l}"]


def chemin_photo(c, n):
    return f"photos-4000/{c['cle']}/{n:02d}-{c['photos'][n]}.jpg"


def musique(c, langue):
    return c["musique_fr"] if langue == "fr" else c["musique"]


def textes(c, langue):
    """Textes de l'accroche et de la fin, dans la langue de la vidéo."""
    d = c[langue]
    if langue == "zh":
        surtitre, promesse, tags = d["accroche"]
    else:
        surtitre, titre, tags, _ = d["couverture"]
        promesse = d.get("promesse", titre.replace("\n", " "))
        promesse = V.typographie(promesse, langue)
        surtitre = V.typographie(surtitre, langue)
    credit_exige = "CC BY" in MUSIQUES[os.path.basename(musique(c, langue))]["credit"]
    titre_couverture = promesse if langue == "zh" else V.typographie(d["couverture"][1], langue)
    bas = "" if langue == "zh" else d["couverture"][3]
    return {"surtitre": surtitre, "promesse": promesse, "tags": tags, "fin": FIN[langue],
            "credit": c.get(f"credit_{langue}"), "credit_exige": credit_exige,
            "titre_couverture": titre_couverture, "bas": bas}


def nom(c, langue):
    return f"{c['fichier']} ({SUFFIXE[langue]})"


def dossier_sortie(langue, fmt):
    d = SORTIE + DOSSIERS[langue] + ("/" if fmt == "9x16" else f"/{fmt}/")
    os.makedirs(d, exist_ok=True)
    return d


# --- Préparation --------------------------------------------------------------------------

def telecharger(url, chemin, essais=6):
    """Téléchargement sûr : fichier provisoire, renommé seulement s'il est complet."""
    if os.path.exists(chemin) and os.path.getsize(chemin) > 0:
        return
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    for k in range(essais):
        r = subprocess.run(["curl", "-sSLf", "--retry", "3", "-o", chemin + ".part", url])
        if r.returncode == 0:
            os.replace(chemin + ".part", chemin)
            return
        if os.path.exists(chemin + ".part"):
            os.remove(chemin + ".part")
        time.sleep(2 ** (k + 1))
    raise RuntimeError(f"téléchargement impossible : {url}")


def caracteres_chinois():
    car = set("0123456789·、，。：；！？（）「」“”《》… ©%")
    for c in CARROUSELS:
        z = c["zh"]
        car |= set("".join(z["accroche"]))
        for _, lignes in z["plans"]:
            car |= set("".join(lignes or []))
        titre, entrees = z["lecon"]
        car |= set(titre + "".join(m + "".join(e) for m, e in entrees))
    car |= set("".join(FIN["zh"]))
    car |= set("Karl Forterre Pexels 张 · 可在 Pexels 免费下载")  # dernière ligne des couvertures
    return "".join(sorted(x for x in car if x.strip() or x == " "))


def polices():
    """Archivo (400, 600, 700) et Noto Sans SC (400, 500, 700) réduite aux caractères utiles."""
    os.makedirs(V.POLICES, exist_ok=True)
    for g in (400, 600, 700):
        f = os.path.join(V.POLICES, f"archivo-{g}.ttf")
        if not os.path.exists(f):
            police_google("Archivo", g, f)
    texte = caracteres_chinois()
    for g in (400, 500, 700):
        police_google("Noto+Sans+SC", g, os.path.join(V.POLICES, f"noto-{g}.ttf"), texte)
    manque = V.caracteres_absents(texte, "zh")
    print("police chinoise :", len(texte), "caractères", f"(manquants : {''.join(manque)})" if manque else "")


def preparer(filtre=None):
    carrousels = {c["cle"]: c for c, _, _ in choisis(filtre)}.values()
    for c in carrousels:
        for n, numero in c["photos"].items():
            url = f"https://images.pexels.com/photos/{numero}/pexels-photo-{numero}.jpeg?auto=compress&cs=tinysrgb&w=4000"
            telecharger(url, chemin_photo(c, n))
            V.saillance(chemin_photo(c, n))
        for cle in ("musique", "musique_fr"):
            telecharger(MUSIQUES[os.path.basename(c[cle])]["url"], c[cle])
            Ry.charger(c[cle])
    polices()
    print("préparation faite")


# --- Vidéos -------------------------------------------------------------------------------

def monter(c, langue, fmt):
    analyse = Ry.charger(musique(c, langue))
    style = MUSIQUES[os.path.basename(musique(c, langue))].get("style")
    rythme = Ry.Rythme(analyse, style)
    sujets = {n: V.saillance(chemin_photo(c, n)) for n in c["photos"]}
    t = textes(c, langue)
    M = V.construire(c, langue, fmt, rythme, rythme.style, lambda n: chemin_photo(c, n), sujets, t)
    R = V.Rendu(M, lambda n: chemin_photo(c, n), sujets, t, LOGO)
    return M, R, t, analyse


def video(travail):
    """Une vidéo : montage, images, son, assemblage, sous-titres, fiche et contrôle qualité."""
    c, langue, fmt, apercu, hq = travail
    debut_calcul = time.time()
    M, R, t, analyse = monter(c, langue, fmt)
    V.mesurer(R)
    cle = f"{c['cle']}-{langue}-{fmt}"
    atelier = f"studio/{cle}/"
    os.makedirs(atelier, exist_ok=True)
    muette, wav = atelier + "muette.mp4", atelier + "son.wav"
    debit = int(min(8000 if fmt == "9x16" else 6500, (POIDS_MAX * 8 / M.duree - 200e3) / 1000))
    if apercu:
        V.rendre(R, muette, debit_k=debit, crf=23, pas=3, preset="veryfast")
    else:
        V.rendre(R, muette, debit_k=debit, crf=19)
    V.son(musique(c, langue), analyse["debut"], M.duree, M.bouton, wav)
    dossier = dossier_sortie(langue, fmt) if not apercu else atelier
    sortie = dossier + nom(c, langue) + (" (aperçu)" if apercu else "") + ".mp4"
    V.assembler(muette, wav, sortie)
    if hq and not apercu:
        haute = atelier + "haute-qualite.mp4"
        V.rendre(R, atelier + "muette-hq.mp4", debit_k=25000, crf=16)
        V.assembler(atelier + "muette-hq.mp4", wav, haute)
    V.srt(M, t, dossier + nom(c, langue) + ".srt")
    donnees = V.fiche(M, R, t, atelier + "fiche.json")
    V.chronogramme(M, atelier + "chronogramme.png")
    rapport = Q.verifier(donnees, sortie, poids_max=POIDS_MAX, apercu=apercu)
    with open(atelier + "qualite.txt", "w", encoding="utf-8") as f:
        f.write(rapport.texte(f"{nom(c, langue)} — {fmt}"))
    if not rapport.reussi and not apercu:
        refus = SORTIE + "Refusées/"
        os.makedirs(refus, exist_ok=True)
        os.replace(sortie, refus + os.path.basename(sortie))
    etat = "réussi" if rapport.reussi else "ÉCHEC (vidéo non livrée, voir " + atelier + "qualite.txt)"
    taille = os.path.getsize(sortie if rapport.reussi or apercu else refus + os.path.basename(sortie)) / 1e6
    return (f"{cle} : {M.duree:.1f} s, {len(M.plans)} plans, {taille:.1f} Mo, style {M.style}, "
            f"contrôle qualité {etat} ({time.time() - debut_calcul:.0f} s de calcul)")


def videos(filtre=None, formats=("9x16", "3x4"), apercu=False, hq=False):
    travaux = [(c, l, f, apercu, hq) for c, l, f in choisis(filtre, formats)]
    with Pool(min(4, os.cpu_count() or 1)) as p:
        for ligne in p.imap_unordered(video, travaux):
            print(ligne, flush=True)
    licences()


def licences():
    """Fichier « Musiques et licences » de chaque langue (crédits, licences)."""
    for langue in LANGUES:
        cle = "musique_fr" if langue == "fr" else "musique"
        d = dossier_sortie(langue, "9x16")
        with open(d + f"Musiques et licences ({SUFFIXE[langue]}).txt", "w") as f:
            f.write("Musiques des vidéos : libres de droits, utilisables même commercialement.\n\n")
            for c in CARROUSELS:
                f.write(f"{c['fichier']} :\n{MUSIQUES[os.path.basename(c[cle])]['credit']}\n\n")


def qualite(filtre=None, formats=("9x16", "3x4")):
    for c, langue, fmt in choisis(filtre, formats):
        atelier = f"studio/{c['cle']}-{langue}-{fmt}/"
        sortie = dossier_sortie(langue, fmt) + nom(c, langue) + ".mp4"
        if not os.path.exists(atelier + "fiche.json") or not os.path.exists(sortie):
            continue
        with open(atelier + "fiche.json") as f:
            rapport = Q.verifier(json.load(f), sortie, poids_max=POIDS_MAX)
        print(rapport.texte(f"{nom(c, langue)} — {fmt}"))


def couvertures(filtre=None):
    """Couvertures à part (règle A4) : 3:4 pour RedNote et la grille, 9:16 pour les Reels."""
    for c, langue, _ in choisis(filtre):
        for fmt in ("3x4", "9x16"):
            n = c.get("couverture_photo", 1)  # la photo de couverture du carrousel
            chemin = dossier_sortie(langue, "9x16") + f"{nom(c, langue)} couverture {fmt}.jpg"
            V.couverture(chemin_photo(c, n), V.saillance(chemin_photo(c, n)), textes(c, langue), langue, fmt,
                         nb_photos(c), chemin)
            print(chemin)


def nb_photos(c):
    return len({1} | {n for n, _ in c["zh"]["plans"]})


def planche(filtre):
    """Planche de contrôle et chronogramme d'une vidéo, sans la fabriquer."""
    for c, langue, fmt in choisis(filtre, ("9x16",)):
        M, R, t, _ = monter(c, langue, fmt)
        atelier = f"studio/{c['cle']}-{langue}-{fmt}/"
        os.makedirs(atelier, exist_ok=True)
        V.planche(R, atelier + "planche.jpg")
        V.chronogramme(M, atelier + "chronogramme.png")
        print(os.path.join(TRAVAIL, atelier + "planche.jpg"))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    options = [a for a in sys.argv[1:] if a.startswith("--")]
    commande = args[0] if args else ""
    filtre = args[1] if len(args) > 1 else None
    formats = ("9x16", "3x4")
    for o in options:
        if o.startswith("--formats="):
            formats = tuple(o.split("=", 1)[1].split(","))
    actions = {
        "preparer": lambda: preparer(filtre),
        "videos": lambda: videos(filtre, formats, "--apercu" in options, "--hq" in options),
        "qualite": lambda: qualite(filtre, formats),
        "couvertures": lambda: couvertures(filtre),
        "planche": lambda: planche(filtre),
    }
    if commande not in actions:
        sys.exit(__doc__)
    actions[commande]()
