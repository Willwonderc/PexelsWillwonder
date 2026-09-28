#!/usr/bin/python3
# <xbar.title>Vues Pexels</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Karl Forterre</xbar.author>
# <xbar.author.github>Willwonderc</xbar.author.github>
# <xbar.desc>Vues Pexels de Karl Forterre dans la barre des menus, d'après le tableau de bord de photos.karlforterre.fr.</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>
# <xbar.abouturl>https://github.com/Willwonderc/PexelsWillwonder/tree/main/releves/barre-des-menus</xbar.abouturl>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>
"""Compteur des vues Pexels dans la barre des menus du Mac, pour SwiftBar.

Toutes les heures (le « 1h » du nom du fichier), relit le compteur que le site publie chaque
nuit et après chaque relevé, https://photos.karlforterre.fr/tableau-de-bord/compteur.json :
le nombre de vues dans la barre, le détail et les liens au clic. Si le site ne répond pas,
garde la dernière lecture réussie et le dit. Rien à installer : le Python et le curl du Mac
suffisent. Mode d'emploi : releves/barre-des-menus/README.md du dépôt PexelsWillwonder.
"""
import json
import os
import subprocess
from datetime import date
from pathlib import Path

COMPTEUR = "https://photos.karlforterre.fr/tableau-de-bord/compteur.json"
TABLEAU = "https://photos.karlforterre.fr/tableau-de-bord/"
PROFIL = "https://www.pexels.com/@karl-forterre-28489473"
GOATCOUNTER = "https://karlforterre.goatcounter.com"
MOIS = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre")
# Dernière lecture réussie, dans le dossier que SwiftBar réserve à chaque script.
CACHE = Path(os.environ.get("SWIFTBAR_PLUGIN_CACHE_PATH") or Path.home() / "Library/Caches/vues-pexels")


def lire():
    """Le compteur du site, ou None s'il ne répond pas. curl, celui du Mac, gère lui-même les
    certificats du système."""
    try:
        reponse = subprocess.run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--location",
                                  "--max-time", "20", COMPTEUR], capture_output=True, text=True, timeout=30)
        if reponse.returncode == 0:
            return json.loads(reponse.stdout)
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None


def nombre(n):
    """878500 → « 878 500 », avec l'espace fine insécable des nombres en français."""
    return "—" if n is None else f"{n:,}".replace(",", " ")


def jour(texte, annee=True):
    """« 2026-09-24 » ou « 2026-09-24T12:42:00+02:00 » → « 24 septembre 2026 »."""
    try:
        d = date.fromisoformat(texte[:10])
    except (TypeError, ValueError):
        return ""
    return f"{'1er' if d.day == 1 else d.day} {MOIS[d.month - 1]}" + (f" {d.year}" if annee else "")


def afficher(compteur, ancien):
    lignes = []
    pexels = (compteur or {}).get("pexels") or {}
    vues = pexels.get("vues")
    if vues is None:
        lignes += ["Pexels ? | sfimage=eye.slash", "---",
                   "Le tableau de bord ne répond pas ; nouvel essai dans une heure."]
    else:
        lignes += [f"{nombre(vues)} | sfimage=eye", "---"]
        gain = pexels.get("vues_gain")
        ecart = ""
        if gain is not None and pexels.get("vues_gain_depuis"):
            signe = "+" if gain >= 0 else "−"
            ecart = f" ({signe}{nombre(abs(gain))} depuis le {jour(pexels['vues_gain_depuis'], annee=False)})"
        lignes.append(f"Vues sur Pexels : {nombre(vues)}{ecart}")
        for libelle, cle in (("Abonnés", "abonnes"), ("Téléchargements", "telechargements"),
                             ("J'aime", "jaime"), ("Photos retenues", "retenues")):
            if pexels.get(cle) is not None:
                lignes.append(f"{libelle} : {nombre(pexels[cle])}")
        releve = pexels.get("releve") or pexels.get("vues_releve")
        if releve:
            lignes.append(f"Relevé du {jour(releve)} | size=12")
        site = compteur.get("site_7_jours")
        if site:
            lignes += ["---", "Site photo, 7 derniers jours",
                       f"{nombre(site.get('visites'))} visites, {nombre(site.get('clics_pexels'))} clics vers Pexels"]
        if ancien:
            lignes += ["---", "Le tableau de bord ne répond pas : chiffres de la dernière lecture."]
    lignes += ["---",
               f"Ouvrir le tableau de bord | href={TABLEAU}",
               f"Profil Pexels | href={PROFIL}",
               f"GoatCounter | href={GOATCOUNTER}",
               "---",
               "Actualiser | refresh=true"]
    print("\n".join(lignes))


def main():
    fichier = CACHE / "compteur.json"
    compteur = lire()
    ancien = False
    if compteur:
        try:
            CACHE.mkdir(parents=True, exist_ok=True)
            fichier.write_text(json.dumps(compteur, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass
    else:
        try:
            compteur = json.loads(fichier.read_text(encoding="utf-8"))
            ancien = True
        except (OSError, ValueError):
            compteur = None
    afficher(compteur, ancien)


if __name__ == "__main__":
    main()
