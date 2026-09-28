"""Diapositive de carrousel RedNote, au style des carrousels du 27 septembre 2026.

Photo en paysage entière sur fond flou, étape en doré, légende blanche, compteur en
haut à gauche, « © Karl Forterre » en bas à droite ; 1080 × 1440 pixels. Réglages
mesurés sur les images d'origine (écart d'un pixel au plus). Les photos en portrait,
la couverture et l'image de fin ne sont pas encore reproduites (docs/plan-videos.md).

    python3 reseaux/videos/diapositive.py photo.jpg 4 9 "第2站 · 加利西亚（西班牙）" "日全食当晚…" zh sortie.jpg
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from diaporama import police_google  # noqa: E402

POLICES = os.path.join(ICI, "travail", "polices")
ARCHIVO = os.path.join(POLICES, "Archivo.ttf")
NOTO = os.path.join(POLICES, "diapositive-zh.ttf")

W, H = 1080, 1440
DORE = (226, 201, 158)
REGLAGES = {
    "fr": {"etape": 27.8, "legende": 32.2, "interligne": 45, "dy_etape": 73, "dy_legende": 53},
    "zh": {"etape": 28, "legende": 35, "interligne": 50, "dy_etape": 73, "dy_legende": 57},
}


def preparer_polices(textes):
    """Archivo (latin) et Noto Sans SC réduite aux caractères chinois des textes."""
    os.makedirs(POLICES, exist_ok=True)
    if not os.path.exists(ARCHIVO):
        police_google("Archivo", 400, ARCHIVO)
    chinois = "".join(c for c in "".join(textes) if cjk(c))
    if chinois:
        police_google("Noto+Sans+SC", 400, NOTO, chinois)


def cjk(c):
    return ord(c) >= 0x2E80


def polices(taille):
    noto = ImageFont.truetype(NOTO, taille) if os.path.exists(NOTO) else None
    return ImageFont.truetype(ARCHIVO, taille), noto


def longueur(txt, taille):
    fa, fn = polices(taille)
    return sum((fn if cjk(c) else fa).getlength(c) for c in txt)


def ecrire(masque, x, base, txt, taille):
    """Écrit `txt` sur le masque, ligne de base `base` : Archivo, puis Noto Sans SC pour le chinois."""
    fa, fn = polices(taille)
    d = ImageDraw.Draw(masque)
    for c in txt:
        f = fn if cjk(c) else fa
        d.text((x, base), c, font=f, fill=255, anchor="ls")
        x += f.getlength(c)


def couper(txt, taille, largeur):
    if cjk(txt[0]):
        lignes, cur = [], ""
        for c in txt:
            if longueur(cur + c, taille) > largeur:
                lignes.append(cur)
                cur = c
            else:
                cur += c
        return lignes + [cur]
    lignes, cur = [], ""
    for m in txt.split():
        essai = (cur + " " + m).strip()
        if longueur(essai, taille) > largeur and cur:
            lignes.append(cur)
            cur = m
        else:
            cur = essai
    return lignes + [cur]


def cover(im, z=1.1):
    s = max(W / im.width, H / im.height) * z
    w, h = round(im.width * s), round(im.height * s)
    im = im.resize((w, h), Image.LANCZOS)
    return im.crop(((w - W) // 2, (h - H) // 2, (w - W) // 2 + W, (h - H) // 2 + H))


def texte_ombre(fond, masque, couleur, alpha_ombre=0.6, flou=4, dy=2):
    """Colle le texte (masque) avec une ombre portée douce."""
    ombre = ImageChops.offset(masque, 0, dy).filter(ImageFilter.GaussianBlur(flou))
    ombre = ombre.point(lambda v: int(v * alpha_ombre))
    fond = Image.composite(Image.new("RGB", fond.size, (0, 0, 0)), fond, ombre)
    return Image.composite(Image.new("RGB", fond.size, couleur), fond, masque)


def diapo(chemin_photo, numero, total, etape, legende, langue, sortie=None):
    r = REGLAGES[langue]
    preparer_polices([etape, legende])
    photo = Image.open(chemin_photo).convert("RGB")
    # fond : la photo en plein cadre, floutée et assombrie, avec l'ombre portée de la photo
    fond = cover(photo).filter(ImageFilter.GaussianBlur(50)).point(lambda v: v * 0.415)
    pw = 1000
    ph = round(photo.height * pw / photo.width)
    px, py = 40, round(640 - ph / 2)  # photo entière centrée à y = 640
    om = Image.new("L", (W, H), 0)
    ImageDraw.Draw(om).rectangle((px, py + 17, px + pw - 1, py + ph - 1 + 17), fill=255)
    om = om.filter(ImageFilter.GaussianBlur(23)).point(lambda v: int(v * 0.46))
    fond = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), fond, om)
    fond.paste(photo.resize((pw, ph), Image.LANCZOS), (px, py))
    # étape (doré), puis légende (blanc), centrées sous la photo
    m_etape = Image.new("L", (W, H), 0)
    base_etape = py + ph + r["dy_etape"]
    ecrire(m_etape, (W - longueur(etape, r["etape"])) / 2, base_etape, etape, r["etape"])
    m_leg = Image.new("L", (W, H), 0)
    base = base_etape + r["dy_legende"]
    for ligne in couper(legende, r["legende"], 920):
        ecrire(m_leg, (W - longueur(ligne, r["legende"])) / 2, base, ligne, r["legende"])
        base += r["interligne"]
    # compteur et signature
    m_blanc = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m_blanc)
    d.text((56, 74), f"{numero:02d} / {total:02d}", font=ImageFont.truetype(ARCHIVO, 26), fill=255, anchor="ls")
    d.text((1041, 1409), "© Karl Forterre", font=ImageFont.truetype(ARCHIVO, 23.8), fill=255, anchor="rs")
    img = texte_ombre(fond, m_etape, DORE)
    img = texte_ombre(img, m_leg, (255, 255, 255))
    img = texte_ombre(img, m_blanc, (255, 255, 255))
    if sortie:
        img.save(sortie, quality=90, subsampling=0)
    return img


if __name__ == "__main__":
    if len(sys.argv) != 8:
        sys.exit(__doc__)
    chemin, numero, total, etape, legende, langue, sortie = sys.argv[1:]
    diapo(chemin, int(numero), int(total), etape, legende, langue, sortie)
    print(sortie)
