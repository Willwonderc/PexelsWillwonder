"""Montage des vidéos carrousel au rythme de la musique, dans les formats des réseaux.

Déroulé d'une vidéo (docs/plan-videos.md, règles A, R, T, I, S et M) :
- l'accroche : la photo la plus forte (celle de la couverture, sauf choix contraire),
  déjà en mouvement, et sa promesse à l'écran, mot à mot sur les premières notes ;
- le récit : chaque photo et son texte, coupé en sous-titres de deux lignes au plus ;
  les mots apparaissent sur les attaques des notes, les coupes tombent sur les temps
  forts, les mouvements (poussée, recul, travelling, bascule, révélation, dérive)
  changent d'un plan à l'autre et visent le sujet de la photo (carte de saillance) ;
- une barre de progression et un compteur (« 03 / 08 ») qui avancent avec les coupes
  et battent la mesure ;
- le petit cours de français (chinois et anglais), puis une fin courte : logo KF’
  animé, appel à chercher Karl Forterre sur Pexels, dernière note sur un temps fort.

Formats natifs, sans bandes noires : 9:16 (Reels, TikTok, Shorts, RedNote), 3:4
(RedNote, grille Instagram), 1:1 (Facebook), chacun avec ses zones de sécurité.
Chaque image est calculée en numpy et Pillow, puis encodée par ffmpeg (H.264 High,
4:2:0, BT.709, 30 images par seconde) ; le son est ramené à −14 LUFS.
"""
import json
import math
import os
import re
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 30
OR = (232, 196, 120)        # doré des couvertures et des fins des carrousels
BLANC = (255, 255, 255)
GRIS = (214, 214, 218)
FF = imageio_ffmpeg.get_ffmpeg_exe()
POLICES = "polices"

# Zones de sécurité : ce que cachent les boutons et légendes des applications (pixels).
FORMATS = {
    "9x16": {"taille": (1080, 1920), "haut": 250, "bas": 420, "gauche": 60, "droite": 140,
             "reseaux": "Reels, TikTok, YouTube Shorts, Stories, RedNote"},
    "3x4": {"taille": (1080, 1440), "haut": 90, "bas": 150, "gauche": 70, "droite": 70,
            "reseaux": "RedNote, grille du profil Instagram, Facebook"},
    "1x1": {"taille": (1080, 1080), "haut": 70, "bas": 90, "gauche": 70, "droite": 70,
            "reseaux": "Facebook"},
}

# Lecture : caractères par seconde, au plus (règle T2) et visés ; lignes (règle T1).
LECTURE = {"zh": (8.0, 7.2), "fr": (15.0, 14.0), "en": (15.0, 14.0)}
CARACTERES_LIGNE = {"zh": 16, "fr": 38, "en": 38}
MAX_SOUS_TITRE = 70  # caractères par sous-titre : lus en 5 s au plus, dans un plan de 6 s au plus
PONCT_FIN_ZH = "，。：、）」”！？；…"
OUVRANTES_ZH = "（「“《"


# --- Outils ----------------------------------------------------------------------------

def borne(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lisse(u):
    u = borne(u)
    return u * u * (3 - 2 * u)


def sortie(u):
    """Départ rapide, arrivée douce (cubique)."""
    return 1 - (1 - borne(u)) ** 3


def ressort(u):
    """Arrivée avec un léger dépassement (pour les titres)."""
    u = borne(u)
    c = 1.4
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


_polices = {}


def police(langue, graisse, taille):
    """Archivo (latin) ou Noto Sans SC (chinois), graisse 400, 500, 600 ou 700."""
    nom = f"noto-{graisse}" if langue == "zh" else f"archivo-{graisse}"
    cle = (nom, int(taille))
    if cle not in _polices:
        _polices[cle] = ImageFont.truetype(os.path.join(POLICES, nom + ".ttf"), int(taille))
    return _polices[cle]


def caracteres_absents(texte, langue):
    """Caractères que la police ne sait pas dessiner (ils sortiraient en carrés vides)."""
    def dessin(f, c):
        im = Image.new("L", (90, 90), 0)
        ImageDraw.Draw(im).text((15, 65), c, font=f, fill=255, anchor="ls")
        return im.tobytes()

    manquants = []
    for graisse in ((400, 500, 700) if langue == "zh" else (400, 600, 700)):
        f = police(langue, graisse, 40)
        vide = dessin(f, "\U0010fffd")  # glyphe de remplacement de la police (carré vide)
        manquants += [c for c in set(texte) if c.strip() and dessin(f, c) == vide]
    return sorted(set(manquants))


def typographie(texte, langue):
    """Apostrophes typographiques, espaces insécables du français (règle T5)."""
    if langue == "zh":
        return texte
    t = texte.replace("'", "’")
    if langue == "fr":
        t = re.sub(r"«\s*", "«\u00a0", t)
        t = re.sub(r"\s*»", "\u00a0»", t)
        t = re.sub(r"\s+([:;!?])", "\u00a0\\1", t)
    return t


def chasse(texte):
    """Largeur d'une ligne chinoise en caractères pleins : une lettre latine compte pour moitié."""
    return sum(0.5 if ord(c) < 0x2E80 else 1 for c in texte)


def longueur_lecture(texte, langue):
    """Longueur à lire : caractères (espaces compris) ; en chinois, un mot latin compte 2."""
    if langue != "zh":
        return len(texte)
    latin = re.findall(r"[A-Za-zÀ-ÿ’'\-]+|\d+", texte)
    reste = re.sub(r"[A-Za-zÀ-ÿ’'\-]+|\d+|\s", "", texte)
    return len(reste) + 2 * len(latin)


def flou(a, sigma):
    """Flou gaussien d'un tableau 2D (numpy, séparable)."""
    r = max(1, int(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    a = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), k, "valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), k, "valid"), 1, a)


def luminance(rgb):
    """Luminance relative (WCAG) d'un tableau sRGB entre 0 et 1."""
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


# --- Saillance : ce qui attire l'œil dans la photo ----------------------------------------

def saillance(chemin, cache="analyses"):
    """Centre et boîte du sujet, en fractions de la photo (x0, y0, x1, y1), et confiance.

    Résidu spectral (Hou et Zhang, 2007) et contraste des couleurs, avec un léger
    biais vers le centre ; calcul gardé dans travail/analyses/."""
    os.makedirs(cache, exist_ok=True)
    f = os.path.join(cache, "saillance-" + os.path.splitext(os.path.basename(chemin))[0] + ".json")
    if os.path.exists(f):
        with open(f) as g:
            return json.load(g)
    im = Image.open(chemin).convert("RGB")
    im.thumbnail((128, 128), Image.LANCZOS)
    rgb = np.asarray(im, np.float32) / 255
    gris = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    spectre = np.fft.fft2(gris)
    amp = np.log(np.abs(spectre) + 1e-6)
    residu = amp - flou(amp, 1.0)
    s1 = np.abs(np.fft.ifft2(np.exp(residu + 1j * np.angle(spectre)))) ** 2
    s1 = flou(s1, 3.0)
    # contraste des couleurs dans un espace opposé (luminance, rouge-vert, jaune-bleu)
    opp = np.stack([gris, rgb[..., 0] - rgb[..., 1], 0.5 * (rgb[..., 0] + rgb[..., 1]) - rgb[..., 2]], -1)
    s2 = flou(np.linalg.norm(opp - opp.reshape(-1, 3).mean(0), axis=-1), 3.0)
    h, w = gris.shape
    yy, xx = np.mgrid[0:h, 0:w]
    centre = np.exp(-(((xx / w - 0.5) / 0.45) ** 2 + ((yy / h - 0.5) / 0.45) ** 2))
    carte = (s1 / (s1.max() + 1e-9) * 0.5 + s2 / (s2.max() + 1e-9) * 0.5) * (0.6 + 0.4 * centre)
    carte /= carte.max() + 1e-9
    masque = carte >= np.percentile(carte, 88)
    poids = carte * masque
    cx = float((poids * xx).sum() / poids.sum()) / w
    cy = float((poids * yy).sum() / poids.sum()) / h
    ys, xs = np.where(masque)
    boite = [float(np.percentile(xs, 5)) / w, float(np.percentile(ys, 5)) / h,
             float(np.percentile(xs, 95) + 1) / w, float(np.percentile(ys, 95) + 1) / h]
    confiance = float(carte[masque].mean() / (carte.mean() + 1e-9))
    res = {"centre": [round(cx, 4), round(cy, 4)], "boite": [round(b, 4) for b in boite],
           "confiance": round(confiance, 3)}
    with open(f, "w") as g:
        json.dump(res, g)
    return res


# --- Photos et cadrages ------------------------------------------------------------------

_images = {}


def ouvrir(chemin):
    """Photo en RGB, gardée en mémoire pour les plans suivants (trois au plus)."""
    if chemin not in _images:
        if len(_images) >= 3:
            _images.pop(next(iter(_images)))
        _images[chemin] = Image.open(chemin).convert("RGB")
    return _images[chemin]


class Camera:
    """Cadre au rapport a (largeur / hauteur) promené dans une photo w × h (pixels)."""

    def __init__(self, w, h, a):
        self.w, self.h = w, h
        self.bw, self.bh = (h * a, h) if w / h > a else (w, w / a)

    def boite(self, cx, cy, z):
        z = max(z, 1.0)  # jamais plus grand que la photo
        cw, ch = self.bw / z, self.bh / z
        cx = borne(cx, cw / 2, self.w - cw / 2)
        cy = borne(cy, ch / 2, self.h - ch / 2)
        return (max(0.0, cx - cw / 2), max(0.0, cy - ch / 2), min(self.w, cx + cw / 2), min(self.h, cy + ch / 2))

    def centre_sujet(self, sujet, z, ys=0.5):
        """Centre du cadre qui place le sujet à la hauteur ys de l'image."""
        sx, sy = sujet[0] * self.w, sujet[1] * self.h
        return sx, sy - (ys - 0.5) * self.bh / z


def trajectoire(cam, mouvement, sujet, dz, ys, sens=1, zb=1.0):
    """Cadre de départ et d'arrivée (cx, cy, z) d'un mouvement dirigé vers le sujet.

    `zb` : zoom de base, 1 pour un plan large, plus pour un plan serré sur le sujet.
    Travelling et bascule gardent le sujet dans l'image du début à la fin (règle R4)."""
    z0, z1 = zb, zb * (1 + dz)
    cs0 = cam.centre_sujet(sujet, z0, ys)
    neutre = (cam.w / 2, cam.h / 2)
    melange = ((neutre[0] + cs0[0]) / 2, (neutre[1] + cs0[1]) / 2) if zb == 1.0 else cs0
    if mouvement == "poussee":
        return (*melange, z0), (*cam.centre_sujet(sujet, z1, ys), z1)
    if mouvement == "recul":
        return (*cam.centre_sujet(sujet, z1, ys), z1), (*melange, z0)
    if mouvement == "revelation":
        zr = zb * (1 + 2.2 * dz)
        return (*cam.centre_sujet(sujet, zr, ys), zr), (*melange, z0)
    if mouvement in ("travelling", "bascule"):
        z = zb * 1.03
        cw, ch = cam.bw / z, cam.bh / z
        horizontal = mouvement == "travelling"
        lo, hi = (cw / 2, cam.w - cw / 2) if horizontal else (ch / 2, cam.h - ch / 2)
        cs = cam.centre_sujet(sujet, z, ys)
        arrivee = borne(cs[0] if horizontal else cs[1], lo, hi)
        pas = 0.3 * (cw if horizontal else ch)
        departs = [borne(arrivee - pas * sens, lo, hi), borne(arrivee + pas * sens, lo, hi)]
        depart = max(departs, key=lambda d: abs(d - arrivee) + 1e-3 * (d == departs[0]))
        if horizontal:
            return (depart, cs[1], z), (arrivee, cs[1], z)
        return (cs[0], depart, z), (cs[0], arrivee, z)
    # dérive : léger glissement en diagonale, zoom presque fixe
    d = 0.03 * cam.bw / zb * sens
    return (cs0[0] - d, cs0[1] - d / 2, zb * 1.05), (cs0[0] + d, cs0[1] + d / 2, zb * (1.05 + dz / 2))


def fond_flou(im, W, H, assombrir):
    """La photo en plein cadre, très floue et assombrie : fond des plans « cadre » et des cartes."""
    cam = Camera(im.width, im.height, W / H)
    petit = im.resize((max(8, W // 8), max(8, H // 8)), Image.BILINEAR, box=cam.boite(im.width / 2, im.height / 2, 1.0))
    petit = petit.filter(ImageFilter.GaussianBlur(5))
    fond = np.asarray(petit.resize((W, H), Image.BICUBIC), np.float32) / 255
    return fond * (1 - assombrir)


def fond_sombre(W, H):
    """Fond noir en dégradé radial, comme l'image de fin des carrousels."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (0.75 * W)) ** 2 + ((yy - H * 0.45) / (0.75 * H)) ** 2)
    k = np.clip(1 - r, 0, 1)[..., None]
    bas, haut = np.array([11, 12, 16], np.float32) / 255, np.array([29, 30, 36], np.float32) / 255
    return bas + (haut - bas) * k


def ombre_portee(W, H, boite, decalage, flou_px, opacite):
    """Opacité (0 à 1) de l'ombre portée d'un rectangle."""
    m = Image.new("L", (W, H), 0)
    x0, y0, x1, y1 = boite
    ImageDraw.Draw(m).rectangle((x0, y0 + decalage, x1 - 1, y1 - 1 + decalage), fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(flou_px)), np.float32) / 255 * opacite


# --- Texte animé ---------------------------------------------------------------------

class Unite:
    """Un mot (ou un caractère chinois) posé à sa place, qui apparaît à l'instant t0."""

    def __init__(self, texte, f, x, y, t0, couleur=BLANC, montee=12, duree=0.2, ombre=0.62,
                 flou_ombre=7, rebond=False):
        x0, y0, x1, y1 = f.getbbox(texte, anchor="ls")
        m = max(4, int(3 * flou_ombre))
        w, h = x1 - x0 + 2 * m, y1 - y0 + 2 * m
        masque = Image.new("L", (w, h), 0)
        ImageDraw.Draw(masque).text((m - x0, m - y0), texte, font=f, fill=255, anchor="ls")
        self.masque = np.asarray(masque, np.float32) / 255
        self.ombre = (np.asarray(masque.filter(ImageFilter.GaussianBlur(flou_ombre)), np.float32) / 255
                      * ombre if ombre else None)
        self.x, self.y = int(round(x + x0 - m)), int(round(y + y0 - m))
        self.boite = (x + x0, y + y0, x + x1, y + y1)
        self.t0, self.couleur = t0, np.array(couleur, np.float32) / 255
        self.montee, self.duree, self.rebond = montee, duree, rebond
        self.texte = texte

    def poser(self, img, t, opacite=1.0):
        u = (t - self.t0) / self.duree
        if u <= 0 or opacite <= 0:
            return
        a = sortie(u) * opacite
        dy = int(round((1 - (ressort(u) if self.rebond else sortie(u))) * self.montee))
        coller(img, self.x, self.y + dy, self.masque, self.couleur, a, self.ombre)


def coller(img, x, y, masque, couleur, a, ombre=None, dy_ombre=3, fenetre=None):
    """Pose un masque de texte coloré (et son ombre) sur l'image, à l'opacité a.

    `fenetre` (haut, bas) : lignes de l'image hors desquelles rien n'est posé."""
    H, W = img.shape[:2]
    h, w = masque.shape
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if fenetre:
        y0, y1 = max(y0, fenetre[0]), min(y1, fenetre[1])
    if x1 <= x0 or y1 <= y0:
        return
    zone = img[y0:y1, x0:x1]
    if ombre is not None:
        oy0, oy1 = y0 - y - dy_ombre, y1 - y - dy_ombre
        o = np.zeros((y1 - y0, x1 - x0), np.float32)
        a0, a1 = max(0, oy0), min(h, oy1)
        if a1 > a0:
            o[a0 - oy0:a1 - oy0] = ombre[a0:a1, x0 - x:x1 - x]
        zone *= (1 - o * a)[..., None]
    m = masque[y0 - y:y1 - y, x0 - x:x1 - x][..., None] * a
    zone *= 1 - m
    zone += m * couleur


def couper_latin(mots, f, largeur, max_car):
    """Mots répartis en lignes qui tiennent dans la largeur (mot à mot)."""
    lignes, cur = [], []
    for m in mots:
        essai = cur + [m]
        if cur and (f.getlength(" ".join(essai)) > largeur or len(" ".join(essai)) > max_car):
            lignes.append(cur)
            cur = [m]
        else:
            cur = essai
    return lignes + [cur] if cur else lignes


# mots qui ouvrent un groupe : jamais en fin de ligne ni de sous-titre
PETITS_MOTS = {"de", "la", "le", "les", "l’", "un", "une", "des", "du", "à", "au", "aux", "et", "en", "par",
               "pour", "sur", "dans", "que", "qui", "où", "se", "ce", "son", "sa", "ses", "ne", "avec",
               "the", "a", "an", "of", "to", "and", "in", "on", "at", "by", "for", "with", "from", "that",
               "my", "our", "its"}


def repartir(mots, f, largeur, max_car, n):
    """Meilleure répartition des mots en n lignes : largeurs voisines, pas de ligne finie
    sur un petit mot (« de », « la »…), coupure de préférence après une ponctuation."""
    meilleur, choix = None, None

    def essais(debut, reste):
        if reste == 1:
            yield [mots[debut:]]
            return
        for k in range(debut + 1, len(mots) - reste + 2):
            for suite in essais(k, reste - 1):
                yield [mots[debut:k]] + suite

    for lignes in essais(0, n):
        textes = [" ".join(l) for l in lignes]
        largeurs = [f.getlength(t) for t in textes]
        if max(largeurs) > largeur or max(len(t) for t in textes) > max_car:
            continue
        cout = max(largeurs) - 0.15 * min(largeurs)
        for l in lignes[:-1]:
            if l[-1].lower() in PETITS_MOTS:
                cout += 0.25 * largeur
            if l[-1][-1] in ",:;.!?":
                cout -= 0.1 * largeur
        if meilleur is None or cout < meilleur:
            meilleur, choix = cout, textes
    return choix


def equilibrer(mots, f, largeur, max_car):
    """Une ligne si elle tient sans excès, sinon deux lignes de largeurs voisines."""
    texte = " ".join(mots)
    if len(mots) == 1 or (f.getlength(texte) <= largeur * 0.72 and len(texte) <= max_car):
        return [texte]
    return repartir(mots, f, largeur, max_car, 2) or [" ".join(l) for l in couper_latin(mots, f, largeur, max_car)]


def decouper_latin(texte, f, largeur, max_car):
    """Texte coupé en sous-titres de deux lignes au plus, de préférence après une ponctuation."""
    mots = texte.split(" ")
    morceaux, i = [], 0
    while i < len(mots):
        j = i + 1
        while (j < len(mots) and len(couper_latin(mots[i:j + 1], f, largeur, max_car)) <= 2
               and len(" ".join(mots[i:j + 1])) <= MAX_SOUS_TITRE):
            j += 1
        if j < len(mots):
            for k in range(j, i + max(1, (j - i) // 2), -1):
                if mots[k - 1][-1] in ".:;!?," or mots[k - 1].endswith("»"):
                    j = k
                    break
            else:  # pas de ponctuation : ne pas finir sur un petit mot (« …le ciel de »)
                while j - 1 > i and mots[j - 1].lower() in PETITS_MOTS:
                    j -= 1
        morceaux.append(equilibrer(mots[i:j], f, largeur, max_car))
        i = j
    return morceaux


def couper_zh(ligne, f, largeur, max_car):
    """Ligne chinoise trop longue coupée en deux, au mieux : après une ponctuation ou avant
    une parenthèse, jamais au milieu d'un mot latin ni d'une parenthèse, jamais de
    ponctuation en début de ligne (règles de mise en page du chinois)."""
    ligne = ligne.strip()
    if chasse(ligne) <= max_car and f.getlength(ligne) <= largeur:
        return [ligne]

    def latin(c):
        return (c.isalnum() and ord(c) < 0x2E80) or c in "'’-"

    meilleur, choix = None, None
    for k in range(1, len(ligne)):
        a, b = ligne[k - 1], ligne[k]
        if b in PONCT_FIN_ZH or a in OUVRANTES_ZH or (latin(a) and latin(b)):
            continue
        g, d = ligne[:k].strip(), ligne[k:].strip()
        if not g or not d or d[0] in PONCT_FIN_ZH:
            continue
        cout = abs(chasse(g) - chasse(d))
        cout -= 8 if a in PONCT_FIN_ZH else 0
        cout -= 8 if b in OUVRANTES_ZH else 0
        cout += 10 if g.count("（") > g.count("）") else 0  # à l'intérieur d'une parenthèse
        cout += 5 if latin(g[-1]) and latin(d[0]) else 0  # entre deux mots latins
        if meilleur is None or cout < meilleur:
            meilleur, choix = cout, (g, d)
    if choix is None:
        k = len(ligne) // 2
        choix = (ligne[:k], ligne[k:])
    return couper_zh(choix[0], f, largeur, max_car) + couper_zh(choix[1], f, largeur, max_car)


def decouper_zh(lignes, f, largeur, max_car):
    """Lignes validées du carrousel, regroupées par deux ; une fin de phrase clôt un sous-titre."""
    courtes = [l for ligne in lignes for l in couper_zh(ligne, f, largeur, max_car)]
    morceaux, cur = [], []
    for l in courtes:
        cur.append(l)
        if len(cur) == 2 or l[-1] in "。！？：":
            morceaux.append(cur)
            cur = []
    return morceaux + [cur] if cur else morceaux


def unites_bloc(lignes, langue, f, cx, base_y, pas, t0, t1, rythme, couleur=BLANC, aligne="centre",
                x_gauche=0, montee=12, rebond=False, duree=0.2):
    """Unités d'un bloc de lignes, apparaissant entre t0 et t1, posées sur les attaques des notes.

    Français et anglais : mot à mot. Chinois : ligne par ligne, chaque ligne en rafale de
    caractères (28 ms de l'un à l'autre)."""
    unites = []

    def instant(t):
        t = rythme.attaque_proche(t, 0.07) if rythme else t
        return max(t, unites[-1].t0) if unites else t

    for i, ligne in enumerate(lignes):
        y = base_y + i * pas
        x = x_gauche if aligne == "gauche" else cx - f.getlength(ligne) / 2
        if langue == "zh":
            t = instant(t0 + (t1 - t0) * i / max(1, len(lignes)))
            vus = [(k, c) for k, c in enumerate(ligne) if c.strip()]
            for j, (k, c) in enumerate(vus):
                unites.append(Unite(c, f, x + f.getlength(ligne[:k]), y, t + 0.028 * j, couleur,
                                    montee=montee, rebond=rebond, duree=duree))
    if langue == "zh":
        return unites
    places = []
    for i, ligne in enumerate(lignes):
        y = base_y + i * pas
        x = x_gauche if aligne == "gauche" else cx - f.getlength(ligne) / 2
        mots = ligne.split(" ")
        for k, m in enumerate(mots):
            if m:
                places.append((m, x + f.getlength(" ".join(mots[:k]) + (" " if k else "")), y))
    n = len(places)
    for k, (texte, x, y) in enumerate(places):
        t = instant(t0 + (t1 - t0) * k / max(1, n - 1))
        unites.append(Unite(texte, f, x, y, t, couleur, montee=montee, rebond=rebond, duree=duree))
    return unites


def boite_unites(unites):
    xs0, ys0, xs1, ys1 = zip(*[u.boite for u in unites])
    return (min(xs0), min(ys0), max(xs1), max(ys1))


# --- Logo KF’ (vitrine/statique/logo.svg) --------------------------------------------------

def logo_masques(hauteur, chemin_svg):
    """Masques du logo : (barres, lettres), à la hauteur voulue, lissés (suréchantillonnage)."""
    with open(chemin_svg) as f:
        svg = f.read()
    d = re.search(r' d="([^"]+)"', svg).group(1)
    jetons = re.findall(r"[MLCZ]|-?\d+(?:\.\d+)?", d)
    chemins, cur, i, pos = [], [], 0, (0.0, 0.0)
    while i < len(jetons):
        c = jetons[i]
        i += 1
        if c == "M":
            if cur:
                chemins.append(cur)
            pos = (float(jetons[i]), float(jetons[i + 1]))
            cur, i = [pos], i + 2
        elif c == "L":
            pos = (float(jetons[i]), float(jetons[i + 1]))
            cur.append(pos)
            i += 2
        elif c == "C":
            x1, y1, x2, y2, x, y = (float(v) for v in jetons[i:i + 6])
            i += 6
            x0, y0 = pos
            for k in range(1, 17):
                u = k / 16
                a, b, cc, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
                cur.append((a * x0 + b * x1 + cc * x2 + e * x, a * y0 + b * y1 + cc * y2 + e * y))
            pos = (x, y)
    if cur:
        chemins.append(cur)
    # boîte de vue du logo : 0 130 1500 1130
    ech = 4 * hauteur / 1130
    taille = (int(1500 * ech) + 8, int(1130 * ech) + 8)
    barres, lettres = Image.new("L", taille, 0), Image.new("L", taille, 0)
    for ch in chemins:
        pts = [(x * ech + 4, (y - 130) * ech + 4) for x, y in ch]
        ys = [p[1] for p in pts]
        hauteur_ch = max(ys) - min(ys)
        cible = barres if hauteur_ch < 80 * ech else lettres  # les deux barres sont fines
        k = Image.new("L", taille, 0)
        ImageDraw.Draw(k).polygon(pts, fill=255)
        # remplissage pair-impair : chaque sous-chemin inverse la zone qu'il couvre
        cible.paste(Image.fromarray(np.asarray(cible, np.uint8) ^ np.asarray(k, np.uint8)))
    petit = (taille[0] // 4, taille[1] // 4)
    return (np.asarray(barres.resize(petit, Image.LANCZOS), np.float32) / 255,
            np.asarray(lettres.resize(petit, Image.LANCZOS), np.float32) / 255)


# --- Plans -------------------------------------------------------------------------------

class Plan:
    """Un plan de la vidéo, de `debut` à `fin` (secondes)."""

    def __init__(self, genre, debut, fin, **kw):
        self.genre, self.debut, self.fin = genre, debut, fin
        self.entree, self.duree_entree = "coupe", 0.0
        self.photo, self.numero, self.lignes = None, None, None
        self.cadrage, self.mouvement = None, None
        self.unites, self.boite_texte, self.taille_texte = [], None, None
        self.contraste, self.agrandissement = None, None
        self.__dict__.update(kw)
        self.pret = False

    @property
    def duree(self):
        return self.fin - self.debut


class Montage:
    """Toute la vidéo : plans, habillage, rythme ; construit par `construire`."""

    def __init__(self, W, H, fmt, langue, rythme, style):
        self.W, self.H, self.fmt, self.langue = W, H, fmt, langue
        self.m = FORMATS[fmt]
        self.u = W / 1080
        self.rythme, self.style = rythme, style
        self.plans = []
        self.duree = 0.0
        self.bouton = None

    # -- mise en page -----------------------------------------------------------------
    def zone(self):
        m = self.m
        return m["gauche"], m["haut"], self.W - m["droite"], self.H - m["bas"]

    def largeur_texte(self):
        """Largeur des sous-titres centrés, symétrique, hors des boutons des applications."""
        x0, _, x1, _ = self.zone()
        return 2 * min(self.W / 2 - x0, x1 - self.W / 2) - 20 * self.u

    def taille_sous_titre(self):
        return round((50 if self.langue == "zh" else 46) * self.u)

    def pas_ligne(self):
        return round(self.taille_sous_titre() * (1.36 if self.langue == "zh" else 1.3))


# --- Construction du montage ---------------------------------------------------------------

def durees(n, langue, texte):
    """Durées (au plus court, visée, au plus long) d'un plan portant n caractères à lire."""
    if not texte:
        return 1.8, 2.4, 3.2
    maxi, vise = LECTURE[langue]
    dmin = max(1.8, n / maxi + 0.35)
    dvise = max(2.4, n / vise + 0.5)
    return dmin, dvise, min(6.0, max(dvise * 1.3 + 0.3, dmin + 0.6))


def construire(c, langue, fmt, rythme, style, photo, sujets, textes):
    """Plan de montage complet d'une vidéo (sans calculer d'image).

    `photo(n)` : chemin de la photo n ; `sujets[n]` : saillance ; `textes` : accroche,
    fin et crédit de la langue."""
    W, H = FORMATS[fmt]["taille"]
    M = Montage(W, H, fmt, langue, rythme, style)
    d = c[langue]
    f_st = police(langue, 500 if langue == "zh" else 600, M.taille_sous_titre())
    largeur = M.largeur_texte()
    max_car = CARACTERES_LIGNE[langue]

    # 1. accroche : 2,3 à 3,7 s, coupée sur un temps fort ; la promesse est écrite dès 0,3 s
    n_acc = c.get("accroche_photo", 1)
    promesse = textes["promesse"]
    n_promesse = longueur_lecture(promesse.replace("\n", " "), langue)
    dmin = max(2.3, n_promesse / LECTURE[langue][0] + 0.8)
    fin = rythme.coupe(dmin, max(dmin, 3.0), max(dmin + 0.3, 3.7))
    M.plans.append(Plan("accroche", 0.0, fin, photo=n_acc, cadrage="plein", mouvement="poussee"))

    # 2. récit : chaque photo, ses sous-titres (deux lignes au plus)
    t = fin
    numero = 0
    vues = []
    for n, texte in d["plans"]:
        if n not in vues:
            vues.append(n)
        numero = vues.index(n) + 1
        if texte is None:
            morceaux = [None]
        elif langue == "zh":
            morceaux = decouper_zh(texte, f_st, largeur, max_car)
        else:
            mots = typographie(texte, langue).split(" ")
            morceaux = decouper_latin(" ".join(mots), f_st, largeur, max_car)
        for k, lignes in enumerate(morceaux):
            nlec = longueur_lecture(" ".join(lignes), langue) if lignes else 0
            dmin, dvise, dmax = durees(nlec, langue, lignes)
            fin = rythme.coupe(t + dmin, t + dvise, t + dmax)
            M.plans.append(Plan("recit", t, fin, photo=n, numero=numero, lignes=lignes, morceau=k,
                                morceaux=len(morceaux)))
            t = fin

    # 3. petit cours de français (chinois et anglais) : les entrées apparaissent sur les temps forts
    if "lecon" in d:
        titre, entrees = d["lecon"]
        # le mot français se lit d'un coup d'œil : seule l'explication compte
        lectures = [longueur_lecture(" ".join(e) if isinstance(e, list) else e, langue) + 4 for _, e in entrees]
        duree = sum(n / LECTURE[langue][1] + 0.5 for n in lectures) + 0.8
        fin = rythme.coupe(t + duree - 0.4, t + duree, t + duree + 1.2)
        apparitions, tt = [], t + 0.1
        for n in lectures:
            apparitions.append(rythme.coupe(tt, tt + 0.1, tt + 0.6))
            tt = apparitions[-1] + n / LECTURE[langue][1] + 0.6
        M.plans.append(Plan("lecon", t, fin, titre=titre, entrees=entrees, apparitions=apparitions,
                            photo=c.get("fond_lecon", max(c["photos"]))))
        t = fin

    # 4. fin : logo, appel à chercher sur Pexels ; la dernière ligne tombe sur un temps fort
    bouton = rythme.fin_de_phrase(t + 2.4, t + 4.2)
    queue = borne(2 * rythme.periode, 1.2, 2.0)
    M.plans.append(Plan("fin", t, bouton + queue, bouton=bouton, photo=n_acc))
    M.bouton = bouton
    M.duree = bouton + queue

    choisir_cadrages(M, c, photo, sujets)
    choisir_transitions(M)
    return M


def orientation(chemin):
    with Image.open(chemin) as im:
        return im.width / im.height


def choisir_cadrages(M, c, photo, sujets):
    """Cadrage, échelle et mouvement de chaque plan.

    Photo en paysage : vue entière sur fond flou (« cadre ») ou détail en plein cadre,
    en alternance. Deux plans de suite sur la même photo en plein cadre : un large, un
    serré sur le sujet (+45 %), pour que la coupe se voie. Jamais deux fois le même
    mouvement de suite (règle R3)."""
    a_cadre = M.W / M.H
    prec = M.plans[0]
    prec.echelle = "large"
    rotation = 0
    for p in M.plans:
        if p.genre != "recit":
            continue
        r = orientation(photo(p.photo))
        s = sujets[p.photo]
        paysage = r > a_cadre * 1.35
        meme = p.photo == prec.photo
        if paysage:
            # le sujet tient-il dans un cadre plein ? sinon, la photo entière
            cam = Camera(1000, 1000 / r, a_cadre)
            tient = (s["boite"][2] - s["boite"][0]) * 1000 <= cam.bw * 1.05 and s["confiance"] > 1.6
            if meme:  # même photo : la vue entière, puis un détail (et inversement)
                cadrage = "plein" if prec.cadrage == "cadre" else "cadre"
            else:
                cadrage = "plein" if (prec.cadrage == "cadre" and tient and p.morceaux == 1) else "cadre"
        else:
            cadrage = "plein"
        echelle = "large"
        if cadrage == "plein" and meme and prec.cadrage == "plein" and prec.echelle == "large":
            echelle = "serre"
        if cadrage == "cadre":
            choix = ["poussee", "recul", "derive"]
        elif echelle == "serre":
            choix = ["poussee", "derive", "recul"]
        elif paysage:
            choix = ["travelling", "poussee", "recul", "revelation"]
        else:
            vertical = r < a_cadre * 0.9
            choix = ["poussee", "bascule" if vertical else "derive", "recul", "revelation"]
        if s["confiance"] < 1.5 and "revelation" in choix:
            choix.remove("revelation")
        k = rotation % len(choix)
        while choix[k % len(choix)] == prec.mouvement:
            k += 1
        rotation += 1
        p.cadrage, p.echelle, p.mouvement = cadrage, echelle, choix[k % len(choix)]
        prec = p


def choisir_transitions(M):
    """Coupe franche par défaut ; fondus pour la musique calme ; fondu au noir avant la fin."""
    changements = 0
    for i in range(1, len(M.plans)):
        a, b = M.plans[i - 1], M.plans[i]
        if b.genre == "fin":
            b.entree, b.duree_entree = "noir", 0.5
        elif b.genre == "lecon":
            b.entree, b.duree_entree = ("fondu", 0.5) if M.style == "calme" else ("glisse", 0.32)
        elif a.photo == b.photo and a.genre == b.genre:
            # même photo, autre cadrage : coupe sèche sur le temps (fondu bref si calme)
            b.entree, b.duree_entree = ("fondu", 0.4) if M.style == "calme" else ("coupe", 0.0)
        else:
            changements += 1
            if M.style == "calme":
                b.entree, b.duree_entree = ("coupe", 0.0) if changements % 3 == 0 else ("fondu", 0.6)
            else:
                b.entree, b.duree_entree = ("glisse", 0.32) if changements % 4 == 0 else ("coupe", 0.0)


# --- Préparation des plans (images, textes) ------------------------------------------------

class Rendu:
    """Calcule les images d'un montage."""

    def __init__(self, M, photo, sujets, textes, svg):
        self.M, self.photo, self.sujets, self.textes, self.svg = M, photo, sujets, textes, svg
        W, H = M.W, M.H
        self.degrade_cache = {}
        rng = np.random.default_rng(7)
        # grain très fin (en niveaux de 0 à 255, arrondi compris), contre les bandes dans les
        # dégradés et les fonds flous (règle I4) : 8 images en boucle
        self.grain = [(rng.normal(0, 1.1, (H, W)) + 0.5).astype(np.float32)[..., None] for _ in range(8)]
        self.habillage = Habillage(M)

    # -- photo en plein cadre ou entière sur fond flou --------------------------------------
    def preparer(self, p):
        if p.pret:
            return
        M = self.M
        W, H, u = M.W, M.H, M.u
        im = ouvrir(self.photo(p.photo)) if p.photo and p.genre != "fin" else None
        s = self.sujets.get(p.photo)
        vif = M.style == "vif"
        dz = borne((0.03 if vif else 0.022) * p.duree + 0.04, 0.07, 0.17 if vif else 0.13)
        if p.genre in ("accroche", "recit"):
            if p.cadrage == "plein":
                ys = 0.36 if M.fmt == "9x16" else 0.42
                if p.genre == "accroche":
                    dz = 0.12
                cam = Camera(im.width, im.height, W / H)
                sens = 1 if (p.numero or 0) % 2 else -1
                zb = 1.0
                if getattr(p, "echelle", "large") == "serre":  # plan serré, sans jamais agrandir la photo
                    zb = borne(cam.bw / W / ((1 + dz) * 1.05), 1.0, 1.45)
                a, b = trajectoire(cam, p.mouvement, s["centre"], dz, ys, sens, zb)
                # jamais au-delà de la résolution de la photo, impulsions comprises (règle I5)
                zlim = max(1.0, cam.bw / W / (1.04 if vif else 1.015))
                a, b = (a[0], a[1], min(a[2], zlim)), (b[0], b[1], min(b[2], zlim))
                zmax = max(a[2], b[2]) * (1.04 if vif else 1.015)
                # photo réduite une fois pour toutes à la taille utile (au plus la taille réelle)
                ech = min(1.0, W * zmax / cam.bw * 1.02)
                src = im.resize((round(im.width * ech), round(im.height * ech)), Image.LANCZOS) if ech < 1 else im
                p.src = src
                p.cam = Camera(src.width, src.height, W / H)
                p.a = (a[0] * ech, a[1] * ech, a[2])
                p.b = (b[0] * ech, b[1] * ech, b[2])
                p.agrandissement = W * zmax / cam.bw  # > 1 : la photo serait agrandie (règle I5)
                p.fond = None
            else:
                r = im.width / im.height
                x0, y0, x1, y1 = M.zone()
                # photo entière, réduite si besoin pour que photo et sous-titres tiennent dans la zone sûre
                place = (y1 - y0) - round(104 * u) - 2 * M.pas_ligne()
                pw = min(round(1000 * u) if M.fmt != "1x1" else round(900 * u), int(place * r))
                ph = round(pw / r)
                bloc = ph + round(64 * u) + 2 * M.pas_ligne()
                haut = borne((H - bloc) / 2 - 0.03 * H, y0 + 40 * u, y1 - bloc)
                px, py = (W - pw) // 2, round(haut)
                p.boite_photo = (px, py, px + pw, py + ph)
                fond = fond_flou(im, W, H, 0.58)
                ombre = ombre_portee(W, H, p.boite_photo, round(17 * u), round(23 * u), 0.46)
                p.fond = fond * (1 - ombre[..., None])
                ech = min(1.0, pw * 1.12 / im.width * 1.02)
                src = im.resize((round(im.width * ech), round(im.height * ech)), Image.LANCZOS) if ech < 1 else im
                p.src = src
                p.cam = Camera(src.width, src.height, pw / ph)
                dzc = dz * 0.6
                a, b = trajectoire(p.cam, {"poussee": "poussee", "recul": "recul"}.get(p.mouvement, "derive"),
                                   s["centre"], dzc, 0.5, 1 if (p.numero or 0) % 2 else -1)
                p.a, p.b = a, b
                p.agrandissement = pw * max(a[2], b[2]) / im.width
        if p.genre == "lecon":  # fond flou qui avance lentement
            p.fond = Image.fromarray((fond_flou(im, W, H, 0.7) * 255 + 0.5).astype(np.uint8))
        if p.genre == "fin":
            p.fond = fond_sombre(W, H)
        self.textes_du_plan(p)
        p.pret = True

    @staticmethod
    def position(p, tl):
        """Centre et zoom du cadre à l'instant tl du plan ; le mouvement continue un peu
        au-delà de ses bornes pendant les fondus."""
        uu = tl / max(p.duree, 0.1)
        base = borne(uu)
        if p.mouvement == "revelation" or p.genre == "accroche":
            k = sortie(base)
        else:
            k = 0.82 * lisse(base) + 0.18 * base
        k += 0.12 * (uu - base)  # au-delà du plan : même sens, plus lentement
        return tuple(a + (b - a) * k for a, b in zip(p.a, p.b))

    def sujet_a_l_image(self, p, s, tl):
        """Où se trouve le centre du sujet dans l'image (fractions), à l'instant tl du plan."""
        cx, cy, z = self.position(p, tl)
        x0, y0, x1, y1 = p.cam.boite(cx, cy, z)
        sx, sy = s["centre"][0] * p.src.width, s["centre"][1] * p.src.height
        return round((sx - x0) / (x1 - x0), 3), round((sy - y0) / (y1 - y0), 3)

    def base(self, p, t):
        """Image du plan sans son texte, à l'instant t (secondes de la vidéo)."""
        M = self.M
        W, H = M.W, M.H
        tl = t - p.debut
        if p.genre == "fin":
            return p.fond.copy()
        if p.genre == "lecon":
            z = 1 + 0.06 * lisse(tl / max(p.duree, 0.1))
            cw, ch = W / z, H / z
            boite = ((W - cw) / 2, (H - ch) * 0.4, (W + cw) / 2, (H - ch) * 0.4 + ch)
            out = np.asarray(p.fond.resize((W, H), Image.BILINEAR, box=boite), np.float32)
            out *= 1 / 255
            return out
        cx, cy, z = self.position(p, tl)
        # impact de la coupe et impulsions des temps forts (musique vive)
        if M.style == "vif":
            z *= 1 + 0.028 * math.exp(-max(tl, 0) / 0.12) * (p.genre != "accroche")
            z *= 1 + 0.010 * M.rythme.impulsion(t, seuil=1.2)
        else:
            z *= 1 + 0.012 * math.exp(-max(tl, 0) / 0.3) * (p.genre != "accroche")
        boite = p.cam.boite(cx, cy, z)
        # redimensionnement d'une boîte à coordonnées décimales : précis sous le pixel
        if p.cadrage == "plein":
            out = np.asarray(p.src.resize((W, H), Image.BICUBIC, box=boite), np.float32)
            out *= 1 / 255
            return out
        x0, y0, x1, y1 = p.boite_photo
        out = p.fond.copy()
        photo = np.asarray(p.src.resize((x1 - x0, y1 - y0), Image.BICUBIC, box=boite), np.float32)
        photo *= 1 / 255
        out[y0:y1, x0:x1] = photo
        return out

    def degrade(self, y_haut, force):
        """Assombrissement du bas de l'image, sous le texte : (première ligne touchée, facteurs)."""
        cle = (round(y_haut), round(force, 2))
        if cle not in self.degrade_cache:
            H = self.M.H
            debut = max(0, int(y_haut - 260 * self.M.u))
            y = np.arange(debut, H, dtype=np.float32)
            a = np.clip((y - debut) / (y_haut + 40 * self.M.u - debut), 0, 1)
            a = a * a * (3 - 2 * a) * force
            self.degrade_cache[cle] = (debut, (1 - a)[:, None, None].astype(np.float32))
        return self.degrade_cache[cle]

    def voiler(self, img, voile):
        debut, facteurs = self.degrade(*voile)
        img[debut:] *= facteurs
        return img

    # -- textes des plans -----------------------------------------------------------
    def textes_du_plan(self, p):
        M = self.M
        L, u, W = M.langue, M.u, M.W
        x0, y0, x1, y1 = M.zone()
        R = M.rythme
        p.voile = None
        if p.genre == "accroche":
            self.textes_accroche(p)
        elif p.genre == "recit" and p.lignes:
            f = police(L, 500 if L == "zh" else 600, M.taille_sous_titre())
            pas = M.pas_ligne()
            n = len(p.lignes)
            if p.cadrage == "plein":
                base = y1 - round(34 * u) - (n - 1) * pas
            else:
                base = p.boite_photo[3] + round(64 * u) + round(M.taille_sous_titre() * 0.8)
            t0 = p.debut + 0.06
            t1 = t0 + min(0.9, 0.3 * p.duree) + (0.2 if n > 1 else 0)
            p.unites = unites_bloc(p.lignes, L, f, W / 2, base, pas, t0, t1, R)
            p.taille_texte = M.taille_sous_titre()
            p.boite_texte = boite_unites(p.unites)
            if p.cadrage == "plein":
                p.voile = self.voile_adapte(p, p.boite_texte)
        elif p.genre == "lecon":
            self.textes_lecon(p)
        elif p.genre == "fin":
            self.textes_fin(p)

    def voile_adapte(self, p, boite, cible=5.2, plancher=4.7):
        """Assombrissement juste suffisant pour un contraste d'au moins `cible` : 1 (WCAG),
        mesuré au milieu du plan, puis renforcé si le mouvement amène ailleurs un fond plus
        clair sous le texte (contraste sous `plancher`)."""
        x0, y0, x1, y1 = (int(v) for v in boite)
        lmax = 1.05 / cible - 0.05

        def clarte(k):
            zone = self.base(p, p.debut + k * p.duree)[max(0, y0):y1, max(0, x0):x1]
            return float(np.percentile(luminance(zone), 90))

        def force_pour(lum):
            f = 0.35 if lum <= lmax else 1 - (lmax / lum) ** (1 / 2.2)
            return borne(f + 0.04, 0.35, 0.85)

        force = force_pour(clarte(0.5))
        for k in (0.05, 0.25, 0.75, 0.97):
            lum = clarte(k)
            if 1.05 / (lum * (1 - force) ** 2.2 + 0.05) < plancher:
                force = max(force, force_pour(lum))
        return (y0, force)

    def textes_accroche(self, p):
        M, L, u = self.M, self.M.langue, self.M.u
        x0, y0, x1, y1 = M.zone()
        surtitre, titre, tags = self.textes["surtitre"], self.textes["promesse"], self.textes["tags"]
        xg = x0 + round(20 * u)
        largeur = x1 - xg - round(10 * u)
        taille = round((96 if L == "zh" else 88) * u)
        f_titre = police(L, 700, taille)
        while True:
            if "\n" in titre:
                lignes = titre.split("\n")
            elif L == "zh":
                lignes = couper_zh(titre, f_titre, largeur, 9)
            elif f_titre.getlength(titre) <= 0.7 * largeur:
                lignes = [titre]
            else:
                mots = titre.split(" ")
                lignes = repartir(mots, f_titre, largeur, 60, 2) or repartir(mots, f_titre, largeur, 60, 3) or \
                    [" ".join(l) for l in couper_latin(mots, f_titre, largeur, 60)]
            if all(f_titre.getlength(l) <= largeur for l in lignes) and len(lignes) <= 3:
                break
            taille -= 4
            f_titre = police(L, 700, taille)
        pas = round(taille * 1.18)
        f_sur = police(L, 400, round(34 * u))
        f_tags = police(L, 500 if L == "zh" else 600, round(31 * u))
        while f_tags.getlength(tags) > largeur and f_tags.size > 22:
            f_tags = police(L, 500 if L == "zh" else 600, f_tags.size - 1)
        base_tags = y1 - round(36 * u)
        base_titre = base_tags - round(70 * u) - (len(lignes) - 1) * pas
        base_sur = base_titre - taille - round(26 * u)
        p.regle = (xg, base_sur - round(34 * u) - round(58 * u), round(66 * u), round(5 * u))
        R = M.rythme
        p.unites = [Unite(surtitre, f_sur, xg, base_sur, 0.05, BLANC, montee=8, duree=0.35)]
        t_titre = R.attaque_proche(0.25, 0.1)
        p.unites += unites_bloc(lignes, L, f_titre, 0, base_titre, pas, t_titre,
                                t_titre + min(1.0, 0.16 * len(" ".join(lignes).split(" ")) + 0.3), R,
                                aligne="gauche", x_gauche=xg, montee=26, rebond=True, duree=0.28)
        t_tags = max(u_.t0 for u_ in p.unites) + 0.3
        p.unites.append(Unite(tags, f_tags, xg, base_tags, t_tags, OR, montee=8, duree=0.35))
        # signature en haut à gauche, comme sur la couverture des carrousels
        f_sig = police("fr", 600, round(24 * u))
        p.unites.append(Unite("KF’   KARL FORTERRE", f_sig, xg, y0 + round(40 * u), 0.0, BLANC, montee=0,
                              duree=0.4, ombre=0.5))
        p.taille_texte = taille
        titre_unites = [x for x in p.unites if x.montee == 26]
        p.boite_texte = boite_unites(titre_unites)
        p.premier_titre = min(x.t0 for x in titre_unites)
        p.boite_bloc = boite_unites(p.unites[:-1])
        p.voile = self.voile_adapte(p, (p.boite_bloc[0], p.regle[1] - 20 * u, p.boite_bloc[2], p.boite_bloc[3]))
        p.lignes = lignes

    def textes_lecon(self, p):
        M, L, u, W = self.M, self.M.langue, self.M.u, self.M.W
        x0, y0, x1, y1 = M.zone()
        largeur = M.largeur_texte()
        f_titre = police(L, 500 if L == "zh" else 600, round(46 * u))
        f_mot = police("fr", 600, round(72 * u))
        f_expl = police(L, 400, round(40 * u))
        pas_expl = round(40 * u * 1.4)
        blocs = []
        for mot, expl in p.entrees:
            if isinstance(expl, list):
                lignes = [l for e in expl for l in couper_zh(e, f_expl, largeur, 16)] if L == "zh" else expl
            elif L == "zh":
                lignes = couper_zh(expl, f_expl, largeur, 16)
            else:
                lignes = [" ".join(l) for l in couper_latin(typographie(expl, L).split(" "), f_expl, largeur, 40)]
            blocs.append((mot, lignes))
        hauteur = sum(round(92 * u) + len(l) * pas_expl + round(56 * u) for _, l in blocs)
        haut_titre = y0 + round(90 * u)
        y = haut_titre + round(150 * u) + max(0, (y1 - haut_titre - round(150 * u) - hauteur) / 2 - round(40 * u))
        p.regle = (W / 2 - round(34 * u), haut_titre, round(68 * u), round(5 * u))
        R = M.rythme
        titre = p.titre if L == "zh" else p.titre.upper()
        p.unites = [Unite(titre, f_titre, W / 2 - f_titre.getlength(titre) / 2, haut_titre + round(80 * u),
                          p.debut + 0.05, OR, montee=10, duree=0.35)]
        for (mot, lignes), t_app in zip(blocs, p.apparitions):
            y += round(72 * u)
            p.unites.append(Unite(typographie(mot, "fr"), f_mot, W / 2 - f_mot.getlength(typographie(mot, "fr")) / 2,
                                  y, t_app, BLANC, montee=22, rebond=True, duree=0.3))
            y += round(20 * u) + pas_expl
            p.unites += unites_bloc(lignes, L, f_expl, W / 2, y, pas_expl, t_app + 0.25,
                                    t_app + 0.25 + min(0.8, 0.05 * sum(len(l) for l in lignes)), R,
                                    couleur=GRIS, montee=8)
            y += (len(lignes) - 1) * pas_expl + round(56 * u)
        p.taille_texte = round(40 * u)
        p.boite_texte = boite_unites(p.unites)

    def textes_fin(self, p):
        M, L, u, W = self.M, self.M.langue, self.M.u, self.M.W
        x0, y0, x1, y1 = M.zone()
        fin = self.textes["fin"]
        R = M.rythme
        h_logo = round(150 * u)
        barres, lettres = logo_masques(h_logo, self.svg)
        hauteur_bloc = barres.shape[0] + round(620 * u)
        haut = y0 + max(0, (y1 - y0 - hauteur_bloc) / 2 - 30 * u)
        p.logo = (barres, lettres, round(W / 2 - barres.shape[1] / 2), round(haut))
        y = haut + barres.shape[0] + round(80 * u)
        t = p.debut
        temps = [t + 0.1]
        # les lignes apparaissent sur les temps forts qui mènent au « bouton »
        for k in range(1, 4):
            temps.append(R.coupe(temps[-1] + 0.35, temps[-1] + 0.5, max(temps[-1] + 0.6, p.bouton - (3 - k) * 0.35)))
        temps = [min(x, p.bouton) for x in temps]
        f_nom = police("fr", 600, round(58 * u))
        f_ligne = police(L, 400, round(35 * u))
        f_appel = police(L, 500 if L == "zh" else 600, round(44 * u))
        f_petit = police(L, 400, round(33 * u))
        centre = W / 2

        def ligne(texte, f, y, t0, couleur=BLANC, montee=10):
            texte = typographie(texte, L)
            return Unite(texte, f, centre - f.getlength(texte) / 2, y, t0, couleur, montee=montee, duree=0.3)

        p.unites = [ligne("Karl Forterre", f_nom, y, temps[0] + 0.15)]
        y += round(58 * u)
        p.unites.append(ligne(fin[0], f_ligne, y, temps[0] + 0.3, GRIS))
        y += round(70 * u)
        p.regle = (centre - round(36 * u), y, round(72 * u), round(5 * u))
        p.t_regle = temps[1]
        y += round(95 * u)
        p.unites.append(ligne(fin[1], f_appel if f_appel.getlength(fin[1]) < M.largeur_texte() else f_ligne,
                              y, temps[1]))
        y += round(78 * u)
        p.unites.append(ligne(fin[2], f_ligne, y, temps[2], GRIS))
        y += round(78 * u)
        p.unites.append(ligne("Karl Forterre", police("fr", 600, round(60 * u)), y, p.bouton, OR, montee=16))
        y += round(120 * u)
        p.unites.append(ligne(fin[3], f_petit, y, p.bouton + 0.25, (190, 190, 196)))
        credit = self.textes.get("credit")
        if credit:
            fc = police(L, 400, round(24 * u))
            lignes_credit = couper_latin(typographie(credit, L).split(" "), fc, M.largeur_texte(), 80)
            yc = y1 - round(24 * u) - (len(lignes_credit) - 1) * round(32 * u)  # au-dessus du bas de la zone sûre
            for i, l in enumerate(lignes_credit):
                p.unites.append(ligne(" ".join(l), fc, yc + i * round(32 * u), p.debut + 0.2, (170, 170, 176), 0))
        p.taille_texte = round(44 * u)
        p.boite_texte = boite_unites(p.unites)
        p.temps_fin = temps

    # -- image finale d'un plan -------------------------------------------------------------
    def image_plan(self, p, t):
        self.preparer(p)
        img = self.base(p, t)
        if p.voile is not None:
            self.voiler(img, p.voile)
        if p.genre == "accroche":
            x, y, w, h = p.regle
            k = sortie((t - 0.0) / 0.45)
            if k > 0:
                img[int(y):int(y + h), int(x):int(x + w * k)] = np.array(OR, np.float32) / 255
        elif p.genre == "lecon":
            x, y, w, h = p.regle
            k = sortie((t - p.debut) / 0.45)
            if k > 0:
                xc = x + w / 2
                img[int(y):int(y + h), int(xc - w * k / 2):int(xc + w * k / 2)] = np.array(OR, np.float32) / 255
        elif p.genre == "fin":
            self.logo(img, p, t)
            x, y, w, h = p.regle
            k = sortie((t - p.t_regle) / 0.4)
            if k > 0:
                xc = x + w / 2
                img[int(y):int(y + h), int(xc - w * k / 2):int(xc + w * k / 2)] = np.array(OR, np.float32) / 255
        for un in p.unites:
            un.poser(img, t)
        return img

    def logo(self, img, p, t):
        barres, lettres, x, y = p.logo
        tl = t - p.debut
        kb = sortie((tl - 0.05) / 0.45)
        kl = sortie((tl - 0.2) / 0.5)
        blanc = np.ones(3, np.float32)
        if kb > 0:  # les deux barres se tracent depuis le centre
            h, w = barres.shape
            demi = int(w * kb / 2)
            m = np.zeros_like(barres)
            m[:, w // 2 - demi:w // 2 + demi] = barres[:, w // 2 - demi:w // 2 + demi]
            coller(img, x, y, m, blanc, 1.0)
        if kl > 0:  # les lettres montent et apparaissent
            coller(img, x, y + int((1 - kl) * 18 * self.M.u), lettres, blanc, kl)


class Habillage:
    """Barre de progression (un segment par photo), compteur « 03 / 08 » et signature.

    Le segment en cours se remplit en doré et brille sur les temps forts ; le compteur
    bascule à chaque changement de photo, donc sur un temps."""

    def __init__(self, M):
        self.M = M
        u = M.u
        L = "fr"
        self.f_compteur = police(L, 600, round(26 * u))
        self.f_sig = police(L, 400, round(23 * u))
        x0, y0, x1, y1 = M.zone()
        self.x0, self.x1 = x0 + round(20 * u), x1 - round(20 * u) if M.fmt != "9x16" else M.W - x0 - round(20 * u)
        self.y = y0 + round(14 * u)
        self.epaisseur = max(2, round(4 * u))
        self.chiffres = {}

    def segments(self):
        M = self.M
        if not hasattr(self, "_segments"):
            seg = {}
            for p in M.plans:
                if p.genre == "recit":
                    a, b = seg.get(p.numero, (p.debut, p.fin))
                    seg[p.numero] = (min(a, p.debut), max(b, p.fin))
            self._segments = [seg[k] for k in sorted(seg)]
            recit = [p for p in M.plans if p.genre == "recit"]
            self.debut, self.fin = recit[0].debut, recit[-1].fin
        return self._segments

    def texte(self, s, f):
        cle = (s, f.size)
        if cle not in self.chiffres:
            x0, y0, x1, y1 = f.getbbox(s, anchor="ls")
            m = Image.new("L", (x1 - x0 + 8, y1 - y0 + 8), 0)
            ImageDraw.Draw(m).text((4 - x0, 4 - y0), s, font=f, fill=255, anchor="ls")
            a = np.asarray(m, np.float32) / 255
            self.chiffres[cle] = (a, np.asarray(m.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255 * 0.5,
                                  x0 - 4, y0 - 4)
        return self.chiffres[cle]

    def poser(self, img, t):
        M, u = self.M, self.M.u
        seg = self.segments()
        vis = lisse((t - self.debut) / 0.3) * (1 - lisse((t - self.fin + 0.3) / 0.3))
        if vis <= 0:
            return
        n = len(seg)
        ecart = round(8 * u)
        largeur = (self.x1 - self.x0 - ecart * (n - 1)) / n
        e = self.epaisseur
        impulsion = M.rythme.impulsion(t, seuil=1.1, decroissance=0.18)
        blanc, dore = np.ones(3, np.float32), np.array(OR, np.float32) / 255
        actif = 0
        for k, (a, b) in enumerate(seg):
            xa = round(self.x0 + k * (largeur + ecart))
            xb = round(xa + largeur)
            zone = img[self.y:self.y + e, xa:xb]
            zone *= 1 - 0.35 * vis
            zone += 0.35 * vis * blanc * 0.85
            if t >= a:
                remp = borne((t - a) / (b - a))
                xr = round(xa + (xb - xa) * remp)
                couleur = blanc if t >= b else dore * (1 - 0.45 * impulsion) + blanc * 0.45 * impulsion
                ep = e + (round(2 * u * impulsion) if t < b else 0)
                z = img[self.y - (ep - e):self.y + e, xa:xr]
                z *= 1 - vis
                z += vis * couleur
                if a <= t < b:
                    actif = k
            elif k == 0:
                actif = 0
        # compteur : ancien numéro qui monte et s'efface, nouveau qui arrive
        yb = self.y + e + round(46 * u)
        total = f" / {n:02d}"
        a_debut = seg[actif][0]
        bascule = sortie((t - a_debut) / 0.28)
        fenetre = (int(yb - 26 * u), int(yb + 6 * u))  # les chiffres défilent dans cette fenêtre
        for num, dy, alpha in ((actif + 1, (1 - bascule) * 30 * u, bascule),
                               (actif, -bascule * 30 * u, 1 - bascule)):
            if num < 1 or alpha <= 0.01:
                continue
            m, o, ox, oy = self.texte(f"{num:02d}", self.f_compteur)
            coller(img, self.x0 + ox, int(yb + oy + dy), m, blanc, alpha * vis, o, fenetre=fenetre)
        m, o, ox, oy = self.texte(total, self.f_compteur)
        xt = self.x0 + self.f_compteur.getlength("00")
        coller(img, int(xt + ox), int(yb + oy), m, np.array([0.85, 0.85, 0.87], np.float32), vis, o)
        m, o, ox, oy = self.texte("© Karl Forterre", self.f_sig)
        xs = self.x1 - self.f_sig.getlength("© Karl Forterre")
        coller(img, int(xs + ox), int(yb + oy), m, blanc, 0.8 * vis, o)

    def boite(self):
        u = self.M.u
        return (self.x0, self.y - round(2 * u), self.x1, self.y + self.epaisseur + round(52 * u))


# --- Enchaînement des plans et rendu -------------------------------------------------------

def image(R, t):
    """Image de la vidéo à l'instant t : plans, transitions, habillage."""
    M = R.M
    plans = M.plans
    # la coupe tombe sur l'image la plus proche du temps musical (à une demi-image près)
    tc = t + 0.5 / FPS
    i = next((k for k, p in enumerate(plans) if p.debut <= tc < p.fin), len(plans) - 1)
    p = plans[i]
    img = None
    # transition d'entrée du plan i (centrée sur la coupe) ou de sortie vers le plan i+1
    for a, b in ((plans[i - 1] if i > 0 else None, p), (p, plans[i + 1] if i + 1 < len(plans) else None)):
        if a is None or b is None or b.entree == "coupe":
            continue
        c, d = b.debut, b.duree_entree
        if b.entree == "noir":
            if c - d <= t < c:
                img = R.image_plan(a, t) * (1 - lisse((t - c + d) / d))
            elif c <= t < c + d * 0.6:
                img = R.image_plan(b, t) * lisse((t - c) / (d * 0.6))
        elif c - d / 2 <= t < c + d / 2:
            s = (t - c + d / 2) / d
            A, B = R.image_plan(a, t), R.image_plan(b, t)
            if b.entree == "fondu":
                k = lisse(s)
                img = A * (1 - k) + B * k
            else:  # glissé : l'ancienne image sort à gauche, la nouvelle entre, flou de bougé
                k = 0.5 - 0.5 * math.cos(math.pi * s)
                x = int(round(k * M.W))
                img = np.concatenate([A[:, x:], B[:, :x]], axis=1) if x else A
                vitesse = math.pi / 2 * math.sin(math.pi * s) * M.W / d / FPS
                img = flou_horizontal(img, int(vitesse * 0.8))
        if img is not None:
            break
    if img is None:
        img = R.image_plan(p, t)
    R.habillage.poser(img, t)
    return img


def flou_horizontal(img, r):
    """Flou de bougé horizontal (moyenne glissante de largeur 2r+1)."""
    if r < 2:
        return img
    c = np.cumsum(np.pad(img, ((0, 0), (r + 1, r), (0, 0)), mode="edge"), axis=1, dtype=np.float32)
    return (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)


def quantifier(img, grain):
    """Image (0 à 1) en octets RGB, avec le grain qui sert aussi de tramage."""
    img *= 255
    img += grain
    np.clip(img, 0, 255, out=img)
    return img.astype(np.uint8).tobytes()


def encoder_cmd(W, H, sortie_muette, debit_k, crf, preset="slow"):
    """H.264 High, 4:2:0, couleurs BT.709 (conversion comprise), 30 images par seconde (règle I3)."""
    return [FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-",
            "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
            "-maxrate", f"{debit_k}k", "-bufsize", f"{2 * debit_k}k",
            "-profile:v", "high", "-level", "4.2", "-x264-params", "aq-mode=3",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
            "-an", "-movflags", "+faststart", sortie_muette]


def liberer(p):
    """Oublie les images d'un plan déjà passé (mémoire)."""
    for attr in ("src", "fond"):
        if hasattr(p, attr):
            setattr(p, attr, None)
    p.pret = False


def rendre(R, sortie_muette, debit_k=5000, crf=19, pas=1, preset="slow"):
    """Calcule toutes les images et les encode (vidéo muette). `pas` > 1 : aperçu rapide."""
    M = R.M
    n = int(round(M.duree * FPS))
    proc = subprocess.Popen(encoder_cmd(M.W, M.H, sortie_muette, debit_k, crf, preset), stdin=subprocess.PIPE)
    precedent = None
    for i in range(n):
        t = i / FPS
        if pas > 1 and i % pas and precedent is not None:
            proc.stdin.write(precedent)
            continue
        precedent = quantifier(image(R, t), R.grain[i % len(R.grain)])
        proc.stdin.write(precedent)
        for p in M.plans:
            if p.pret and p.fin + 1.0 < t:
                liberer(p)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg a échoué pour " + sortie_muette)
    return n


# --- Son -------------------------------------------------------------------------------

def son(musique, debut, duree, bouton, sortie_wav, cible=-14.0, crete=-1.0):
    """Extrait de la musique : départ sur la première note, fin en fondu après le « bouton »,
    volume ramené à −14 LUFS et crêtes sous −1 dBTP (deux passes de loudnorm)."""
    fondu = max(0.8, duree - bouton)
    filtre = (f"aresample=48000,afade=t=in:st=0:d=0.03,"
              f"afade=t=out:st={bouton:.3f}:d={fondu:.3f}:curve=exp")
    brut = sortie_wav.replace(".wav", "-brut.wav")
    subprocess.run([FF, "-y", "-loglevel", "fatal", "-ss", f"{debut:.3f}", "-i", musique, "-t", f"{duree:.3f}",
                    "-ac", "2", "-af", filtre, "-c:a", "pcm_s16le", brut], check=True)
    r = subprocess.run([FF, "-hide_banner", "-i", brut, "-af",
                        f"loudnorm=I={cible}:TP={crete - 0.5}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    mes = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    ln = (f"loudnorm=I={cible}:TP={crete - 0.5}:LRA=11:measured_I={mes['input_i']}:"
          f"measured_TP={mes['input_tp']}:measured_LRA={mes['input_lra']}:"
          f"measured_thresh={mes['input_thresh']}:offset={mes['target_offset']}:linear=true,aresample=48000")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", brut, "-af", ln, "-ar", "48000",
                    "-t", f"{duree:.3f}", "-c:a", "pcm_s16le", sortie_wav], check=True)
    os.remove(brut)


def assembler(muette, wav, sortie):
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", muette, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", sortie], check=True)


# --- Sous-titres, fiche, planche, chronogramme ----------------------------------------------

DEUX_POINTS = {"fr": " : ", "en": ": ", "zh": "："}


def horodatage(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def srt(M, textes, chemin):
    """Fichier de sous-titres (SRT) pour YouTube et Facebook (règle T6)."""
    blocs = []
    acc = M.plans[0]
    blocs.append((0.2, acc.fin, textes["promesse"].replace("\n", " " if M.langue != "zh" else "")))
    for p in M.plans:
        if p.genre == "recit" and p.lignes:
            debut = min(u.t0 for u in p.unites) if p.unites else p.debut
            blocs.append((debut, p.fin, "\n".join(p.lignes)))
        elif p.genre == "lecon":
            for (mot, expl), t in zip(p.entrees, p.apparitions):
                e = "".join(expl) if isinstance(expl, list) else expl
                blocs.append((t, p.fin, f"{mot}{DEUX_POINTS[M.langue]}{e}"))
    fin = textes["fin"]
    appel = f"{fin[2]} Karl Forterre" if M.langue == "zh" else f"{fin[2]}{DEUX_POINTS[M.langue]}Karl Forterre"
    blocs.append((M.plans[-1].debut + 0.3, M.duree, f"Karl Forterre · {fin[1]}\n{appel}"))
    with open(chemin, "w", encoding="utf-8") as f:
        for k, (a, b, texte) in enumerate(blocs, 1):
            f.write(f"{k}\n{horodatage(a)} --> {horodatage(b)}\n{typographie(texte, M.langue)}\n\n")


def fiche(M, R, textes, chemin):
    """Tout ce que le contrôle qualité doit savoir du montage (qualite.py)."""
    plans = []
    for p in M.plans:
        plans.append({
            "genre": p.genre, "debut": round(p.debut, 4), "fin": round(p.fin, 4), "photo": p.photo,
            "numero": p.numero, "cadrage": p.cadrage, "mouvement": p.mouvement, "entree": p.entree,
            "duree_entree": p.duree_entree,
            "lignes": p.lignes if p.genre in ("recit", "accroche") else None,
            "taille_texte": p.taille_texte,
            "boite_texte": [round(v, 1) for v in p.boite_texte] if p.boite_texte else None,
            "contraste": p.contraste, "agrandissement": round(p.agrandissement, 3) if p.agrandissement else None,
            "premier_mot": round(getattr(p, "premier_titre", None) or min(u.t0 for u in p.unites), 3)
            if p.unites else None,
            "sujet": getattr(p, "sujet", None),
        })
    donnees = {
        "format": M.fmt, "largeur": M.W, "hauteur": M.H, "langue": M.langue, "duree": round(M.duree, 4),
        "style": M.style, "zone": M.zone(), "marges": {k: M.m[k] for k in ("haut", "bas", "gauche", "droite")},
        "promesse": textes["promesse"], "surtitre": textes["surtitre"], "tags": textes["tags"],
        "fin": textes["fin"], "credit": textes.get("credit"), "credit_exige": textes.get("credit_exige", False),
        "coupes": [round(p.debut, 4) for p in M.plans[1:]],
        "points": [round(float(x), 4) for x in R.M.rythme.points if 0 <= x <= M.duree + 1],
        "attaques": [round(float(x), 4) for x in R.M.rythme.attaques if 0 <= x <= M.duree + 1],
        "bouton": round(M.bouton, 4), "habillage": R.habillage.boite(), "plans": plans,
    }
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)
    return donnees


def mesurer(R):
    """Mesures pour le contrôle qualité, plan par plan : contraste du texte blanc sur l'image
    là où il est posé (règle T3, WCAG), place du sujet dans l'image (règle R4)."""
    for p in R.M.plans:
        if p.genre == "fin":
            continue
        R.preparer(p)
        if p.cadrage == "plein":
            s = R.sujets[p.photo]
            p.sujet = [R.sujet_a_l_image(p, s, p.duree * k) for k in (0.5, 1.0)]
        if p.boite_texte:  # le plus faible contraste, une fois le texte écrit, jusqu'à la fin du plan
            t0 = min(p.fin - 0.05, max(u.t0 for u in p.unites) + 0.4)
            x0, y0, x1, y1 = (int(v) for v in p.boite_texte)
            contrastes = []
            for t in np.linspace(t0, p.fin - 0.05, 4):
                img = R.base(p, t)
                if p.voile is not None:
                    R.voiler(img, p.voile)
                zone = img[max(0, y0):y1, max(0, x0):x1]
                lum = float(np.percentile(luminance(np.clip(zone, 0, 1)), 90))
                contrastes.append(1.05 / (lum + 0.05))
            p.contraste = round(min(contrastes), 2)
        liberer(p)


def planche(R, chemin, largeur=216):
    """Planche de contrôle : une image au milieu de chaque plan, avec son instant."""
    M = R.M
    h = round(largeur * M.H / M.W)
    n = len(M.plans)
    cols = min(n, 8)
    lignes = (n + cols - 1) // cols
    pl = Image.new("RGB", (cols * (largeur + 6), lignes * (h + 26)), (245, 245, 245))
    d = ImageDraw.Draw(pl)
    for k, p in enumerate(M.plans):
        t = p.debut + 0.75 * p.duree if p.genre != "fin" else M.duree - 0.05
        img = (np.clip(image(R, t), 0, 1) * 255).astype(np.uint8)
        vignette = Image.fromarray(img).resize((largeur, h), Image.LANCZOS)
        x, y = (k % cols) * (largeur + 6), (k // cols) * (h + 26)
        pl.paste(vignette, (x, y))
        d.text((x + 2, y + h + 4), f"{p.debut:5.2f} s · {p.mouvement or p.genre}", fill=(20, 20, 20))
    pl.save(chemin, quality=88)


def chronogramme(M, chemin):
    """Les attaques de la musique, les temps retenus et les coupes : preuve de la synchronisation."""
    Wc, Hc = 1800, 260
    img = Image.new("RGB", (Wc, Hc), (18, 18, 22))
    d = ImageDraw.Draw(img)
    T = M.duree
    X = lambda t: 20 + (Wc - 40) * t / T
    R = M.rythme
    for t in R.attaques:
        if 0 <= t <= T:
            d.line([(X(t), 150), (X(t), 142)], fill=(90, 110, 140))
    for t, pds in zip(R.points, R.poids):
        if 0 <= t <= T:
            d.line([(X(t), 150), (X(t), 150 - 16 * pds)], fill=(150, 170, 200), width=2)
    couleurs = {"accroche": (232, 196, 120), "recit": (90, 150, 220), "lecon": (140, 200, 140), "fin": (200, 120, 160)}
    for p in M.plans:
        d.rectangle([X(p.debut), 170, X(p.fin) - 2, 200], fill=couleurs[p.genre])
        d.text((X(p.debut) + 3, 204), (p.mouvement or p.genre)[:5], fill=(200, 200, 200))
    for p in M.plans[1:]:
        d.line([(X(p.debut), 60), (X(p.debut), 205)], fill=(255, 255, 255))
    d.line([(X(M.bouton), 40), (X(M.bouton), 205)], fill=(232, 196, 120), width=3)
    for s in range(0, int(T) + 1, 5):
        d.text((X(s) - 6, 230), f"{s}s", fill=(160, 160, 160))
    d.text((20, 10), f"{M.fmt} · {M.langue} · style {M.style} · {len(M.plans)} plans · {T:.1f} s "
                     f"(traits bleus : temps et attaques fortes ; blanc : coupes ; doré : dernière note)",
           fill=(230, 230, 230))
    img.save(chemin)


# --- Couverture à part (règle A4) --------------------------------------------------------

def couverture(chemin_photo, sujet, textes, langue, fmt, nb_photos, sortie_jpg):
    """Couverture au style des carrousels : photo en plein cadre, surtitre, titre, mots-clés dorés.

    En 9:16, le texte reste dans le 3:4 central, seule partie visible dans la grille du profil."""
    W, H = (1080, 1440) if fmt == "3x4" else (1080, 1920)
    L = langue
    im = Image.open(chemin_photo).convert("RGB")
    cam = Camera(im.width, im.height, W / H)
    cx, cy = cam.centre_sujet(sujet["centre"], 1.0, 0.34)
    img = np.asarray(im.resize((W, H), Image.LANCZOS, box=cam.boite(cx, cy, 1.0)), np.float32) / 255
    bas_grille = H if fmt == "3x4" else (H + round(W * 4 / 3)) // 2
    y = np.arange(H, dtype=np.float32)[:, None, None]
    debut = bas_grille - 0.62 * round(W * 4 / 3)
    voile = np.clip((y - debut) / (bas_grille - debut), 0, 1) ** 1.3 * 0.92
    haut = (H - round(W * 4 / 3)) // 2 if fmt == "9x16" else 0
    voile = np.maximum(voile, np.clip(1 - (y - haut) / (H * 0.12), 0, 1) * 0.45 * (y >= 0))
    img = img * (1 - voile)
    x = 60
    largeur = W - 2 * x
    bas = "{} 张 · 可在 Pexels 免费下载".format(nb_photos) if L == "zh" else textes.get("bas", "")
    f_bas = police(L, 400, 30)
    f_tags = police(L, 500 if L == "zh" else 600, 32)
    while f_tags.getlength(textes["tags"]) > largeur and f_tags.size > 20:
        f_tags = police(L, 500 if L == "zh" else 600, f_tags.size - 1)
    taille = 88 if L == "zh" else 82
    f_titre = police(L, 700, taille)
    titre = textes["titre_couverture"]
    lignes = titre.split("\n") if "\n" in titre else (repartir(titre.split(" "), f_titre, largeur, 60, 2)
                                                        or [titre])
    while any(f_titre.getlength(l) > largeur for l in lignes):
        taille -= 4
        f_titre = police(L, 700, taille)
    y_bas = bas_grille - 95
    y_tags = y_bas - 118
    pas = round(taille * 1.2)
    y_titre = y_tags - 84 - (len(lignes) - 1) * pas
    y_sur = y_titre - taille - 30
    unites = [Unite(bas, f_bas, x, y_bas, 0, (235, 235, 235)),
              Unite(textes["tags"], f_tags, x, y_tags, 0, OR),
              Unite(textes["surtitre"], police(L, 400, 34), x, y_sur, 0, (238, 238, 238))]
    unites += [Unite(l, f_titre, x, y_titre + k * pas, 0, BLANC) for k, l in enumerate(lignes)]
    unites.append(Unite("KF’   KARL FORTERRE", police("fr", 600, 25), x, haut + 95, 0, BLANC, ombre=0.4))
    for un in unites:
        un.poser(img, 10.0)
    ry = y_sur - 34 - 36
    img[ry:ry + 5, x:x + 66] = np.array(OR, np.float32) / 255
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sortie_jpg, quality=93)
