#!/usr/bin/env python3
"""Palette d'une photo pour la rubrique (version 4A) : 4 couleurs franches de teintes distinctes, tirées de l'image,
chacune avec l'encre lisible posée dessus (contraste ≥ 4,5:1). Usage : python3 palette.py <image.jpeg>  (Pillow requis)
Pour une nouvelle photo : télécharger l'original Pexels, lancer ce script, copier le résultat dans donnees/rubrique-monde.json."""
import collections, json, sys
from PIL import Image, ImageOps

def _lum(c):
    f = lambda v: (v / 255 / 12.92) if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])
def _contraste(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True); return (la + 0.05) / (lb + 0.05)
def palette(chemin):
    """Palette tirée de la photo : 4 couleurs franches, de teintes distinctes, chacune avec l'encre lisible posée dessus."""
    import colorsys
    with Image.open(chemin) as im:
        im = ImageOps.exif_transpose(im).convert("RGB"); im.thumbnail((160, 160))
        q = im.quantize(colors=24, method=Image.Quantize.MEDIANCUT).convert("RGB")
    compte = collections.Counter(q.getdata())
    cand = []
    for c, n in compte.items():
        h, l, s_ = colorsys.rgb_to_hls(*(v / 255 for v in c))
        if s_ > 0.09 and 0.12 < l < 0.9: cand.append((n * (s_ ** 1.2), h, l, s_))
    cand.sort(reverse=True); choix = []
    for _, h, l, s_ in cand:
        if all(min(abs(h - h2), 1 - abs(h - h2)) > 0.06 for h2, _ in choix):
            # La teinte vient de la photo ; on la rend franche (saturation relevée, clarté moyenne), comme sur la maquette.
            s2 = min(0.92, max(0.62, s_ * 1.7)); l2 = min(0.6, max(0.4, l))
            choix.append((h, tuple(round(v * 255) for v in colorsys.hls_to_rgb(h, l2, s2))))
        if len(choix) == 4: break
    if len(choix) < 2:  # photo presque sans couleur (noir et blanc, nuit) : une gamme de gris, du plus sombre au plus clair
        choix = [(0, (g, g, g)) for g in (28, 84, 150, 205)]
    while len(choix) < 4:  # une seule ou deux teintes : on décline la première en plus sombre et plus clair
        h, c = choix[0]; hh, ll, ss = colorsys.rgb_to_hls(*(v / 255 for v in c))
        ll = [0.28, 0.72][len(choix) % 2]; choix.append((h, tuple(round(v * 255) for v in colorsys.hls_to_rgb(hh, ll, ss))))
    out = []
    for _, c in choix:
        # Si ni l'encre ni le blanc n'atteignent 4,5:1 sur la couleur, on l'assombrit un peu (texte des boutons)
        hh, ll, ss = colorsys.rgb_to_hls(*(v / 255 for v in c))
        while max(_contraste(c, (18, 18, 18)), _contraste(c, (255, 255, 255))) < 4.6 and ll > 0.05:
            ll -= 0.03; c = tuple(round(v * 255) for v in colorsys.hls_to_rgb(hh, ll, ss))
        encre = "#121212" if _contraste(c, (18, 18, 18)) >= _contraste(c, (255, 255, 255)) else "#ffffff"
        out.append({"c": "#%02x%02x%02x" % c, "sur": encre, "contraste": round(max(_contraste(c, (18, 18, 18)), _contraste(c, (255, 255, 255))), 2)})
    return out


if __name__ == "__main__":
    print(json.dumps(palette(sys.argv[1]), ensure_ascii=False, indent=1))
