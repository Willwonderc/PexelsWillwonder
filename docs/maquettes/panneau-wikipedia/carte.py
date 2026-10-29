"""Contours de la France, de l'Espagne et des voisins, d'après world-atlas (TopoJSON 50m),
en chemins SVG projetés (Mercator), simplifiés, pour la maquette de l'atlas."""
import json, math, sys
sys.setrecursionlimit(20000)
source, sortie = sys.argv[1], sys.argv[2]
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

LON0, LON1, LAT0, LAT1 = -7.6, 8.6, 41.2, 51.4
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
LIEUX = {
    "39423921": (-1.7889, 43.3381), "39228699": (-5.6130, 43.5250), "39376205": (-0.5747, 44.8452),
    "13087478": (6.5397, 48.3517), "23414381": (-0.4606, 46.3268), "38279508": (-0.4589, 46.3238),
    "39182179": (-0.4600, 43.1370), "34894959": (-1.8237, 48.8738)}
resultat["lieux"] = {k: [round(c, 1) for c in proj(*v)] for k, v in LIEUX.items()}
json.dump(resultat, open(sortie, "w", encoding="utf-8"), ensure_ascii=False)
print("hauteur", round(HAUT, 1), "pays", [p["nom"] for p in resultat["pays"]], "taille", sum(len(p["d"]) for p in resultat["pays"]))
print(resultat["lieux"])
