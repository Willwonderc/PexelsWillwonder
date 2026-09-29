"""Contrôle qualité des vidéos : le cahier des charges de docs/plan-videos.md en tests.

Chaque vidéo du studio est vérifiée dès sa fabrication (studio.py) ; une vidéo en
échec n'est pas livrée (elle part dans sortie/Studio/Refusées/). Le rapport donne une
ligne par règle, lisible sans connaître le programme :

    ✔ réussi   ✘ échec (bloquant)   ! à surveiller (non bloquant)

Sources des mesures : ffmpeg (caractéristiques techniques, volume par le filtre
ebur128) et la fiche du montage écrite par montage.py (plans, coupes, textes,
contrastes, place du sujet).
"""
import os
import re
import subprocess

import imageio_ffmpeg
import numpy as np

import montage
import rythme

FF = imageio_ffmpeg.get_ffmpeg_exe()
MOTS_INTERDITS = {
    "fr": ["photographe français", "photographe francais", "en france, on", "ma fiancée"],
    "tous": ["girondins", "吉伦特"],
}


class Rapport:
    def __init__(self):
        self.lignes = []

    def regle(self, code, ok, texte, bloquant=True):
        self.lignes.append(("✔" if ok else ("✘" if bloquant else "!"), code, texte))

    @property
    def reussi(self):
        return not any(s == "✘" for s, _, _ in self.lignes)

    def texte(self, titre):
        tete = f"Contrôle qualité : {titre}\nRésultat : {'RÉUSSI' if self.reussi else 'ÉCHEC'}\n\n"
        return tete + "\n".join(f"{s} {c:<3} {t}" for s, c, t in self.lignes) + "\n"


def caracteristiques(chemin):
    """Ce que ffmpeg lit du fichier : codec, profil, couleurs, cadence, son, durée."""
    r = subprocess.run([FF, "-hide_banner", "-i", chemin], capture_output=True, text=True).stderr
    v = re.search(r"Video: (.*)", r).group(1)
    a = re.search(r"Audio: (.*)", r)
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).groups()
    return {"video": v, "audio": a.group(1) if a else "", "duree": int(h) * 3600 + int(m) * 60 + float(s)}


def volume(chemin):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", chemin, "-map", "0:a:0", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    resume = r[r.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", resume).group(1))
    tp = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", resume).group(1)
    return i, (-99.0 if tp == "-inf" else float(tp))


def debut_rapide(chemin):
    """Index « moov » avant les données : lecture immédiate en ligne (faststart)."""
    with open(chemin, "rb") as f:
        tete = f.read(4 << 20)
    m, d = tete.find(b"moov"), tete.find(b"mdat")
    return m != -1 and (d == -1 or m < d)


def coupes_mesurees(video, W, H):
    """Coupes franches vues dans la vidéo finie : sauts brusques d'une image à la suivante
    (instant de la première image du nouveau plan ; sauts voisins regroupés)."""
    w, h = 48, round(48 * H / W)
    brut = subprocess.run([FF, "-v", "error", "-i", video, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo",
                           "-"], capture_output=True, check=True).stdout
    img = np.frombuffer(brut, np.uint8).reshape(-1, h, w).astype(np.float32)
    ecarts = np.abs(np.diff(img, axis=0)).mean(axis=(1, 2))
    coupes = []
    for i, e in enumerate(ecarts):
        voisins = np.concatenate([ecarts[max(0, i - 6):i], ecarts[i + 1:i + 7]])
        if e > 10 and e > 4 * (np.median(voisins) + 0.5):
            t = (i + 1) / 30
            if not coupes or t - coupes[-1] > 0.2:
                coupes.append(t)
    return coupes


def decalage_son(video, attaques_prevues):
    """Décalage du son de la vidéo finie par rapport aux attaques prévues (corrélation, ± 0,35 s)."""
    x = rythme.decoder(video, 400)
    env = rythme.enveloppe(rythme.bandes(x)[0])
    ref = np.zeros(len(env))
    for t in attaques_prevues:
        i = int(round((t - rythme.CALAGE) * rythme.IPS))
        if 0 <= i < len(ref):
            ref[i] = 1
    ref = rythme.lisser(ref, 3)
    n = len(env)
    retards = range(-30, 31)
    score = [float(np.dot(env[max(0, r):n + min(0, r)], ref[max(0, -r):n - max(0, r)])) for r in retards]
    return retards[int(np.argmax(score))] / rythme.IPS


def textes_affiches(fiche):
    t = [fiche["promesse"], fiche["surtitre"], fiche["tags"], *fiche["fin"]]
    for p in fiche["plans"]:
        if p["genre"] == "recit" and p["lignes"]:
            t += p["lignes"]
    return t


def verifier(fiche, video, poids_max=29.5e6, apercu=False):
    R = Rapport()
    L, W, H = fiche["langue"], fiche["largeur"], fiche["hauteur"]
    ips = 30
    plans = fiche["plans"]

    # --- image et fichier (I1, I3, poids) ---
    car = caracteristiques(video)
    v = car["video"]
    R.regle("I1", f"{W}x{H}" in v, f"format natif {fiche['format']} ({W} × {H}), sans bandes noires")
    ok = all(x in v for x in ("h264", "High", "yuv420p", "bt709")) and re.search(r"\b30 fps", v) is not None
    R.regle("I3", ok, "H.264 High, 4:2:0, couleurs BT.709, 30 images par seconde"
            + ("" if ok else f" — lu : {v[:120]}"))
    ok = "aac" in car["audio"] and "48000 Hz" in car["audio"]
    R.regle("I3", ok, "son AAC à 48 kHz" + ("" if ok else f" — lu : {car['audio'][:80]}"))
    R.regle("I3", debut_rapide(video), "lecture immédiate en ligne (index en tête du fichier)")
    poids = os.path.getsize(video)
    R.regle("L2", poids <= poids_max, f"poids {poids / 1e6:.1f} Mo (30 Mo au plus pour l'envoi)", not apercu)
    ecart = abs(car["duree"] - fiche["duree"])
    R.regle("A5", ecart < 0.1, f"durée {car['duree']:.1f} s (montage : {fiche['duree']:.1f} s)")
    R.regle("A5", 15 <= fiche["duree"] <= 90, "durée entre 15 et 90 s (Reels, Shorts, RedNote)")

    # --- son (S1, S2, C4) ---
    i, tp = volume(video)
    R.regle("S1", -15.0 <= i <= -13.0, f"volume intégré {i:.1f} LUFS (visé : −14)")
    R.regle("S1", tp <= -1.0, f"crête vraie {tp:.1f} dBTP (−1 au plus)")
    fin = plans[-1]
    R.regle("S2", fin["fin"] - fiche["bouton"] >= 1.0,
            f"fin musicale : dernière note à {fiche['bouton']:.2f} s, "
            f"puis {fin['fin'] - fiche['bouton']:.1f} s de fondu")
    if fiche.get("credit_exige"):
        R.regle("C4", bool(fiche.get("credit")), "crédit de la musique (licence CC BY ou CC BY-SA) sur l'image de fin")

    # --- accroche et structure (A1, A2, A3) ---
    acc = plans[0]
    R.regle("A1", acc["genre"] == "accroche" and acc["cadrage"] == "plein" and acc["mouvement"] is not None,
            "ouverture sur une photo en plein cadre, déjà en mouvement (pas de carton de titre)")
    promesse = fiche["promesse"].replace("\n", " " if L != "zh" else "")
    if L == "zh":
        n = len(re.sub(r"\s", "", promesse))
        R.regle("A2", n <= 14, f"promesse de {n} caractères (14 au plus) : {promesse}")
    else:
        n = len(promesse.split())
        R.regle("A2", n <= 7, f"promesse de {n} mots (7 au plus) : {promesse}")
    R.regle("A2", acc["premier_mot"] is not None and acc["premier_mot"] <= 1.0,
            f"promesse à l'écran dès {acc['premier_mot']:.2f} s (1 s au plus)")
    genres = [p["genre"] for p in plans]
    R.regle("A3", genres[0] == "accroche" and genres[-1] == "fin" and "recit" in genres,
            "structure : accroche, récit" + (", petit cours" if "lecon" in genres else "") + ", fin avec appel")

    # --- rythme et mouvement (R1 à R5) ---
    d_acc = acc["fin"] - acc["debut"]
    R.regle("R1", 1.5 <= d_acc <= 3.7, f"accroche de {d_acc:.2f} s (1,5 à 3,7 s)")
    recits = [p for p in plans if p["genre"] == "recit"]
    durees = [p["fin"] - p["debut"] for p in recits]
    ok = all(1.5 <= x <= 6.0 for x in durees)
    R.regle("R1", ok, f"plans du récit de {min(durees):.1f} à {max(durees):.1f} s (1,5 à 6 s ; moyenne "
                      f"{sum(durees) / len(durees):.1f} s)")
    points = fiche["points"] + fiche["attaques"]
    ecarts = [min(abs(c - p) for p in points) for c in fiche["coupes"]]
    pire = max(ecarts) if ecarts else 0
    R.regle("R2", pire <= 2 / ips, f"{len(ecarts)} coupes prévues sur les temps ou les attaques de la musique "
                                   f"(écart le plus grand : {pire * 1000:.0f} ms, 67 ms au plus)")
    # vérification sur la vidéo finie : son calé sur l'analyse, coupes franches à leur place
    decalage = decalage_son(video, fiche["attaques"])
    vues = coupes_mesurees(video, W, H)
    franches = [p["debut"] for p in plans[1:] if p["entree"] == "coupe"]
    toutes = [p["debut"] for p in plans[1:]]
    imprevues = [t for t in vues if min(abs(t - c) for c in toutes) > 0.3]
    ecarts = [min(abs(t - c) for t in vues) for c in franches if vues]
    ecarts = [e for e in ecarts if e < 0.3]
    pire = max(ecarts) + abs(decalage) if ecarts else abs(decalage)
    R.regle("R2", pire <= 2 / ips + 1e-6 and not imprevues,
            f"mesuré sur la vidéo finie : son décalé de {decalage * 1000:+.0f} ms, {len(ecarts)} coupes franches "
            f"retrouvées, écart total au temps musical {pire * 1000:.0f} ms au plus"
            + (f" — sauts d'image imprévus à {[round(t, 2) for t in imprevues]}" if imprevues else ""),
            bloquant=not apercu)
    mvts = [p["mouvement"] for p in plans if p["genre"] in ("accroche", "recit")]
    doublons = sum(1 for a, b in zip(mvts, mvts[1:]) if a == b)
    R.regle("R3", doublons == 0, f"mouvements variés, jamais deux fois le même de suite "
                                 f"({len(set(mvts))} mouvements différents)")
    hors = []
    for p in plans:
        if p.get("sujet"):
            for (x, y) in p["sujet"]:
                if not (0.04 <= x <= 0.96 and 0.04 <= y <= 0.96):
                    hors.append(f"{p['debut']:.1f} s")
                elif p["boite_texte"]:
                    bx0, by0, bx1, by1 = p["boite_texte"]
                    if bx0 / W <= x <= bx1 / W and by0 / H <= y <= by1 / H:
                        hors.append(f"{p['debut']:.1f} s (sous le texte)")
    R.regle("R4", not hors, "sujet de chaque photo dans l'image et hors du texte"
            + (f" — à revoir : {', '.join(sorted(set(hors)))}" if hors else ""), bloquant=False)
    R.regle("R5", all(p["entree"] in ("coupe", "fondu", "glisse", "noir") for p in plans),
            "transitions choisies : " + ", ".join(sorted({p["entree"] for p in plans[1:]})))

    # --- texte (T1 à T5) ---
    max_car = 16 if L == "zh" else 38
    lignes = [l for p in recits if p["lignes"] for l in p["lignes"]]
    trop = [l for l in lignes if (montage.chasse(l) if L == "zh" else len(l)) > max_car]
    nb = max((len(p["lignes"]) for p in recits if p["lignes"]), default=0)
    R.regle("T1", nb <= 2 and not trop, f"sous-titres de {nb} lignes au plus, {max_car} caractères par ligne au plus"
            + (" (une lettre latine comptant pour moitié)" if L == "zh" else "")
            + (f" — trop longues : {trop[:2]}" if trop else ""))
    vitesse_max = 8 if L == "zh" else 15
    pire = 0.0
    for p in recits:
        if p["lignes"]:
            n = montage.longueur_lecture(" ".join(p["lignes"]), L)
            pire = max(pire, n / (p["fin"] - p["premier_mot"]))
    R.regle("T2", pire <= vitesse_max, f"vitesse de lecture {pire:.1f} caractères par seconde au plus "
                                       f"({vitesse_max} au plus)")
    tailles = [p["taille_texte"] for p in recits if p["taille_texte"]]
    R.regle("T3", min(tailles) >= 0.04 * W, f"sous-titres de {min(tailles)} px (4 % de la largeur : {0.04 * W:.0f} px)")
    contrastes = [(p["contraste"], p["debut"]) for p in plans if p["contraste"]]
    mini = min(contrastes)
    R.regle("T3", mini[0] >= 4.5, f"contraste du texte {mini[0]:.1f} : 1 au plus faible (à {mini[1]:.1f} s ; "
                                  f"4,5 : 1 au moins)")
    x0, y0, x1, y1 = fiche["zone"]
    dehors = [p["debut"] for p in plans if p["boite_texte"] and not (
        p["boite_texte"][0] >= x0 - 1 and p["boite_texte"][1] >= y0 - 1
        and p["boite_texte"][2] <= x1 + 1 and p["boite_texte"][3] <= y1 + 1)]
    hb = fiche["habillage"]
    habillage_ok = hb[1] >= y0 - 1 and hb[3] <= y1 + 1
    R.regle("T4", not dehors and habillage_ok,
            f"textes dans la zone de sécurité ({fiche['marges']['haut']} px en haut, "
            f"{fiche['marges']['bas']} en bas, "
            f"{fiche['marges']['droite']} à droite)" + (f" — hors zone à {dehors}" if dehors else ""))
    affiches = textes_affiches(fiche)
    if L == "fr":
        fautes = [t for t in affiches if "'" in t or '"' in t or re.search(r"\w [:;!?»]", t) or "« " in t]
        R.regle("T5", not fautes, "typographie française : apostrophes ’, guillemets « », espaces insécables"
                + (f" — à revoir : {fautes[:2]}" if fautes else ""))
    elif L == "en":
        fautes = [t for t in affiches if "'" in t or '"' in t]
        R.regle("T5", not fautes, "typographie : apostrophes et guillemets typographiques"
                + (f" — à revoir : {fautes[:2]}" if fautes else ""))
    else:
        fautes = [t for t in affiches if re.search(r"[\u4e00-\u9fff][,.:;!?]", t)]
        R.regle("T5", not fautes, "ponctuation chinoise pleine chasse"
                + (f" — à revoir : {fautes[:2]}" if fautes else ""))
    try:
        tous = affiches + [l for p in plans if p["lignes"] for l in p["lignes"]]
        absents = montage.caracteres_absents("".join(tous), L)
        R.regle("T5", not absents, "tous les caractères existent dans la police"
                + (f" — absents : {''.join(absents)}" if absents else ""))
    except OSError:
        pass
    srt = os.path.splitext(video)[0].replace(" (aperçu)", "") + ".srt"
    R.regle("T6", os.path.exists(srt), "fichier de sous-titres SRT livré à côté de la vidéo")

    # --- marque et conformité (M2, C1, C3, I5) ---
    R.regle("M2", plans[-1]["genre"] == "fin" and bool(fiche["habillage"]),
            "signature « © Karl Forterre » et logo KF’ animé en fin (jamais en ouverture)")
    tout = " ".join(affiches).lower()
    interdits = [m for m in MOTS_INTERDITS["tous"] + MOTS_INTERDITS.get(L, []) if m in tout]
    R.regle("C1", not interdits, "ligne éditoriale : aucun mot interdit"
            + (f" — trouvés : {interdits}" if interdits else "") + " (relecture de Karl avant publication)")
    if L == "zh":
        liens = [t for t in affiches if re.search(r"https?://|www\.|\.com|\.fr", t)]
        R.regle("C3", not liens, "RedNote : aucun lien à l'écran")
    agr = [p["agrandissement"] for p in plans if p["agrandissement"]]
    R.regle("I5", max(agr) <= 1.0, f"photos jamais agrandies au-delà de leur taille réelle "
                                   f"(au plus {max(agr) * 100:.0f} % de leur résolution)")
    return R
