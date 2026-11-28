#!/usr/bin/env python3
"""Rubrique « Mes photos utilisées dans le monde », version 4A : scénario de contrôle (brief, étape 5, et contrôles ajoutés).
Joue le parcours dans Chromium sans tête (Playwright pour Python), contre la page de démonstration ou une page du site servie en local.
Usage : python3 scenario.py                                  -> ../demo/index.html (fichier local)
        python3 scenario.py http://127.0.0.1:8000/galeries/  -> la page du site, servie en local
Code de sortie 0 si tout passe ; résultats dans resultats.txt et resultats.json. Scénario de contrôle du brief (étape 5), joué dans Chromium sans tête, sur les fichiers locaux (aucun port ouvert).
Usage : <python avec playwright> controle/scenario.py ; code 0 si tout passe. Les liens externes ne sont pas suivis."""
import json, os, sys
from playwright.sync_api import sync_playwright
ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.dirname(ICI)
CIBLE = next((a for a in sys.argv[1:] if not a.startswith("-")), None) or ("file://" + os.path.join(RACINE, "demo", "index.html"))
ATTENDU = json.load(open(ICI + "/comptes-attendus.json"))
PAGES = {"4A": CIBLE}
A, B = "38694055", "38694057"
resultats = []
def note(cas, nom, ok, detail=""):
    resultats.append((cas, nom, bool(ok), detail))
    print(("  ok  " if ok else "ÉCHEC ") + f"[{cas}] {nom}" + (f" : {detail}" if detail and not ok else ""))
def url(v, ancre=""): return PAGES[v].split("#")[0] + ancre
def racine(v, pid): return "#scene .panneau"
def attendre_ouvert(page): page.wait_for_function("document.querySelector('#monde')?.hidden===false && document.querySelector('#scene h1')", timeout=8000)
def attendre_fiche(page): page.wait_for_function("document.querySelector('#scene').dataset.vue==='fiche'", timeout=5000)
def attendre_fin_ouverture(page): page.wait_for_function("document.querySelector('#passer').hidden", timeout=8000)
def fiche(page, pid):
    page.evaluate(f"location.hash='#monde/photo-{pid}'"); attendre_fiche(page)
def lien_retour(v, pid): return '#scene .retour a[href="#monde"]'

def parcours(page, v, cas, mouvement=True):
    erreurs = []; page.on("pageerror", lambda e: erreurs.append(str(e)))
    page.goto(url(v)); page.wait_for_load_state("load")
    page.locator("#entree").scroll_into_view_if_needed(); y0 = page.evaluate("scrollY")
    page.locator("#entree").click(); attendre_ouvert(page)
    note(cas, "le bouton ouvre la rubrique", page.evaluate("document.querySelector('#scene').dataset.vue") == "index")
    if mouvement:
        page.wait_for_timeout(500)
        vis = page.evaluate("(()=>{const b=document.querySelector('#fermer').getBoundingClientRect();const e=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2);return !!e&&!!e.closest('#fermer')})()")
        note(cas, "pendant l'ouverture, « Fermer » est visible et cliquable", vis)
        note(cas, "pendant l'ouverture, « Passer l'ouverture » est proposé", page.evaluate("!document.querySelector('#passer').hidden"))
    attendre_fin_ouverture(page); page.wait_for_timeout(300)
    note(cas, "le voile est retiré après l'ouverture", page.evaluate("(document.querySelector('#voile')?.hidden ?? true)"))
    if True:
        note(cas, "three.js : le globe est dessiné (canevas WebGL)", page.evaluate("!!document.querySelector('#decor canvas') && !!document.querySelector('#decor canvas').getContext('webgl2')"))
        note(cas, "les étiquettes du globe nomment les pays", page.evaluate("[...document.querySelectorAll('.etq b')].map(e=>e.textContent).includes('France')"))
    n = page.locator("#scene .vue[data-cle]").count()
    note(cas, "index : 14 photos", n == len(ATTENDU["photos"]), f"{n}")
    if True:
        pts = page.locator(".vue-compte i").count(); note(cas, "index : 23 ronds, un par parution", pts == ATTENDU["total"], f"{pts}")
    page.locator(f'.vue[data-cle="{A}"]').scroll_into_view_if_needed()
    s0 = page.evaluate("document.querySelector('#monde').scrollTop")
    page.locator(f'.vue[data-cle="{A}"]').click(); attendre_fiche(page); page.wait_for_timeout(700)
    R = racine(v, A)
    noms = page.locator(f"{R} .notice-nom").all_inner_texts()
    note(cas, "fiche du premier cliché : les deux guides sont nommés", any("Torre Eiffel" in x for x in noms) and any("Off We Gooo" in x for x in noms), str(noms))
    lien = page.locator('#USE-021 .notice-lien')
    note(cas, "lien « Lire le guide de Torre Eiffel », vers le guide, nouvel onglet",
         lien.locator(".lien-libelle").inner_text() == "Lire le guide de Torre Eiffel" and lien.get_attribute("href") == "https://torreeiffel.com.br/fr/chateaux-de-la-loire/" and lien.get_attribute("target") == "_blank")
    note(cas, "crédit « Karl Forterre », liens vers la photo du site et vers Pexels", "Karl Forterre" in page.locator(f"{R} .credit").first.inner_text() and page.locator(f'{R} a[href="https://www.pexels.com/photo/{A}/"]').count() == 1 and page.locator(f'{R} a[href="https://photos.karlforterre.fr/photo/{A}/"]').count() == 1)
    haut = page.evaluate(f"document.querySelector('{R} .notice-texte').getBoundingClientRect().top")
    note(cas, "le premier usage se lit sur le premier écran", haut < page.viewport_size["height"] - 20, f"texte à {haut:.0f} px pour {page.viewport_size['height']}")
    note(cas, "le pays ou « en ligne » est dit en toutes lettres", "brésil" in page.locator("#USE-021").inner_text().lower() and "lieu non établi" in page.locator("#USE-022").inner_text().lower())
    page.locator(lien_retour(v, A)).click(); page.wait_for_function("document.querySelector('#scene').dataset.vue==='index'")
    note(cas, "retour à l'index : la photo quittée a le focus", page.evaluate("document.activeElement && document.activeElement.dataset.cle") == A)
    s1 = page.evaluate("document.querySelector('#monde').scrollTop")
    dans = page.evaluate("(()=>{const r=document.activeElement.getBoundingClientRect();return r.top<innerHeight&&r.bottom>0})()")
    note(cas, "retour à l'index : même position de lecture", abs(s1 - s0) <= 2 and dans, f"avant {s0}, après {s1}, visible {dans}")
    page.locator(f'.vue[data-cle="{B}"]').click(); attendre_fiche(page); page.wait_for_timeout(500)
    t = page.locator(racine(v, B)).inner_text(); tl = t.lower()
    note(cas, "second cliché : l'autrice est nommée", "Nipuni Dissanayake" in t)
    note(cas, "second cliché : titre original et date gardés", "The Cost of Mistaking Reactivity for Agility" in t and "30 juillet 2026" in tl)
    page.locator("#fermer").click(); page.wait_for_function("(document.querySelector('#monde')?.hidden ?? true)")
    y1 = page.evaluate("scrollY")
    note(cas, "fermer ramène au bouton, à la même position de lecture", y1 == y0 and page.evaluate("document.activeElement.id") == "entree", f"avant {y0}, après {y1}")
    note(cas, "l'adresse revient à la page hôte", page.evaluate("location.hash") == "")
    try: page.wait_for_function("(document.querySelector('#voile')?.hidden ?? true)", timeout=1500); vh = True
    except Exception: vh = False
    note(cas, "le voile est retiré après la fermeture (1,5 s au plus)", vh)
    note(cas, "aucun défilement de côté", page.evaluate("document.scrollingElement.scrollWidth<=innerWidth"))
    note(cas, "aucune erreur de script", not erreurs, "; ".join(erreurs[:3]))

def lien_direct(page, v, cas):
    page.goto("about:blank"); page.goto(url(v, f"#monde/photo-{B}")); attendre_ouvert(page); attendre_fiche(page); page.wait_for_timeout(400)
    note(cas, "lien direct : la seconde fiche s'ouvre", "Nipuni Dissanayake" in page.locator(racine(v, B)).inner_text())
    note(cas, "lien direct : la sortie dit sa destination", page.locator("#fermer-texte").inner_text() == "Fermer, vers les galeries")
    page.locator("#fermer").click(); page.wait_for_function("(document.querySelector('#monde')?.hidden ?? true)")
    vu = page.evaluate("(()=>{const r=document.querySelector('#entree').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight})()")
    note(cas, "lien direct : la sortie mène au bouton de la page Galeries", vu and page.evaluate("document.activeElement.id") == "entree")

def clavier(page, v, cas):
    page.goto(url(v)); page.wait_for_load_state("load")
    for _ in range(30):
        page.keyboard.press("Tab")
        if page.evaluate("document.activeElement.id") == "entree": break
    note(cas, "clavier : la tabulation atteint le bouton", page.evaluate("document.activeElement.id") == "entree")
    note(cas, "clavier : le focus est visible sur le bouton", page.evaluate("getComputedStyle(document.activeElement).outlineStyle") == "solid")
    page.keyboard.press("Enter"); attendre_ouvert(page)
    for _ in range(8):
        page.keyboard.press("Tab")
        if page.evaluate("!!document.activeElement.dataset.cle"): break
    note(cas, "clavier : la tabulation reste dans la rubrique et atteint l'index", page.evaluate("!!document.activeElement.closest('#monde') && !!document.activeElement.dataset.cle"))
    note(cas, "clavier : le focus est visible dans l'index", page.evaluate("getComputedStyle(document.activeElement).outlineStyle") == "solid")
    attendre_fin_ouverture(page)
    page.keyboard.press("Enter"); attendre_fiche(page)
    page.locator(f"{racine(v, page.evaluate('location.hash').split('photo-')[-1])} .notice-lien").first.focus()
    note(cas, "clavier : le lien d'une notice prend le focus", page.evaluate("document.activeElement.classList.contains('notice-lien')"))
    note(cas, "clavier : focus visible sur le lien", page.evaluate("getComputedStyle(document.activeElement).outlineStyle") == "solid")
    avant = page.evaluate("location.hash"); page.keyboard.press("ArrowRight"); page.wait_for_timeout(300)
    note(cas, "clavier : la flèche droite passe à la photo suivante", page.evaluate("location.hash") != avant, avant)
    page.keyboard.press("Escape"); page.wait_for_function("(document.querySelector('#monde')?.hidden ?? true)")
    note(cas, "clavier : Échap ferme et rend le focus au bouton", page.evaluate("document.activeElement.id") == "entree")
    page.wait_for_timeout(500)
    page.locator("#entree").click(); page.wait_for_timeout(120); page.keyboard.press("Escape"); page.wait_for_timeout(700)
    note(cas, "Échap pendant le voile : la rubrique reste fermée, le voile est retiré",
         page.evaluate("(document.querySelector('#monde')?.hidden ?? true) && (document.querySelector('#voile')?.hidden ?? true) && location.hash===''"))
    page.locator("#entree").click(); attendre_ouvert(page); page.wait_for_timeout(700); page.keyboard.press("Escape"); page.wait_for_timeout(1500)
    note(cas, "Échap pendant la séquence d'ouverture : fermé, rien ne reste à l'écran",
         page.evaluate("(document.querySelector('#monde')?.hidden ?? true) && (document.querySelector('#voile')?.hidden ?? true) && location.hash==='' && document.activeElement.id==='entree'"))
    page.locator("#entree").click(); attendre_ouvert(page); page.wait_for_timeout(600); page.locator("#passer").click(); page.wait_for_timeout(200)
    note(cas, "« Passer l'ouverture » montre aussitôt l'état final", page.evaluate("document.querySelector('#passer').hidden && !document.querySelector('#monde').classList.contains('en-ouverture')"))

def comptes(page, v, cas):
    page.goto(url(v, "#monde")); attendre_ouvert(page)
    ecarts, titres = [], []
    for pid, n in ATTENDU["photos"].items():
        fiche(page, pid); vu = page.locator(f"{racine(v, pid)} .notice").count()
        if vu != n: ecarts.append(f"{pid} : {vu} pour {n}")
        t = page.locator("#scene h1").get_attribute("aria-label") or ""
        regard = page.locator(".regards-titre").inner_text().lower()
        if not t.endswith(", une photographie qui voyage") or "une image" not in regard: titres.append(pid + " : " + t)
        # le texte des boutons de couleur est lisible (contraste ≥ 4,5:1)
        mauvais = page.evaluate("""(() => { const L = (c) => { const m = c.match(/\\d+(\\.\\d+)?/g).slice(0,3).map(Number).map(v => { v /= 255; return v <= .04045 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }); return .2126*m[0] + .7152*m[1] + .0722*m[2]; };
          return [...document.querySelectorAll('.regard .notice-lien')].filter(a => { const s = getComputedStyle(a); const l1 = L(s.color), l2 = L(s.backgroundColor); return (Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05) < 4.5; }).length; })()""")
        if mauvais: titres.append(pid + f" : {mauvais} bouton(s) sous 4,5:1")
    note(cas, "chaque fiche a son titre « <lieu>, une photographie qui voyage », « Une image, N regards » et des boutons lisibles", not titres, " ; ".join(titres))
    note(cas, "chaque fiche liste autant de parutions que le registre", not ecarts, " ; ".join(ecarts))

JS_ETIQUETTES = """(() => {
  const d = document.querySelector('#decor').getBoundingClientRect(), b = document.querySelector('.barre').getBoundingClientRect();
  const pan = document.querySelector('.panneau'), pr = pan ? pan.getBoundingClientRect() : null;
  const vis = [...document.querySelectorAll('.etq')].filter(e => parseFloat(e.style.opacity || '0') > 0.3);
  const pb = [];
  const R = vis.map(e => ({ n: e.textContent, r: e.getBoundingClientRect() }));
  R.forEach(({ n, r }) => {
    if (r.left < d.left - 0.5 || r.right > d.right + 0.5 || r.top < d.top - 0.5 || r.bottom > d.bottom + 0.5) pb.push('coupée par le bord : ' + n);
    if (r.left < innerWidth && r.right > 0 && r.top < b.bottom - 0.5 && r.bottom > b.top) pb.push('sous la barre : ' + n);
    if (pr && r.right > pr.left + 0.5 && r.left < pr.right && r.bottom > pr.top && r.top < pr.bottom) pb.push('sous la colonne : ' + n);
  });
  for (let i = 0; i < R.length; i++) for (let j = i + 1; j < R.length; j++) { const a = R[i].r, c = R[j].r;
    if (a.left < c.right - 0.5 && a.right > c.left + 0.5 && a.top < c.bottom - 0.5 && a.bottom > c.top + 0.5) pb.push('recouvrement : ' + R[i].n + ' / ' + R[j].n); }
  return { n: R.length, pb };
})()"""

def etiquettes(page, v, cas):
    page.goto(url(v, "#monde")); attendre_ouvert(page)
    ecarts, total = [], 0
    for pid in ATTENDU["photos"]:
        fiche(page, pid); page.wait_for_timeout(2600)
        r = page.evaluate(JS_ETIQUETTES); total += r["n"]
        if r["pb"]: ecarts.append(pid + " : " + " ; ".join(r["pb"]))
    note(cas, f"fiches : aucune étiquette coupée, sous la barre ou la colonne, ni recouverte (14 fiches, {total} étiquettes lues)", not ecarts, " | ".join(ecarts))
    page.goto(url(v, "#monde")); attendre_ouvert(page); page.wait_for_timeout(2600)
    r = page.evaluate(JS_ETIQUETTES)
    note(cas, f"index : aucune étiquette coupée ni recouverte ({r['n']} lues)", not r["pb"], " ; ".join(r["pb"]))

if __name__ == "__main__":
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        for v in PAGES:
            ctx = nav.new_context(viewport={"width": 1280, "height": 800}); p = ctx.new_page()
            parcours(p, v, f"{v} · ordinateur"); lien_direct(p, v, f"{v} · ordinateur"); clavier(p, v, f"{v} · clavier"); comptes(p, v, f"{v} · registre")
            etiquettes(p, v, f"{v} · étiquettes · ordinateur")
            ctx.close()
            ctx = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True, is_mobile=True); p = ctx.new_page()
            parcours(p, v, f"{v} · téléphone"); lien_direct(p, v, f"{v} · téléphone")
            etiquettes(p, v, f"{v} · étiquettes · téléphone")
            ctx.close()
            ctx = nav.new_context(viewport={"width": 1280, "height": 800}, reduced_motion="reduce"); p = ctx.new_page()
            parcours(p, v, f"{v} · mouvement réduit", mouvement=False); ctx.close()
        nav.close()
    echecs = [r for r in resultats if not r[2]]
    print(f"\n{len(resultats) - len(echecs)} contrôles réussis sur {len(resultats)}")
    json.dump([{"cas": c, "controle": n, "reussi": o, "detail": d} for c, n, o, d in resultats], open(ICI + "/resultats.json", "w"), ensure_ascii=False, indent=1)
    open(ICI + "/resultats.txt", "w").write("\n".join(("ok    " if o else "ÉCHEC ") + f"[{c}] {n}" + (f" : {d}" if d and not o else "") for c, n, o, d in resultats) + f"\n\n{len(resultats) - len(echecs)} contrôles réussis sur {len(resultats)}\n")
    sys.exit(1 if echecs else 0)
