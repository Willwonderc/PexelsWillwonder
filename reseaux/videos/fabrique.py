"""Vidéos diaporama des carrousels RedNote, en chinois, français et anglais.

    python3 reseaux/videos/fabrique.py preparer [filtre]   photos, musiques et polices
    python3 reseaux/videos/fabrique.py cartes [filtre]     couvertures, fins, petits cours
    python3 reseaux/videos/fabrique.py videos [filtre]     vidéos, musique comprise
    python3 reseaux/videos/fabrique.py musique [filtre]    change la musique sans recalculer l'image
    python3 reseaux/videos/fabrique.py apercu <carrousel>  planche de contrôle, un plan par image

Le filtre retient les vidéos dont le nom « carrousel-langue » le contient : 04-roadtrip,
fr, 05-bordeaux-zh… Tout se passe dans reseaux/videos/travail/ (ignoré par git) ; les
vidéos finies sont dans travail/sortie/Caroussels/, rangées par langue. Textes, photos
et musiques : donnees.py. Mode d'emploi : README.md.
"""
import os
import re
import subprocess
import sys
from multiprocessing import Pool

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
TRAVAIL = os.path.join(ICI, "travail")
os.makedirs(TRAVAIL, exist_ok=True)
os.chdir(TRAVAIL)

import diaporama as D  # noqa: E402
from donnees import CARROUSELS, DOSSIERS, FIN, MUSIQUES  # noqa: E402

W, H = 1080, 1440
OR = (232, 196, 120)
FF = imageio_ffmpeg.get_ffmpeg_exe()
SORTIE = "sortie/Caroussels/"
SUFFIXE = {"zh": "chinois", "fr": "français", "en": "anglais"}
PONCT = "，。：、）」”！？；"
LANGUES = ("zh", "fr", "en")


def choisis(filtre, langues=LANGUES):
    return [(c, l) for c in CARROUSELS for l in langues if not filtre or filtre in f"{c['cle']}-{l}"]


def photo(c, n):
    return f"photos/{c['cle']}/{n:02d}-{c['photos'][n]}.jpg"


def latin(taille):
    return ImageFont.truetype(D.LATIN, taille)


# --- Préparation : photos, musiques, polices -------------------------------------------

def telecharger(url, chemin):
    if os.path.exists(chemin) and os.path.getsize(chemin) > 0:
        return False
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    subprocess.run(["curl", "-sSLf", "--retry", "3", "-o", chemin, url], check=True)
    return True


def polices():
    """Noto Sans SC réduite aux caractères chinois des vidéos (Google Fonts, paramètre text)."""
    os.makedirs("polices", exist_ok=True)
    car = set("法语小课堂© Karl Forterre0123456789")
    for c in CARROUSELS:
        for _, lignes in c["zh"]["plans"]:
            car |= set("".join(lignes or []))
        if "lecon" in c["zh"]:
            titre, entrees = c["zh"]["lecon"]
            car |= set(titre + "".join(m + "".join(e) for m, e in entrees))
    D.police_google("Noto+Sans+SC", 400, "polices/sous-titre.ttf", "".join(car))
    D.police_google("Noto+Sans+SC", 300, "polices/legende.ttf", "© Karl Forterre0123456789")
    if not os.path.exists(D.LATIN_SYSTEME):  # Arimo : le dessin de Liberation Sans
        D.police_google("Arimo", 400, "polices/latin.ttf")
    f = ImageFont.truetype("polices/sous-titre.ttf", 40)
    manque = [x for x in car if x.strip() and f.getmask(x).getbbox() is None]
    print("police chinoise :", len(car), "caractères", "(manquants : %s)" % "".join(manque) if manque else "")


def preparer(filtre=None):
    carrousels = {c["cle"]: c for c, _ in choisis(filtre)}.values()
    for c in carrousels:
        for n, numero in c["photos"].items():
            url = f"https://images.pexels.com/photos/{numero}/pexels-photo-{numero}.jpeg?auto=compress&cs=tinysrgb&w=2600"
            telecharger(url, photo(c, n))
        for cle in ("musique", "musique_fr"):
            telecharger(MUSIQUES[os.path.basename(c[cle])]["url"], c[cle])
    polices()
    manquent = [c["zh"][k] for c in carrousels for k in ("couverture", "fin") if not os.path.exists(c["zh"][k])]
    if manquent:
        print("À déposer dans travail/carrousels/ (images de la page des carrousels RedNote, voir README.md) :")
        for m in manquent:
            print("  ", os.path.basename(m))
    print("préparation faite")


# --- Cartes : couvertures et fins (français, anglais), petits cours (chinois, anglais) --

def couper_zh(texte, f, largeur):
    lignes, courante = [], ""
    for x in texte:
        if courante and f.getlength(courante + x) > largeur and x not in PONCT:
            lignes.append(courante)
            courante = x
        else:
            courante += x
    return lignes + [courante] if courante else lignes


def espace(d, pos, texte, f, fill, pas, centre=False):
    """Texte à lettres espacées, aligné à gauche ou centré sur pos."""
    largeur = sum(f.getlength(x) for x in texte) + pas * (len(texte) - 1)
    x, y = pos
    if centre:
        x -= largeur / 2
    for car in texte:
        d.text((x, y), car, font=f, fill=fill, anchor="ls")
        x += f.getlength(car) + pas


def fond_flou(chemin, assombrir):
    im = Image.open(chemin).convert("RGB")
    fond = im.resize((W // 4, H // 4), Image.BILINEAR, box=D.cadre_rempli(im, W, H))
    fond = fond.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)
    return Image.blend(fond, Image.new("RGB", (W, H), (16, 16, 18)), assombrir)


def signature(d):
    d.text((W - 70, H - 58), "© Karl Forterre", font=D.police("legende", 23), fill=(255, 255, 255, 170), anchor="rs")


def lecon(chemin_fond, titre, entrees, langue, sortie):
    im = fond_flou(chemin_fond, 0.66)
    d = ImageDraw.Draw(im)
    fe = D.police("sous-titre", 34) if langue == "zh" else latin(34)
    y = H * 0.24
    d.line([(W / 2 - 34, y), (W / 2 + 34, y)], fill=OR, width=5)
    if langue == "zh":
        d.text((W / 2, y + 62), titre, font=D.police("sous-titre", 44), fill=OR, anchor="ms")
    else:
        espace(d, (W / 2, y + 62), titre, latin(42), OR, 3, centre=True)
    y += 62 + H * 0.12
    for mot, expl in entrees:
        d.text((W / 2, y), mot, font=latin(72), fill=(250, 250, 250), anchor="ms")
        if isinstance(expl, list):
            lignes = expl
        else:
            lignes = couper_zh(expl, fe, W * 0.8) if langue == "zh" else D.couper(expl, fe, W * 0.8)
        for i, ligne in enumerate(lignes):
            d.text((W / 2, y + 62 + i * 48), ligne, font=fe, fill=(215, 215, 215), anchor="ms")
        y += (H * 0.17 if len(entrees) <= 2 else H * 0.14) + (len(lignes) - 1) * 48
    signature(d)
    im.save(sortie, quality=95)


def couverture(chemin, sous, titre, tags, bas, sortie):
    """Couverture française ou anglaise, dans le style des carrousels."""
    im = Image.open(chemin).convert("RGB").resize((W, H), Image.LANCZOS, box=D.cadre_rempli(Image.open(chemin), W, H))
    voile = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(voile)
    for y in range(H):
        a = int(235 * ((y - H * 0.38) / (H * 0.62)) ** 1.3) if y > H * 0.38 else 0
        if y < H * 0.14:
            a = max(a, int(110 * (1 - y / (H * 0.14))))
        dv.line([(0, y), (W, y)], fill=(8, 8, 10, a))
    im = Image.alpha_composite(im.convert("RGBA"), voile)
    d = ImageDraw.Draw(im)
    espace(d, (60, 95), "KF’  KARL FORTERRE", latin(25), (255, 255, 255, 235), 2)
    y_bas = H - 95
    d.text((60, y_bas), bas, font=latin(30), fill=(235, 235, 235), anchor="ls")
    taille = 34
    while latin(taille).getlength(tags) > W - 120:
        taille -= 1
    y_tags = y_bas - 120
    d.text((60, y_tags), tags, font=latin(taille), fill=OR, anchor="ls")
    ft = latin(84)
    lignes = titre.split("\n") if "\n" in titre else D.couper(titre, ft, W * 0.80)
    y = y_tags - 80
    for ligne in reversed(lignes):
        d.text((60, y), ligne, font=ft, fill=(255, 255, 255), anchor="ls")
        y -= 102
    y_sous = y + 102 - 64 - 36
    d.text((60, y_sous), sous, font=latin(32), fill=(235, 235, 235), anchor="ls")
    d.line([(60, y_sous - 62), (126, y_sous - 62)], fill=OR, width=5)
    im.convert("RGB").save(sortie, quality=95)


def fin(chemin_fond, lignes, sortie, credit=None):
    im = fond_flou(chemin_fond, 0.74)
    d = ImageDraw.Draw(im)
    d.text((W / 2, H * 0.29), "KF’", font=latin(150), fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, H * 0.385), "Karl Forterre", font=latin(56), fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, H * 0.437), lignes[0], font=latin(33), fill=(215, 215, 215), anchor="mm")
    d.line([(W / 2 - 36, H * 0.5), (W / 2 + 36, H * 0.5)], fill=OR, width=5)
    d.text((W / 2, H * 0.565), lignes[1], font=latin(36), fill=(255, 255, 255), anchor="mm")
    d.text((W / 2, H * 0.63), lignes[2], font=latin(38), fill=(215, 215, 215), anchor="mm")
    d.text((W / 2, H * 0.678), "Karl Forterre", font=latin(56), fill=OR, anchor="mm")
    d.text((W / 2, H * 0.815), lignes[3], font=latin(32), fill=(190, 190, 190), anchor="mm")
    if credit:  # crédit de la musique, exigé par sa licence
        fc = latin(22)
        for i, ligne in enumerate(D.couper(credit, fc, W * 0.84)):
            d.text((W / 2, H * 0.9 + i * 30), ligne, font=fc, fill=(170, 170, 170), anchor="mm")
    im.save(sortie, quality=95)


def cartes(filtre=None):
    os.makedirs("cartes", exist_ok=True)
    for c in {c["cle"]: c for c, _ in choisis(filtre)}.values():
        k = c["cle"]
        for langue in ("en", "fr"):
            couverture(photo(c, 1), *c[langue]["couverture"], f"cartes/{k}-couverture-{langue}.jpg")
            fin(photo(c, 1), FIN[langue], f"cartes/{k}-fin-{langue}.jpg", c.get(f"credit_{langue}"))
        fond = photo(c, c.get("fond_lecon", max(c["photos"])))
        for langue in ("zh", "en"):
            if "lecon" in c[langue]:
                lecon(fond, *c[langue]["lecon"], langue, f"cartes/{k}-lecon-{langue}.jpg")
    print("cartes prêtes")


# --- Vidéos -----------------------------------------------------------------------------

def duree_plan(texte, langue):
    if texte is None:
        return 3.6
    if langue == "zh":
        return max(4.4, 1.8 + len("".join(texte)) / 9)
    return max(4.4, 1.7 + len(texte) / 16)


def plans(c, langue):
    d, k = c[langue], c["cle"]
    couv = f"cartes/{k}-couverture-{langue}.jpg" if langue != "zh" else d["couverture"]
    image_fin = f"cartes/{k}-fin-{langue}.jpg" if langue != "zh" else d["fin"]
    liste = [D.Plan(W, H, couv, 3.2, diapo=True)]
    for n, texte in d["plans"]:
        liste.append(D.Plan(W, H, photo(c, n), duree_plan(texte, langue), lignes=texte, langue=langue))
    if "lecon" in d:
        liste.append(D.Plan(W, H, f"cartes/{k}-lecon-{langue}.jpg", 5.5, diapo=True))
    liste.append(D.Plan(W, H, image_fin, 4.2, diapo=True))
    return liste


def debut_musique(f):
    """Saute le silence du début de l'enregistrement."""
    r = subprocess.run([FF, "-hide_banner", "-t", "20", "-i", f, "-af", "silencedetect=noise=-50dB:d=0.3",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"silence_start: (-?[\d.]+).*?silence_end: ([\d.]+)", r, re.S)
    return float(m.group(2)) if m and float(m.group(1)) <= 0.05 else 0.0


def duree_video(f):
    r = subprocess.run([FF, "-hide_banner", "-i", f], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def video(travail):
    """Image puis son ; `refaire` faux : garde l'image déjà calculée et change la musique."""
    c, langue, refaire = travail
    muet = f"rendu/{c['cle']}-{langue}-muet.mp4"
    if refaire or not os.path.exists(muet):
        duree = D.fabriquer(plans(c, langue), muet, W, H, crf=21, debit_max="4M")
    else:
        duree = duree_video(muet)
    dossier = SORTIE + DOSSIERS[langue] + "/"
    os.makedirs(dossier, exist_ok=True)
    sortie = dossier + f"{c['fichier']} ({SUFFIXE[langue]}).mp4"
    musique = c["musique_fr"] if langue == "fr" else c["musique"]
    debut = debut_musique(musique)
    filtre = (f"loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,afade=t=in:st=0:d=0.8,"
              f"afade=t=out:st={duree - 3.5:.2f}:d=3.5")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", muet, "-ss", f"{debut:.2f}", "-i", musique,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", filtre, "-c:a", "aac", "-b:a", "160k",
                    "-t", f"{duree:.2f}", "-movflags", "+faststart", sortie], check=True)
    taille = os.path.getsize(sortie) / 1e6
    alerte = "  ATTENTION : plus de 30 Mo, trop lourd pour l'envoi" if taille > 30 * 1.048576 else ""
    return f"{DOSSIERS[langue]}/{c['fichier']}.mp4 : {duree:.1f} s, {taille:.1f} Mo, musique dès {debut:.1f} s{alerte}"


def licences():
    for langue in LANGUES:
        cle = "musique_fr" if langue == "fr" else "musique"
        os.makedirs(SORTIE + DOSSIERS[langue], exist_ok=True)
        with open(SORTIE + DOSSIERS[langue] + f"/Musiques et licences ({SUFFIXE[langue]}).txt", "w") as f:
            f.write("Musiques des vidéos : libres de droits, utilisables même commercialement.\n\n")
            for c in CARROUSELS:
                f.write(f"{c['fichier']} :\n{MUSIQUES[os.path.basename(c[cle])]['credit']}\n\n")


def videos(filtre=None, refaire=True):
    os.makedirs("rendu", exist_ok=True)
    travaux = [(c, l, refaire) for c, l in choisis(filtre)]
    with Pool(4) as p:
        for ligne in p.imap_unordered(video, travaux):
            print(ligne, flush=True)
    licences()


def apercu(filtre):
    """Planche de contrôle : le milieu de chaque plan, une ligne par langue."""
    lignes = [plans(c, l) for c, l in choisis(filtre)]
    w, h = 270, 360
    planche = Image.new("RGB", ((w + 6) * max(len(p) for p in lignes), (h + 6) * len(lignes)), "white")
    for j, liste in enumerate(lignes):
        for i, p in enumerate(liste):
            planche.paste(p.image(p.duree / 2).resize((w, h)), (i * (w + 6), j * (h + 6)))
    nom = f"apercu-{filtre}.jpg"
    planche.save(nom, quality=88)
    print(os.path.join(TRAVAIL, nom))


if __name__ == "__main__":
    commande = sys.argv[1] if len(sys.argv) > 1 else ""
    filtre = sys.argv[2] if len(sys.argv) > 2 else None
    actions = {"preparer": lambda: preparer(filtre), "cartes": lambda: cartes(filtre),
               "videos": lambda: videos(filtre), "musique": lambda: videos(filtre, refaire=False),
               "apercu": lambda: apercu(filtre or CARROUSELS[0]["cle"])}
    if commande not in actions:
        sys.exit(__doc__)
    actions[commande]()
