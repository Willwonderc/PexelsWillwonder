"""Contours de la France, de l'Espagne et des voisins, d'après world-atlas (TopoJSON 50m),
en chemins SVG projetés (Mercator), simplifiés.

Maquettes (étendue d'origine, avec la place des huit premières photos) :
    python3 carte.py countries-50m.json carte.json
Site photo (fond de carte du panneau Wikipédia, avec les noms des mers et des pays en
trois langues ; l'étendue se donne en degrés : ouest, est, sud, nord) :
    python3 carte.py countries-50m.json ../../../vitrine/statique/carte.json --site --etendue -9.8 8.6 41.2 51.4
"""
import argparse, json, math, sys
sys.setrecursionlimit(20000)
options = argparse.ArgumentParser()
options.add_argument("source")
options.add_argument("sortie")
options.add_argument("--site", action="store_true", help="fond de carte du site (statique/carte.json)")
options.add_argument("--etendue", nargs=4, type=float, metavar=("OUEST", "EST", "SUD", "NORD"),
                     default=(-7.6, 8.6, 41.2, 51.4))
args = options.parse_args()
source, sortie = args.source, args.sortie
topo = json.load(open(source, encoding="utf-8"))
sx, sy = topo["transform"]["scale"]
tx, ty = topo["transform"]["translate"]
arcs = []
for arc in topo["arcs"]:
    x = y = 0
    points = []
    for dx, dy in arc:
        x += dx; y += dy
        points.append((x * sx + tx, y * sy + ty))
    arcs.append(points)

def anneau(indices):
    pts = []
    for i in indices:
        a = arcs[i] if i >= 0 else list(reversed(arcs[~i]))
        pts.extend(a if not pts else a[1:])
    return pts

LON0, LON1, LAT0, LAT1 = args.etendue
LARGEUR = 1000.0
def merc(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
ech = LARGEUR / math.radians(LON1 - LON0)
HAUT = (merc(LAT1) - merc(LAT0)) * ech
def proj(lon, lat):
    return ((math.radians(lon - LON0)) * ech, (merc(LAT1) - merc(lat)) * ech)

def rdp(pts, tol):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dmax, imax = 0, 0
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1e-9
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / n
        if d > dmax:
            dmax, imax = d, i
    if dmax > tol:
        return rdp(pts[:imax + 1], tol)[:-1] + rdp(pts[imax:], tol)
    return [pts[0], pts[-1]]

PRINCIPAUX = {"250": "France", "724": "Espagne", "620": "Portugal", "020": "Andorre"}
VOISINS = {"056": "Belgique", "442": "Luxembourg", "276": "Allemagne", "756": "Suisse", "380": "Italie",
           "826": "Royaume-Uni", "528": "Pays-Bas", "492": "Monaco", "438": "Liechtenstein", "040": "Autriche"}
resultat = {"largeur": LARGEUR, "hauteur": round(HAUT, 1), "pays": []}
for geo in topo["objects"]["countries"]["geometries"]:
    gid = str(geo.get("id", "")).zfill(3)
    if gid not in PRINCIPAUX and gid not in VOISINS:
        continue
    polys = geo["arcs"] if geo["type"] == "MultiPolygon" else [geo["arcs"]]
    d = []
    for poly in polys:
        for k, ring in enumerate(poly):
            pts = anneau(ring)
            lons = [p[0] for p in pts]; lats = [p[1] for p in pts]
            if max(lons) < LON0 - 1 or min(lons) > LON1 + 1 or max(lats) < LAT0 - 1 or min(lats) > LAT1 + 1:
                continue
            xy = [proj(lo, la) for lo, la in pts]
            # Anneau fermé : le couper au point le plus éloigné du départ avant de simplifier.
            m = max(range(len(xy)), key=lambda j: math.hypot(xy[j][0] - xy[0][0], xy[j][1] - xy[0][1]))
            xy = rdp(xy[:m + 1], 0.6)[:-1] + rdp(xy[m:], 0.6)
            if len(xy) < 4:
                continue
            d.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in xy) + "Z")
    if d:
        resultat["pays"].append({"id": gid, "nom": PRINCIPAUX.get(gid) or VOISINS[gid], "principal": gid in PRINCIPAUX, "d": "".join(d)})

if args.site:
    # Noms posés sur la carte (longitude, latitude), en français, en anglais et en chinois.
    ETIQUETTES = [
        {"lon": -9.2, "lat": 45.96, "classe": "mer", "fr": ["Océan", "Atlantique"], "en": ["Atlantic", "Ocean"], "zh": ["大西洋"]},
        {"lon": 5.44, "lat": 42.02, "classe": "mer", "milieu": True, "fr": ["Méditerranée"], "en": ["Mediterranean"], "zh": ["地中海"]},
        {"lon": 2.12, "lat": 46.97, "milieu": True, "fr": ["France"], "en": ["France"], "zh": ["法国"]},
        {"lon": -2.74, "lat": 41.65, "milieu": True, "fr": ["Espagne"], "en": ["Spain"], "zh": ["西班牙"]},
    ]
    etiquettes = []
    for e in ETIQUETTES:
        x, y = proj(e["lon"], e["lat"])
        etiquettes.append({"x": round(x), "y": round(y), **{k: v for k, v in e.items() if k not in ("lon", "lat")}})
    site = {
        "source": "Natural Earth (domaine public), via world-atlas 2.0.2 ; tracé par docs/maquettes/panneau-wikipedia/carte.py",
        "projection": "Mercator",
        "etendue": {"lon": [LON0, LON1], "lat": [LAT0, LAT1]},
        "largeur": resultat["largeur"],
        "hauteur": resultat["hauteur"],
        "etiquettes": etiquettes,
        "pays": [{"nom": p["nom"], "principal": p["principal"], "d": p["d"]} for p in resultat["pays"]],
    }
    json.dump(site, open(sortie, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print("hauteur", resultat["hauteur"], "pays", [p["nom"] for p in site["pays"]], "étiquettes", [(e["x"], e["y"]) for e in etiquettes])
    sys.exit()

LIEUX = {
    "39423921": (-1.7889, 43.3381), "39228699": (-5.6130, 43.5250), "39376205": (-0.5747, 44.8452),
    "13087478": (6.5397, 48.3517), "23414381": (-0.4606, 46.3268), "38279508": (-0.4589, 46.3238),
    "39182179": (-0.4600, 43.1370), "34894959": (-1.8237, 48.8738)}
resultat["lieux"] = {k: [round(c, 1) for c in proj(*v)] for k, v in LIEUX.items()}
json.dump(resultat, open(sortie, "w", encoding="utf-8"), ensure_ascii=False)
print("hauteur", round(HAUT, 1), "pays", [p["nom"] for p in resultat["pays"]], "taille", sum(len(p["d"]) for p in resultat["pays"]))
print(resultat["lieux"])
