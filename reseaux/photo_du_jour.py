#!/usr/bin/env python3
"""Publie la « photo du jour » sur Bluesky, sur Mastodon (ou Pixelfed) et sur Instagram.

Chaque matin, la tâche .github/workflows/photo-du-jour.yml publie sur chaque réseau
l'image d'une photo, un texte et le lien vers sa page du site (sur Instagram, dont les
légendes n'ont pas de liens cliquables, un renvoi vers le lien de la biographie). Le
journal reseaux/photo-du-jour.json note, réseau par réseau, les photos publiées et leur
date. Un réseau ne reçoit qu'une photo par jour, et une photo n'y revient qu'après un
long délai (réglage rediffusion_jours de site.ini).

Les textes sont écrits à l'avance, dans le style de Karl (reseaux/style-karl.md), par la
session programmée du 26 de chaque mois (consigne M) :
  - reseaux/calendrier.csv, pour Bluesky et Mastodon : chaque jour, la photo, la langue
    choisie selon l'audience (français ou anglais) et le texte. Sur Bluesky, le lien part
    en réponse sous la photo, à la manière de la communauté #UnJourUnePhoto ; sur
    Mastodon, il suit le texte, avant les hashtags de fin ;
  - reseaux/legendes-instagram.csv, pour Instagram, toujours en français.
Un jour sans texte écrit, la photo la plus vue pas encore publiée part avec un texte
automatique (hashtags et titre).

Accès, lus dans les variables d'environnement (secrets du dépôt dans GitHub Actions) :
  BLUESKY_IDENTIFIANT, BLUESKY_MOT_DE_PASSE_APPLI   pour Bluesky
  MASTODON_INSTANCE, MASTODON_JETON                 pour Mastodon ou Pixelfed
  INSTAGRAM_JETON                                   pour Instagram
Un réseau sans ses accès est laissé de côté, sans erreur.

Options :
  --essai             affiche les publications du jour sans rien publier ni enregistrer
  --langue L          langue des publications (fr, en ou zh), à la place du réglage de site.ini
  --renouveler-jeton  renouvelle le jeton Instagram, valable 60 jours, et range le nouveau
                      dans le secret INSTAGRAM_JETON du dépôt (tâche « Jeton Instagram »)
  --a-venir N         liste les N prochaines photos de la file d'un réseau (--reseau,
                      Instagram par défaut) : pour Instagram, dans l'ordre de parution, avec
                      l'état de leur légende ; pour Bluesky et Mastodon, les photos que le
                      calendrier n'a pas encore prévues, des plus vues aux moins vues
  --reseau R          avec --a-venir : bluesky, mastodon ou instagram
  --jour AAAA-MM-JJ   avec --essai : les publications de ce jour-là (calendrier compris) ;
                      avec --calendrier ou --a-venir : à partir de ce jour-là
  --calendrier        vérifie le calendrier à venir : une ligne par jour et par réseau,
                      photo, langue, longueur, délai de rediffusion
"""

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

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
MASTODON_LONGUEUR = 500  # caractères au plus sur mastodon.social, où un lien compte pour 23
MASTODON_LIEN = 23
HASHTAGS = 4
# Hashtag ajouté en tête de chaque publication, en plus des mots-clés : un sujet très
# suivi sur Mastodon et Bluesky.
HASHTAG_FIXE = {"fr": "Photographie", "en": "Photography", "zh": "摄影"}
# Bluesky en français, les jours sans texte écrit : les hashtags de la communauté plutôt
# que des mots-clés. Mesuré le 30 septembre 2026 sur les 100 derniers messages de chacun
# (reseaux/audience.md) : #UnJourUnePhoto, 65 messages par jour, 14 « j'aime » en médiane,
# 91 % en français ; #FleurisTonFil (fleurs), 15 en médiane ; #NoirEtBlanc, 8 ; contre 0 à 4
# pour des mots-clés comme #Train ou #France. Les messages les plus aimés de la communauté
# ajoutent #Photography.
HASHTAGS_BLUESKY = ("UnJourUnePhoto", "Photography")
# Hashtag de communauté ajouté quand un mot-clé français de la photo contient l'un de ces mots.
COMMUNAUTES_BLUESKY = (
    ("FleurisTonFil", ("fleur", "floraison", "tulipe", "pivoine", "coquelicot", "lavande",
                       "hortensia", "marguerite", "orchidée", "magnolia", "dahlia", "tournesol",
                       "glycine", "camélia", "lilas", "bouquet")),
    ("NoirEtBlanc", ("noir et blanc", "monochrome")),
)
# Calendrier : jour et réseau → photo, langue et texte, écrit chaque mois en session.
CALENDRIER = ICI / "calendrier.csv"
RESEAUX_CALENDRIER = ("bluesky", "mastodon")
# Délai avant qu'une photo revienne sur un même réseau, si site.ini ne dit rien.
REDIFFUSION_JOURS = 180

TEXTES = {
    "fr": "Libre de droits, à télécharger gratuitement sur Pexels :",
    "en": "Royalty-free, free to download on Pexels:",
    "zh": "免版税，可在 Pexels 免费下载：",
}

# Instagram (API avec connexion Instagram, documentation de Meta vérifiée le 28 septembre
# 2026) : image JPEG qu'Instagram télécharge lui-même à une adresse publique, de 320 à
# 1440 pixels de large, rapport largeur/hauteur de 4:5 à 1,91:1 ; 100 publications par
# 24 heures au plus ; 5 hashtags au plus par publication depuis décembre 2025.
INSTAGRAM_API = "https://graph.instagram.com/v25.0"
INSTAGRAM_RENOUVELLEMENT = "https://graph.instagram.com/refresh_access_token"
INSTAGRAM_LARGEUR = 1440
INSTAGRAM_RAPPORT_MIN = 4 / 5
INSTAGRAM_RAPPORT_MAX = 1.91
INSTAGRAM_HASHTAGS = 5
TEXTES_INSTAGRAM = {
    "fr": "Libre de droits, à télécharger gratuitement sur Pexels : lien dans la bio.",
    "en": "Royalty-free, free to download on Pexels: link in bio.",
    "zh": "免版税，可在 Pexels 免费下载：链接见主页简介。",
}
# Instagram est toujours en français, dans le style de Karl (reseaux/style-karl.md) :
# légendes écrites à l'avance, une par photo ; sans légende prête, le titre français.
LEGENDES_INSTAGRAM = ICI / "legendes-instagram.csv"


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
    """Le hashtag fixe, puis les premiers mots-clés de la photo, sans les mots d'ambiance
    ni les doublons."""
    fixe = HASHTAG_FIXE.get(langue, "")
    tags, vus = ([fixe], {fixe.lower()}) if fixe else ([], set())
    for mot in photo["mots"][langue]:
        tag = hashtag(mot)
        if tag and build.cle_mot(mot) not in build.MOTS_VAGUES and tag.lower() not in vus:
            tags.append(tag)
            vus.add(tag.lower())
        if len(tags) == HASHTAGS + bool(fixe):
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


def jours_entre(debut, fin):
    return (datetime.fromisoformat(fin).date() - datetime.fromisoformat(debut).date()).days


def rediffusable(parues, photo_id, jour, delai):
    """Vrai si la photo n'est jamais parue sur ce réseau, ou il y a au moins « delai » jours."""
    entree = parues.get(str(photo_id))
    return not entree or jours_entre(entree["date"], jour) >= delai


def photo_suivante(photos, parues, reservees=(), jour=AUJOURDHUI, delai=REDIFFUSION_JOURS):
    """La plus vue des photos jamais publiées sur ce réseau, hors photos réservées par le
    calendrier ; quand toutes l'ont été, la plus anciennement publiée, si elle l'a été il y
    a au moins « delai » jours."""
    libres = [p for p in photos if str(p["id"]) not in reservees]
    neuve = next((p for p in libres if str(p["id"]) not in parues), None)
    if neuve:
        return neuve
    anciennes = [p for p in libres if rediffusable(parues, p["id"], jour, delai)]
    return min(anciennes, key=lambda p: parues[str(p["id"])]["date"], default=None)


def noter_publication(journal, cle, photo_id, lien):
    """Inscrit la publication du jour ; une rediffusion garde la trace des précédentes."""
    reseau = journal.setdefault(cle, {})
    ancienne = reseau.get(str(photo_id))
    entree = {"date": AUJOURDHUI, "lien": lien}
    if ancienne:
        entree["precedentes"] = ancienne.get("precedentes", []) + [
            {"date": ancienne["date"], "lien": ancienne.get("lien", "")}]
    reseau[str(photo_id)] = entree


def lignes_calendrier():
    """Lignes du calendrier : date (AAAA-MM-JJ), reseau, photo, langue, theme, texte."""
    if not CALENDRIER.exists():
        return []
    with CALENDRIER.open(encoding="utf-8", newline="") as fichier:
        return [{cle: (valeur or "").strip() for cle, valeur in ligne.items() if cle}
                for ligne in csv.DictReader(fichier) if (ligne.get("date") or "").strip()]


def lire_calendrier():
    """Calendrier des publications : (date, réseau) → ligne (photo, langue, texte…)."""
    return {(ligne["date"], ligne.get("reseau") or "bluesky"): ligne for ligne in lignes_calendrier()}


def texte_ecrit(entree):
    """Texte d'une ligne du calendrier, où « \\n » marque un retour à la ligne."""
    return (entree or {}).get("texte", "").replace("\\n", "\n")


def hashtags_communaute(photo):
    """#UnJourUnePhoto, #Photographie, et le hashtag de communauté qui convient à la photo."""
    tags = list(HASHTAGS_BLUESKY)
    mots = [m.lower() for m in photo["mots"]["fr"]]
    for tag, termes in COMMUNAUTES_BLUESKY:
        if any(terme in mot for mot in mots for terme in termes):
            tags.append(tag)
    return tags


def textes_bluesky(photo, langue, adr, entree=None):
    """Texte de la publication Bluesky et texte de la réponse qui porte le lien : la
    publication elle-même reste celle d'un membre de la communauté, sans lien. Un jour du
    calendrier, son texte remplace le texte automatique."""
    lien = adr.absolue(adr.chemin(langue, "photo", photo["id"]))
    if texte_ecrit(entree):
        return texte_ecrit(entree), f"{TEXTES[langue]} {lien}"
    if langue != "fr":
        return publication(photo, langue, adr, BLUESKY_LONGUEUR)[0], None
    texte = " ".join("#" + t for t in hashtags_communaute(photo)) + "\n\n" + photo["titre"]["fr"]
    return texte, f"{TEXTES['fr']} {lien}"


def texte_mastodon(photo, langue, adr, entree=None):
    """Texte Mastodon : celui du calendrier, suivi du lien vers la page de la photo, placé
    avant le paragraphe final de hashtags s'il y en a un ; sinon, le texte automatique."""
    if not texte_ecrit(entree):
        return publication(photo, langue, adr)[0]
    lien = f'{TEXTES[langue]} {adr.absolue(adr.chemin(langue, "photo", photo["id"]))}'
    blocs = texte_ecrit(entree).split("\n\n")
    fin = blocs[-1].split()
    if len(blocs) > 1 and fin and all(mot.startswith("#") for mot in fin):
        blocs.insert(len(blocs) - 1, lien)
    else:
        blocs.append(lien)
    return "\n\n".join(blocs)


def longueur_mastodon(texte):
    """Longueur comptée par Mastodon, où chaque lien vaut 23 caractères."""
    return len(LIEN.sub("x" * MASTODON_LIEN, texte))


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
        # L'adresse sans ses paramètres, où peut figurer un jeton d'accès.
        raise RuntimeError(f"{methode} {adresse.split('?')[0]} : erreur {erreur.code} {detail}") from None


IMAGES = {}  # images téléchargées, une seule fois par photo pour Bluesky et Mastodon


def telecharger_image(photo):
    """Image JPEG de la photo, servie par Pexels, sous la limite de poids de Bluesky."""
    if photo["id"] in IMAGES:
        return IMAGES[photo["id"]]
    for largeur in LARGEURS:
        image = appel("GET", build.url_image(photo, largeur))
        if len(image) <= POIDS_MAX:
            IMAGES[photo["id"]] = image
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


LIEN = re.compile(r"https?://[^\s]+[^\s.,;:!?)»]")
DIESE = re.compile(r"(?<![\w#])#(\w*[^\W\d]\w*)")


def facettes(texte):
    """Liens et hashtags cliquables d'une publication Bluesky, repérés en octets UTF-8."""
    def octets(position):
        return len(texte[:position].encode("utf-8"))

    trouvees = [{"index": {"byteStart": octets(m.start()), "byteEnd": octets(m.end())},
                 "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}]}
                for m in LIEN.finditer(texte)]
    trouvees += [{"index": {"byteStart": octets(m.start()), "byteEnd": octets(m.end())},
                  "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": m.group(1)}]}
                 for m in DIESE.finditer(texte)]
    return trouvees


def enregistrement_bluesky(texte, langue, **extra):
    return {"$type": "app.bsky.feed.post", "text": texte, "facets": facettes(texte), "langs": [langue],
            "createdAt": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            **extra}


def publier_bluesky(photo, langue, adr, acces, entree=None):
    identifiant, mot_de_passe = acces
    image = telecharger_image(photo)
    session = appel("POST", f"{BLUESKY_SERVICE}/xrpc/com.atproto.server.createSession",
                    {"identifier": identifiant, "password": mot_de_passe})
    # Le serveur qui héberge le compte (PDS), indiqué par la session ; bsky.social sinon.
    service = next((s.get("serviceEndpoint") for s in (session.get("didDoc") or {}).get("service", [])
                    if s.get("id") == "#atproto_pds"), None) or BLUESKY_SERVICE
    auth = {"Authorization": f'Bearer {session["accessJwt"]}'}
    blob = appel("POST", f"{service}/xrpc/com.atproto.repo.uploadBlob", image,
                 {**auth, "Content-Type": "image/jpeg"})["blob"]
    texte, reponse = textes_bluesky(photo, langue, adr, entree)
    enregistrement = enregistrement_bluesky(texte, langue, embed={
        "$type": "app.bsky.embed.images",
        "images": [{
            "alt": photo["titre"][langue],
            "image": blob,
            "aspectRatio": {"width": photo["largeur"], "height": photo["hauteur"]},
        }],
    })
    resultat = appel("POST", f"{service}/xrpc/com.atproto.repo.createRecord",
                     {"repo": session["did"], "collection": "app.bsky.feed.post", "record": enregistrement}, auth)
    adresse = f'https://bsky.app/profile/{session.get("handle") or session["did"]}/post/{resultat["uri"].rsplit("/", 1)[-1]}'
    if reponse:
        # Le lien en réponse sous la photo. S'il échoue, la photo reste publiée.
        parent = {"uri": resultat["uri"], "cid": resultat["cid"]}
        try:
            appel("POST", f"{service}/xrpc/com.atproto.repo.createRecord",
                  {"repo": session["did"], "collection": "app.bsky.feed.post",
                   "record": enregistrement_bluesky(reponse, langue, reply={"root": parent, "parent": parent})}, auth)
        except (RuntimeError, OSError) as erreur:
            print(f"Bluesky : photo publiée, mais pas la réponse qui porte le lien : {erreur}")
    return adresse


# ---------------------------------------------------------------- Mastodon et Pixelfed


def instance(texte):
    """« mastodon.social », « https://pixelfed.social/ » → « https://… » sans barre finale."""
    texte = texte.strip().rstrip("/")
    return texte if texte.startswith(("https://", "http://")) else "https://" + texte


def publier_mastodon(photo, langue, adr, acces, entree=None):
    serveur, jeton = instance(acces[0]), acces[1]
    auth = {"Authorization": f"Bearer {jeton}"}
    texte = texte_mastodon(photo, langue, adr, entree)
    corps, type_corps = formulaire({"description": photo["titre"][langue]}, telecharger_image(photo))
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


# ---------------------------------------------------------------- Instagram


def image_instagram(photo):
    """Adresse de l'image qu'Instagram télécharge chez Pexels : JPEG imposé par fm=jpg
    (images.pexels.com sert sinon de l'AVIF ou du WebP aux clients qui les acceptent),
    1440 pixels de large, recadrée au centre quand elle sort des proportions permises :
    en 4:5 pour les photos en hauteur, en 1,91:1 pour les panoramas."""
    largeur = min(INSTAGRAM_LARGEUR, photo["largeur"])
    adresse = f'{photo["image"]}?auto=compress&cs=tinysrgb&fm=jpg&w={largeur}'
    rapport = photo["largeur"] / photo["hauteur"]
    if rapport < INSTAGRAM_RAPPORT_MIN:
        adresse += f"&fit=crop&h={math.floor(largeur / INSTAGRAM_RAPPORT_MIN)}"
    elif rapport > INSTAGRAM_RAPPORT_MAX:
        adresse += f"&fit=crop&h={math.ceil(largeur / INSTAGRAM_RAPPORT_MAX)}"
    return adresse


def lire_legendes():
    """Légendes Instagram écrites à l'avance : numéro de la photo → (texte, hashtags). La
    colonne hashtags est facultative : vide, la photo garde ses hashtags automatiques."""
    if not LEGENDES_INSTAGRAM.exists():
        return {}
    with LEGENDES_INSTAGRAM.open(encoding="utf-8", newline="") as fichier:
        return {ligne["photo"].strip(): (ligne["legende"].strip(),
                                         [m.lstrip("#") for m in (ligne.get("hashtags") or "").split() if m.lstrip("#")])
                for ligne in csv.DictReader(fichier) if (ligne.get("legende") or "").strip()}


def legende_instagram(photo, langue):
    """Légende écrite à l'avance (en français) ou titre, renvoi vers le lien du site dans
    la biographie, et hashtags."""
    texte, tags = (lire_legendes().get(str(photo["id"])) if langue == "fr" else None) or (None, None)
    tags = (tags or hashtags(photo, langue))[:INSTAGRAM_HASHTAGS]
    return f'{texte or photo["titre"][langue]}\n\n{TEXTES_INSTAGRAM[langue]}\n\n' + " ".join("#" + t for t in tags)


def api_instagram(methode, chemin, jeton, donnees=None):
    """Appel de l'API Instagram, le jeton dans l'en-tête et jamais dans l'adresse."""
    reponse = appel(methode, f"{INSTAGRAM_API}/{chemin}", donnees, {"Authorization": f"Bearer {jeton}"}, delai=120)
    return reponse if isinstance(reponse, dict) else json.loads(reponse or b"{}")


def publier_instagram(photo, langue, adr, acces, entree=None):
    jeton = acces[0]
    compte = api_instagram("GET", "me?fields=user_id,username", jeton)
    compte = (compte.get("data") or [compte])[0]
    profil = f'https://www.instagram.com/{compte.get("username", "")}/'
    # 1. Le conteneur : Instagram télécharge l'image et la prépare. La documentation
    # conseille d'interroger son état une fois par minute, cinq minutes au plus.
    conteneur = api_instagram("POST", f'{compte["user_id"]}/media', jeton, {
        "image_url": image_instagram(photo),
        "caption": legende_instagram(photo, langue),
        "alt_text": photo["titre"][langue],
    })["id"]
    etat = None
    for attente in (5, 60, 60, 60, 60):
        time.sleep(attente)
        etat = api_instagram("GET", f"{conteneur}?fields=status_code", jeton).get("status_code")
        if etat != "IN_PROGRESS":
            break
    if etat != "FINISHED":
        try:
            detail = api_instagram("GET", f"{conteneur}?fields=status", jeton).get("status", "")
        except (RuntimeError, OSError, ValueError):
            detail = ""
        raise RuntimeError(f"image non préparée par Instagram : {etat} {detail}".strip())
    # 2. La publication.
    try:
        media = api_instagram("POST", f'{compte["user_id"]}/media_publish', jeton, {"creation_id": conteneur})
    except (RuntimeError, OSError):
        # Instagram répond parfois par une erreur alors que la photo est bien publiée :
        # l'état du conteneur le dit, et la photo n'est pas republiée le lendemain.
        if api_instagram("GET", f"{conteneur}?fields=status_code", jeton).get("status_code") != "PUBLISHED":
            raise
        return profil
    try:
        return api_instagram("GET", f'{media["id"]}?fields=permalink', jeton).get("permalink") or profil
    except (RuntimeError, OSError, KeyError):
        return profil


def renouveler_jeton():
    """Échange le jeton Instagram (valable 60 jours) contre un neuf et range celui-ci dans
    le secret INSTAGRAM_JETON du dépôt, avec l'outil gh de GitHub. Le jeton de la tâche
    GitHub n'a pas le droit d'écrire les secrets : gh reçoit, dans GH_TOKEN, le jeton
    GitHub personnel du secret JETON_GITHUB. Le nouveau jeton n'est jamais affiché."""
    jeton = os.environ.get("INSTAGRAM_JETON", "").strip()
    depot = os.environ.get("GITHUB_REPOSITORY", "")
    if not jeton:
        print("Instagram : secret INSTAGRAM_JETON absent, aucun jeton à renouveler.")
        return
    if not os.environ.get("GH_TOKEN", "").strip() or not depot:
        sys.exit("Instagram : secret JETON_GITHUB absent, le jeton renouvelé ne pourrait pas être "
                 "enregistré. Voir reseaux/README.md, rubrique « Instagram ».")
    if not shutil.which("gh"):
        sys.exit("Instagram : outil gh introuvable, installé d'office dans les tâches GitHub.")
    # D'abord s'assurer que le jeton GitHub ouvre bien les secrets du dépôt.
    essai = subprocess.run(["gh", "api", f"repos/{depot}/actions/secrets/public-key", "--silent"],
                           capture_output=True, text=True)
    if essai.returncode:
        sys.exit(f"Instagram : le secret JETON_GITHUB ne donne pas accès aux secrets du dépôt "
                 f"(droit « Secrets » en lecture et écriture) : {essai.stderr.strip()}")
    try:
        reponse = appel("GET", INSTAGRAM_RENOUVELLEMENT + "?"
                        + urlencode({"grant_type": "ig_refresh_token", "access_token": jeton}))
        if not isinstance(reponse, dict):
            reponse = json.loads(reponse or b"{}")
        nouveau = reponse["access_token"]
    except (RuntimeError, OSError, KeyError, ValueError) as erreur:
        sys.exit(f"Instagram : jeton non renouvelé ({erreur}). Un jeton se renouvelle 24 heures "
                 "au moins après sa création et avant son expiration ; expiré, il faut en créer "
                 "un neuf (reseaux/README.md, rubrique « Instagram »).")
    enregistrement = subprocess.run(["gh", "secret", "set", "INSTAGRAM_JETON", "--repo", depot],
                                    input=nouveau, capture_output=True, text=True)
    if enregistrement.returncode:
        sys.exit(f"Instagram : jeton renouvelé mais non enregistré : {enregistrement.stderr.strip()}")
    duree = int(reponse.get("expires_in") or 0)
    fin = datetime.now(timezone.utc) + timedelta(seconds=duree)
    print("Instagram : jeton renouvelé et enregistré dans le secret INSTAGRAM_JETON"
          + (f", valable jusqu'au {fin:%d/%m/%Y}." if duree else "."))


# ---------------------------------------------------------------- programme


def texte_bluesky_essai(photo, langue, adr, entree=None):
    texte, reponse = textes_bluesky(photo, langue, adr, entree)
    return texte + (f"\n  ↳ en réponse : {reponse}" if reponse else "")


# Pour chaque réseau : nom, secrets, publication, et texte publié (affiché par --essai).
RESEAUX = {
    "bluesky": ("Bluesky", ("BLUESKY_IDENTIFIANT", "BLUESKY_MOT_DE_PASSE_APPLI"), publier_bluesky,
                texte_bluesky_essai),
    "mastodon": ("Mastodon", ("MASTODON_INSTANCE", "MASTODON_JETON"), publier_mastodon, texte_mastodon),
    "instagram": ("Instagram", ("INSTAGRAM_JETON",), publier_instagram,
                  lambda photo, langue, adr, entree=None: legende_instagram(photo, langue)),
}


def verifier_calendrier(lignes, photos, journal, jour, delai, adr):
    """Passe en revue les lignes du calendrier à partir de « jour », réseau par réseau, et
    dit ce qui empêcherait de les publier : photo absente ou parue trop récemment, langue
    inconnue, texte vide ou trop long, deux lignes pour un même jour, jour oublié. Les
    lignes qui restent à publier avant « jour » comptent comme déjà parues."""
    par_id = {str(p["id"]): p for p in photos}
    debut = min(jour, AUJOURDHUI)
    problemes = 0
    for reseau in sorted({ligne.get("reseau") or "bluesky" for ligne in lignes} | set(RESEAUX_CALENDRIER)):
        en_attente = sorted((ligne for ligne in lignes if (ligne.get("reseau") or "bluesky") == reseau
                             and ligne["date"] >= debut), key=lambda ligne: ligne["date"])
        a_venir = [ligne for ligne in en_attente if ligne["date"] >= jour]
        if not a_venir:
            continue
        print(f"--- {reseau}")
        parues = dict(journal.get(reseau, {}))
        for entree in en_attente:
            if entree["date"] < jour and entree.get("photo") in par_id:
                parues[entree["photo"]] = {"date": entree["date"]}
        vues = set()
        for entree in a_venir:
            date, langue = entree["date"], entree.get("langue") or ""
            photo = par_id.get(entree.get("photo", ""))
            texte = texte_ecrit(entree)
            alertes = []
            if reseau not in RESEAUX_CALENDRIER:
                alertes.append(f"réseau « {reseau} » inconnu (bluesky ou mastodon)")
            if date in vues:
                alertes.append("deux lignes pour ce jour")
            vues.add(date)
            if langue not in build.LANGUES:
                alertes.append(f"langue « {langue} » inconnue (fr ou en)")
            if not photo:
                alertes.append(f"photo {entree.get('photo') or '?'} absente du site")
            elif not rediffusable(parues, photo["id"], date, delai):
                alertes.append(f"déjà parue le {parues[str(photo['id'])]['date']}, moins de {delai} jours avant")
            if not texte:
                alertes.append("texte vide")
            longueur = len(texte)
            if reseau == "bluesky" and longueur > BLUESKY_LONGUEUR:
                alertes.append(f"texte de {longueur} caractères, {BLUESKY_LONGUEUR} au plus")
            if reseau == "mastodon" and photo and langue in build.LANGUES and texte:
                longueur = longueur_mastodon(texte_mastodon(photo, langue, adr, entree))
                if longueur > MASTODON_LONGUEUR:
                    alertes.append(f"message de {longueur} caractères avec le lien, {MASTODON_LONGUEUR} au plus")
            if photo:
                parues[str(photo["id"])] = {"date": date}
            problemes += bool(alertes)
            titre = photo["titre"]["fr"] if photo else ""
            print(f"{date}  {langue:2}  {entree.get('photo', ''):>9}  {longueur:>3} car.  {titre[:55]}"
                  + (f"\n                ⚠ {' ; '.join(alertes)}" if alertes else ""))
        # Jours oubliés entre le premier et le dernier jour prévus : la file ordinaire et
        # son texte automatique partiraient.
        premier = datetime.fromisoformat(a_venir[0]["date"]).date()
        dernier = datetime.fromisoformat(a_venir[-1]["date"]).date()
        oublies = [(premier + timedelta(days=n)).isoformat() for n in range((dernier - premier).days + 1)
                   if (premier + timedelta(days=n)).isoformat() not in vues]
        if oublies:
            problemes += len(oublies)
            print(f"                ⚠ jours sans ligne : {', '.join(oublies)}")
    print(f"{problemes} point(s) à corriger." if problemes else "Calendrier prêt.")
    return problemes


def main():
    options = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    options.add_argument("--essai", action="store_true")
    options.add_argument("--langue", choices=build.LANGUES)
    options.add_argument("--renouveler-jeton", action="store_true")
    options.add_argument("--a-venir", type=int, metavar="N")
    options.add_argument("--reseau", choices=RESEAUX, default="instagram")
    options.add_argument("--jour", metavar="AAAA-MM-JJ")
    options.add_argument("--calendrier", action="store_true")
    args = options.parse_args()
    if args.renouveler_jeton:
        renouveler_jeton()
        return
    if args.jour and not (args.essai or args.calendrier or args.a_venir):
        sys.exit("--jour ne sert qu'avec --essai, --calendrier ou --a-venir : la tâche publie toujours "
                 "pour aujourd'hui.")
    jour = args.jour or AUJOURDHUI

    reglages = build.lire_ini("site.ini")
    langue = args.langue or reglages.get("photo_du_jour", "langue", fallback="en").strip() or "en"
    # Instagram a sa propre langue : le français, règle de Karl (reseaux/style-karl.md).
    langues = {"instagram": args.langue or reglages.get("photo_du_jour", "langue_instagram",
                                                          fallback=langue).strip() or langue,
               # Bluesky a la sienne : le français, pour la communauté #UnJourUnePhoto. Un jour
               # du calendrier, la langue de sa ligne l'emporte.
               "bluesky": args.langue or reglages.get("photo_du_jour", "langue_bluesky",
                                                        fallback=langue).strip() or langue}
    delai = reglages.getint("photo_du_jour", "rediffusion_jours", fallback=REDIFFUSION_JOURS)
    for choix in (langue, *langues.values()):
        if choix not in build.LANGUES:
            sys.exit(f"Langue inconnue dans site.ini, rubrique [photo_du_jour] : {choix} (fr, en ou zh).")
    adr = build.Adresses(reglages["site"]["adresse"])
    photos = lire_photos()
    par_id = {str(p["id"]): p for p in photos}
    journal = charger_journal()
    calendrier = lire_calendrier()
    if args.calendrier:
        sys.exit(1 if verifier_calendrier(lignes_calendrier(), photos, journal, jour, delai, adr) else 0)
    # Photos que le calendrier réserve pour plus tard, réseau par réseau : la file ordinaire
    # les laisse de côté jusqu'à leur jour.
    reservees = {}
    for (date, reseau), entree in calendrier.items():
        if date > jour:
            reservees.setdefault(reseau, set()).add(entree.get("photo"))
    echecs = 0
    if args.a_venir:
        if args.reseau == "instagram":
            legendes = lire_legendes()
            suite = [p for p in photos if str(p["id"]) not in journal.get("instagram", {})]
            for p in suite[:args.a_venir]:
                etat = "prête   " if str(p["id"]) in legendes else "à écrire"
                print(f'{p["id"]:>9}  {p["vues"]:>6} vues  légende {etat}  {p["titre"]["fr"]}')
            return
        # Bluesky et Mastodon : les photos que le calendrier ne prévoit pas encore, dans
        # l'ordre de la file ordinaire (jamais publiées, des plus vues aux moins vues, puis
        # les plus anciennement publiées).
        parues = journal.get(args.reseau, {})
        prevues = {e.get("photo") for (d, r), e in calendrier.items()
                   if r == args.reseau and d >= min(jour, AUJOURDHUI)}
        libres = [p for p in photos if str(p["id"]) not in prevues and rediffusable(parues, p["id"], jour, delai)]
        suite = ([p for p in libres if str(p["id"]) not in parues]
                 + sorted((p for p in libres if str(p["id"]) in parues), key=lambda p: parues[str(p["id"])]["date"]))
        for p in suite[:args.a_venir]:
            deja = f'  (parue le {parues[str(p["id"])]["date"]})' if str(p["id"]) in parues else ""
            print(f'{p["id"]:>9}  {p["vues"]:>6} vues  {p["titre"]["fr"]}{deja}')
        return

    for cle, (nom, variables, publier, texte_publie) in RESEAUX.items():
        acces = [os.environ.get(v, "").strip() for v in variables]
        parues = journal.get(cle, {})
        if not args.essai and not all(acces):
            print(f"{nom} : accès non renseignés ({', '.join(variables)}), rien à publier.")
            continue
        if any(entree["date"] == jour for entree in parues.values()):
            print(f"{nom} : photo du jour déjà publiée aujourd'hui.")
            continue
        langue_reseau = langues.get(cle, langue)
        # La photo, la langue et le texte du calendrier, s'il en prévoit un ce jour-là.
        entree = calendrier.get((jour, cle))
        photo = par_id.get(entree.get("photo", "")) if entree else None
        if entree and not photo:
            print(f"{nom} : photo {entree.get('photo')} du calendrier absente du site ; file ordinaire.")
            entree = None
        elif entree and (entree.get("langue") not in build.LANGUES or not texte_ecrit(entree)):
            print(f"{nom} : ligne du calendrier sans langue connue ou sans texte ; file ordinaire.")
            entree, photo = None, None
        elif entree and not rediffusable(parues, photo["id"], jour, delai):
            print(f"{nom} : photo {photo['id']} du calendrier déjà parue il y a moins de {delai} jours ; "
                  "file ordinaire.")
            entree, photo = None, None
        if entree:
            langue_reseau = entree["langue"]  # le texte écrit est dans cette langue
        photo = photo or photo_suivante(photos, parues, reservees.get(cle, ()), jour, delai)
        if not photo:
            print(f"{nom} : toutes les photos ont déjà été publiées il y a moins de {delai} jours.")
            continue
        if args.essai:
            texte = texte_publie(photo, langue_reseau, adr, entree)
            origine = "calendrier" if entree else ("rediffusion" if str(photo["id"]) in parues else "file ordinaire")
            print(f"--- {nom} ({jour}) : photo {photo['id']} ({photo['vues']} vues, {origine})\n{texte}\n")
            if cle == "instagram":
                print(f"Image téléchargée par Instagram : {image_instagram(photo)}\n")
            continue
        try:
            lien = publier(photo, langue_reseau, adr, acces, entree)
        except (RuntimeError, OSError, KeyError, ValueError) as erreur:
            echecs += 1
            print(f"{nom} : échec de la publication de la photo {photo['id']} : {erreur}")
            continue
        noter_publication(journal, cle, photo["id"], lien)
        enregistrer_journal(journal)
        print(f"{nom} : photo {photo['id']} publiée, {lien}")

    legendes = lire_legendes()
    for cle, (nom, _, _, _) in RESEAUX.items():
        a_venir = [p for p in photos if str(p["id"]) not in journal.get(cle, {})]
        ligne = f"{nom} : {len(journal.get(cle, {}))} photos publiées depuis le début, {len(a_venir)} à venir."
        if cle == "instagram":
            pretes = next((i for i, p in enumerate(a_venir) if str(p["id"]) not in legendes), len(a_venir))
            ligne += f" Légendes prêtes pour les {pretes} prochaines."
        print(ligne)
    if echecs:
        sys.exit(1)


if __name__ == "__main__":
    main()
