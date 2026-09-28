"""Moteur des vidéos diaporama : plans animés, sous-titres, fondus, encodage.

Chaque image est calculée avec Pillow (zoom lent et glissement, sous le pixel), puis
envoyée à ffmpeg qui l'encode en H.264. Les chemins sont relatifs au dossier de
travail (voir fabrique.py) : polices dans polices/.
"""
import os
import subprocess
import sys
from urllib.parse import quote

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FPS = 30
FONDU = 0.6  # secondes de fondu enchaîné entre deux plans

LATIN_SYSTEME = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LATIN = LATIN_SYSTEME if os.path.exists(LATIN_SYSTEME) else "polices/latin.ttf"


def police_google(famille, poids, sortie, texte=None):
    """Police Google Fonts en TTF, réduite aux caractères de `texte` s'il est donné."""
    url = f"https://fonts.googleapis.com/css?family={famille}:{poids}"
    if texte:
        url += "&text=" + quote("".join(sorted(set(texte))))
    css = subprocess.run(["curl", "-sS", url], capture_output=True, text=True, check=True).stdout
    subprocess.run(["curl", "-sS", "-o", sortie, css.split("url(")[1].split(")")[0]], check=True)
    return sortie


def police(nom, taille):
    return ImageFont.truetype("polices/" + nom + ".ttf", taille)


def adoucir(t):
    """Accélération et freinage doux (0 → 1)."""
    return t * t * (3 - 2 * t)


def cadre_rempli(im, W, H):
    """Plus grand cadre au rapport W:H dans la photo, centré : (x0, y0, x1, y1)."""
    w, h = im.size
    if w / h > W / H:
        cw, ch = h * W / H, h
    else:
        cw, ch = w, w * H / W
    return ((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2)


def rogner(c, zoom, dx=0.0, dy=0.0, im=None):
    """Resserre le cadre c d'un facteur zoom et le décale (fractions de la marge libre)."""
    x0, y0, x1, y1 = c
    cw, ch = (x1 - x0) / zoom, (y1 - y0) / zoom
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if im is not None:
        w, h = im.size
        cx += dx * (w - cw) / 2
        cy += dy * (h - ch) / 2
        cx = min(max(cx, cw / 2), w - cw / 2)
        cy = min(max(cy, ch / 2), h - ch / 2)
    return (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)


def interpoler(a, b, t):
    return tuple(p + (q - p) * t for p, q in zip(a, b))


def degrade_bas(W, H, hauteur, opacite):
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    for i in range(hauteur):
        a = int(opacite * (i / hauteur) ** 1.6)
        d.line([(0, H - hauteur + i), (W, H - hauteur + i)], fill=(0, 0, 0, a))
    return calque


def couper(texte, f, largeur):
    """Coupe une phrase en lignes qui tiennent dans la largeur donnée (mot à mot)."""
    lignes, courante = [], ""
    for mot in texte.split():
        essai = (courante + " " + mot).strip()
        if courante and f.getlength(essai) > largeur:
            lignes.append(courante)
            courante = mot
        else:
            courante = essai
    if courante:
        lignes.append(courante)
    return lignes


def sous_titres(W, H, lignes, haut_y=None, langue="zh"):
    """Calque transparent : récit en sous-titres centrés (plusieurs lignes).

    En chinois, `lignes` est une liste de lignes ; en français et en anglais, une phrase
    coupée ici selon la largeur de l'image."""
    calque = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if langue == "zh":
        taille = round(W * 0.046)
        f = police("sous-titre", taille)
    else:
        taille = round(W * 0.043)
        f = ImageFont.truetype(LATIN, taille)
        lignes = couper(lignes, f, W * 0.84)
    for ligne in lignes:
        if f.getlength(ligne) > W * 0.92:
            print("  trop large :", ligne, file=sys.stderr)
    sig = police("legende", round(W * 0.021))
    pas = round(taille * 1.5)
    if haut_y is None:  # plein cadre : bloc posé en bas, sur un dégradé
        calque = Image.alpha_composite(calque, degrade_bas(W, H, round(H * 0.46), 235))
        haut_y = H - round(H * 0.10) - pas * len(lignes)
    texte = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ombre = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, ligne in enumerate(lignes):
        pos = (W / 2, haut_y + pas * i + pas / 2)
        ImageDraw.Draw(ombre).text(pos, ligne, font=f, fill=(0, 0, 0, 210), anchor="mm")
        ImageDraw.Draw(texte).text(pos, ligne, font=f, fill=(255, 255, 255, 252), anchor="mm")
    calque = Image.alpha_composite(calque, ombre.filter(ImageFilter.GaussianBlur(7)))
    calque = Image.alpha_composite(calque, texte)
    marge = round(W * 0.065)
    ImageDraw.Draw(calque).text((W - marge, H - round(H * 0.04)), "© Karl Forterre", font=sig,
                                fill=(255, 255, 255, 170), anchor="rs")
    return calque


class Plan:
    """Un plan du diaporama : une image, sa durée et son mouvement.

    `diapo` : image déjà composée (couverture, cours, fin), montrée entière. Sinon une
    photo : en paysage, entière sur fond flou ; en portrait, plein cadre."""

    def __init__(self, W, H, chemin, duree, diapo=False, lignes=None, langue="zh"):
        self.W, self.H, self.duree = W, H, duree
        im = Image.open(chemin).convert("RGB")
        self.calque = None
        r = im.width / im.height
        if diapo and abs(r - W / H) < 0.01:  # couverture ou fin déjà au bon format
            self.im = im.resize((round(W * 1.1), round(H * 1.1)), Image.LANCZOS)
            c = (0, 0, self.im.width, self.im.height)
            self.debut, self.fin = rogner(c, 1.0), rogner(c, 1.06)
            self.fond = None
            return
        if diapo or r > 1:  # entière sur fond flou, qui grandit doucement
            fond = im.resize((round(W / 4), round(H / 4)), Image.BILINEAR, box=cadre_rempli(im, W, H))
            fond = fond.filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BICUBIC)
            self.fond = Image.blend(fond, Image.new("RGB", (W, H), (18, 18, 20)), 0.45)
            lw = W if diapo else round(W * 0.88)
            self.im = im.resize((round(lw * 1.1), round(lw * 1.1 / r)), Image.LANCZOS)
            self.boite = (lw, round(lw / r))
            c = (0, 0, self.im.width, self.im.height)
            self.debut, self.fin = rogner(c, 1.0), rogner(c, 1.06 if diapo else 1.07)
            y_photo = H // 2 if diapo else round(H * 0.44)
            self.pos = ((W - lw) // 2, y_photo - self.boite[1] // 2)
            bas_photo = y_photo + self.boite[1] // 2
            if lignes:
                self.calque = sous_titres(W, H, lignes, haut_y=bas_photo + round(H * 0.035), langue=langue)
            return
        # portrait ou presque carré : plein cadre, zoom lent et léger glissement
        self.fond = None
        echelle = max(W / im.width, H / im.height) * 1.12
        self.im = im.resize((round(im.width * echelle), round(im.height * echelle)), Image.LANCZOS)
        c = cadre_rempli(self.im, W, H)
        vertical = self.im.height / self.im.width > H / W * 1.05
        glisse = (0, -0.35) if vertical else (-0.35, 0)
        self.debut = rogner(c, 1.0, *glisse, im=self.im)
        self.fin = rogner(c, 1.08, -glisse[0], -glisse[1], im=self.im)
        if lignes:
            self.calque = sous_titres(W, H, lignes, langue=langue)

    def image(self, t):
        """Image du plan à l'instant t (secondes depuis le début du plan)."""
        k = adoucir(min(max(t / self.duree, 0), 1)) * 0.85 + min(max(t / self.duree, 0), 1) * 0.15
        boite = interpoler(self.debut, self.fin, k)
        if self.fond is None:
            img = self.im.transform((self.W, self.H), Image.EXTENT, boite, Image.BICUBIC)
        else:
            img = self.fond.copy()
            img.paste(self.im.transform(self.boite, Image.EXTENT, boite, Image.BICUBIC), self.pos)
        if self.calque is not None:
            img = Image.alpha_composite(img.convert("RGBA"), self.calque).convert("RGB")
        return img


def fabriquer(plans, sortie, W, H, crf=19, debit_max="12M"):
    """Encode les plans enchaînés en fondu ; piste son muette. Rend la durée."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    total = sum(p.duree for p in plans) - FONDU * (len(plans) - 1)
    cmd = [ffmpeg, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-map", "0:v", "-map", "1:a", "-shortest",
           "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-maxrate", debit_max, "-bufsize", "8M", "-profile:v", "high", "-level", "4.2",
           "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
           "-color_trc", "bt709", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", sortie]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    debuts, t0 = [], 0.0
    for p in plans:
        debuts.append(t0)
        t0 += p.duree - FONDU
    n = round(total * FPS)
    for i in range(n):
        t = i / FPS
        actifs = [(p, t - d) for p, d in zip(plans, debuts) if d <= t < d + p.duree]
        img = actifs[0][0].image(actifs[0][1])
        if len(actifs) > 1:  # fondu enchaîné
            p2, t2 = actifs[1]
            img = Image.blend(img, p2.image(t2), min(t2 / FONDU, 1))
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    return total
