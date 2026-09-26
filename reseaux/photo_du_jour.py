#!/usr/bin/env python3
"""Publie la « photo du jour » sur Bluesky et sur Mastodon (ou Pixelfed).

Chaque matin, la tâche .github/workflows/photo-du-jour.yml publie sur chaque réseau
l'image d'une photo, son titre, quelques mots-clés en hashtags et le lien vers sa page
du site. Les photos passent des plus vues aux moins vues sur Pexels (fiche de suivi) ;
le journal reseaux/photo-du-jour.json note, réseau par réseau, les photos publiées et
leur date : aucune ne l'est deux fois, et un réseau ne reçoit qu'une photo par jour.

Accès, lus dans les variables d'environnement (secrets du dépôt dans GitHub Actions) :
  BLUESKY_IDENTIFIANT, BLUESKY_MOT_DE_PASSE_APPLI   pour Bluesky
  MASTODON_INSTANCE, MASTODON_JETON                 pour Mastodon ou Pixelfed
Un réseau sans ses accès est laissé de côté, sans erreur.

Options :
  --essai     affiche les publications du jour sans rien publier ni enregistrer
  --langue L  langue des publications (fr, en ou zh), à la place du réglage de site.ini
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / "vitrine"))
import build  # noqa: E402  (fonctions du site : fiches, textes, fiche de suivi, adresses)

JOURNAL = ICI / "photo-du-jour.json"
AUJOURDHUI = datetime.now(timezone.utc).date().isoformat()
AGENT = "photo-du-jour-karl-forterre"
# Bluesky refuse les images de plus de 1 000 000 d'octets : Pexels les fournit
# compressées, à la plus grande de ces largeurs qui reste sous la limite.
LARGEURS = (2048, 1600, 1280, 1024)
POIDS_MAX = 950_000
BLUESKY_SERVICE = "https://bsky.social"
BLUESKY_LONGUEUR = 300  # caractères au plus dans une publication Bluesky
HASHTAGS = 4

TEXTES = {
    "fr": "Libre de droits, à télécharger gratuitement sur Pexels :",
    "en": "Royalty-free, free to download on Pexels:",
    "zh": "免版税，可在 Pexels 免费下载：",
}


# ---------------------------------------------------------------- choix et texte


def lire_photos():
    """Photos publiées sur le site, des plus vues aux moins vues sur Pexels."""
    ids = build.lire_photos()
    anglais, francais = build.lire_textes()
    photos, _ = build.assembler_photos(ids, build.charger_fiches(), anglais, francais,
                                       build.lire_suivi(), build.lire_traductions("zh"))
    return sorted(photos, key=lambda p: (-p["vues"], -p["id"]))


def charger_journal():
    if JOURNAL.exists():
        return json.loads(JOURNAL.read_text(encoding="utf-8"))
    return {}


def enregistrer_journal(journal):
    JOURNAL.write_text(json.dumps(journal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def hashtag(mot):
    """« crescent moon » → « CrescentMoon » ; « coucher de soleil » → « CoucherDeSoleil »."""
    morceaux = re.split(r"[\W_]+", mot)
    tag = "".join(m[:1].upper() + m[1:] for m in morceaux if m)
    return tag if tag and not tag.isdigit() and len(tag) <= 30 else ""


def hashtags(photo, langue):
    """Les premiers mots-clés de la photo, sans les mots d'ambiance ni les doublons."""
    tags, vus = [], set()
    for mot in photo["mots"][langue]:
        tag = hashtag(mot)
        if tag and build.cle_mot(mot) not in build.MOTS_VAGUES and tag.lower() not in vus:
            tags.append(tag)
            vus.add(tag.lower())
        if len(tags) == HASHTAGS:
            break
    return tags


def composer(photo, langue, lien, tags):
    return f'{photo["titre"][langue]}\n\n{TEXTES[langue]} {lien}\n\n' + " ".join("#" + t for t in tags)


def publication(photo, langue, adr, longueur=None):
    """Texte, lien et hashtags d'une publication ; avec « longueur », des hashtags sont
    retirés, puis le titre raccourci, jusqu'à tenir dans la limite du réseau."""
    lien = adr.absolue(adr.chemin(langue, "photo", photo["id"]))
    tags = hashtags(photo, langue)
    texte = composer(photo, langue, lien, tags)
    while longueur and len(texte) > longueur and tags:
        tags.pop()
        texte = composer(photo, langue, lien, tags)
    if longueur and len(texte) > longueur:
        exces = len(texte) - longueur
        titre = build.tronquer(photo["titre"][langue], len(photo["titre"][langue]) - exces)
        texte = f"{titre}\n\n{TEXTES[langue]} {lien}"
    return texte, lien, tags


def photo_suivante(photos, parues):
    return next((p for p in photos if str(p["id"]) not in parues), None)


# ---------------------------------------------------------------- appels HTTP


def appel(methode, adresse, donnees=None, entetes=None, delai=60):
    """Requête HTTP ; renvoie la réponse JSON (ou les octets bruts pour une image)."""
    entetes = {"User-Agent": AGENT, **(entetes or {})}
    if isinstance(donnees, (dict, list)):
        donnees = json.dumps(donnees).encode("utf-8")
        entetes.setdefault("Content-Type", "application/json")
    requete = urllib.request.Request(adresse, data=donnees, headers=entetes, method=methode)
    try:
        with urllib.request.urlopen(requete, timeout=delai) as reponse:
            corps = reponse.read()
            if "json" in (reponse.headers.get("Content-Type") or ""):
                return json.loads(corps or b"{}")
            return corps
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"{methode} {adresse} : erreur {erreur.code} {detail}") from None


def telecharger_image(photo):
    """Image JPEG de la photo, servie par Pexels, sous la limite de poids de Bluesky."""
    for largeur in LARGEURS:
        image = appel("GET", build.url_image(photo, largeur))
        if len(image) <= POIDS_MAX:
            return image
    raise RuntimeError(f"Photo {photo['id']} : image trop lourde, même en {LARGEURS[-1]} pixels de large.")


def formulaire(champs, fichier):
    """Corps multipart/form-data : des champs texte et un fichier « file »."""
    limite = uuid.uuid4().hex
    corps = b""
    for nom, valeur in champs.items():
        corps += (f'--{limite}\r\nContent-Disposition: form-data; name="{nom}"\r\n\r\n{valeur}\r\n').encode("utf-8")
    corps += (f'--{limite}\r\nContent-Disposition: form-data; name="file"; filename="photo.jpg"\r\n'
              "Content-Type: image/jpeg\r\n\r\n").encode("utf-8") + fichier + f"\r\n--{limite}--\r\n".encode("utf-8")
    return corps, f"multipart/form-data; boundary={limite}"


# ---------------------------------------------------------------- Bluesky


def facettes(texte, lien, tags):
    """Liens et hashtags cliquables d'une publication Bluesky, repérés en octets UTF-8."""
    octets = texte.encode("utf-8")
    trouvees = []

    def reperer(morceau, caracteristique, depuis=0):
        debut = octets.find(morceau.encode("utf-8"), depuis)
        if debut >= 0:
            fin = debut + len(morceau.encode("utf-8"))
            trouvees.append({"index": {"byteStart": debut, "byteEnd": fin}, "features": [caracteristique]})
            return fin
        return depuis

    fin_lien = reperer(lien, {"$type": "app.bsky.richtext.facet#link", "uri": lien})
    for tag in tags:
        fin_lien = reperer("#" + tag, {"$type": "app.bsky.richtext.facet#tag", "tag": tag}, fin_lien)
    return trouvees


def publier_bluesky(photo, image, langue, adr, acces):
    identifiant, mot_de_passe = acces
    session = appel("POST", f"{BLUESKY_SERVICE}/xrpc/com.atproto.server.createSession",
                    {"identifier": identifiant, "password": mot_de_passe})
    # Le serveur qui héberge le compte (PDS), indiqué par la session ; bsky.social sinon.
    service = next((s.get("serviceEndpoint") for s in (session.get("didDoc") or {}).get("service", [])
                    if s.get("id") == "#atproto_pds"), None) or BLUESKY_SERVICE
    auth = {"Authorization": f'Bearer {session["accessJwt"]}'}
    blob = appel("POST", f"{service}/xrpc/com.atproto.repo.uploadBlob", image,
                 {**auth, "Content-Type": "image/jpeg"})["blob"]
    texte, lien, tags = publication(photo, langue, adr, BLUESKY_LONGUEUR)
    enregistrement = {
        "$type": "app.bsky.feed.post",
        "text": texte,
        "facets": facettes(texte, lien, tags),
        "langs": [langue],
        "createdAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "embed": {
            "$type": "app.bsky.embed.images",
            "images": [{
                "alt": photo["titre"][langue],
                "image": blob,
                "aspectRatio": {"width": photo["largeur"], "height": photo["hauteur"]},
            }],
        },
    }
    resultat = appel("POST", f"{service}/xrpc/com.atproto.repo.createRecord",
                     {"repo": session["did"], "collection": "app.bsky.feed.post", "record": enregistrement}, auth)
    return f'https://bsky.app/profile/{session.get("handle") or session["did"]}/post/{resultat["uri"].rsplit("/", 1)[-1]}'


# ---------------------------------------------------------------- Mastodon et Pixelfed


def instance(texte):
    """« mastodon.social », « https://pixelfed.social/ » → « https://… » sans barre finale."""
    texte = texte.strip().rstrip("/")
    return texte if texte.startswith(("https://", "http://")) else "https://" + texte


def publier_mastodon(photo, image, langue, adr, acces):
    serveur, jeton = instance(acces[0]), acces[1]
    auth = {"Authorization": f"Bearer {jeton}"}
    texte, _, _ = publication(photo, langue, adr)
    corps, type_corps = formulaire({"description": photo["titre"][langue]}, image)
    try:
        media = appel("POST", f"{serveur}/api/v2/media", corps, {**auth, "Content-Type": type_corps}, delai=120)
    except RuntimeError as erreur:
        if " erreur 404 " not in str(erreur):
            raise
        # Instances qui ne connaissent que l'ancienne adresse (certaines Pixelfed).
        media = appel("POST", f"{serveur}/api/v1/media", corps, {**auth, "Content-Type": type_corps}, delai=120)
    # Mastodon peut préparer l'image en arrière-plan : attendre qu'elle soit prête.
    for _ in range(10):
        if media.get("url"):
            break
        time.sleep(3)
        media = appel("GET", f'{serveur}/api/v1/media/{media["id"]}', entetes=auth)
    statut = appel("POST", f"{serveur}/api/v1/statuses",
                   {"status": texte, "media_ids": [str(media["id"])], "language": langue, "visibility": "public"},
                   {**auth, "Idempotency-Key": f'photo-du-jour-{photo["id"]}-{AUJOURDHUI}'})
    return statut.get("url") or statut.get("uri") or ""


# ---------------------------------------------------------------- programme


RESEAUX = {
    "bluesky": ("Bluesky", ("BLUESKY_IDENTIFIANT", "BLUESKY_MOT_DE_PASSE_APPLI"), publier_bluesky, BLUESKY_LONGUEUR),
    "mastodon": ("Mastodon", ("MASTODON_INSTANCE", "MASTODON_JETON"), publier_mastodon, None),
}


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("--essai", action="store_true")
    options.add_argument("--langue", choices=build.LANGUES)
    args = options.parse_args()

    reglages = build.lire_ini("site.ini")
    langue = args.langue or reglages.get("photo_du_jour", "langue", fallback="en").strip() or "en"
    if langue not in build.LANGUES:
        sys.exit(f"Langue inconnue dans site.ini, rubrique [photo_du_jour] : {langue} (fr, en ou zh).")
    adr = build.Adresses(reglages["site"]["adresse"])
    photos = lire_photos()
    journal = charger_journal()
    images = {}
    echecs = 0

    for cle, (nom, variables, publier, longueur) in RESEAUX.items():
        acces = [os.environ.get(v, "").strip() for v in variables]
        parues = journal.get(cle, {})
        if not args.essai and not all(acces):
            print(f"{nom} : accès non renseignés ({', '.join(variables)}), rien à publier.")
            continue
        if any(entree["date"] == AUJOURDHUI for entree in parues.values()):
            print(f"{nom} : photo du jour déjà publiée aujourd'hui.")
            continue
        photo = photo_suivante(photos, parues)
        if not photo:
            print(f"{nom} : toutes les photos ont déjà été publiées.")
            continue
        if args.essai:
            texte = publication(photo, langue, adr, longueur)[0]
            print(f"--- {nom} : photo {photo['id']} ({photo['vues']} vues, {len(texte)} caractères)\n{texte}\n")
            continue
        try:
            if photo["id"] not in images:
                images[photo["id"]] = telecharger_image(photo)
            lien = publier(photo, images[photo["id"]], langue, adr, acces)
        except (RuntimeError, OSError, KeyError, ValueError) as erreur:
            echecs += 1
            print(f"{nom} : échec de la publication de la photo {photo['id']} : {erreur}")
            continue
        journal.setdefault(cle, {})[str(photo["id"])] = {"date": AUJOURDHUI, "lien": lien}
        enregistrer_journal(journal)
        print(f"{nom} : photo {photo['id']} publiée, {lien}")

    for cle, (nom, _, _, _) in RESEAUX.items():
        print(f"{nom} : {len(journal.get(cle, {}))} photos publiées depuis le début, "
              f"{sum(1 for p in photos if str(p['id']) not in journal.get(cle, {}))} à venir.")
    if echecs:
        sys.exit(1)


if __name__ == "__main__":
    main()
