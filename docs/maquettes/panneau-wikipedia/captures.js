// Captures des cinq propositions (ordinateur, téléphone, mode sombre) et quelques gestes.
// Usage : PW=$(npm root -g)/playwright node captures.js <fichier.html> <dossier des photos> <dossier des captures> [ordi|tel|sombre]
// Le dossier des photos contient <id>-800.jpg et <id>-1600.jpg, téléchargés par curl depuis images.pexels.com :
// Chromium ne charge pas ces images à travers le proxy des sessions, on lui répond avec ces fichiers.
const { chromium } = require(process.env.PW);
const fs = require("fs"), path = require("path");
const FICHIER = path.resolve(process.argv[2]), PHOTOS = process.argv[3], SORTIE = process.argv[4];
(async () => {
  const navigateur = await chromium.launch();
  const SEULE = process.argv[5];
  fs.mkdirSync(SORTIE, { recursive: true });
  for (const [nom, viewport, theme] of [["ordi", { width: 1440, height: 900 }, "light"], ["tel", { width: 390, height: 844 }, "light"], ["sombre", { width: 1440, height: 900 }, "dark"]]) {
    if (SEULE && SEULE !== nom) continue;
    const page = await navigateur.newPage({ viewport, colorScheme: theme, deviceScaleFactor: nom === "tel" ? 2 : 1, hasTouch: nom === "tel" });
    const erreurs = [];
    page.on("pageerror", e => erreurs.push("pageerror: " + e.message));
    page.on("console", m => { if (m.type() === "error") erreurs.push("console: " + m.text()); });
    await page.route(/images\.pexels\.com/, r => {
      const u = new URL(r.request().url()), id = u.pathname.split("/")[2], w = +(u.searchParams.get("w") || 1600);
      const f = path.join(PHOTOS, `${id}-${w <= 1000 ? 800 : 1600}.jpg`);
      if (fs.existsSync(f)) r.fulfill({ status: 200, contentType: "image/jpeg", body: fs.readFileSync(f) }); else r.abort();
    });
    await page.goto("file://" + FICHIER, { waitUntil: "load" });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: `${SORTIE}/${nom}-intro.png` });
    for (const id of ["p1", "p2", "p3", "p4", "p5"]) {
      await page.locator("#" + id).scrollIntoViewIfNeeded();
      await page.evaluate(id => window.scrollBy(0, document.querySelector("#" + id + " .prop-tete").getBoundingClientRect().top - 70), id);
      await page.waitForTimeout(1600);
      await page.screenshot({ path: `${SORTIE}/${nom}-${id}.png` });
    }
    // Interactions
    await page.locator(".p1 [data-a=suiv]").click(); await page.waitForTimeout(1300);
    await page.locator("#p1").scrollIntoViewIfNeeded();
    await page.evaluate(() => window.scrollBy(0, document.querySelector("#p1 .prop-tete").getBoundingClientRect().top - 70));
    await page.waitForTimeout(300);
    await page.screenshot({ path: `${SORTIE}/${nom}-p1-suivante.png` });
    await page.evaluate(() => window.scrollBy(0, document.querySelector("#p2 .prop-tete").getBoundingClientRect().top - 70));
    await page.locator('.p2-epingle[data-i="3"] .point').click(); await page.waitForTimeout(1300);
    await page.screenshot({ path: `${SORTIE}/${nom}-p2-moyemont.png` });
    await page.locator('.p2 .p2-filtre[data-l="eu"]').click(); await page.waitForTimeout(1300);
    await page.screenshot({ path: `${SORTIE}/${nom}-p2-filtre.png` });
    await page.evaluate(() => window.scrollBy(0, document.querySelector("#p3 .prop-tete").getBoundingClientRect().top - 70));
    await page.evaluate(() => { const c = document.querySelector(".p3-cadre"); c.scrollTop = c.querySelectorAll(".p3-chap")[2].offsetTop - 60; });
    await page.waitForTimeout(1600);
    await page.screenshot({ path: `${SORTIE}/${nom}-p3-defile.png` });
    await page.evaluate(() => window.scrollBy(0, document.querySelector("#p4 .prop-tete").getBoundingClientRect().top - 70));
    await page.locator('.p4 [data-a=tourner]').click(); await page.waitForTimeout(1300);
    await page.screenshot({ path: `${SORTIE}/${nom}-p4-verso.png` });
    await page.locator('.p4 [data-a=suiv]').click(); await page.waitForTimeout(1200);
    await page.screenshot({ path: `${SORTIE}/${nom}-p4-suivante.png` });
    await page.evaluate(() => window.scrollBy(0, document.querySelector("#p5 .prop-tete").getBoundingClientRect().top - 70));
    await page.locator('.p5-filtres .p2-filtre[data-l="fr"]').click(); await page.waitForTimeout(900);
    await page.screenshot({ path: `${SORTIE}/${nom}-p5-filtre.png` });
    await page.locator('.p5-tuile[data-i="3"]').click(); await page.waitForTimeout(1000);
    await page.screenshot({ path: `${SORTIE}/${nom}-p5-vision.png` });
    await page.keyboard.press("Escape");
    console.log(nom, erreurs.length ? erreurs.join(" | ") : "aucune erreur");
    await page.close();
  }
  await navigateur.close();
})();
