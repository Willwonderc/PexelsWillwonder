// Captures de la version retenue (ordinateur, téléphone, mode sombre, moins d'animations), avec les gestes.
// Usage : PW=$(npm root -g)/playwright node captures-retenu.js <retenu.html> <dossier des photos> <dossier des captures> [ordi|tel|sombre|calme]
// Comme captures.js, on répond aux demandes d'images de images.pexels.com avec les fichiers téléchargés par curl.
const { chromium } = require(process.env.PW);
const fs = require("fs"), path = require("path");
const FICHIER = path.resolve(process.argv[2]), PHOTOS = process.argv[3], SORTIE = process.argv[4], SEULE = process.argv[5];
(async () => {
  const navigateur = await chromium.launch();
  fs.mkdirSync(SORTIE, { recursive: true });
  const vues = [["ordi", { width: 1440, height: 900 }, "light", "no-preference"], ["tel", { width: 390, height: 844 }, "light", "no-preference"],
    ["sombre", { width: 1440, height: 900 }, "dark", "no-preference"], ["calme", { width: 1280, height: 800 }, "light", "reduce"]];
  for (const [nom, viewport, theme, mouvement] of vues) {
    if (SEULE && SEULE !== nom) continue;
    const tel = nom === "tel";
    const page = await navigateur.newPage({ viewport, colorScheme: theme, reducedMotion: mouvement, deviceScaleFactor: tel ? 2 : 1, hasTouch: tel });
    const erreurs = [];
    page.on("pageerror", e => erreurs.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error") erreurs.push("console: " + m.text()); });
    await page.route(/images\.pexels\.com/, r => {
      const u = new URL(r.request().url()), id = u.pathname.split("/")[2], w = +(u.searchParams.get("w") || 1600);
      const f = path.join(PHOTOS, `${id}-${w <= 1000 ? 800 : 1600}.jpg`);
      if (fs.existsSync(f)) r.fulfill({ status: 200, contentType: "image/jpeg", body: fs.readFileSync(f) }); else r.abort();
    });
    await page.goto("file://" + FICHIER, { waitUntil: "load" });
    const debut = await page.evaluate(() => window.scrollY + document.querySelector(".wp-piste").getBoundingClientRect().top - parseFloat(getComputedStyle(document.querySelector(".wp-panneau")).top));
    const pas = await page.evaluate(() => (document.querySelector(".wp-piste").offsetHeight - document.querySelector(".wp-panneau").offsetHeight) / 7);
    const cliche = async (n, attente = 900) => { await page.waitForTimeout(attente); await page.screenshot({ path: `${SORTIE}/${nom}-${n}.png` }); };
    await page.evaluate(y => window.scrollTo(0, y), debut - 260); await cliche("1-arrivee");
    await page.evaluate(y => window.scrollTo(0, y), debut + 1); await cliche("2-photo1");
    await page.evaluate(y => window.scrollTo(0, y), debut + pas * 1.55); await cliche("3-entre-deux", 300);
    // Molette : la page défile, rien n'est retenu
    await page.mouse.move(viewport.width / 3, viewport.height / 2);
    await page.mouse.wheel(0, pas * 1.45); await cliche("4-molette", 1200);
    await page.evaluate(y => window.scrollTo(0, y), debut + pas * 2 + 1); await cliche("5-bordeaux");
    // La pilule : survol à la souris, toucher sur téléphone ; le sommaire s'ouvre sur la photo
    if (tel) await page.locator(".wp-pilule").tap(); else await page.locator(".wp-pilule").hover();
    await cliche("5b-sommaire-vol", 300);
    await cliche("5c-sommaire", 900);
    if (tel) await page.locator(".wp-fermer").tap(); else await page.mouse.move(viewport.width - 60, viewport.height / 2);
    await cliche("5d-sommaire-ferme", 1000);
    await page.locator('.wp-cartel[data-i="2"] .wp-situer').click();
    await cliche("6-carte-vol", 450);
    await cliche("7-carte", 1500);
    await page.keyboard.press("ArrowRight");
    await cliche("8-carte-suivante", 1800);
    await page.keyboard.press("Escape"); await cliche("9-retour", 1200);
    const avant = await page.evaluate(() => window.scrollY);
    await page.mouse.wheel(0, 9000); await page.waitForTimeout(800);
    const apres = await page.evaluate(() => window.scrollY);
    const fin = await page.evaluate(() => document.documentElement.scrollHeight - innerHeight - 5);
    await cliche("10-apres", 300);
    await page.evaluate(() => document.querySelector(".wp-panneau").focus());
    await page.keyboard.press("Tab"); await cliche("11-focus", 300);
    const actuelle = await page.evaluate(() => document.querySelector('.wp-tuiles [aria-current="true"]').dataset.i);
    console.log(nom, "défilement libre :", apres >= Math.min(fin, avant + 2000) ? "oui" : "NON " + avant + "→" + apres, "· photo courante", actuelle, "·", erreurs.length ? erreurs.join(" | ") : "aucune erreur");
    await page.close();
  }
  await navigateur.close();
})();
