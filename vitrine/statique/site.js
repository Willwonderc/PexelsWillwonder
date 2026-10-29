/* Site de Karl Forterre : fondu de l'accueil, photos utilisées dans des projets et
   visionneuse plein écran. JavaScript léger, sans bibliothèque. Sans lui, le site
   fonctionne tout autant : chaque vignette mène à la page de sa photo. */
(function () {
  "use strict";

  var calme = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Accueil : fondu lent entre les photos de l'ouverture ---------- */

  var defile = document.querySelector(".defile");
  if (defile && !calme && "content" in document.createElement("template")) {
    var modeles = defile.querySelectorAll("template");
    var diapos = [defile.querySelector(".diapo")];
    var total = modeles.length + 1, actuelle = 0, montree = diapos[0], DUREE = 7000;

    var preparer = function (i) {
      if (!diapos[i]) {
        var contenu = document.importNode(modeles[i - 1].content, true);
        diapos[i] = contenu.firstElementChild;
        defile.appendChild(diapos[i]);
      }
      return diapos[i];
    };

    var avancer = function () {
      if (document.hidden) { setTimeout(avancer, DUREE); return; }
      var i = (actuelle + 1) % total, diapo = preparer(i), img = diapo.querySelector("img"), fait = false;
      var suite = function (reussie) {
        if (fait) return;
        fait = true;
        actuelle = i;
        if (reussie) {
          montree.classList.remove("visible");
          diapo.classList.add("visible");
          montree = diapo;
        }
        if (total > 2) preparer((i + 1) % total);
        setTimeout(avancer, DUREE);
      };
      if (img.complete) { suite(img.naturalWidth > 0); return; }
      img.addEventListener("load", function () { suite(true); });
      img.addEventListener("error", function () { suite(false); });
    };

    if (total > 1) {
      preparer(1);
      setTimeout(avancer, DUREE);
    }
  }

  /* ---------- Galeries : index des photos utilisées dans des projets ----------
     Les noms entrent l'un après l'autre quand l'index arrive à l'écran. Les grandes
     photos du survol se chargent au premier passage de la souris ou du clavier ; sur
     ordinateur, aussi d'avance, une fois la page chargée, pour que le premier survol soit
     immédiat. Chacune ne se montre qu'une fois chargée. */

  var index = document.querySelector(".index-usages");
  if (index && !calme && "IntersectionObserver" in window) {
    index.classList.add("index-anime");
    var arrivee = new IntersectionObserver(function (entrees) {
      if (!entrees[0].isIntersecting) return;
      index.classList.add("vu");
      arrivee.disconnect();
    }, { threshold: 0.12 });
    arrivee.observe(index);
  }
  if (index && "content" in document.createElement("template")) {
    var chargerFonds = function () {
      index.removeEventListener("pointerenter", auPointeur);
      index.removeEventListener("focusin", chargerFonds);
      Array.prototype.forEach.call(index.querySelectorAll(".index-fond"), function (fond) {
        var modele = fond.querySelector("template");
        if (!modele) return;
        var img = document.importNode(modele.content, true).firstElementChild;
        var pret = function () { fond.classList.add("pret"); };
        img.addEventListener("load", pret);
        fond.replaceChild(img, modele);
        if (img.complete && img.naturalWidth) pret();
      });
    };
    var auPointeur = function (ev) {
      if (ev.pointerType !== "touch") chargerFonds();
    };
    index.addEventListener("pointerenter", auPointeur);
    index.addEventListener("focusin", chargerFonds);
    var ordinateur = window.matchMedia && window.matchMedia("(hover: hover) and (min-width: 641px)").matches;
    var economie = navigator.connection && navigator.connection.saveData;
    if (ordinateur && !economie) {
      window.addEventListener("load", function () {
        (window.requestIdleCallback || function (f) { setTimeout(f, 1500); })(chargerFonds);
      });
    }
  }

  /* Une bande par photo : quand plusieurs sites ou campagnes ont utilisé la même photo,
     leurs noms (et le mois du signalement, s'il diffère) y défilent comme au générique.
     Les bandes défilent chacune à son tour ; tout s'arrête quand l'index sort de l'écran
     ou que la page est cachée. Sans script, ou si l'appareil demande moins d'animations,
     les noms restent l'un sous l'autre. */

  var bandes = [];
  if (index && !calme && "IntersectionObserver" in window) {
    Array.prototype.forEach.call(index.querySelectorAll(".index-ligne"), function (ligne) {
      var noms = ligne.querySelectorAll(".index-nom > span");
      var mois = ligne.querySelectorAll(".index-quand > span");
      if (noms.length > 1) bandes.push({ suites: mois.length > 1 ? [noms, mois] : [noms], rang: 0 });
    });
  }
  if (bandes.length) {
    var RELAIS = 6000, PREMIER = 4500, tour = 0, minuterie = null, enVue = false;
    bandes.forEach(function (b) {
      b.montres = b.suites.map(function (suite) {
        suite[0].parentNode.classList.add("index-relais");
        suite[0].classList.add("actif");
        return suite[0];
      });
    });
    /* Relais d'une bande : le nom affiché sort, le suivant entre ; un mois identique au
       précédent reste en place. */
    var relayer = function () {
      var b = bandes[tour++ % bandes.length];
      b.rang = (b.rang + 1) % b.suites[0].length;
      b.suites.forEach(function (suite, k) {
        var avant = b.montres[k], apres = suite[b.rang];
        if (apres.textContent === avant.textContent) return;
        avant.parentNode.classList.add("demarre");
        avant.classList.remove("actif");
        avant.classList.add("sortant");
        apres.classList.remove("sortant");
        apres.classList.add("actif");
        b.montres[k] = apres;
      });
    };
    var planifier = function (delai) {
      minuterie = setTimeout(function () {
        relayer();
        planifier(RELAIS / bandes.length);
      }, delai);
    };
    var regler = function () {
      var marche = enVue && !document.hidden;
      if (marche && minuterie === null) planifier(PREMIER);
      if (!marche && minuterie !== null) {
        clearTimeout(minuterie);
        minuterie = null;
      }
    };
    new IntersectionObserver(function (entrees) {
      enVue = entrees[entrees.length - 1].isIntersecting;
      regler();
    }).observe(index);
    document.addEventListener("visibilitychange", regler);
  }

  /* ---------- Photos utilisées : chaque photo apparaît à son arrivée à l'écran ---------- */

  var salles = document.querySelectorAll(".salle");
  if (salles.length && !calme && "IntersectionObserver" in window) {
    document.documentElement.classList.add("salles-animees");
    var observateur = new IntersectionObserver(function (entrees) {
      entrees.forEach(function (entree) {
        if (!entree.isIntersecting) return;
        entree.target.classList.add("vue");
        observateur.unobserve(entree.target);
      });
    }, { threshold: 0.2 });
    Array.prototype.forEach.call(salles, function (s) { observateur.observe(s); });
  }

  /* ---------- À propos : la pastille de la distinction tombe sur le titre ---------- */

  var titreSceau = document.querySelector(".titre-sceau");
  if (titreSceau && !calme) titreSceau.classList.add("vue");

  /* ---------- Galeries : mes photos dans Wikipédia ----------
     La salle de projection choisie par Karl (maquette : docs/maquettes/panneau-wikipedia/
     retenu.html). Arrivé au panneau, il se fixe à l'écran et chaque photo a sa part de la
     hauteur de défilement : la page reste courte, même avec vingt photos, et la molette
     n'est jamais retenue. La photo suivante se découvre de bas en haut, le cartel glisse
     avec un palier par photo. Une pilule à trois billes montre l'avancée ; survolée,
     touchée ou ouverte au clavier, elle devient le sommaire de toutes les photos. Flèches,
     clavier, doigt, sommaire et épingles font défiler la page jusqu'à la photo voulue.
     « Situer » dévoile la carte (statique/carte.json, chargée quand le panneau approche) :
     la photo se réduit en vignette et vole jusqu'à son épingle ; d'une photo à l'autre,
     la carte vole au lieu suivant. Les grandes photos ne se chargent qu'à l'approche du
     panneau, par trois : l'affichée et ses voisines. */

  var panneauWp = document.querySelector(".wp-panneau");
  if (panneauWp && panneauWp.parentNode.classList.contains("wp-piste")) panneauWikipedia(panneauWp);

  function panneauWikipedia(panneau) {
    var piste = panneau.parentNode, scene = panneau.querySelector(".wp-scene");
    var diapos = panneau.querySelectorAll(".wp-diapo"), cartels = panneau.querySelectorAll(".wp-cartel");
    var N = Math.min(diapos.length, cartels.length);
    if (!N || !scene) return;
    var textes = {};
    try { textes = JSON.parse(panneau.getAttribute("data-textes") || "{}"); } catch (erreur) { textes = {}; }
    document.documentElement.classList.add("wp-js");

    var ruban = panneau.querySelector(".wp-ruban"), pilule = panneau.querySelector(".wp-pilule");
    var billes = panneau.querySelector(".wp-billes"), lesBilles = billes.querySelectorAll("i");
    var index = panneau.querySelector(".wp-index"), tuiles = index.querySelectorAll(".wp-tuiles button");
    var lieu = panneau.querySelector(".wp-lieu");
    var prec = panneau.querySelector('[data-a="prec"]'), suiv = panneau.querySelector('[data-a="suiv"]');
    var situer = panneau.querySelectorAll(".wp-situer");
    var photos = Array.prototype.map.call(cartels, function (c, k) {
      return {
        x: parseFloat(c.getAttribute("data-x")), y: parseFloat(c.getAttribute("data-y")),
        dx: parseFloat(c.getAttribute("data-dx")) || 0, dy: parseFloat(c.getAttribute("data-dy")) || 0,
        couleur: c.getAttribute("data-couleur"),
        lieu: diapos[k].getAttribute("data-lieu") || "", region: diapos[k].getAttribute("data-region") || ""
      };
    });
    photos.forEach(function (p) { p.place = !isNaN(p.x) && !isNaN(p.y); });

    function forme(modele, valeurs) {
      return String(modele || "").replace(/\{(\w+)\}/g, function (tout, cle) { return cle in valeurs ? valeurs[cle] : tout; });
    }
    function esc(s) {
      return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
    }
    function borne(v, a, b) { return Math.max(a, Math.min(b, v)); }
    function douce(t) { return t * t * (3 - 2 * t); }

    /* Le défilement : la page avance, le panneau reste fixé, chaque photo a sa part de la piste */
    var pas = 300, haut = 0, actuelle = -1, position = 0, proche = false, attente = false;
    function mesurer() {
      var h = panneau.offsetHeight;
      haut = parseFloat(getComputedStyle(panneau).top) || 0;
      pas = N > 1 ? borne(h * 2.6 / (N - 1), 130, h * .42) : 0;
      piste.style.height = (h + (N - 1) * pas) + "px";
      suivre();
    }
    function charger(k) {
      var img = proche && diapos[k] && diapos[k].querySelector("img");
      if (img && img.getAttribute("data-src")) {
        img.srcset = img.getAttribute("data-srcset") || "";
        img.src = img.getAttribute("data-src");
        img.removeAttribute("data-src");
      }
    }
    function suivre() {
      attente = false;
      var parcouru = borne(haut - piste.getBoundingClientRect().top, 0, (N - 1) * pas);
      var brut = pas ? parcouru / pas : 0, i = Math.min(Math.floor(brut), N - 1), f = brut - i;
      // Un palier par photo : le cartel reste lisible, puis glisse vers le suivant
      var e = douce(borne((f - .3) / .55, 0, 1));
      position = i + e;
      panneau.classList.toggle("parti", parcouru > 8);
      ruban.style.transform = "translateY(" + (-position * 100) + "%)";
      cartels.forEach(function (c, k) { c.style.opacity = (1 - Math.min(1, Math.abs(k - position) * 1.5)).toFixed(3); });
      diapos.forEach(function (d, k) {
        var vue = k === i || (k === i + 1 && e > 0);
        d.classList.toggle("vue", vue);
        if (k === i + 1 && e > 0) {
          d.style.clipPath = "inset(" + ((1 - e) * 100).toFixed(2) + "% 0 0 0)";
          d.style.transform = calme ? "" : "scale(" + (1.06 - .06 * e).toFixed(4) + ")";
        } else {
          d.style.clipPath = "";
          d.style.transform = "";
        }
        d.style.zIndex = k === i + 1 ? 2 : 1;
        if (!calme) d.querySelector("img").classList.toggle("vit", vue);
      });
      for (var k = i - 1; k <= i + 2; k++) charger(k);
      // Les billes glissent d'un cran par photo : celle du milieu grossit, les voisines s'estompent
      billes.style.transform = "translateY(" + (-position * 14).toFixed(2) + "px)";
      lesBilles.forEach(function (b, k) {
        var d = Math.abs(k - position);
        b.style.transform = "scale(" + (d < 1 ? 1.5 - .5 * d : Math.max(0, 1 - (d - 1) * 1.6)).toFixed(3) + ")";
        b.style.opacity = (d < 1 ? 1 - .5 * d : Math.max(0, .5 - (d - 1))).toFixed(3);
      });
      var nouvelle = Math.round(position);
      if (nouvelle !== actuelle) changer(nouvelle);
    }
    function changer(i) {
      var avant = actuelle, p = photos[i];
      actuelle = i;
      panneau.style.setProperty("--c", p.couleur);
      var nom = document.createElement("span"), region = document.createElement("small");
      nom.textContent = p.lieu;
      region.textContent = p.region;
      nom.appendChild(region);
      lieu.textContent = "";
      lieu.appendChild(nom);
      tuiles.forEach(function (b, k) { b.setAttribute("aria-current", k === i ? "true" : "false"); });
      pilule.setAttribute("aria-label", forme(textes.rang, { i: i + 1, n: N }));
      // Le focus ne se perd pas dans une fiche qui s'efface : il revient au panneau
      if (avant >= 0 && cartels[avant].contains(document.activeElement)) panneau.focus({ preventScroll: true });
      cartels.forEach(function (c, k) { c.inert = k !== i; c.setAttribute("aria-hidden", k === i ? "false" : "true"); });
      prec.disabled = i === 0;
      suiv.disabled = i === N - 1;
      if (ouverte) { if (p.place) volerVers(avant, i); else fermer(); }
    }
    function aller(i) {
      i = borne(i, 0, N - 1);
      var cible = window.pageYOffset + piste.getBoundingClientRect().top - haut + i * pas + 1;
      window.scrollTo({ top: cible, behavior: calme ? "auto" : "smooth" });
    }
    window.addEventListener("scroll", function () {
      if (!attente) { attente = true; requestAnimationFrame(suivre); }
    }, { passive: true });
    window.addEventListener("resize", mesurer);
    prec.addEventListener("click", function () { aller(actuelle - 1); });
    suiv.addEventListener("click", function () { aller(actuelle + 1); });

    /* Le sommaire : au survol de la pilule (ou au toucher, ou au clavier), il prend la place de la photo */
    var minuterie = null;
    function sommaire(ouvrir, auClavier) {
      clearTimeout(minuterie);
      if (ouvrir === index.classList.contains("ouvert")) return;
      if (ouvrir) {
        // Le sommaire part de la pilule : son découpage de départ épouse la forme de la pilule
        var s = scene.getBoundingClientRect(), r = pilule.getBoundingClientRect();
        index.style.setProperty("--t", (r.top - s.top) + "px");
        index.style.setProperty("--b", (s.bottom - r.bottom) + "px");
        index.style.setProperty("--g", (r.left - s.left) + "px");
        index.style.setProperty("--d", (s.right - r.right) + "px");
        index.querySelectorAll("img[data-src]").forEach(function (img) {
          img.src = img.getAttribute("data-src");
          img.removeAttribute("data-src");
        });
        void index.offsetWidth;
      }
      index.classList.toggle("ouvert", ouvrir);
      pilule.setAttribute("aria-expanded", ouvrir ? "true" : "false");
      if (ouvrir && auClavier) setTimeout(function () { tuiles[actuelle].focus({ preventScroll: true }); }, calme ? 0 : 250);
      if (!ouvrir && index.contains(document.activeElement)) pilule.focus({ preventScroll: true });
    }
    pilule.addEventListener("pointerenter", function (ev) {
      if (ev.pointerType !== "mouse") return;
      clearTimeout(minuterie);
      minuterie = setTimeout(function () { sommaire(true); }, 120);
    });
    pilule.addEventListener("pointerleave", function (ev) {
      if (ev.pointerType === "mouse" && !index.classList.contains("ouvert")) clearTimeout(minuterie);
    });
    pilule.addEventListener("click", function (ev) { sommaire(!index.classList.contains("ouvert"), ev.detail === 0); });
    index.addEventListener("pointerenter", function () { clearTimeout(minuterie); });
    index.addEventListener("pointerleave", function (ev) {
      if (ev.pointerType === "mouse") minuterie = setTimeout(function () { sommaire(false); }, 350);
    });
    index.querySelector(".wp-fermer").addEventListener("click", function () { sommaire(false); });
    tuiles.forEach(function (b) {
      b.addEventListener("click", function () {
        var k = +b.getAttribute("data-i");
        sommaire(false);
        pilule.focus({ preventScroll: true });
        aller(k);
      });
    });
    panneau.addEventListener("keydown", function (ev) {
      if (ev.target.closest && ev.target.closest(".wp-epingle")) return;
      var cible = { ArrowLeft: actuelle - 1, ArrowRight: actuelle + 1, Home: 0, End: N - 1 }[ev.key];
      if (cible !== undefined && ev.target.tagName !== "A") { aller(cible); ev.preventDefault(); }
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape") return;
      if (index.classList.contains("ouvert")) { sommaire(false); ev.preventDefault(); }
      else if (ouverte) { fermer(); ev.preventDefault(); }
    });
    // Glissement du doigt sur la photo, comme une story : la page défile jusqu'à la photo voisine
    (function () {
      var x0 = null, y0 = 0;
      scene.addEventListener("pointerdown", function (ev) {
        x0 = ev.target.closest(".wp-index, .wp-atlas") ? null : ev.clientX;
        y0 = ev.clientY;
      });
      scene.addEventListener("pointerup", function (ev) {
        if (x0 === null) return;
        var dx = ev.clientX - x0, dy = ev.clientY - y0;
        x0 = null;
        if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.3) aller(actuelle + (dx < 0 ? 1 : -1));
      });
      scene.addEventListener("pointercancel", function () { x0 = null; });
    })();

    /* La carte : chargée quand le panneau approche, dessinée au premier clic sur « Situer » */
    var atlas = panneau.querySelector(".wp-atlas"), vol = panneau.querySelector(".wp-vol"), volImg = vol.querySelector("img");
    var adresseCarte = panneau.getAttribute("data-carte"), langue = panneau.getAttribute("data-langue") || "fr";
    var CARTE = null, promesse = null, svg = null, epingles = [], fixes = [], L = 1000, HC = 915;
    var vue = [0, 0, L, HC], anim = null, ouverte = false, enCours = false;
    if (!adresseCarte || !window.fetch) situer.forEach(function (b) { b.hidden = true; });
    function chargerCarte() {
      if (!promesse) {
        promesse = fetch(adresseCarte).then(function (reponse) {
          if (!reponse.ok) throw new Error("carte " + reponse.status);
          return reponse.json();
        }).then(function (donnees) {
          CARTE = donnees;
          L = donnees.largeur;
          HC = donnees.hauteur;
          return donnees;
        });
        promesse.catch(function () { promesse = null; });
      }
      return promesse;
    }
    function construire() {
      if (svg) return;
      var pays = function (principal) {
        return CARTE.pays.filter(function (c) { return !!c.principal === principal; }).map(function (c) {
          return '<path class="' + (principal ? "principal" : "voisin") + '" d="' + c.d + '"/>';
        }).join("");
      };
      atlas.insertAdjacentHTML("afterbegin",
        '<svg viewBox="0 0 ' + L + " " + HC + '" preserveAspectRatio="xMidYMid slice" role="img" aria-label="' + esc(textes.carte || "") + '">'
        + "<g>" + pays(false) + pays(true) + "</g>"
        + "<g>" + (CARTE.etiquettes || []).map(function (e) {
            var lignes = e[langue] || e.fr || [];
            return '<g class="fixe" data-x="' + e.x + '" data-y="' + e.y + '"><text class="etiquette ' + (e.classe || "") + '" text-anchor="' + (e.milieu ? "middle" : "start") + '">'
              + lignes.map(function (l, k) { return '<tspan x="0" dy="' + (k ? "1.4em" : "0") + '">' + esc(l) + "</tspan>"; }).join("") + "</text></g>";
          }).join("") + "</g>"
        + "<g>" + photos.map(function (p, i) {
            if (!p.place) return "";
            return '<g class="fixe wp-epingle" data-i="' + i + '" data-x="' + p.x + '" data-y="' + p.y + '" tabindex="-1" role="button" aria-label="' + esc(forme(textes.epingle, { i: i + 1, lieu: p.lieu })) + '">'
              + '<g transform="translate(' + p.dx + " " + p.dy + ')"><g class="chute"><circle class="halo" r="12"/><circle class="anneau" r="15"/><circle class="point" r="11"/><text>' + (i + 1) + "</text></g></g></g>";
          }).join("") + "</g></svg>");
      svg = atlas.querySelector("svg");
      fixes = atlas.querySelectorAll(".fixe");
      epingles = atlas.querySelectorAll(".wp-epingle");
      epingles.forEach(function (g) {
        g.addEventListener("click", function () { aller(+g.getAttribute("data-i")); });
        g.addEventListener("keydown", function (ev) {
          if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); aller(+g.getAttribute("data-i")); }
        });
      });
    }
    function epingle(i) {
      return Array.prototype.filter.call(epingles, function (g) { return +g.getAttribute("data-i") === i; })[0];
    }
    // Les épingles et les noms gardent la même taille à l'écran, quel que soit le zoom
    function echelle() {
      var k = (vue[2] / scene.clientWidth).toFixed(4);
      fixes.forEach(function (g) {
        g.setAttribute("transform", "translate(" + g.getAttribute("data-x") + " " + g.getAttribute("data-y") + ") scale(" + k + ")");
      });
    }
    function cadrage(i, large) {
      var W = scene.clientWidth, H = scene.clientHeight, r = W / H;
      if (large) {
        var w0 = Math.max(L, HC * r);
        return [(L - w0) / 2, (HC - w0 / r) / 2, w0, w0 / r];
      }
      var p = photos[i], w = L * (W < 600 ? .8 : .64), h = w / r;
      return [p.x - w / 2, p.y - h * (W < 600 ? .56 : .42), w, h];
    }
    // Position à l'écran (en pixels dans la scène) de l'épingle i pour un cadrage donné
    function ecran(i, v) {
      var W = scene.clientWidth, p = photos[i];
      return [(p.x - v[0]) / v[2] * W + p.dx, (p.y - v[1]) / v[2] * W + p.dy];
    }
    function placeVignette(xy) {
      var t = scene.clientWidth < 600 ? [112, 84] : [168, 120];
      return { left: xy[0] - t[0] / 2, top: xy[1] - t[1] - 30, width: t[0], height: t[1] };
    }
    function poser(r) {
      vol.style.left = r.left + "px";
      vol.style.top = r.top + "px";
      vol.style.width = r.width + "px";
      vol.style.height = r.height + "px";
    }
    function cadrer(cible, duree, chaqueImage) {
      if (anim) cancelAnimationFrame(anim);
      var depart = vue.slice(), t0 = performance.now();
      duree = calme ? 0 : duree;
      function etape(t) {
        var k = duree ? Math.min(1, (t - t0) / duree) : 1, e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
        vue = depart.map(function (v, j) { return v + (cible[j] - v) * e; });
        svg.setAttribute("viewBox", vue.join(" "));
        echelle();
        if (chaqueImage) chaqueImage(e);
        anim = k < 1 ? requestAnimationFrame(etape) : null;
      }
      anim = requestAnimationFrame(etape);
    }
    function lacher(i) {
      epingles.forEach(function (g) {
        g.classList.toggle("active", +g.getAttribute("data-i") === i);
        g.classList.remove("tombe");
      });
      var g = epingle(i);
      if (!g) return;
      void atlas.offsetWidth;
      g.classList.add("tombe");
      g.parentNode.appendChild(g);
    }
    function titreCarte(i) {
      atlas.querySelector(".wp-titre-carte b").textContent = photos[i].lieu;
      atlas.querySelector(".wp-titre-carte span").textContent = photos[i].region;
    }
    function ouvrir() {
      if (ouverte || enCours || !photos[actuelle].place) return;
      enCours = true;
      situer.forEach(function (b) { b.setAttribute("aria-busy", "true"); });
      chargerCarte().then(function () {
        enCours = false;
        situer.forEach(function (b) { b.removeAttribute("aria-busy"); });
        construire();
        var i = actuelle;
        if (!photos[i].place) return;
        ouverte = true;
        var img = diapos[i].querySelector("img"), cible = cadrage(i), fin = placeVignette(ecran(i, cible));
        vue = cadrage(i, true);
        svg.setAttribute("viewBox", vue.join(" "));
        echelle();
        epingles.forEach(function (g) { g.classList.remove("active", "tombe"); g.setAttribute("tabindex", "0"); });
        titreCarte(i);
        atlas.setAttribute("aria-hidden", "false");
        panneau.classList.add("carte");
        majBoutons();
        volImg.src = img.currentSrc || img.src;
        vol.classList.add("visible");
        if (calme || !vol.animate) {
          poser(fin);
          vue = cible;
          svg.setAttribute("viewBox", vue.join(" "));
          echelle();
          lacher(i);
          return;
        }
        var W = scene.clientWidth, H = scene.clientHeight;
        vol.animate([
          { left: "0px", top: "0px", width: W + "px", height: H + "px", borderRadius: "0px" },
          { left: fin.left + "px", top: fin.top + "px", width: fin.width + "px", height: fin.height + "px", borderRadius: "12px" }
        ], { duration: 1050, easing: "cubic-bezier(.65, 0, .25, 1)" });
        poser(fin);
        setTimeout(function () { cadrer(cible, 1100); }, 120);
        setTimeout(function () { if (ouverte) lacher(i); }, 820);
      }, function () {
        enCours = false;
        situer.forEach(function (b) { b.removeAttribute("aria-busy"); });
      });
    }
    function fermer() {
      if (!ouverte) return;
      ouverte = false;
      majBoutons();
      var img = diapos[actuelle].querySelector("img"), W = scene.clientWidth, H = scene.clientHeight;
      volImg.src = img.currentSrc || img.src;
      var depuis = placeVignette(ecran(actuelle, vue));
      function fini() {
        vol.classList.remove("visible");
        atlas.setAttribute("aria-hidden", "true");
        epingles.forEach(function (g) { g.setAttribute("tabindex", "-1"); });
      }
      if (calme || !vol.animate) { panneau.classList.remove("carte"); fini(); return; }
      var a = vol.animate([
        { left: depuis.left + "px", top: depuis.top + "px", width: depuis.width + "px", height: depuis.height + "px", borderRadius: "12px" },
        { left: "0px", top: "0px", width: W + "px", height: H + "px", borderRadius: "0px" }
      ], { duration: 800, easing: "cubic-bezier(.65, 0, .25, 1)" });
      poser({ left: 0, top: 0, width: W, height: H });
      setTimeout(function () { panneau.classList.remove("carte"); }, 450);
      a.onfinish = fini;
    }
    // D'une photo à l'autre, la carte vole jusqu'au lieu suivant et la vignette suit
    function volerVers(avant, i) {
      var img = diapos[i].querySelector("img");
      charger(i);
      titreCarte(i);
      volImg.style.opacity = "0";
      setTimeout(function () { volImg.src = img.currentSrc || img.src; volImg.style.opacity = "1"; }, calme ? 0 : 300);
      lacher(i);
      var depart = avant >= 0 && photos[avant].place ? avant : i;
      cadrer(cadrage(i), 1000, function (e) {
        var a = ecran(depart, vue), b = ecran(i, vue);
        poser(placeVignette([a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e]));
      });
    }
    function majBoutons() {
      situer.forEach(function (b) {
        b.setAttribute("aria-pressed", ouverte ? "true" : "false");
        b.querySelector(".mot").textContent = ouverte ? textes.revenir : textes.situer;
        b.querySelector("small").hidden = ouverte;
      });
    }
    situer.forEach(function (b) { b.addEventListener("click", function () { if (ouverte) fermer(); else ouvrir(); }); });
    atlas.querySelector(".wp-retour").addEventListener("click", fermer);
    vol.addEventListener("click", fermer);
    window.addEventListener("resize", function () {
      if (!ouverte) return;
      vue = cadrage(actuelle);
      svg.setAttribute("viewBox", vue.join(" "));
      echelle();
      poser(placeVignette(ecran(actuelle, vue)));
    });

    // Les grandes photos et la carte ne se chargent qu'à l'approche du panneau
    function approcher() {
      if (proche) return;
      proche = true;
      suivre();
      if (adresseCarte && window.fetch) chargerCarte().catch(function () {});
    }
    if ("IntersectionObserver" in window) {
      var guet = new IntersectionObserver(function (entrees) {
        if (entrees.some(function (en) { return en.isIntersecting; })) { approcher(); guet.disconnect(); }
      }, { rootMargin: "800px 0px" });
      guet.observe(piste);
    } else {
      approcher();
    }
    mesurer();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(mesurer);
  }

  /* ---------- Visionneuse plein écran ---------- */

  var dialogue = document.querySelector("dialog.visionneuse");
  if (!dialogue || typeof dialogue.showModal !== "function" || !window.history.pushState) return;

  var cadre = dialogue.querySelector(".v-cadre"),
      lienImage = dialogue.querySelector(".v-image"),
      apercu = dialogue.querySelector(".v-apercu"),
      grande = dialogue.querySelector(".v-grande"),
      lienTitre = dialogue.querySelector(".v-titre a"),
      boutonPexels = dialogue.querySelector(".v-pexels"),
      texteRang = dialogue.querySelector(".v-rang");
  var LARGEURS = [800, 1200, 1600, 2200, 3000];
  var nomSite = document.querySelector('meta[property="og:site_name"]');
  var suffixe = nomSite ? " — " + nomSite.getAttribute("content") : "";
  var titreOrigine = document.title;
  var liens = [], rang = 0, poussee = false, balayage = false, depart = null;

  function photo(lien) {
    var img = lien.querySelector("img");
    var base = img.getAttribute("src").split("?")[0];
    return {
      page: lien.getAttribute("href"),
      pexels: lien.getAttribute("data-pexels"),
      titre: img.getAttribute("alt"),
      base: base,
      id: (base.match(/photos\/(\d+)/) || ["", ""])[1],
      apercu: img.currentSrc || img.src,
      ratio: img.getAttribute("width") / img.getAttribute("height"),
      couleur: lien.style.backgroundColor
    };
  }

  function sources(base) {
    return LARGEURS.map(function (l) {
      return base + "?auto=compress&cs=tinysrgb&w=" + l + " " + l + "w";
    }).join(", ");
  }

  function largeurAffichee(ratio) {
    var boite = cadre.getBoundingClientRect();
    return Math.ceil(Math.min(boite.width, boite.height * ratio)) || window.innerWidth;
  }

  function precharger(i) {
    var lien = liens[(i + liens.length) % liens.length];
    if (!lien) return;
    var p = photo(lien), img = new Image();
    img.sizes = largeurAffichee(p.ratio) + "px";
    img.srcset = sources(p.base);
  }

  function afficher() {
    var p = photo(liens[rang]);
    lienImage.style.setProperty("--r", p.ratio);
    lienImage.style.backgroundColor = p.couleur;
    lienImage.href = p.pexels;
    lienImage.setAttribute("data-goatcounter-click", "pexels-image-" + p.id);
    boutonPexels.href = p.pexels;
    boutonPexels.setAttribute("data-goatcounter-click", "pexels-" + p.id);
    boutonPexels.setAttribute("data-goatcounter-title", p.titre);
    lienTitre.href = p.page;
    lienTitre.textContent = p.titre;
    texteRang.textContent = (rang + 1) + " / " + liens.length;
    apercu.src = p.apercu;
    grande.classList.remove("prete");
    grande.removeAttribute("srcset");
    grande.removeAttribute("src");
    grande.alt = p.titre;
    grande.sizes = largeurAffichee(p.ratio) + "px";
    grande.srcset = sources(p.base);
    grande.src = p.base + "?auto=compress&cs=tinysrgb&w=1600";
    document.title = p.titre + suffixe;
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({ path: p.page, title: p.titre });
    }
    precharger(rang + 1);
    precharger(rang - 1);
  }

  function noter() {
    var etat = { visionneuse: liens[rang].getAttribute("href") };
    if (poussee) {
      history.replaceState(etat, "", etat.visionneuse);
    } else {
      history.pushState(etat, "", etat.visionneuse);
      poussee = true;
    }
  }

  function ouvrir(i) {
    rang = i;
    if (!dialogue.open) {
      dialogue.showModal();
      document.documentElement.classList.add("v-ouverte");
    }
    afficher();
    noter();
  }

  function aller(sens) {
    if (liens.length < 2) return;
    rang = (rang + sens + liens.length) % liens.length;
    afficher();
    noter();
  }

  grande.addEventListener("load", function () { grande.classList.add("prete"); });

  document.addEventListener("click", function (ev) {
    if (ev.defaultPrevented || ev.button !== 0 || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    var lien = ev.target.closest ? ev.target.closest("a.carreau") : null;
    if (!lien || !lien.getAttribute("data-pexels")) return;
    var grille = lien.closest(".grille");
    liens = Array.prototype.slice.call(grille.querySelectorAll("a.carreau"));
    ev.preventDefault();
    ouvrir(liens.indexOf(lien));
  });

  dialogue.querySelector(".v-precedente").addEventListener("click", function () { aller(-1); });
  dialogue.querySelector(".v-suivante").addEventListener("click", function () { aller(1); });
  dialogue.querySelector(".v-fermer").addEventListener("click", function () { dialogue.close(); });

  dialogue.addEventListener("keydown", function (ev) {
    if (ev.key === "ArrowRight") { ev.preventDefault(); aller(1); }
    else if (ev.key === "ArrowLeft") { ev.preventDefault(); aller(-1); }
  });

  /* Fermeture : bouton, touche Échap, clic à côté de la photo ou retour arrière. */
  dialogue.addEventListener("close", function () {
    document.documentElement.classList.remove("v-ouverte");
    document.title = titreOrigine;
    if (poussee) {
      poussee = false;
      history.back();
    }
    var lien = liens[rang];
    if (lien) {
      lien.focus({ preventScroll: true });
      lien.scrollIntoView({ block: "nearest" });
    }
  });

  cadre.addEventListener("click", function (ev) {
    if (ev.target === cadre) dialogue.close();
  });

  window.addEventListener("popstate", function (ev) {
    var etat = ev.state && ev.state.visionneuse;
    if (dialogue.open && !etat) {
      poussee = false;
      dialogue.close();
    } else if (!dialogue.open && etat) {
      location.reload();
    }
  });

  window.addEventListener("pageshow", function (ev) {
    if (ev.persisted && dialogue.open && !(history.state && history.state.visionneuse)) {
      poussee = false;
      dialogue.close();
    }
  });

  /* Au doigt : glisser vers la gauche ou la droite pour changer de photo. */
  cadre.addEventListener("pointerdown", function (ev) {
    balayage = false;
    depart = ev.pointerType === "mouse" ? null : { x: ev.clientX, y: ev.clientY };
  });
  cadre.addEventListener("pointerup", function (ev) {
    if (!depart) return;
    var dx = ev.clientX - depart.x, dy = ev.clientY - depart.y;
    depart = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) {
      balayage = true;
      aller(dx < 0 ? 1 : -1);
    }
  });
  cadre.addEventListener("pointercancel", function () { depart = null; });
  lienImage.addEventListener("click", function (ev) {
    if (balayage) { ev.preventDefault(); balayage = false; }
  });
})();
