"""Rythme d'une musique : temps, accents, premiers temps de mesure et attaques.

    python3 reseaux/videos/rythme.py travail/musiques/lfm-roller-fever.mp3

Méthodes classiques de l'analyse musicale, écrites en numpy : flux spectral
(enveloppe des attaques des notes), tempo par autocorrélation, suivi des temps par
programmation dynamique (D. Ellis, « Beat Tracking by Dynamic Programming », 2007),
puis mesure et premiers temps d'après les accents, surtout ceux des basses. Le
montage coupe sur ces temps (règle R2 de docs/plan-videos.md). Chaque morceau n'est
analysé qu'une fois : le résultat est gardé dans travail/analyses/.
"""
import json
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np

SR = 22050          # fréquence d'échantillonnage de l'analyse
SAUT = 256          # pas d'analyse : 11,6 ms
FENETRE = 1024
IPS = SR / SAUT     # trames d'analyse par seconde
MAX_SECONDES = 200  # les vidéos n'emploient que le début du morceau
CALAGE = 0.028      # avance de la détection, mesurée sur une piste de clics synthétique
VERSION = 3


def decoder(chemin, secondes=MAX_SECONDES):
    """Signal mono, en flottants, des `secondes` premières secondes du morceau."""
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", chemin, "-t", str(secondes),
           "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def bandes(x):
    """Spectre à court terme en 72 bandes logarithmiques (30 Hz à 11 kHz), compressé."""
    n = 1 + (len(x) - FENETRE) // SAUT
    freqs = np.fft.rfftfreq(FENETRE, 1 / SR)
    bords = np.searchsorted(freqs, np.geomspace(30, 11000, 73))
    matrice = np.zeros((len(freqs), 72), np.float32)
    for k in range(72):
        a, b = bords[k], max(bords[k + 1], bords[k] + 1)
        matrice[a:b, k] = 1 / (b - a)
    fenetre = np.hanning(FENETRE).astype(np.float32)
    sortie = np.empty((n, 72), np.float32)
    pas = x.strides[0]
    for a in range(0, n, 2048):
        b = min(n, a + 2048)
        trames = np.lib.stride_tricks.as_strided(x[a * SAUT:], (b - a, FENETRE), (pas * SAUT, pas))
        sortie[a:b] = np.abs(np.fft.rfft(trames * fenetre, axis=1)) @ matrice
    centres = np.sqrt(np.geomspace(30, 11000, 73)[:-1] * np.geomspace(30, 11000, 73)[1:])
    return np.log1p(1000 * sortie), centres


def lisser(v, largeur):
    largeur = max(1, int(largeur))
    return np.convolve(v, np.ones(largeur) / largeur, mode="same")


def enveloppe(spectre, masque=None):
    """Enveloppe des attaques : hausses d'énergie d'une trame à l'autre, moyenne locale ôtée."""
    s = spectre if masque is None else spectre[:, masque]
    flux = np.maximum(0, s[2:] - s[:-2]).mean(axis=1)
    flux = np.concatenate([[0, 0], flux])
    flux = np.maximum(0, flux - lisser(flux, 0.4 * IPS))
    return flux / (flux.std() + 1e-9)


def tempo(env):
    """Période des temps (en trames) par autocorrélation, pondérée autour de 110 BPM."""
    e = env - env.mean()
    n = len(e)
    spectre = np.fft.rfft(e, 2 * n)
    ac = np.fft.irfft(spectre * np.conj(spectre))[:n]
    ac /= ac[0] + 1e-9
    retards = np.arange(int(IPS * 60 / 200), int(IPS * 60 / 45))
    bpm = 60 * IPS / retards
    poids = np.exp(-0.5 * (np.log2(bpm / 110) / 0.9) ** 2)
    k = int(np.argmax(ac[retards] * poids))
    r = retards[k]
    if 0 < k < len(retards) - 1:  # affinage parabolique
        y0, y1, y2 = ac[r - 1], ac[r], ac[r + 1]
        r = r + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
    return float(r), float(ac[retards[k]])


def suivre(env, periode, rigueur=60.0):
    """Suivi des temps par programmation dynamique (Ellis, 2007) : rend les trames des temps."""
    n = len(env)
    local = env - env.mean()
    cumul = local.copy()
    lien = -np.ones(n, int)
    p = periode
    for t in range(int(p / 2), n):
        a, b = max(0, int(t - 2 * p)), int(t - p / 2)
        if b <= a:
            continue
        precedents = np.arange(a, b)
        score = cumul[a:b] - rigueur * np.log((t - precedents) / p) ** 2
        k = int(np.argmax(score))
        cumul[t] = local[t] + score[k]
        lien[t] = precedents[k]
    fin = n - 1 - int(np.argmax(cumul[::-1][: int(p)]))
    temps = [fin]
    while lien[temps[-1]] >= 0:
        temps.append(lien[temps[-1]])
    temps = np.array(temps[::-1])
    # chaque temps se pose sur le sommet d'attaque le plus proche (± 35 ms)
    rayon = int(0.035 * IPS)
    for i, t in enumerate(temps):
        a, b = max(0, t - rayon), min(n, t + rayon + 1)
        temps[i] = a + int(np.argmax(env[a:b]))
    return temps


def sommets(env, seuil=1.0, ecart=0.07):
    """Attaques nettes : maximums locaux de l'enveloppe au-dessus du seuil, espacés de 70 ms."""
    rayon = max(1, int(ecart * IPS))
    idx = [i for i in range(1, len(env) - 1)
           if env[i] >= seuil and env[i] == env[max(0, i - rayon):i + rayon + 1].max()]
    return np.array(idx, int)


def valeur(env, trames, rayon=2):
    return np.array([env[max(0, t - rayon):t + rayon + 1].max() for t in trames])


def mesure(accents, basses):
    """Mesure (3 ou 4 temps) et place du premier temps, d'après les accents réguliers."""
    fort = accents + 1.5 * basses
    meilleur = (4, 0, -1e9)
    for m in (4, 3):
        for phase in range(m):
            sel = np.zeros(len(fort), bool)
            sel[phase::m] = True
            if sel.sum() < 4 or (~sel).sum() < 4:
                continue
            ecart = (fort[sel].mean() - fort[~sel].mean()) / (fort.std() + 1e-9)
            ecart *= 1.0 if m == 4 else 0.92  # à égalité, la mesure à 4 temps, la plus courante
            if ecart > meilleur[2]:
                meilleur = (m, phase, ecart)
    return meilleur[0], meilleur[1], float(meilleur[2])


def analyser(chemin):
    """Analyse complète d'un morceau (temps en secondes depuis le début du fichier)."""
    x = decoder(chemin)
    spectre, centres = bandes(x)
    env = enveloppe(spectre)
    env_basses = enveloppe(spectre, centres < 200)
    periode, clarte = tempo(env)
    temps = suivre(env, periode, rigueur=60.0 if clarte > 0.25 else 25.0)
    accents = valeur(env, temps)
    basses = valeur(env_basses, temps)
    m, phase, nettete = mesure(accents, basses)
    attaques = sommets(env)
    # énergie (décibels) par trame, lissée sur un quart de seconde
    trames = np.concatenate([x, np.zeros(SAUT, np.float32)])[: len(env) * SAUT].reshape(-1, SAUT)
    rms = np.sqrt(lisser((trames.astype(np.float64) ** 2).mean(axis=1), 0.25 * IPS))
    debut = float(attaques[0] / IPS + CALAGE) if len(attaques) else 0.0
    return {
        "version": VERSION,
        "fichier": os.path.basename(chemin),
        "taille": os.path.getsize(chemin),
        "duree": round(len(x) / SR, 3),
        "debut": round(max(0.0, debut - 0.03), 3),
        "tempo": round(60 * IPS / periode, 2),
        "clarte": round(clarte, 3),
        # vif : pulsation nette (pop, danse) ; calme : piano ou cordes, souvent en rubato
        "style": "vif" if clarte >= 0.35 else "calme",
        "mesure": m,
        "nettete_mesure": round(nettete, 3),
        "temps": [round(t / IPS + CALAGE, 4) for t in temps],
        "accents": [round(float(a), 3) for a in accents],
        "basses": [round(float(b), 3) for b in basses],
        "premiers": list(range(phase, len(temps), m)),
        "attaques": [[round(t / IPS + CALAGE, 4), round(float(env[t]), 3), round(float(env_basses[t]), 3)]
                     for t in attaques],
        "energie_db": [round(float(20 * np.log10(v + 1e-6)), 1) for v in rms[:: int(IPS / 10)]],  # tous les 0,1 s
    }


def charger(chemin, dossier="analyses"):
    """Analyse du morceau, lue dans le cache ou calculée puis gardée."""
    os.makedirs(dossier, exist_ok=True)
    cache = os.path.join(dossier, os.path.splitext(os.path.basename(chemin))[0] + ".json")
    if os.path.exists(cache):
        with open(cache) as f:
            a = json.load(f)
        if a.get("version") == VERSION and a.get("taille") == os.path.getsize(chemin):
            return a
    a = analyser(chemin)
    with open(cache, "w") as f:
        json.dump(a, f)
    return a


class Rythme:
    """Points de coupe d'un morceau, en secondes depuis l'instant 0 de la vidéo.

    L'instant 0 est la première attaque du morceau (`debut`). Pulsation nette : les
    coupes se font sur les temps, de préférence les premiers temps et les débuts de
    phrase (toutes les 4 mesures). Pulsation floue (piano en rubato) : sur les attaques
    de notes les plus fortes, basses comprises."""

    def __init__(self, analyse, style=None):
        self.a = analyse
        d = analyse["debut"]
        self.style = style or analyse["style"]
        self.tempo = analyse["tempo"]
        att = np.array(analyse["attaques"], float).reshape(-1, 3)
        self.attaques = att[:, 0] - d
        temps = np.array(analyse["temps"]) - d
        self.temps = temps
        self.periode = float(np.median(np.diff(temps))) if len(temps) > 1 else 0.5
        self.sur_les_temps = analyse["clarte"] >= 0.2
        if self.sur_les_temps:
            acc = np.array(analyse["accents"]) + 0.8 * np.array(analyse["basses"])
            premier = np.zeros(len(temps), bool)
            premier[analyse["premiers"]] = True
            numero = np.cumsum(premier) - 1
            force = np.minimum(acc / (np.percentile(acc, 90) + 1e-9), 1.6)
            bonus = np.where(premier, 0.6 + np.where(numero % 4 == 0, 0.35, np.where(numero % 2 == 0, 0.15, 0)), 0)
            self.points, self.poids = temps, force + bonus
        else:
            fort = att[:, 1] + 0.8 * att[:, 2]
            garde = fort >= np.percentile(fort, 50)
            self.points = self.attaques[garde]
            self.poids = np.minimum(fort[garde] / (np.percentile(fort[garde], 90) + 1e-9), 1.6)
        self.ecart_type = max(self.periode, 0.3)

    def coupe(self, t_min, t_cible, t_max):
        """Meilleur point de coupe entre t_min et t_max, près de t_cible."""
        idx = np.where((self.points >= t_min - 1e-6) & (self.points <= t_max + 1e-6))[0]
        if len(idx) == 0:  # aucun point dans la fenêtre : le plus proche de ses bords
            if not len(self.points):
                return float(t_cible)
            hors = np.where(self.points < t_min, t_min - self.points, self.points - t_max)
            return float(self.points[int(np.argmin(hors))])
        ecart = np.abs(self.points[idx] - t_cible) / self.ecart_type
        return float(self.points[idx[int(np.argmax(self.poids[idx] - 0.45 * ecart))]])

    def fin_de_phrase(self, t_min, t_max):
        """Point d'arrivée pour la fin : le plus fort entre t_min et t_max (premier temps de
        phrase de préférence), sur lequel la musique finit en fondu."""
        idx = np.where((self.points >= t_min) & (self.points <= t_max))[0]
        if len(idx) == 0:
            return self.coupe(t_min, t_min, t_max + 2)
        return float(self.points[idx[int(np.argmax(self.poids[idx]))]])

    def attaque_proche(self, t, rayon=0.08):
        """L'attaque de note la plus proche de t (± rayon), sinon t."""
        if len(self.attaques) == 0:
            return t
        i = int(np.argmin(np.abs(self.attaques - t)))
        return float(self.attaques[i]) if abs(self.attaques[i] - t) <= rayon else t

    def impulsion(self, t, seuil=1.0, decroissance=0.14):
        """Impulsion (0 à 1) des temps forts : 1 sur le temps, puis décroissance rapide."""
        i = int(np.searchsorted(self.points, t, side="right")) - 1
        while i >= 0 and self.poids[i] < seuil:
            i -= 1
        if i < 0 or t - self.points[i] > 6 * decroissance:
            return 0.0
        return float(np.exp(-(t - self.points[i]) / decroissance)) * min(1.0, float(self.poids[i]) / 1.6)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for chemin in sys.argv[1:]:
        a = analyser(chemin)
        print(f"{a['fichier']} : {a['tempo']} BPM, clarté {a['clarte']}, style {a['style']}, "
              f"mesure à {a['mesure']} temps (netteté {a['nettete_mesure']}), début {a['debut']} s, "
              f"{len(a['temps'])} temps, {len(a['attaques'])} attaques")
